
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction, IntegrityError
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_POST

from employees.models import Employee
from tasks.models import Task

from .models import DailyReport, WorkEntryImage
from .forms import DailyReportForm, WorkEntryFormSet


# ==========================================
# TASK PROGRESS VALIDATION
# ==========================================

def validate_task_progress(formset):
    """
    Require progress when a task is selected.
    Prevent employees from reducing existing task progress.
    """

    is_valid = True

    for entry_form in formset.forms:

        if not hasattr(entry_form, 'cleaned_data'):
            continue

        cleaned_data = entry_form.cleaned_data

        if not cleaned_data:
            continue

        if cleaned_data.get('DELETE', False):
            continue

        task = cleaned_data.get('task')
        progress = cleaned_data.get('task_progress')

        if not task:
            continue

        if progress is None:

            entry_form.add_error(
                'task_progress',
                'Please enter the current progress for the selected task.'
            )

            is_valid = False
            continue

        if progress < task.progress:

            entry_form.add_error(
                'task_progress',
                f'Progress cannot be reduced below the current task progress of {task.progress}%.'
            )

            is_valid = False

    return is_valid


# ==========================================
# UPDATE ACTUAL TASK PROGRESS AND STATUS
# ==========================================

def update_task_progress(daily_report):
    """
    Update task progress using the highest progress
    reported for each task in this daily report.
    Progress can never move backwards.
    """

    reported_progress = {}

    work_entries = daily_report.work_entries.select_related(
        'task'
    ).filter(
        task__isnull=False,
        task_progress__isnull=False
    )

    for entry in work_entries:

        task_id = entry.task_id
        progress = entry.task_progress

        if task_id not in reported_progress:
            reported_progress[task_id] = progress
        else:
            reported_progress[task_id] = max(
                reported_progress[task_id],
                progress
            )

    for task_id, reported_value in reported_progress.items():

        task = Task.objects.select_for_update().get(
            id=task_id
        )

        # Never reduce existing progress.
        new_progress = max(
            task.progress,
            reported_value
        )

        if new_progress == 0:
            new_status = Task.Status.PENDING

        elif new_progress < 100:
            new_status = Task.Status.IN_PROGRESS

        else:
            new_status = Task.Status.COMPLETED

        task.progress = new_progress
        task.status = new_status

        if new_progress == 100 and not task.completed_at:
            task.completed_at = timezone.now()

        task.save(
            update_fields=[
                'progress',
                'status',
                'completed_at',
                'updated_at',
            ]
        )


# ==========================================
# EMPLOYEE DAILY REPORT SUBMISSION
# ==========================================

