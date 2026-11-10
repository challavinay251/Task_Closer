
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.views.decorators.http import require_POST

from .forms import LoginForm


# ==========================================
# LOGIN VIEW
# ==========================================

def login_view(request):

    # Redirect already authenticated users
    if request.user.is_authenticated:

        if request.user.role == 'ADMIN':
            return redirect('/dashboard/admin/')

        return redirect('/dashboard/employee/')

    form = LoginForm(request, data=request.POST or None)

    if request.method == 'POST':

        if form.is_valid():

            user = form.get_user()

            # Authenticate and create session
            login(request, user)

            # Role-based dashboard redirection
            if user.role == 'ADMIN':
                return redirect('/dashboard/admin/')

            elif user.role == 'EMPLOYEE':
                return redirect('/dashboard/employee/')

    return render(
        request,
        'accounts/login.html',
        {'form': form}
    )


# ==========================================
# LOGOUT VIEW
# ==========================================

@require_POST
def logout_view(request):

    logout(request)

    return redirect('/accounts/login/')
