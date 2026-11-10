
from django.urls import path
from . import views


app_name = 'dashboard'


urlpatterns = [

    # Admin Dashboard
    path(
        'admin/',
        views.admin_dashboard,
        name='admin_dashboard'
    ),

    # Admin Analytics
    path(
        'admin/analytics/',
        views.admin_analytics,
        name='admin_analytics'
    ),

    # Employee Dashboard
    path(
        'employee/',
        views.employee_dashboard,
        name='employee_dashboard'
    ),

]
