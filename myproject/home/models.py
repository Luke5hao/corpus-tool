from django.db import models
from django.contrib.auth.models import User
from .text_processing import tokenize_and_clean  # import the text processing function

class TextEntry(models.Model):
    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.text

    def save(self, *args, **kwargs):
        # Process the text before saving to the database
        self.text = tokenize_and_clean(self.text)
        super().save(*args, **kwargs)