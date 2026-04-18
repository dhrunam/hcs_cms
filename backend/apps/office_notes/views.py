from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import Efiling
from .models import OfficeNote
from .serializers import OfficeNoteSerializer


class OfficeNoteListCreateView(APIView):
    def get(self, request):
        case_id = request.query_params.get("case_id")
        if not case_id:
            return Response(
                {"error": "case_id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        notes = OfficeNote.objects.filter(efiling_id=case_id).order_by("-created_at")
        serializer = OfficeNoteSerializer(notes, many=True)
        return Response(serializer.data)

    def post(self, request):
        case_id = request.data.get("case_id")
        note_content = request.data.get("note_content")
        if not case_id or not note_content:
            return Response(
                {"error": "case_id and note_content are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not Efiling.objects.filter(id=case_id).exists():
            return Response(
                {"error": "Case not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        note = OfficeNote.objects.create(
            efiling_id=case_id,
            note_content=note_content,
            created_by=request.user,
        )
        serializer = OfficeNoteSerializer(note)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OfficeNoteUpdateView(APIView):
    def patch(self, request, pk):
        try:
            note = OfficeNote.objects.get(pk=pk)
        except OfficeNote.DoesNotExist:
            return Response(
                {"error": "Note not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        note_content = request.data.get("note_content")
        if note_content is not None:
            note.note_content = note_content
            note.updated_by = request.user
            note.save()
        serializer = OfficeNoteSerializer(note)
        return Response(serializer.data)