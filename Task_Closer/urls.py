
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from accounts import views as account_views


urlpatterns = [

    # ==========================================
    # HOME PAGE - LOGIN
    # ==========================================

    path(
        '',
        account_views.login_view,
        name='home'
    ),

    # ==========================================
    # DJANGO ADMINISTRATION
    # ==========================================

    path(
        'admin/',
        admin.site.urls
    ),

    # ==========================================
    # ACCOUNTS
    # ==========================================

    path(
        'accounts/',
        include('accounts.urls')
    ),

    # ==========================================
    # DASHBOARDS
    # ==========================================

    path(
        'dashboard/',
        include('dashboard.urls')
    ),

    # ==========================================
    # EMPLOYEE MANAGEMENT
    # ==========================================

    path(
        'employees/',
        include('employees.urls')
    ),

    # ==========================================
    # TASK MANAGEMENT
    # ==========================================

    path(
        'tasks/',
        include('tasks.urls')
    ),

    # ==========================================
    # DAILY REPORTS
    # ==========================================

    path(
        'daily-reports/',
        include('daily_reports.urls')
    ),

]

# ==========================================================
# CUSTOM ERROR HANDLERS
# ==========================================================

handler404 = "core.views.custom_404"

handler500 = "core.views.custom_500"

# ==========================================
# MEDIA FILES - DEVELOPMENT
# ==========================================

if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
