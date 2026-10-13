import os

from django.db import models


class FileItem(models.Model):
    file = models.FileField(upload_to="uploads/")
    name = models.CharField(max_length=255, blank=True)
    extension = models.CharField(max_length=10, blank=True)
    size = models.BigIntegerField(default=0)
    uploaded_by = models.CharField(max_length=100, default="Студент")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.file:
            self.name = os.path.basename(self.file.name)
            self.extension = os.path.splitext(self.name)[1].lower()
            self.size = self.file.size
        super().save(*args, **kwargs)

    def get_formatted_size(self):
        return f"{self.size / 1024.0:.2f} KB"

    def __str__(self):
        return self.name
