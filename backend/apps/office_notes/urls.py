from django.urls import path

from .views import OfficeNoteListCreateView, OfficeNoteUpdateView

app_name = "office_notes"

urlpatterns = [
    path("", OfficeNoteListCreateView.as_view(), name="office-note-list-create"),
    path("<int:pk>/", OfficeNoteUpdateView.as_view(), name="office-note-detail"),
]