from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import logout
from django.contrib.auth.models import Group
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from .forms import *
from .models import Profile

def logout_request(request):
	logout(request)
	messages.info(request, "Вы разлогинились") 
	return redirect("home")

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
    user_type_set = request.user.profile.user_type != ''
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        user_type_form = UserTypeForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid() and user_type_form.is_valid():
            user_form.save()
            profile_form.save()
            user_type_data = user_type_form.cleaned_data
            request.user.profile.user_type = user_type_data['usertype']
            if user_type_data['usertype'] == UserType.CREATOR:
                group = Group.objects.get(name='Creators')
                request.user.groups.add(group)
            else:
                group = Group.objects.get(name='Participants')
                request.user.groups.add(group)
            request.user.save()
            #messages.success(request, _('Your profile was successfully updated!'))
            #return redirect('settings:profile')
            return render(request, 'accounts/profile.html', {
                'user_form': user_form,
                'profile_form': profile_form,
                'user_type_form': user_type_form,
                'user_type_set': user_type_set,
            })
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
        user_type_form = UserTypeForm()
    return render(request, 'accounts/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_type_form': user_type_form,
        'user_type_set': user_type_set,
    })

def view403(request):
    return render(request, 'accounts/403.html')
