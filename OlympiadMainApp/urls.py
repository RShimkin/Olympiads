from django.urls import path, re_path

from .views import *

urlpatterns = [
    path('', code, name='home'),
    path('tasks/', tasks, name='tasks'),
    path('task/<task_name>/', task, name='task'),
    path('createtask/', create_task, name='createtaskdef'),
    path('createtask/<olymp_name>/', create_task, name='createtask'),
    path('updatetask/<task_name>/', update_task, name='updatetask'),
    path('olympiads/', olympiads, name='olympiads'),
    path('createolympiad', create_olympiad, name='createolympiad'),
    path('olympiad/<olymp_name>/', olympiad, name='olympiad'),
]