@login_required
def create_daily_report(request):

    if request.user.role != 'EMPLOYEE':
        return redirect('dashboard:admin_dashboard')

    employee = get_object_or_404(
        Employee,
        user=request.user
    )

    # ------------------------------------------
    # PRESELECT TASK FROM MY TASKS PAGE
    # ------------------------------------------

    selected_task = None
    task_id = request.GET.get('task')

    if task_id and request.method == 'GET':

        selected_task = get_object_or_404(
            Task,
            id=task_id,
            assigned_to=employee
        )

    report_instance = DailyReport(
        employee=employee
    )

    report_form = DailyReportForm(
        request.POST or None
    )

    formset_kwargs = {
        'instance': report_instance,
        'form_kwargs': {
            'employee': employee
        }
    }

    if selected_task:
        formset_kwargs['initial'] = [
            {'task': selected_task}
        ]

    work_entry_formset = WorkEntryFormSet(
        request.POST or None,
        request.FILES or None,
        **formset_kwargs
    )

    entry_image_errors = {}
    general_errors = []

    # ==========================================
    # HANDLE FORM SUBMISSION
    # ==========================================

    if request.method == 'POST':

        report_is_valid = report_form.is_valid()
        entries_are_valid = work_entry_formset.is_valid()

        progress_is_valid = False

        if entries_are_valid:
            progress_is_valid = validate_task_progress(
                work_entry_formset
            )

        if report_is_valid and entries_are_valid and progress_is_valid:

            report_date = report_form.cleaned_data['report_date']

            # --------------------------------------
            # CHECK DUPLICATE REPORT
            # --------------------------------------

            report_exists = DailyReport.objects.filter(
                employee=employee,
                report_date=report_date
            ).exists()

            if report_exists:

                report_form.add_error(
                    'report_date',
                    'You have already submitted a report for this date.'
                )

            else:

                active_entries = []

                # ----------------------------------
                # VALIDATE WORK ENTRIES AND IMAGES
                # ----------------------------------

                for index, entry_form in enumerate(
                    work_entry_formset.forms
                ):

                    if not entry_form.has_changed():
                        continue

                    cleaned_data = entry_form.cleaned_data

                    if cleaned_data.get('DELETE', False):
                        continue

                    title = cleaned_data.get('title')
                    description = cleaned_data.get('description')
                    task = cleaned_data.get('task')

                    has_activity = bool(
                        title or description or task
                    )

                    if not has_activity:
                        continue

                    active_entries.append(index)

                    uploaded_images = request.FILES.getlist(
                        f'images-{index}'
                    )

                    if not uploaded_images:

                        entry_image_errors[index] = (
                            'Please upload at least one image for this work activity.'
                        )

                # ----------------------------------
                # REQUIRE AT LEAST ONE WORK ENTRY
                # ----------------------------------

                if not active_entries:

                    general_errors.append(
                        'Please add at least one work activity to your daily report.'
                    )

                # ----------------------------------
                # SAVE REPORT AND ENTRIES
                # ----------------------------------

                if not entry_image_errors and not general_errors:

                    try:

                        with transaction.atomic():

                            daily_report = report_form.save(
                                commit=False
                            )

                            daily_report.employee = employee
                            daily_report.status = (
                                DailyReport.Status.SUBMITTED
                            )
                            daily_report.submitted_at = timezone.now()

                            daily_report.save()

                            work_entry_formset.instance = daily_report
                            work_entry_formset.save()

                            # Save uploaded images.
                            for index in active_entries:

                                entry_form = (
                                    work_entry_formset.forms[index]
                                )

                                work_entry = entry_form.instance

                                uploaded_images = request.FILES.getlist(
                                    f'images-{index}'
                                )

                                for uploaded_image in uploaded_images:

                                    WorkEntryImage.objects.create(
                                        work_entry=work_entry,
                                        image=uploaded_image
                                    )

                            # Update actual task progress and status.
                            update_task_progress(daily_report)

                        messages.success(
                            request,
                            'Your daily report has been submitted successfully.'
                        )

                        return redirect(
                            'dashboard:employee_dashboard'
                        )

                    except IntegrityError:

                        report_form.add_error(
                            'report_date',
                            'A report for this date already exists.'
                        )

    # ==========================================
    # EMPLOYEE REPORT FORM CONTEXT
    # ==========================================

    context = {
        'report_form': report_form,
        'work_entry_formset': work_entry_formset,
        'entry_image_errors': entry_image_errors,
        'general_errors': general_errors,
    }

    return render(
        request,
        'daily_reports/report_form.html',
        context
    )


# ==========================================
# ADMIN DAILY REPORT LIST
# ==========================================

@login_required
def admin_daily_reports(request):

    if request.user.role != 'ADMIN':
        return redirect('dashboard:employee_dashboard')

    reports = DailyReport.objects.select_related(
        'employee',
        'employee__user',
        'reviewed_by'
    ).prefetch_related(
        'work_entries',
        'work_entries__images'
    )

    # ------------------------------------------
    # SEARCH REPORTS
    # ------------------------------------------

    search_query = request.GET.get('q', '').strip()

    if search_query:

        reports = reports.filter(
            Q(employee__user__username__icontains=search_query) |
            Q(employee__user__first_name__icontains=search_query) |
            Q(employee__user__last_name__icontains=search_query) |
            Q(employee__employee_id__icontains=search_query) |
            Q(summary__icontains=search_query)
        )

    # ------------------------------------------
    # FILTER BY REPORT STATUS
    # ------------------------------------------

    selected_status = request.GET.get(
        'status',
        ''
    ).strip()

    valid_statuses = [
        value
        for value, label in DailyReport.Status.choices
    ]

    if selected_status in valid_statuses:

        reports = reports.filter(
            status=selected_status
        )

    # ------------------------------------------
    # REPORT STATISTICS
    # ------------------------------------------

    total_reports = DailyReport.objects.count()

    submitted_reports = DailyReport.objects.filter(
        status=DailyReport.Status.SUBMITTED
    ).count()

    approved_reports = DailyReport.objects.filter(
        status=DailyReport.Status.APPROVED
    ).count()

    rejected_reports = DailyReport.objects.filter(
        status=DailyReport.Status.REJECTED
    ).count()

    revision_reports = DailyReport.objects.filter(
        status=DailyReport.Status.REVISION
    ).count()

    # ------------------------------------------
    # PAGINATION
    # ------------------------------------------

    reports = reports.order_by(
        '-report_date',
        '-created_at'
    )

    paginator = Paginator(
        reports,
        10
    )

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(
        page_number
    )

    context = {
        'page_obj': page_obj,
        'reports': page_obj.object_list,
        'search_query': search_query,
        'selected_status': selected_status,
        'total_reports': total_reports,
        'submitted_reports': submitted_reports,
        'approved_reports': approved_reports,
        'rejected_reports': rejected_reports,
        'revision_reports': revision_reports,
        'status_choices': DailyReport.Status.choices,
    }

    return render(
        request,
        'daily_reports/admin_report_list.html',
        context
    )


