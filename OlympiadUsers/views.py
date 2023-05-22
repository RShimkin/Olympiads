from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm

from .forms import SignUpForm, ProfileForm
from OlympiadMainApp.models import Profile

class SignUpView(generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/signup.html'

def RegisterUserView(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        form.save()
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'title': 'Регистрация', 'form': form})

def ProfileView(request):
    us = request.user
    print('user:', us)
    prof, _ = Profile.objects.get_or_create(user=us)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=prof)
        form.save()
    else:
        form = ProfileForm()
    return render(request, 'accounts/profile.html', {'title': 'Профиль', 'form': form})
