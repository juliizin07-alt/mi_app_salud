from django.contrib import admin
from django.urls import path, include

urlpatterns = [

    # ==========================================
    # PANEL ADMINISTRADOR DJANGO
    # ==========================================

    path(
        "admin/",
        admin.site.urls
    ),

    # ==========================================
    # JARVICE HEALTH AI
    # ==========================================

    path(
        "",
        include("mi_app_salud.urls")
    ),

]