# ==========================================
# ADMIN REPORT DETAIL
# ==========================================

@login_required
def admin_report_detail(request, report_id):

    if request.user.role != 'ADMIN':
        return redirect('dashboard:employee_dashboard')

    report = get_object_or_404(
        DailyReport.objects.select_related(
            'employee',
            'employee__user',
            'reviewed_by'
        ).prefetch_related(
            'work_entries',
            'work_entries__images',
            'work_entries__task'
        ),
        id=report_id
    )

    context = {
        'report': report,
    }

    return render(
        request,
        'daily_reports/admin_report_detail.html',
        context
    )


# ==========================================
# ADMIN REVIEW DAILY REPORT
# ==========================================

@login_required
@require_POST
def review_daily_report(request, report_id):

    if request.user.role != 'ADMIN':
        return redirect('dashboard:employee_dashboard')

    report = get_object_or_404(
        DailyReport,
        id=report_id
    )

    action = request.POST.get('action', '').strip()
    feedback = request.POST.get('admin_feedback', '').strip()

    allowed_actions = {
        'approve': DailyReport.Status.APPROVED,
        'reject': DailyReport.Status.REJECTED,
        'revision': DailyReport.Status.REVISION,
    }

    if action not in allowed_actions:

        messages.error(
            request,
            'Invalid review action.'
        )

        return redirect(
            'daily_reports:admin_report_detail',
            report_id=report.id
        )

    if report.status != DailyReport.Status.SUBMITTED:

        messages.error(
            request,
            'Only submitted reports can be reviewed.'
        )

        return redirect(
            'daily_reports:admin_report_detail',
            report_id=report.id
        )

    if action in ['reject', 'revision'] and not feedback:

        messages.error(
            request,
            'Please provide feedback before rejecting or requesting a revision.'
        )

        return redirect(
            'daily_reports:admin_report_detail',
            report_id=report.id
        )

    report.status = allowed_actions[action]
    report.admin_feedback = feedback
    report.reviewed_by = request.user
    report.reviewed_at = timezone.now()

    report.save(
        update_fields=[
            'status',
            'admin_feedback',
            'reviewed_by',
            'reviewed_at',
            'updated_at',
        ]
    )

    if action == 'approve':

        messages.success(
            request,
            'Daily report approved successfully.'
        )

    elif action == 'reject':

        messages.success(
            request,
            'Daily report rejected successfully.'
        )

    else:

        messages.success(
            request,
            'Revision requested successfully.'
        )

    return redirect(
        'daily_reports:admin_report_detail',
        report_id=report.id
    )


# ==========================================
# EMPLOYEE REPORT HISTORY
# ==========================================

@login_required
def employee_report_history(request):

    if request.user.role != 'EMPLOYEE':
        return redirect('dashboard:admin_dashboard')

    employee = get_object_or_404(
        Employee,
        user=request.user
    )

    reports = DailyReport.objects.filter(
        employee=employee
    ).select_related(
        'reviewed_by'
    ).prefetch_related(
        'work_entries'
    ).order_by(
        '-report_date',
        '-created_at'
    )

    search_query = request.GET.get('q', '').strip()
    selected_status = request.GET.get('status', '').strip()

    if search_query:

        reports = reports.filter(
            Q(summary__icontains=search_query) |
            Q(admin_feedback__icontains=search_query)
        )

    valid_statuses = [
        value
        for value, label in DailyReport.Status.choices
    ]

    if selected_status in valid_statuses:
        reports = reports.filter(status=selected_status)

    paginator = Paginator(
        reports,
        10
    )

    page_obj = paginator.get_page(
        request.GET.get('page')
    )

    context = {
        'page_obj': page_obj,
        'reports': page_obj.object_list,
        'search_query': search_query,
        'selected_status': selected_status,
        'status_choices': DailyReport.Status.choices,

        'total_reports': DailyReport.objects.filter(
            employee=employee
        ).count(),

        'approved_reports': DailyReport.objects.filter(
            employee=employee,
            status=DailyReport.Status.APPROVED
        ).count(),

        'revision_reports': DailyReport.objects.filter(
            employee=employee,
            status=DailyReport.Status.REVISION
        ).count(),

        'rejected_reports': DailyReport.objects.filter(
            employee=employee,
            status=DailyReport.Status.REJECTED
        ).count(),
    }

    return render(
        request,
        'daily_reports/employee_report_history.html',
        context
    )


