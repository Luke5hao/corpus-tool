from django.db import models
from django.contrib.auth.models import User

class TextEntry(models.Model):
    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.text