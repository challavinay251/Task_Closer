
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.utils import timezone

from employees.models import Employee
from tasks.models import Task
from daily_reports.models import DailyReport
import json
from datetime import timedelta

from django.db.models import Avg, Count, Q


# ==========================================
# ADMIN DASHBOARD
# ==========================================

@login_required
def admin_dashboard(request):

    # Only Admin users can access this page
    if request.user.role != 'ADMIN':
        return redirect('dashboard:employee_dashboard')

    today = timezone.localdate()

    # --------------------------------------
    # EMPLOYEE STATISTICS
    # --------------------------------------

    total_employees = Employee.objects.count()

    active_employees = Employee.objects.filter(
        user__is_active=True
    ).count()

    # --------------------------------------
    # TASK STATISTICS
    # --------------------------------------

    tasks = Task.objects.all()

    total_tasks = tasks.count()

    pending_tasks = tasks.filter(
        status=Task.Status.PENDING
    ).count()

    in_progress_tasks = tasks.filter(
        status=Task.Status.IN_PROGRESS
    ).count()

    completed_tasks = tasks.filter(
        status=Task.Status.COMPLETED
    ).count()

    overdue_tasks = tasks.filter(
        due_date__lt=today
    ).exclude(
        status=Task.Status.COMPLETED
    ).count()

    average_task_progress = tasks.aggregate(
        average=Avg('progress')
    )['average'] or 0

    average_task_progress = round(average_task_progress)

    # --------------------------------------
    # DAILY REPORT STATISTICS
    # --------------------------------------

    reports = DailyReport.objects.all()

    today_reports = reports.filter(
        report_date=today
    )

    total_reports_today = today_reports.count()

    pending_review_reports = reports.filter(
        status=DailyReport.Status.SUBMITTED
    ).count()

    approved_reports = reports.filter(
        status=DailyReport.Status.APPROVED
    ).count()

    rejected_reports = reports.filter(
        status=DailyReport.Status.REJECTED
    ).count()

    revision_reports = reports.filter(
        status=DailyReport.Status.REVISION
    ).count()

    # --------------------------------------
    # RECENT TASKS
    # --------------------------------------

    recent_tasks = tasks.select_related(
        'assigned_to__user',
        'assigned_by'
    ).order_by(
        '-created_at'
    )[:5]

    # --------------------------------------
    # RECENT DAILY REPORTS
    # --------------------------------------

    recent_reports = reports.select_related(
        'employee__user',
        'reviewed_by'
    ).order_by(
        '-created_at'
    )[:5]

    # --------------------------------------
    # EMPLOYEE-WISE TASK PROGRESS
    # --------------------------------------

    employee_task_progress = Employee.objects.select_related(
        'user'
    ).annotate(
        total_tasks=Avg('assigned_tasks__progress')
    ).order_by(
        'user__first_name'
    )

    # --------------------------------------
    # DASHBOARD CONTEXT
    # --------------------------------------

    context = {
        # Employees
        'total_employees': total_employees,
        'active_employees': active_employees,

        # Tasks
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks,
        'overdue_tasks': overdue_tasks,
        'average_task_progress': average_task_progress,

        # Reports
        'total_reports_today': total_reports_today,
        'pending_review_reports': pending_review_reports,
        'approved_reports': approved_reports,
        'rejected_reports': rejected_reports,
        'revision_reports': revision_reports,

        # Recent activity
        'recent_tasks': recent_tasks,
        'recent_reports': recent_reports,

        # Employee progress
        'employee_task_progress': employee_task_progress,
    }

    return render(
        request,
        'admin/dashboard.html',
        context
    )


# ==========================================
# EMPLOYEE DASHBOARD
# ==========================================

@login_required
def employee_dashboard(request):

    # Only Employee users can access this page
    if request.user.role != 'EMPLOYEE':
        return redirect('dashboard:admin_dashboard')

    # Get the logged-in employee profile
    employee = get_object_or_404(
        Employee,
        user=request.user
    )

    today = timezone.localdate()

    # --------------------------------------
    # EMPLOYEE TASKS
    # --------------------------------------

    tasks = Task.objects.filter(
        assigned_to=employee
    )

    total_tasks = tasks.count()

    pending_tasks = tasks.filter(
        status=Task.Status.PENDING
    ).count()

    in_progress_tasks = tasks.filter(
        status=Task.Status.IN_PROGRESS
    ).count()

    completed_tasks = tasks.filter(
        status=Task.Status.COMPLETED
    ).count()

    overdue_tasks = tasks.filter(
        due_date__lt=today
    ).exclude(
        status=Task.Status.COMPLETED
    ).count()

    average_task_progress = tasks.aggregate(
        average=Avg('progress')
    )['average'] or 0

    average_task_progress = round(average_task_progress)

    # --------------------------------------
    # TODAY'S ASSIGNED TASKS
    # --------------------------------------

    todays_tasks = tasks.filter(
        start_date__lte=today,
        due_date__gte=today
    ).exclude(
        status=Task.Status.COMPLETED
    ).order_by(
        'due_date'
    )

    # --------------------------------------
    # RECENT TASKS
    # --------------------------------------

    recent_tasks = tasks.order_by(
        '-created_at'
    )[:5]

    # --------------------------------------
    # DAILY REPORT STATISTICS
    # --------------------------------------

    employee_reports = DailyReport.objects.filter(
        employee=employee
    )

    todays_report = employee_reports.filter(
        report_date=today
    ).first()

    total_reports = employee_reports.count()

    approved_reports = employee_reports.filter(
        status=DailyReport.Status.APPROVED
    ).count()

    revision_reports = employee_reports.filter(
        status=DailyReport.Status.REVISION
    ).count()

    rejected_reports = employee_reports.filter(
        status=DailyReport.Status.REJECTED
    ).count()

    recent_reports = employee_reports.select_related(
        'reviewed_by'
    ).order_by(
        '-report_date',
        '-created_at'
    )[:5]

    # --------------------------------------
    # DASHBOARD CONTEXT
    # --------------------------------------

    context = {
        'employee': employee,

        # Task statistics
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks,
        'overdue_tasks': overdue_tasks,
        'average_task_progress': average_task_progress,

        # Task lists
        'todays_tasks': todays_tasks,
        'recent_tasks': recent_tasks,

        # Daily reports
        'todays_report': todays_report,
        'total_reports': total_reports,
        'approved_reports': approved_reports,
        'revision_reports': revision_reports,
        'rejected_reports': rejected_reports,
        'recent_reports': recent_reports,
    }

    return render(
        request,
        'employee/dashboard.html',
        context
    )


