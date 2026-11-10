
from django.urls import path
from . import views


app_name = 'accounts'


urlpatterns = [

    # User Login
    path(
        'login/',
        views.login_view,
        name='login'
    ),

    # User Logout
    path(
        'logout/',
        views.logout_view,
        name='logout'
    ),

]