# ==========================================
# EMPLOYEE EDIT REVISION REPORT
# ==========================================

@login_required
def edit_revision_report(request, report_id):

    # ------------------------------------------
    # EMPLOYEE ACCESS CHECK
    # ------------------------------------------

    if request.user.role != 'EMPLOYEE':
        return redirect('dashboard:admin_dashboard')

    employee = get_object_or_404(
        Employee,
        user=request.user
    )

    report = get_object_or_404(
        DailyReport,
        id=report_id,
        employee=employee,
        status=DailyReport.Status.REVISION
    )

    # ------------------------------------------
    # INITIALIZE FORMS
    # ------------------------------------------

    report_form = DailyReportForm(
        request.POST or None,
        instance=report
    )

    # Employee cannot change the original report date.
    report_form.fields['report_date'].disabled = True

    work_entry_formset = WorkEntryFormSet(
        request.POST or None,
        request.FILES or None,
        instance=report,
        form_kwargs={
            'employee': employee
        }
    )

    entry_image_errors = {}
    general_errors = []

    # ==========================================
    # HANDLE RESUBMISSION
    # ==========================================

    if request.method == 'POST':

        report_is_valid = report_form.is_valid()
        entries_are_valid = work_entry_formset.is_valid()

        progress_is_valid = False

        if entries_are_valid:

            progress_is_valid = validate_task_progress(
                work_entry_formset
            )

        if report_is_valid and entries_are_valid and progress_is_valid:

            active_entries = []

            # ----------------------------------
            # VALIDATE WORK ENTRIES AND IMAGES
            # ----------------------------------

            for index, entry_form in enumerate(
                work_entry_formset.forms
            ):

                cleaned_data = entry_form.cleaned_data

                if cleaned_data.get('DELETE', False):
                    continue

                if (
                    not entry_form.instance.pk
                    and not entry_form.has_changed()
                ):
                    continue

                title = cleaned_data.get('title')
                description = cleaned_data.get('description')
                task = cleaned_data.get('task')

                has_activity = bool(
                    title or description or task
                )

                if not has_activity:
                    continue

                active_entries.append(index)

                uploaded_images = request.FILES.getlist(
                    f'images-{index}'
                )

                existing_images = (
                    entry_form.instance.images.exists()
                    if entry_form.instance.pk
                    else False
                )

                if not uploaded_images and not existing_images:

                    entry_image_errors[index] = (
                        'Please upload at least one image for this work activity.'
                    )

            # ----------------------------------
            # REQUIRE AT LEAST ONE WORK ENTRY
            # ----------------------------------

            if not active_entries:

                general_errors.append(
                    'Please add at least one work activity.'
                )

            # ----------------------------------
            # SAVE REVISED REPORT
            # ----------------------------------

            if not entry_image_errors and not general_errors:

                try:

                    with transaction.atomic():

                        daily_report = report_form.save(
                            commit=False
                        )

                        daily_report.employee = employee
                        daily_report.status = DailyReport.Status.SUBMITTED
                        daily_report.submitted_at = timezone.now()

                        # Reset previous review information.
                        daily_report.admin_feedback = ''
                        daily_report.reviewed_by = None
                        daily_report.reviewed_at = None

                        daily_report.save()

                        work_entry_formset.instance = daily_report

                        work_entry_formset.save()

                        # Save newly uploaded evidence images.
                        for index in active_entries:

                            entry_form = work_entry_formset.forms[index]

                            work_entry = entry_form.instance

                            uploaded_images = request.FILES.getlist(
                                f'images-{index}'
                            )

                            for uploaded_image in uploaded_images:

                                WorkEntryImage.objects.create(
                                    work_entry=work_entry,
                                    image=uploaded_image
                                )

                        # Update actual task progress and status.
                        update_task_progress(daily_report)

                    messages.success(
                        request,
                        'Your revised daily report has been resubmitted successfully.'
                    )

                    return redirect(
                        'daily_reports:employee_report_history'
                    )

                except IntegrityError:

                    messages.error(
                        request,
                        'Unable to save your revised report. Please try again.'
                    )

    # ==========================================
    # TEMPLATE CONTEXT
    # ==========================================

    context = {
        'report': report,
        'report_form': report_form,
        'work_entry_formset': work_entry_formset,
        'entry_image_errors': entry_image_errors,
        'general_errors': general_errors,
    }

    return render(
        request,
        'daily_reports/edit_revision_report.html',
        context
    )
