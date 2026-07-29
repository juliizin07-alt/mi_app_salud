from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views


urlpatterns = [

    path(
        "admin/",
        admin.site.urls
    ),
    path(
    "logout/",
    auth_views.LogoutView.as_view(),
    name="logout"
    ),

    # Login Jarvice
   path(
    "login/",
    auth_views.LoginView.as_view(
        template_name="registration/login.html"
    ),
    name="login"
),

    # Registro y sistema principal
    path(
        "",
        include("mi_app_salud.urls")
    ),

]