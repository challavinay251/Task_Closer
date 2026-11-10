
from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [

    path(
        '',
        views.task_list,
        name='task_list'
    ),

    path(
        'create/',
        views.task_create,
        name='task_create'
    ),

    path(
        '<int:pk>/',
        views.task_detail,
        name='task_detail'
    ),

    path(
        'my-tasks/',
        views.employee_task_list,
        name='employee_task_list'
    ),


]
