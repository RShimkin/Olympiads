from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Profile

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    username = forms.CharField(
        label = 'Придумайте имя пользователя',
        max_length = 200,
        required = True,
        widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password1 = forms.CharField(
        label = 'Придумайте пароль',
        help_text = "(не менее 8 символов, не только цифры)",
        required = True,
        widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        required = True,
        label = 'Повторите пароль',
        widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password again'})
    )

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['location', 'birth_date', 'year']