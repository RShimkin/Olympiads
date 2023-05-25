from django.urls import path

from .views import *

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('profile/', update_profile, name='update_profile'),
    path('logout_request/', logout_request, name='custom_logout'),
    path('403', view403, name='403')
]