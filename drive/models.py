import os

from django.contrib.auth.models import User
from django.db import models


class FileItem(models.Model):
    file = models.FileField(upload_to="uploads/")
    name = models.CharField(max_length=255, blank=True)
    extension = models.CharField(max_length=50, blank=True)
    size = models.IntegerField(null=True, blank=True)

    uploaded_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="uploaded_files", null=True
    )
    edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="edited_files",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.file:
            self.name = os.path.basename(self.file.name)
        self.extension = os.path.splitext(self.name)[1].lower()
        self.size = self.file.size
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
