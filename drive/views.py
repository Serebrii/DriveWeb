from django.shortcuts import render, redirect

from .models import FileItem


def index(request):
    filter_ext = request.GET.get("filter", "")
    sort_order = request.GET.get("sort", "desc")  # desc або asc

    files = FileItem.objects.all()

    if filter_ext in [".cpp", ".png"]:
        files = files.filter(extension=filter_ext)

    if sort_order == "asc":
        files = files.order_by("updated_at")
    else:
        files = files.order_by("-updated_at")

    if request.method == "POST" and request.FILES.get("upload_file"):
        uploaded_file = request.FILES["upload_file"]
        FileItem.objects.create(file=uploaded_file)
        return redirect("index")

    if request.method == "POST" and "delete_id" in request.POST:
        file_id = request.POST.get("delete_id")
        try:
            file_to_delete = FileItem.objects.get(id=file_id)
            file_to_delete.file.delete()
            file_to_delete.delete()
        except FileItem.DoesNotExist:
            pass
        return redirect("index")

    context = {
        "files": files,
        "current_filter": filter_ext,
        "current_sort": sort_order,
    }
    return render(request, "drive/index.html", context)
