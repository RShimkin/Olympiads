from django.urls import path

from .views import RegisterUserView, SignUpView, ProfileView, update_profile

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('profile/', update_profile, name='update_profile')
]