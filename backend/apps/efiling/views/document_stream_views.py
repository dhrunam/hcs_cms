from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Iterable

from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt
from django.http import FileResponse
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import EfilingDocumentsIndex


@method_decorator(xframe_options_exempt, name="dispatch")
class EfilingDocumentStreamByIndexView(APIView):
    """
    Stream a document by EfilingDocumentsIndex id.
    Includes fallback path recovery to handle legacy/misaligned media paths.
    """

    permission_classes = [AllowAny]

    def get(self, request, document_index_id: int):
        doc_index = (
            EfilingDocumentsIndex.objects.select_related("document")
            .filter(pk=document_index_id)
            .first()
        )
        if not doc_index or not doc_index.file_part_path:
            return Response({"detail": "Document not found."}, status=404)

        self._doc_index = doc_index
        media_root = Path(settings.MEDIA_ROOT).resolve()
        direct_path = media_root / str(doc_index.file_part_path.name)
        resolved = self._resolve_existing_path(direct_path, media_root)
        if not resolved:
            return Response({"detail": "Document file missing on server."}, status=404)

        content_type, _ = mimetypes.guess_type(str(resolved))
        return FileResponse(
            open(resolved, "rb"),
            as_attachment=False,
            filename=resolved.name,
            content_type=content_type or "application/pdf",
        )

    def _resolve_existing_path(self, expected_path: Path, media_root: Path) -> Path | None:
        # Fast path
        if expected_path.exists() and expected_path.is_file():
            return expected_path

        # Fallback path discovery by filename under efile tree
        filename = expected_path.name
        efile_root = media_root / "efile"
        if not efile_root.exists() or not efile_root.is_dir():
            return None
        filing_no = (
            (
                getattr(getattr(self, "_doc_index", None), "document", None)
                and getattr(getattr(self, "_doc_index", None).document, "e_filing_number", None)
            )
            or ""
        ).strip()
        search_root = (efile_root / filing_no) if filing_no else efile_root
        if not search_root.exists() or not search_root.is_dir():
            search_root = efile_root

        # Try strict filename first.
        strict_hits = self._safe_hits(search_root.rglob(filename), media_root)
        if strict_hits:
            return strict_hits[0]

        # Case-insensitive filename match.
        filename_lower = filename.lower()
        ci_hits = self._safe_hits(
            (p for p in search_root.rglob("*") if p.is_file() and p.name.lower() == filename_lower),
            media_root,
        )
        if ci_hits:
            return ci_hits[0]

        # Heuristic match by filing number + document part stem.
        # This handles legacy path drift like document_type folder rename/case changes.
        part_stem = expected_path.stem.lower().strip()
        if filing_no:
            filing_root = efile_root / filing_no
            if filing_root.exists() and filing_root.is_dir():
                stem_hits = self._safe_hits(
                    (
                        p
                        for p in filing_root.rglob("*")
                        if p.is_file()
                        and p.suffix.lower() == ".pdf"
                        and (p.stem.lower() == part_stem if part_stem else True)
                    ),
                    media_root,
                )
                if stem_hits:
                    return stem_hits[0]
        return None

    def _safe_hits(self, candidates: Iterable[Path], media_root: Path) -> list[Path]:
        out: list[Path] = []
        for candidate in candidates:
            try:
                c = candidate.resolve()
                c.relative_to(media_root)
                if c.is_file():
                    out.append(c)
            except Exception:
                continue
        return out
