"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from kids_board.views import (
    HomeView,
    KidsBoardView,
    PrepItemsMornView,
    PrepItemsView,
    PrepItemEditView,
    CustomItemsEditView,
    NewItemsEditView,
    ScheduleView,
    SettingsView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("kids_board.urls")),  # ""はhttp://localhost:8000/　#kids_board/urls.pyを使う
    path("home/", HomeView.as_view(template_name="kids_board/home.html"), name="home"),
    path(
        "kids_board/",
        KidsBoardView.as_view(template_name="kids_board/kids_board.html"),
        name="kids_board",
    ),
    path(
        "prep_items_morn/",
        PrepItemsMornView.as_view(template_name="kids_board/prep_items_morn.html"),
        name="prep_items_morn",
    ),
    path(
        "prep_items/",
        PrepItemsView.as_view(template_name="kids_board/prep_items.html"),
        name="prep_items",
    ),
    path(
        "prep_items/<int:prep_item_id>/edit/",
        PrepItemEditView.as_view(template_name="kids_board/prep_items.html"),
        name="prep_items_edit_api",
    ),
    path(
        "custom_items/",
        CustomItemsEditView.as_view(template_name="kids_board/custom_items.html"),
        name="custom_items",
    ),
    path(
        "custom_items/new/",
        NewItemsEditView.as_view(template_name="kids_board/new_items.html"),
        name="new_items",
    ),
    path(
        "schedule/", ScheduleView.as_view(template_name="kids_board/schedule.html"), name="schedule"
    ),
    path(
        "settings/", SettingsView.as_view(template_name="kids_board/settings.html"), name="settings"
    ),
]
