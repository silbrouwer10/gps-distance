import os
import traceback
import uuid

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse, HttpResponse
from django.shortcuts import render

from .forms import CSVUploadForm
from .utils.report_builder import build_graph_only_pdf


def upload_csv_view(request):
    if request.method == "POST":
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data["csv_file"]

            uploads_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
            os.makedirs(uploads_dir, exist_ok=True)
            fs = FileSystemStorage(location=uploads_dir)

            unique_name = f"{uuid.uuid4().hex}_{csv_file.name}"
            file_path = fs.save(unique_name, csv_file)
            full_path = fs.path(file_path)

            try:
                report = build_graph_only_pdf(full_path, settings.MEDIA_ROOT)
                return FileResponse(
                    open(report["pdf_path"], "rb"),
                    content_type="application/pdf",
                    as_attachment=True,
                    filename=report["pdf_filename"],
                )
            except Exception as exc:
                traceback.print_exc()
                return HttpResponse(
                    f"Fout tijdens verwerken van CSV: {exc}",
                    status=400,
                )
    else:
        form = CSVUploadForm()

    return render(request, "gpsapp/upload.html", {"form": form})


def generate_pdf_view(request):
    return HttpResponse("Gebruik het uploadformulier op de homepage.", status=400)
