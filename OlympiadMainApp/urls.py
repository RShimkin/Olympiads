from django.urls import path, re_path

from .views import *

urlpatterns = [
    path('', code, name='home'),
    path('tasks/', tasks, name='tasks'),
    path('edit_stask/<task_oid>/', edit_stask, name='editstask'),
    path('view_stask/<task_oid>/', view_stask, name='viewstask'),
    path('createstask/', create_stask, name='createstask'),
    path('stask/<task_oid>/', stask, name='stask'),
    #path('createtask/', create_task, name='createtaskdef'),
    #path('createtask/<olymp_name>/', create_task, name='createtask'),
    #path('updatetask/<task_name>/', update_task, name='updatetask'),
    path('updatetask/<task_oid>/', update_task, name='updatetask'),
    path('olympiads/', olympiads, name='olympiads'),
    path('createolympiad', create_olympiad, name='createolympiad'),
    path('olympiad/<olymp_name>/', olympiad, name='olympiad'),
    path('test/', test, name='test')
]