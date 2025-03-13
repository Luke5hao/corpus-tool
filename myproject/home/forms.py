from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegistrationForm(UserCreationForm):
    class_id = forms.CharField(max_length=50, required=True, help_text='Enter your class ID')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'class_id']