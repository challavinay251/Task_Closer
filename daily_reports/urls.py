
from django.urls import path
from . import views

app_name = 'daily_reports'

urlpatterns = [

    # Employee Daily Reports
    path(
        'create/',
        views.create_daily_report,
        name='create_daily_report'
    ),

    path(
        'my-reports/',
        views.employee_report_history,
        name='employee_report_history'
    ),

    path(
        'my-reports/<int:report_id>/edit/',
        views.edit_revision_report,
        name='edit_revision_report'
    ),

    # Admin Daily Reports
    path(
        'admin/',
        views.admin_daily_reports,
        name='admin_daily_reports'
    ),

    path(
        'admin/<int:report_id>/',
        views.admin_report_detail,
        name='admin_report_detail'
    ),

    path(
        'admin/<int:report_id>/review/',
        views.review_daily_report,
        name='review_daily_report'
    ),

]
