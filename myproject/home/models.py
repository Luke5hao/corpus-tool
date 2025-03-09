from django.db import models
from django.contrib.auth.models import User
from .text_processing import tokenize_and_clean

class TextEntry(models.Model):
    text = models.TextField()  # Original text
    processed_text = models.TextField(blank=True)  # Processed/cleaned text
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Text entries"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.text[:50]}..." if len(self.text) > 50 else self.text

    def save(self, *args, **kwargs):
        # Store original text in processed_text field after cleaning
        if not self.processed_text:  # Only process if not already processed
            self.processed_text = tokenize_and_clean(self.text)
        super().save(*args, **kwargs)

    def get_word_count(self):
        return len(self.processed_text.split())