from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_ADMIN = 'admin'
    ROLE_TEACHER = 'teacher'
    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_TEACHER, 'Teacher'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_TEACHER)

    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    def is_teacher(self):
        return self.role == self.ROLE_TEACHER
