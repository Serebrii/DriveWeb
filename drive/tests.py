from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from .models import FileItem


class DriveSystemTests(TestCase):

    def setUp(self):
        """Налаштування початкових даних для кожного тесту"""
        self.client = Client()

        self.user1 = User.objects.create_user(username="user1", password="password123")
        self.user2 = User.objects.create_user(username="user2", password="password123")

        self.login_url = reverse("login")
        self.index_url = reverse("index")

    def test_file_item_creation_and_metadata(self):
        """Тест 1: Перевірка автоматичного вилучення метаданих у моделі FileItem"""
        test_file = SimpleUploadedFile("test_script.cpp", b"int main() { return 0; }")
        file_item = FileItem.objects.create(
            file=test_file, uploaded_by=self.user1, edited_by=self.user1
        )

        self.assertEqual(file_item.name, "test_script.cpp")
        self.assertEqual(file_item.extension, ".cpp")
        self.assertGreater(file_item.size, 0)
        self.assertEqual(file_item.uploaded_by, self.user1)

    def test_login_required_redirect(self):
        """Тест 2: Перевірка захисту кабінету (переадресація неавторизованого користувача)"""
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_user_file_isolation(self):
        """Тест 3: Перевірка ізоляції кабінету (користувач 1 не бачить файли користувача 2)"""
        test_file = SimpleUploadedFile("user2_file.png", b"fake_image_data")
        FileItem.objects.create(
            file=test_file, uploaded_by=self.user2, edited_by=self.user2
        )

        self.client.login(username="user1", password="password123")
        response = self.client.get(self.index_url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "user2_file.png")

    def test_file_upload_view(self):
        """Тест 4: Перевірка завантаження файлу через POST-запит"""
        self.client.login(username="user1", password="password123")

        upload_file = SimpleUploadedFile("uploaded_doc.png", b"image_content")
        response = self.client.post(self.index_url, {"files": upload_file})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            FileItem.objects.filter(
                name="uploaded_doc.png", uploaded_by=self.user1
            ).exists()
        )

    def test_file_deletion(self):
        """Тест 5: Перевірка видалення файлу"""
        self.client.login(username="user1", password="password123")

        test_file = SimpleUploadedFile("file_to_delete.cpp", b"content")
        file_item = FileItem.objects.create(file=test_file, uploaded_by=self.user1)

        response = self.client.post(self.index_url, {"delete_id": file_item.id})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(FileItem.objects.filter(id=file_item.id).exists())

    def test_filtering_by_extension(self):
        """Тест 6: Перевірка фільтрації за розширенням (.cpp / .png)"""
        self.client.login(username="user1", password="password123")

        FileItem.objects.create(
            file=SimpleUploadedFile("code.cpp", b"cpp"), uploaded_by=self.user1
        )
        FileItem.objects.create(
            file=SimpleUploadedFile("photo.png", b"png"), uploaded_by=self.user1
        )

        response = self.client.get(self.index_url + "?filter=.cpp")
        self.assertContains(response, "code.cpp")
        self.assertNotContains(response, "photo.png")


# python manage.py test drive.tests.DriveSystemTests
