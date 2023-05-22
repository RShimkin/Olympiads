from django.urls import path

from .views import RegisterUserView, SignUpView, ProfileView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('profile/', ProfileView, name='profile')
]