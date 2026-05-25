from django.urls import path  # URLを書くためのpathを使う
from .views import signup_view, login_view, logout_view
from .views import home_view  # 関数ベース
from .views import child_create_view  # 関数ベース
from .views import child_delete_view  # 関数ベース
from .views import settings_view  # 関数ベース

from .views import (
    # kids_board_view,
    KidsBoardView,
    PrepItemsMornView,
    PrepItemsView,
    PrepItemEditView,
    CustomItemsEditView,
    NewItemsEditView,
    ScheduleView,
    # SettingsView,
)


urlpatterns = [
    path("signup/", signup_view, name="signup"),  # http://localhost:8000/signup/
    path("login/", login_view, name="login"),  # login/
    path("logout/", logout_view, name="logout"),  # logout/
    path("home/", home_view, name="home"),  # home/
    # path("kids_board/",kids_board_view,name="kids_board"), # kids_board/
    path("settings/child/add/", child_create_view, name="child_create"),
    path("settings/child/<int:child_id>/delete/", child_delete_view, name="child_delete"),
    path("settings/", settings_view, name="settings"),
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
    # path(
    #     "settings/", SettingsView.as_view(template_name="kids_board/settings.html"), name="settings"
    # ),
]
