from __future__ import annotations

import mimetypes
from pathlib import Path

from django.conf import settings
from django.http import FileResponse
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import EfilingDocumentsIndex


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

        for candidate in efile_root.rglob(filename):
            try:
                c = candidate.resolve()
                c.relative_to(media_root)
                if c.is_file():
                    return c
            except Exception:
                continue
        return None
