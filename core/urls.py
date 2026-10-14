from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from drive import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("", views.index, name="index"),
    path("download/<int:file_id>/", views.download_file, name="download_file"),
    path("api/sync/list/", views.api_sync_list, name="api_sync_list"),
    path("register/", views.register, name="register"),
    path("preview/<int:file_id>/", views.preview_file, name="preview_file"),
]
