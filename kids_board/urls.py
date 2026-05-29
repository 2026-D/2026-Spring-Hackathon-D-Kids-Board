from django.urls import path  # URLを書くためのpathを使う
from .views import signup_view, login_view, logout_view
from .views import child_create_view  # 関数ベース
from .views import child_delete_view  # 関数ベース
from .views import prep_item_delete_view  # 関数ベース
from .views import schedule_delete_view  # 関数ベース
from .views import settings_view  # 関数ベース

from .views import (
    TopView,
    HomeView,
    KidsBoardView,
    PrepItemsMornView,
    PrepItemsAftView,
    PrepItemsNiteView,
    PrepItemsView,
    PrepItemEditView,
    CustomItemsView,
    NewItemsEditView,
    ScheduleView,
    ScheduleListView,
    CreateScheduleView,
    # しほ追加：完了/未完了View
    PrepItemToggleCompleteView,
)


urlpatterns = [
    path("signup/", signup_view, name="signup"),  # http://localhost:8000/signup/
    path("login/", login_view, name="login"),  # login/
    path("logout/", logout_view, name="logout"),  # logout/
    path("", TopView.as_view(), name="top"),
    # path("kids_board/",kids_board_view,name="kids_board"), # kids_board/
    path("settings/child/add/", child_create_view, name="child_create"),
    path("settings/child/<int:child_id>/delete/", child_delete_view, name="child_delete"),
    path("settings/", settings_view, name="settings"),
    path(
        "home/",
        HomeView.as_view(template_name="kids_board/home.html"),
        name="home",
    ),
    path(
        "kids_board/<int:child_id>/",
        KidsBoardView.as_view(template_name="kids_board/kids_board.html"),
        name="kids_board",
    ),
    # 🔽朝のやることリスト一覧
    path(
        "prep_items_morn/<int:child_id>/",
        PrepItemsMornView.as_view(template_name="kids_board/prep_items_morn.html"),
        name="prep_items_morn",
    ),
    # 🔽帰宅後のやることリスト一覧
    path(
        "prep_items_aft/<int:child_id>/",
        PrepItemsAftView.as_view(template_name="kids_board/prep_items_aft.html"),
        name="prep_items_aft",
    ),
    # 🔽夜のやることリスト一覧
    path(
        "prep_items_nite/<int:child_id>/",
        PrepItemsNiteView.as_view(template_name="kids_board/prep_items_nite.html"),
        name="prep_items_nite",
    ),
    # ✅しほ追加
    # 🔽やることリスト一覧　完了/未完了フラグ
    path(
        "prep_item_toggle_complete/<int:child_id>/<int:prep_item_id>",
        PrepItemToggleCompleteView.as_view(),
        name="prep_item_toggle_complete",
    ),
    path(
        "prep_items/",
        PrepItemsView.as_view(template_name="kids_board/prep_items.html"),
        name="prep_items",
    ),
    path(
        "prep_items/<int:prep_item_id>/edit/",
        PrepItemEditView.as_view(),
        name="prep_items_edit_api",
    ),
    path(
        "prep_items/<int:prep_item_id>/delete/",
        prep_item_delete_view,
        name="prep_item_delete",
    ),
    path(
        "custom_items/",
        CustomItemsView.as_view(template_name="kids_board/custom_items.html"),
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
        "schedule/<int:child_id>/",
        ScheduleView.as_view(template_name="kids_board/schedule.html"),
        name="schedule",
    ),
    path(
        "schedule_list/<int:child_id>/",
        ScheduleListView.as_view(template_name="kids_board/schedule_list.html"),
        name="schedule_list",
    ),
    path(
        "schedule/create/<int:child_id>/",
        CreateScheduleView.as_view(template_name="kids_board/create_schedule.html"),
        name="create_schedule",
    ),
    path(
        "schedule/<int:child_id>/<int:schedule_id>/delete/",
        schedule_delete_view,
        name="schedule_delete",
    ),
]
