import mimetypes
import os

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import FileResponse, Http404
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect

from .models import FileItem


@login_required
def index(request):
    if request.method == "POST":
        files = request.FILES.getlist("files") or request.FILES.getlist("file")
        if files:
            for f in files:
                FileItem.objects.create(
                    file=f, uploaded_by=request.user, edited_by=request.user
                )
            return redirect("index")

        elif "delete_id" in request.POST:
            file_to_delete = FileItem.objects.filter(
                id=request.POST["delete_id"], uploaded_by=request.user
            ).first()
            if file_to_delete:
                if file_to_delete.file:
                    file_to_delete.file.delete(save=False)
                file_to_delete.delete()
            return redirect("index")

    files = FileItem.objects.filter(uploaded_by=request.user)

    filter_ext = request.GET.get("filter")
    if filter_ext and filter_ext != "all":
        files = files.filter(extension=filter_ext)

    sort_by = request.GET.get("sort")
    if sort_by == "date_asc":
        files = files.order_by("updated_at")
    elif sort_by == "date_desc":
        files = files.order_by("-updated_at")

    return render(
        request,
        "index.html",
        {
            "files": files,
            "current_filter": filter_ext or "all",
            "current_sort": sort_by or "date_desc",
        },
    )


@login_required
def download_file(request, file_id):
    file_item = get_object_or_404(FileItem, id=file_id, uploaded_by=request.user)

    if file_item.file and os.path.exists(file_item.file.path):
        return FileResponse(
            file_item.file.open("rb"), as_attachment=True, filename=file_item.name
        )

    raise Http404(
        "Фізичний файл не знайдено на сервері (можливо, він був видалений при перезапуску контейнера). Спробуйте завантажити його заново."
    )


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматичний вхід після реєстрації
            return redirect("index")
    else:
        form = UserCreationForm()
    return render(request, "register.html", {"form": form})


@login_required
def api_sync_list(request):
    """
    API-ендпоінт для отримання списку файлів поточного користувача.
    Використовується клієнтським скриптом синхронізації.
    """
    files = FileItem.objects.filter(uploaded_by=request.user)
    data = []
    for f in files:
        data.append(
            {
                "id": f.id,
                "name": f.name,
                "size": f.size,
                "updated_at": f.updated_at.timestamp(),
            }
        )
    return JsonResponse({"files": data})


@login_required
def preview_file(request, file_id):
    file_item = get_object_or_404(FileItem, id=file_id, uploaded_by=request.user)
    if file_item.file and os.path.exists(file_item.file.path):
        mime_type, _ = mimetypes.guess_type(file_item.file.path)
        return FileResponse(
            file_item.file.open("rb"), content_type=mime_type or "text/plain"
        )
    raise Http404("Файл не знайдено на сервері")