# ==========================================
# ADMIN ANALYTICS
# ==========================================

@login_required
def admin_analytics(request):

    # Only Admin users can access this page
    if request.user.role != 'ADMIN':
        return redirect('dashboard:employee_dashboard')

    today = timezone.localdate()
    start_date = today - timedelta(days=29)

    # --------------------------------------
    # EMPLOYEE ANALYTICS
    # --------------------------------------

    employees = Employee.objects.select_related('user')

    total_employees = employees.count()

    active_employees = employees.filter(
        employment_status='ACTIVE',
        user__is_active=True
    ).count()

    inactive_employees = total_employees - active_employees

    # --------------------------------------
    # TASK ANALYTICS
    # --------------------------------------

    tasks = Task.objects.all()

    total_tasks = tasks.count()

    pending_tasks = tasks.filter(
        status=Task.Status.PENDING
    ).count()

    in_progress_tasks = tasks.filter(
        status=Task.Status.IN_PROGRESS
    ).count()

    completed_tasks = tasks.filter(
        status=Task.Status.COMPLETED
    ).count()

    on_hold_tasks = tasks.filter(
        status=Task.Status.ON_HOLD
    ).count()

    overdue_tasks = tasks.filter(
        due_date__lt=today
    ).exclude(
        status=Task.Status.COMPLETED
    ).count()

    average_task_progress = tasks.aggregate(
        average=Avg('progress')
    )['average'] or 0

    average_task_progress = round(average_task_progress)

    completion_rate = round(
        (completed_tasks / total_tasks) * 100
    ) if total_tasks else 0

    # --------------------------------------
    # PRIORITY ANALYTICS
    # --------------------------------------

    low_priority_tasks = tasks.filter(
        priority=Task.Priority.LOW
    ).count()

    medium_priority_tasks = tasks.filter(
        priority=Task.Priority.MEDIUM
    ).count()

    high_priority_tasks = tasks.filter(
        priority=Task.Priority.HIGH
    ).count()

    urgent_priority_tasks = tasks.filter(
        priority=Task.Priority.URGENT
    ).count()

    # --------------------------------------
    # EMPLOYEE PERFORMANCE
    # --------------------------------------

    employee_performance = Employee.objects.select_related(
        'user'
    ).annotate(
        total_assigned_tasks=Count('assigned_tasks'),
        completed_assigned_tasks=Count(
            'assigned_tasks',
            filter=Q(
                assigned_tasks__status=Task.Status.COMPLETED
            )
        ),
        average_progress=Avg('assigned_tasks__progress')
    ).order_by(
        '-average_progress',
        'user__first_name'
    )

    # --------------------------------------
    # DAILY REPORT ANALYTICS
    # --------------------------------------

    reports = DailyReport.objects.all()

    total_reports = reports.count()

    submitted_reports = reports.filter(
        status=DailyReport.Status.SUBMITTED
    ).count()

    approved_reports = reports.filter(
        status=DailyReport.Status.APPROVED
    ).count()

    rejected_reports = reports.filter(
        status=DailyReport.Status.REJECTED
    ).count()

    revision_reports = reports.filter(
        status=DailyReport.Status.REVISION
    ).count()

    # --------------------------------------
    # DAILY REPORT TRENDS - LAST 30 DAYS
    # --------------------------------------

    report_trends = []

    for day_offset in range(29, -1, -1):

        report_day = today - timedelta(days=day_offset)

        report_count = reports.filter(
            report_date=report_day
        ).count()

        report_trends.append({
            'date': report_day.strftime('%d %b'),
            'count': report_count,
        })

    report_trend_labels = [
        item['date'] for item in report_trends
    ]

    report_trend_values = [
        item['count'] for item in report_trends
    ]

    # --------------------------------------
    # ANALYTICS CONTEXT
    # --------------------------------------

    context = {
        # Employees
        'total_employees': total_employees,
        'active_employees': active_employees,
        'inactive_employees': inactive_employees,

        # Tasks
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks,
        'on_hold_tasks': on_hold_tasks,
        'overdue_tasks': overdue_tasks,
        'average_task_progress': average_task_progress,
        'completion_rate': completion_rate,

        # Priority
        'low_priority_tasks': low_priority_tasks,
        'medium_priority_tasks': medium_priority_tasks,
        'high_priority_tasks': high_priority_tasks,
        'urgent_priority_tasks': urgent_priority_tasks,

        # Employee performance
        'employee_performance': employee_performance,

        # Reports
        'total_reports': total_reports,
        'submitted_reports': submitted_reports,
        'approved_reports': approved_reports,
        'rejected_reports': rejected_reports,
        'revision_reports': revision_reports,

        # Report trends
        'report_trend_labels': json.dumps(report_trend_labels),
        'report_trend_values': json.dumps(report_trend_values),
        'analytics_start_date': start_date,
        'analytics_end_date': today,
    }

    return render(
        request,
        'admin/analytics.html',
        context
    )

