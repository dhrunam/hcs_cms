import io
import json
from django.http import FileResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from apps.efiling.pdf_service import merge_pdfs_with_index


@csrf_exempt
@require_http_methods(["POST"])
def merge_pdfs(request):
    """
    Accept multiple PDF files (field name: files) and optional display names
    (field name: names, JSON array of strings, same order as files). Merge
    with a front page, index page (clickable), and bookmarks, return the merged PDF.
    """
    uploaded = request.FILES.getlist("files")
    if not uploaded:
        return JsonResponse(
            {"error": "No files provided. Use form field 'files' with one or more PDFs."},
            status=400,
        )

    document_names = None
    raw_names = request.POST.get("names")
    if raw_names:
        try:
            parsed = json.loads(raw_names)
            if isinstance(parsed, list) and len(parsed) == len(uploaded):
                document_names = [str(n).strip() or None for n in parsed]
                document_names = [n or f"Document {i+1}" for i, n in enumerate(document_names)]
        except (json.JSONDecodeError, TypeError):
            pass

    petitioner = (request.POST.get("petitioner_name") or "").strip()
    respondent = (request.POST.get("respondent_name") or "").strip()
    case_no = (request.POST.get("case_no") or "").strip()
    case_type = (request.POST.get("case_type") or "").strip()
    front_page = {
        "petitioner_name": petitioner,
        "respondent_name": respondent,
        "case_no": case_no,
        "case_type": case_type,
    }

    files_data: list[tuple[str, bytes]] = []
    for f in uploaded:
        if not f.name.lower().endswith(".pdf"):
            return JsonResponse(
                {"error": f"Only PDF files are allowed. Got: {f.name}"},
                status=400,
            )
        files_data.append((f.name, f.read()))

    try:
        out = io.BytesIO()
        merge_pdfs_with_index(
            files_data, out,
            document_names=document_names,
            front_page=front_page,
        )
        merged_bytes = out.getvalue()
    except Exception as e:
        return JsonResponse(
            {"error": f"Failed to merge PDFs: {str(e)}"},
            status=500,
        )

    filename = "merged_document.pdf"
    response = FileResponse(
        io.BytesIO(merged_bytes),
        as_attachment=True,
        filename=filename,
        content_type="application/pdf",
    )
    response["Content-Length"] = len(merged_bytes)
    return response
