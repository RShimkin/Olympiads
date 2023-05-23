from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from .forms import SignUpForm, ProfileForm, UserForm
from .models import Profile

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

@login_required
#@transaction.atomic
def update_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            #messages.success(request, _('Your profile was successfully updated!'))
            #return redirect('settings:profile')
            return render(request, 'accounts/profile.html', {
                'user_form': user_form,
                'profile_form': profile_form
            })
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'accounts/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })
