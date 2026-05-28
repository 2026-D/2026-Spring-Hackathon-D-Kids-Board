# Create your views here.
from django.contrib.auth import (
    login,
    logout,
)  # 登録ユーザーをログイン状態にする # ログアウト状態にする
from django.shortcuts import render, redirect  # renderはHTML表示 #redirectは別ページ移動
from .forms import (
    SignUpForm,
    LoginForm,
    ChildForm,
    ScheduleForm,
)  # forms.pyからSignUpForm, LoginFormを読み込む
from django.views.generic import TemplateView, ListView, CreateView, View
from django.urls import reverse_lazy
from .models import Child, PrepRule, Schedule, PrepItem
from django.contrib.auth.mixins import LoginRequiredMixin  # ログイン必須のクラスを読み込む
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db import IntegrityError, transaction
from django.db.models import Q
from datetime import date, timedelta, datetime
import calendar
import jpholiday


def signup_view(request):  # signup/へのアクセス時に動く処理
    if request.method == "POST":  # 送信ボタンが押された時
        form = SignUpForm(request.POST)  # 入力された内容をフォームに入れる

        if form.is_valid():  # 入力チェック
            form.save()  # ユーザーをUserテーブルに保存
            return redirect("login")  # 登録後、loginページへ移動
    else:
        form = SignUpForm()  # signup/ページを最初にを開いた時（GET）でフォームは空

    return render(  # signup.htmlを画面表示する処理
        request,  # ユーザーがブラウザから送ってきた情報
        "kids_board/signup.html",  # templates/kids_board/signup.htmlを表示
        {"form": form},  # Pythonで作ったformをHTMLに渡す
    )


def login_view(request):  # login/へのアクセス時に動く処理
    if request.method == "POST":  # ログインボタンが押された時
        form = LoginForm(request, data=request.POST)  # Django標準のログインフォーム

        if form.is_valid():  # ログイン情報が正しいか確認
            user = form.get_user()  # ログインが成功したユーザー
            login(request, user)  # ユーザーをログイン状態にする
            return redirect("home")  # ログイン成功後にhomeページへ移動
    else:
        form = LoginForm()  # 最初にページを開いた時

    return render(  # login.html を表示する
        request,
        "kids_board/login.html",
        {"form": form},
    )


def logout_view(request):  # logout/へのアクセス時に動く処理
    logout(request)  # ログイン状態を解除する
    return redirect("top")  # ログアウト後にトップページへ移動する


@login_required
def child_create_view(request):  # 子ども追加処理
    if request.method == "POST":  # フォームの追加ボタンを押した時の処理
        form = ChildForm(request.POST)  # HTMLから送られた入力値を、forms.pyのChildFormに渡す
        form.instance.parent = request.user  # clean() で parent を参照するため先にセット

        if form.is_valid():  # 入力内容が正しいか確認
            child = form.save(commit=False)  # Childデータを作る、しかしDBには保存はしない
            child.parent = request.user  # ログインしているユーザーを、子どもの親として設定
            child.save()  # childrenテーブルに保存
            return redirect("home")  # home画面へ遷移

        # こども追加に失敗した時は、再度子ども情報とフォームを渡してsettings.htmlを表示する
        children = Child.objects.filter(
            parent=request.user,
            deleted_at__isnull=True,
        )
        return render(
            request,
            "kids_board/settings.html",
            {
                "children": children,  # 子ども情報も渡す（子ども追加に失敗しても、子ども情報は表示するため）
                "form": form,  # エラーの内容が入ったフォームを渡す
                "open_add_child_modal": True,  # 子ども追加モーダルを開いた状態にするためのフラグ
            },
            status=400,
        )

    return redirect("settings")


class HomeView(LoginRequiredMixin, ListView):
    model = Child
    template_name = "kids_board/home.html"
    context_object_name = "children"
    ordering = ["created_at"]  # 子供の表示順を作成日時順にするための指定

    def get_queryset(self):
        # ログインしているユーザー（ファミリー）の子供だけを表示するためのクエリセットを返す
        return Child.objects.filter(parent=self.request.user, deleted_at__isnull=True)


@login_required
def child_delete_view(request, child_id):  # ログインしている人だけが使える削除処理

    if request.method == "POST":  # 削除ボタンから、POST送信されたときだけ削除処理をする
        child = get_object_or_404(  # DBから1件取得、無ければ404エラーを出す
            Child,  # childrenテーブル
            id=child_id,  # URLで指定された子ども
            parent=request.user,  # ログイン中ユーザーの子どもだけ
            deleted_at__isnull=True,  # まだ削除されていない子どもだけ
        )

        child.deleted_at = timezone.now()  # 現在時刻をdeleted_atに入れ、削除済み扱いとする

        child.save()  # 変更をDBに保存

    return redirect("home")  # 削除後にhome画面へ戻る


@login_required
def settings_view(request):  # settings画面を表示

    children = Child.objects.filter(  # Childテーブルから、子供の情報を複数取得
        parent=request.user,  # ログイン中ユーザーの子どもだけ
        deleted_at__isnull=True,  # まだ削除されていない子どもだけ
    )

    return render(
        request,
        "kids_board/settings.html",  # 表示するHTML
        {
            "children": children,  # コンテキスト
        },
    )


class TopView(TemplateView):
    template_name = "kids_board/top.html"


class KidsBoardView(LoginRequiredMixin, TemplateView):
    template_name = "kids_board/kids_board.html"

    # kids_board.htmlに渡すデータ（context)を作るメソッドを定義（花丸表示用）。
    def get_context_data(self, **kwargs):
        # 親クラス(TemplateView)が用意する基本のcontextを取得し、context変数に格納.
        context = super().get_context_data(**kwargs)
        children = Child.objects.filter(parent=self.request.user, deleted_at__isnull=True)
        child_id = self.kwargs.get("child_id")
        selected_child = children.filter(id=child_id).first() if child_id else children.first()
        today = date.today()
        WEEKDAY_JP = ["げつ", "か", "すい", "もく", "きん", "ど", "にち"]
        context["children"] = children
        context["selected_child"] = selected_child
        context["today"] = today
        context["weekday_jp"] = WEEKDAY_JP[today.weekday()]
        # 花丸を表示する場合はTrueにする。
        # 子供のタスク達成状況などに応じてTrue/Falseを切り替える想定。
        context["show_badge"] = False
        return context


# ルールタイプを取得するヘルパー関数を定義(PrepItemsMornView,PrepItemsAftView,PrepItemsNiteViewで使用)
def get_today_rule_type(target_date):
    # 今日が特定日か判定
    if PrepRule.objects.filter(
        rule_type=PrepRule.RuleType.SPECIFIC,
        specific_date=target_date,
    ).exists():
        return PrepRule.RuleType.SPECIFIC

    # 今日が祝日か判定
    if jpholiday.is_holiday(target_date):
        return PrepRule.RuleType.HOLIDAY
    # 今日が曜日指定のルールに該当するか判定
    if target_date.weekday() < 5:
        return PrepRule.RuleType.WEEKDAY

    return PrepRule.RuleType.DAY_OF_WEEK


class PrepItemsMornView(LoginRequiredMixin, ListView):
    template_name = "kids_board/prep_items_morn.html"
    model = PrepItem
    context_object_name = "prep_items"

    # 今日のルールタイプを取得するために、get_today_rule_type関数を呼び出す。
    def get_queryset(self):
        target_date = date.today()
        rule_type = get_today_rule_type(target_date)
        child_id = self.kwargs.get("child_id")

        # Qオブジェクトを使って、表示ルール（prep_item_show_rule(今日が特定日か又は曜日か））を定義
        prep_item_show_rule = Q(
            rules__rule_type=PrepRule.RuleType.SPECIFIC,
            rules__specific_date=target_date,
        ) | Q(
            rules__rule_type=PrepRule.RuleType.DAY_OF_WEEK,
            rules__day_of_week=target_date.weekday(),
        )
        # もし今日が祝日なら、祝日に該当するか表示ルールに加える
        if rule_type == PrepRule.RuleType.HOLIDAY:
            prep_item_show_rule |= Q(rules__rule_type=PrepRule.RuleType.HOLIDAY)
        # もし今日が月〜金で、祝日ではない（平日）なら、今日の曜日に該当するか表示ルールに加える
        elif rule_type == PrepRule.RuleType.WEEKDAY:
            prep_item_show_rule |= Q(rules__rule_type=PrepRule.RuleType.WEEKDAY)

        # ここで表示するprep_itemを絞り込む
        queryset = PrepItem.objects.filter(
            parent=self.request.user,
            is_active=True,
            category_type=PrepItem.CategoryType.MORNING,
            children__id=child_id,
        ).filter(prep_item_show_rule)

        return queryset.distinct()  # 重複するお支度アイテムがある場合は、distinct()で重複を排除

    # 追加のコンテキストで今日の日付とヘッダーの子供をテンプレートに渡す
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        WEEKDAY_JP = ["げつ", "か", "すい", "もく", "きん", "ど", "にち"]
        child_id = self.kwargs.get("child_id")
        selected_child = Child.objects.get(id=child_id)
        context["today"] = today
        context["weekday_jp"] = WEEKDAY_JP[today.weekday()]
        context["selected_child"] = selected_child
        return context


class PrepItemsAftView(LoginRequiredMixin, ListView):
    template_name = "kids_board/prep_items_aft.html"
    model = PrepItem
    context_object_name = "prep_items"

    def get_queryset(self):
        target_date = date.today()
        rule_type = get_today_rule_type(target_date)
        child_id = self.kwargs.get("child_id")

        prep_item_show_rule = Q(
            rules__rule_type=PrepRule.RuleType.SPECIFIC,
            rules__specific_date=target_date,
        ) | Q(
            rules__rule_type=PrepRule.RuleType.DAY_OF_WEEK,
            rules__day_of_week=target_date.weekday(),
        )

        if rule_type == PrepRule.RuleType.HOLIDAY:
            prep_item_show_rule |= Q(rules__rule_type=PrepRule.RuleType.HOLIDAY)
        elif rule_type == PrepRule.RuleType.WEEKDAY:
            prep_item_show_rule |= Q(rules__rule_type=PrepRule.RuleType.WEEKDAY)

        queryset = PrepItem.objects.filter(
            parent=self.request.user,
            is_active=True,
            category_type=PrepItem.CategoryType.AFTERNOON,
            children__id=child_id,
        ).filter(prep_item_show_rule)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        child_id = self.kwargs.get("child_id")
        today = date.today()
        WEEKDAY_JP = ["げつ", "か", "すい", "もく", "きん", "ど", "にち"]
        selected_child = Child.objects.get(id=child_id)
        context["today"] = today
        context["weekday_jp"] = WEEKDAY_JP[today.weekday()]
        context["selected_child"] = selected_child
        return context


class PrepItemsNiteView(LoginRequiredMixin, ListView):
    template_name = "kids_board/prep_items_nite.html"
    model = PrepItem
    context_object_name = "prep_items"

    def get_queryset(self):
        target_date = date.today()
        rule_type = get_today_rule_type(target_date)
        child_id = self.kwargs.get("child_id")

        prep_item_show_rule = Q(
            rules__rule_type=PrepRule.RuleType.SPECIFIC,
            rules__specific_date=target_date,
        ) | Q(
            rules__rule_type=PrepRule.RuleType.DAY_OF_WEEK,
            rules__day_of_week=target_date.weekday(),
        )

        if rule_type == PrepRule.RuleType.HOLIDAY:
            prep_item_show_rule |= Q(rules__rule_type=PrepRule.RuleType.HOLIDAY)
        elif rule_type == PrepRule.RuleType.WEEKDAY:
            prep_item_show_rule |= Q(rules__rule_type=PrepRule.RuleType.WEEKDAY)

        queryset = PrepItem.objects.filter(
            parent=self.request.user,
            is_active=True,
            category_type=PrepItem.CategoryType.NIGHT,
            children__id=child_id,
        ).filter(prep_item_show_rule)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        child_id = self.kwargs.get("child_id")
        today = date.today()
        WEEKDAY_JP = ["げつ", "か", "すい", "もく", "きん", "ど", "にち"]
        selected_child = Child.objects.get(id=child_id)
        context["today"] = today
        context["weekday_jp"] = WEEKDAY_JP[today.weekday()]
        context["selected_child"] = selected_child
        return context


class PrepItemsView(LoginRequiredMixin, ListView):
    model = PrepItem
    template_name = "kids_board/prep_items.html"
    context_object_name = "prep_items"
    paginate_by = 15  # 1ページに表示するアイテム数
    ordering = ["-created_at"]  # 新しい順に表示

    WEEKDAY_JP = [
        "げつようび",
        "かようび",
        "すいようび",
        "もくようび",
        "きんようび",
        "どようび",
        "にちようび",
    ]  # 曜日を日本語で表示するためのリスト

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(parent=self.request.user, is_active=True).prefetch_related(
            "rules", "children"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        children = Child.objects.filter(
            parent=self.request.user,
            deleted_at__isnull=True,
        )
        prep_items = context.get("prep_items", [])

        for prep_item in prep_items:
            prep_item.name = prep_item.item_name

            # 曜日チェック（平日ルール + 曜日指定ルール）
            day_of_week_set = set(
                prep_item.rules.filter(
                    rule_type=PrepRule.RuleType.DAY_OF_WEEK,
                    day_of_week__isnull=False,
                ).values_list("day_of_week", flat=True)
            )
            has_weekday_rule = prep_item.rules.filter(rule_type=PrepRule.RuleType.WEEKDAY).exists()

            weekdays = []
            for day_index, day_name in enumerate(self.WEEKDAY_JP):
                checked = (day_index in day_of_week_set) or (has_weekday_rule and day_index <= 4)
                weekdays.append({"name": day_name, "checked": checked})
            prep_item.weekdays = weekdays

            # 平日だけ（祝日含まない）スイッチ
            prep_item.holiday = [{"name": "しゅくじつ", "checked": has_weekday_rule}]

            # 特定日
            specific_dates = list(
                prep_item.rules.filter(
                    rule_type=PrepRule.RuleType.SPECIFIC,
                    specific_date__isnull=False,
                )
                .order_by("specific_date")
                .values_list("specific_date", flat=True)
            )
            if specific_dates:
                prep_item.special_date = [
                    {
                        "name": "ひづけしてい",
                        "checked": True,
                        "value": f"{d.year}ねん{d.month}がつ{d.day}にち",
                    }
                    for d in specific_dates
                ]
            else:
                prep_item.special_date = [{"name": "ひづけしてい", "checked": False, "value": None}]

            # カテゴリ
            prep_item.category_type = [
                {
                    "name": "あさ",
                    "value": PrepItem.CategoryType.MORNING,
                    "checked": prep_item.category_type == PrepItem.CategoryType.MORNING,
                },
                {
                    "name": "かえってきてから",
                    "value": PrepItem.CategoryType.AFTERNOON,
                    "checked": prep_item.category_type == PrepItem.CategoryType.AFTERNOON,
                },
                {
                    "name": "よる",
                    "value": PrepItem.CategoryType.NIGHT,
                    "checked": prep_item.category_type == PrepItem.CategoryType.NIGHT,
                },
            ]

            assigned_child_ids = {child.id for child in prep_item.children.all()}
            prep_item.children_options = [
                {
                    "id": child.id,
                    "name": child.child_name,
                    "checked": child.id in assigned_child_ids,
                }
                for child in children
            ]

        selected_child_id = self.kwargs.get("child_id")
        selected_child = (
            children.filter(id=selected_child_id).first() if selected_child_id else children.first()
        )
        context["children"] = children
        context["selected_child"] = selected_child
        context["selected_child_id"] = selected_child_id
        return context


# prep_item.htmlのやることリスト一覧からやることを削除するためのビュー関数を定義
@login_required
def prep_item_delete_view(request, prep_item_id):
    if request.method == "POST":
        prep_item = get_object_or_404(
            PrepItem,
            id=prep_item_id,
            parent=request.user,
            is_active=True,
        )
        prep_item.is_active = False
        prep_item.save(update_fields=["is_active", "updated_at"])

    return redirect("prep_items")


# prep_item.htmlのやることリスト一覧からやることを編集するためのビュー関数を定義
class PrepItemEditView(LoginRequiredMixin, View):
    # POSTリクエストを処理するためのメソッドを定義
    def post(self, request, prep_item_id, *args, **kwargs):
        prep_item = get_object_or_404(
            PrepItem,
            id=prep_item_id,
            parent=request.user,
            is_active=True,
        )

        item_name = request.POST.get(
            "item_name", ""
        ).strip()  # やることの名前をPOSTデータから取得し、前後の空白を削除
        category_type = request.POST.get(
            "category_type", ""
        ).strip()  # カテゴリをPOSTデータから取得し、前後の空白を削除
        # ルールの更新は、後でまとめて行うため、ここではitem_nameとcategory_typeの更新だけ行う
        update_fields = ["updated_at"]
        if item_name:
            prep_item.item_name = item_name
            update_fields.append("item_name")
        # category_typeは、PrepItem.CategoryTypeのchoicesにある値だけを受け入れるようにする
        valid_categories = {choice[0] for choice in PrepItem.CategoryType.choices}
        # もしcategory_typeがvalid_categoriesの中にある値なら、prep_itemのcategory_typeを更新する
        if category_type in valid_categories:
            prep_item.category_type = category_type
            update_fields.append("category_type")

        prep_item.save(
            update_fields=update_fields
        )  # item_nameとcategory_typeを更新した後、updated_atも更新するためにupdate_fieldsに"updated_at"を入れている

        # ルール更新（曜日/平日/特定日を作り直し）
        prep_item.rules.filter(
            rule_type__in=[
                PrepRule.RuleType.DAY_OF_WEEK,
                PrepRule.RuleType.WEEKDAY,
                PrepRule.RuleType.SPECIFIC,
            ]
        ).delete()
        # 曜日ルールの更新
        weekday_values = request.POST.getlist("weekday")
        for day_str in weekday_values:
            try:
                day_of_week = int(day_str)
            except (TypeError, ValueError):
                continue
            if 0 <= day_of_week <= 6:
                PrepRule.objects.create(
                    prep_item=prep_item,
                    rule_type=PrepRule.RuleType.DAY_OF_WEEK,
                    day_of_week=day_of_week,
                )
        # 祝日を除くスイッチがオンの場合は、平日ルールを追加
        if request.POST.get("is_not_holiday"):
            PrepRule.objects.create(
                prep_item=prep_item,
                rule_type=PrepRule.RuleType.WEEKDAY,
            )
        # 特定日が指定されている場合は、特定日ルールを追加
        if request.POST.get("use_specific_date"):
            specific_date_str = request.POST.get("specific_date", "").strip()
            # 特定日が「yyyy-mm-dd」形式か「yyyyねんmがつdにち」形式で入力されることを想定し、両方の形式に対応してパースする
            if specific_date_str:
                parsed_specific_date = None  # 入力内容の解析に失敗した場合はNoneのままにする
                # まずは「yyyy-mm-dd」形式で解析を試みる
                try:
                    if "ねん" in specific_date_str:
                        parsed_specific_date = datetime.strptime(
                            specific_date_str, "%Yねん%mがつ%dにち"
                        ).date()
                    else:
                        parsed_specific_date = date.fromisoformat(specific_date_str)
                except ValueError:
                    parsed_specific_date = None
                # 解析に成功し、parsed_specific_dateがNoneでない場合は、特定日ルールを作成する
                if parsed_specific_date:
                    PrepRule.objects.create(
                        prep_item=prep_item,
                        rule_type=PrepRule.RuleType.SPECIFIC,
                        specific_date=parsed_specific_date,
                    )

        # 子ども紐づけ更新
        child_ids = request.POST.getlist("child_ids")
        # child_idsは文字列のリストで送られてくるため、整数のリストに変換する
        assigned_children = Child.objects.filter(
            id__in=child_ids,
            parent=request.user,
            deleted_at__isnull=True,
        )
        prep_item.children.set(assigned_children)

        return redirect("prep_items")


class CustomItemsView(LoginRequiredMixin, View):
    template_name = "kids_board/custom_items.html"
    success_url = reverse_lazy("custom_items")

    WEEKDAY_JP = [
        "げつようび",
        "かようび",
        "すいようび",
        "もくようび",
        "きんようび",
        "どようび",
        "にちようび",
    ]

    def get_context_data(self, **kwargs):
        """テンプレートに渡すコンテキストを作成"""
        context = kwargs.copy()

        # カテゴリ選択肢
        context["category_type"] = [
            {"name": "あさ", "value": PrepItem.CategoryType.MORNING, "checked": False},
            {"name": "かえってから", "value": PrepItem.CategoryType.AFTERNOON, "checked": False},
            {"name": "よる", "value": PrepItem.CategoryType.NIGHT, "checked": False},
        ]

        # 子ども選択肢（DB から取得）
        children_qs = Child.objects.filter(parent=self.request.user, deleted_at__isnull=True)
        context["children"] = [
            {"id": c.id, "name": c.child_name, "checked": False} for c in children_qs
        ]

        # やること一覧（is_active=True のものだけ表示）
        prep_items_qs = PrepItem.objects.filter(
            parent=self.request.user, is_active=True
        ).prefetch_related("rules", "children")

        formatted_items = []
        for item in prep_items_qs:
            rules = list(item.rules.all())
            weekdays_checked = {
                r.day_of_week for r in rules if r.rule_type == PrepRule.RuleType.DAY_OF_WEEK
            }
            has_weekday_rule = any(r.rule_type == PrepRule.RuleType.WEEKDAY for r in rules)
            specific_rule = next(
                (r for r in rules if r.rule_type == PrepRule.RuleType.SPECIFIC), None
            )
            assigned_child_ids = {c.id for c in item.children.all()}

            item.name = item.item_name
            item.weekdays = [
                {"name": jp, "checked": i in weekdays_checked}
                for i, jp in enumerate(self.WEEKDAY_JP)
            ]
            item.holiday = [{"name": "しゅくじつをのぞく", "checked": has_weekday_rule}]
            item.special_date = [
                {
                    "name": "ひづけしてい",
                    "checked": specific_rule is not None,
                    "value": str(specific_rule.specific_date) if specific_rule else None,
                }
            ]
            item.category_type = [
                {
                    "name": "あさ",
                    "checked": item.category_type == PrepItem.CategoryType.MORNING,
                },
                {
                    "name": "かえってきてから",
                    "checked": item.category_type == PrepItem.CategoryType.AFTERNOON,
                },
                {
                    "name": "よる",
                    "checked": item.category_type == PrepItem.CategoryType.NIGHT,
                },
            ]
            item.children_options = [
                {"id": c.id, "name": c.child_name, "checked": c.id in assigned_child_ids}
                for c in children_qs
            ]
            formatted_items.append(item)

        context["prep_items"] = formatted_items
        return context

    def get(self, request, *args, **kwargs):
        """GET: フォーム表示"""
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """POST: データ保存"""
        # PrepItem フォーム検証
        item_name = request.POST.get("item_name", "").strip()
        category_type_values = request.POST.getlist("category_type")
        prep_icon = request.POST.get("prep_icon", "").strip() or "images/prep_item/12_cutlery.png"

        valid_categories = {choice[0] for choice in PrepItem.CategoryType.choices}
        category_types = []
        for category in category_type_values:
            if category in valid_categories and category not in category_types:
                category_types.append(category)

        # 特定日（yyyy-mm-dd / yyyyねんmがつdにち）を正規化
        parsed_specific_date = None
        if request.POST.get("use_specific_date"):
            specific_date_str = request.POST.get("specific_date", "").strip()
            if specific_date_str:
                try:
                    if "ねん" in specific_date_str:
                        parsed_specific_date = datetime.strptime(
                            specific_date_str, "%Yねん%mがつ%dにち"
                        ).date()
                    else:
                        parsed_specific_date = date.fromisoformat(specific_date_str)
                except ValueError:
                    context = self.get_context_data()
                    context["error_message"] = (
                        "ひづけの けいしきが まちがっています（YYYY-MM-DD または YYYYねんMがつDにち）。"
                    )
                    return render(request, self.template_name, context, status=400)

        if not item_name or not category_types:
            context = self.get_context_data()
            context["error_message"] = "やるタイミングを 1つ いじょう えらんでください。"
            return render(request, self.template_name, context, status=400)

        # 子ども M2M を取得（作成する各カテゴリに同じ設定を適用）
        child_ids = request.POST.getlist("child_ids")
        assigned_children = Child.objects.filter(id__in=child_ids, parent=request.user)

        try:
            with transaction.atomic():
                for category_type in category_types:
                    prep_item = PrepItem.objects.create(
                        parent=request.user,
                        item_name=item_name,
                        category_type=category_type,
                        prep_icon=prep_icon,
                        is_custom=True,
                    )

                    # 曜日ルール（チェックボックス value は 0〜6）
                    for day_str in request.POST.getlist("weekday"):
                        PrepRule.objects.create(
                            prep_item=prep_item,
                            rule_type=PrepRule.RuleType.DAY_OF_WEEK,
                            day_of_week=int(day_str),
                        )

                    # 平日ルール
                    if request.POST.get("is_not_holiday"):
                        PrepRule.objects.create(
                            prep_item=prep_item,
                            rule_type=PrepRule.RuleType.WEEKDAY,
                        )

                    # 特定日ルール
                    if parsed_specific_date:
                        PrepRule.objects.create(
                            prep_item=prep_item,
                            rule_type=PrepRule.RuleType.SPECIFIC,
                            specific_date=parsed_specific_date,
                        )

                    if assigned_children.exists():
                        prep_item.children.set(assigned_children)
        except IntegrityError:
            context = self.get_context_data()
            context["error_message"] = (
                "おなじ『なまえ + やるタイミング』は すでに とうろく されています。"
            )
            return render(request, self.template_name, context, status=400)

        return redirect(self.success_url)


class NewItemsEditView(TemplateView, LoginRequiredMixin):
    template_name = "kids_board/new_items.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # prep_itemsの仮データ
        context["prep_items"] = [
            {
                "id": 1,
                "name": "ごはん",
                "prep_icon": "images/prep_item/12_cutlery.png",
                "weekdays": [
                    {"name": "げつようび", "checked": True},
                    {"name": "かようび", "checked": True},
                    {"name": "すいようび", "checked": True},
                    {"name": "もくようび", "checked": True},
                    {"name": "きんようび", "checked": True},
                    {"name": "どようび", "checked": True},
                    {"name": "にちようび", "checked": True},
                ],
                "holiday": [{"name": "しゅくじつ", "checked": False}],
                "special_date": [{"name": "ひづけしてい", "checked": False, "value": None}],
                "category_type": [
                    {"name": "あさ", "checked": True},
                    {"name": "かえってきてから", "checked": False},
                    {"name": "よる", "checked": True},
                ],
                "children": [
                    {"name": "こども1", "checked": True},
                    {"name": "こども2", "checked": True},
                ],
            },
            {
                "id": 2,
                "name": "トイレ",
                "prep_icon": "images/prep_item/5_toilet.png",
                "weekdays": [
                    {"name": "げつようび", "checked": True},
                    {"name": "かようび", "checked": True},
                    {"name": "すいようび", "checked": False},
                    {"name": "もくようび", "checked": True},
                    {"name": "きんようび", "checked": False},
                    {"name": "どようび", "checked": False},
                    {"name": "にちようび", "checked": False},
                ],
                "holiday": [{"name": "しゅくじつ", "checked": False}],
                "special_date": [{"name": "ひづけしてい", "checked": False, "value": None}],
                "category_type": [
                    {"name": "あさ", "checked": True},
                    {"name": "かえってきてから", "checked": False},
                    {"name": "よる", "checked": False},
                ],
                "children": [
                    {"name": "こども1", "checked": True},
                    {"name": "こども2", "checked": False},
                ],
            },
            {
                "id": 3,
                "name": "しゅくだい",
                "prep_icon": "images/prep_item/22_paper_and_pen.png",
                "weekdays": [
                    {"name": "げつようび", "checked": True},
                    {"name": "かようび", "checked": True},
                    {"name": "すいようび", "checked": True},
                    {"name": "もくようび", "checked": True},
                    {"name": "きんようび", "checked": True},
                    {"name": "どようび", "checked": True},
                    {"name": "にちようび", "checked": True},
                ],
                "holiday": [{"name": "しゅくじつ", "checked": False}],
                "special_date": [{"name": "ひづけしてい", "checked": False, "value": None}],
                "category_type": [
                    {"name": "あさ", "checked": False},
                    {"name": "かえってきてから", "checked": True},
                    {"name": "よる", "checked": False},
                ],
                "children": [
                    {"name": "こども1", "checked": True},
                    {"name": "こども2", "checked": True},
                ],
            },
            {
                "id": 4,
                "name": "えんそくのじゅんびみたいにながいもじがはいっているときの表示の仕方を確認するようにする",
                "prep_icon": "images/prep_item/2_backpack.png",
                "weekdays": [
                    {"name": "げつようび", "checked": False},
                    {"name": "かようび", "checked": False},
                    {"name": "すいようび", "checked": False},
                    {"name": "もくようび", "checked": False},
                    {"name": "きんようび", "checked": False},
                    {"name": "どようび", "checked": False},
                    {"name": "にちようび", "checked": False},
                ],
                "holiday": [{"name": "しゅくじつ", "checked": False}],
                "special_date": [
                    {"name": "ひづけしてい", "checked": True, "value": "2026ねん5がつ30にち"}
                ],
                "category_type": [
                    {"name": "あさ", "checked": False},
                    {"name": "かえってきてから", "checked": True},
                    {"name": "よる", "checked": False},
                ],
                "children": [
                    {"name": "こども1", "checked": True},
                    {"name": "こども2", "checked": True},
                ],
            },
        ]
        # カスタムアイテムの入力フォームに必要なデータ
        context["category_type"] = [
            {"name": "あさ", "checked": False},
            {"name": "かえってから", "checked": False},
            {"name": "よる", "checked": False},
        ]
        context["children"] = [
            {"name": "こども1", "checked": False},
            {"name": "こども2", "checked": False},
        ]
        return context


class ScheduleView(LoginRequiredMixin, TemplateView):
    template_name = "kids_board/schedule.html"

    COLOR_CSS_MAP = {
        Schedule.ColorType.RED: "var(--red-400)",
        Schedule.ColorType.YELLOW: "var(--yellow-200)",
        Schedule.ColorType.GREEN: "var(--green-300)",
        Schedule.ColorType.EMERALD_GREEN: "var(--teal-400)",
        Schedule.ColorType.SKY_BLUE: "var(--cyan-300)",
        Schedule.ColorType.BLUE: "var(--blue-400)",
        Schedule.ColorType.PURPLE: "var(--indigo-300)",
        Schedule.ColorType.PINK: "var(--pink-300)",
        Schedule.ColorType.ORANGE: "var(--orange-300)",
        Schedule.ColorType.WHITE: "var(--gray-100)",
    }

    MONTH_WEEKDAYS = ["にち", "げつ", "か", "すい", "もく", "きん", "ど"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        children = Child.objects.filter(parent=self.request.user, deleted_at__isnull=True)
        child_id = self.kwargs.get("child_id")
        selected_child = get_object_or_404(children, id=child_id) if child_id else children.first()
        today = date.today()
        month_param = self.request.GET.get(
            "month"
        )  # クエリパラメータから月を取得（例: "2026-05"）.
        date_param = self.request.GET.get(
            "date"
        )  # クエリパラメータから日付を取得（例: "2026-05-15"）。
        selected_date = today

        # クエリパラメータから日付が指定されている場合は、selected_dateを更新
        if date_param:
            try:
                selected_date = date.fromisoformat(date_param)
            except ValueError:
                pass

        # selected_dateをもとに、表示する月の初日を計算。クエリパラメータで月が指定されている場合は、その月の初日にする。
        display_month = selected_date.replace(day=1)

        # クエリパラメータから月が指定されている場合は、その月の初日にする
        if month_param:
            try:
                display_month = date.fromisoformat(f"{month_param}-01")
            except ValueError:
                pass

        # 日曜始まりに固定: 月曜=0..日曜=6 のため +1 して 7 で剰余
        days_since_sunday = (selected_date.weekday() + 1) % 7
        week_start = selected_date - timedelta(days=days_since_sunday)
        week_dates = [week_start + timedelta(days=i) for i in range(7)]
        week_end = week_start + timedelta(days=6)
        week_weekdays = ["にち", "げつ", "か", "すい", "もく", "きん", "ど"]
        hours = list(range(7, 19))  # 7じ〜18じ
        weekly_grid = {hour: [None] * 7 for hour in hours}
        first_weekday, days_in_month = calendar.monthrange(display_month.year, display_month.month)
        leading_blank_days = (first_weekday + 1) % 7
        month_cells = [None] * leading_blank_days + [
            {
                "day": day,
                "date": date(display_month.year, display_month.month, day),
                "is_today": (
                    display_month.year == today.year
                    and display_month.month == today.month
                    and day == today.day
                ),
                "is_selected": (
                    display_month.year == selected_date.year
                    and display_month.month == selected_date.month
                    and day == selected_date.day
                ),
            }
            for day in range(1, days_in_month + 1)
        ]
        trailing_blank_days = (
            7 - (len(month_cells) % 7)
        ) % 7  # 月のセル数が7の倍数になるように、末尾に空セルを追加
        month_cells.extend([None] * trailing_blank_days)  # 末尾に空セルを追加
        month_weeks = [
            month_cells[index : index + 7] for index in range(0, len(month_cells), 7)
        ]  # 月のセルを7日ごとに分割して週ごとのリストを作成
        if (
            display_month.month == 1
        ):  # 1月のときは、前年の12月を前月として表示するため、年を1つ減らし、月を12にする
            prev_month_year = display_month.year - 1
            prev_month_month = 12
        else:
            prev_month_year = display_month.year
            prev_month_month = display_month.month - 1

        if (
            display_month.month == 12
        ):  # 12月のときは、翌年の1月を次月として表示するため、年を1つ増やし、月を1にする
            next_month_year = display_month.year + 1
            next_month_month = 1
        else:
            next_month_year = display_month.year
            next_month_month = display_month.month + 1

        # 予定を取得して、weekly_gridに配置
        if selected_child:
            schedules = Schedule.objects.filter(
                child=selected_child,
                schedule_date__range=(week_start, week_end),
            )
            # 予定を週のグリッドに配置するためのループ
            for schedule in schedules:
                day_index = (schedule.schedule_date - week_start).days
                # 予定の日付が週の範囲外の場合はスキップ
                if not (0 <= day_index < 7):
                    continue

                # 時刻のない予定は7じ枠に表示する想定
                if schedule.start_time:
                    start_hour = schedule.start_time.hour
                    if schedule.end_time and schedule.end_time > schedule.start_time:
                        end_hour = schedule.end_time.hour
                    else:
                        end_hour = start_hour + 1
                else:
                    # 時刻未設定の場合は7じ枠に表示
                    start_hour = 7
                    end_hour = 8

                start_hour = max(start_hour, hours[0])  # 開始時間は表示する時間帯の最初の時間まで
                end_hour = min(end_hour, hours[-1] + 1)  # 終了時間は表示する時間帯の次の時間まで
                title_hour = start_hour + (
                    (end_hour - start_hour) // 2
                )  # タイトルを表示する時間帯の計算（予定の中央の時間帯に表示する想定）

                for hour in range(start_hour, end_hour):
                    # 予定が重なった場合、現状は先に入った1件を優先表示。
                    if weekly_grid[hour][day_index] is None:
                        weekly_grid[hour][day_index] = {
                            "title": schedule.title
                            if hour == title_hour
                            else "",  # 中央の枠にだけタイトルを表示する
                            "color_css": self.COLOR_CSS_MAP.get(
                                schedule.color, "var(--gray-100)"
                            ),  # 色のCSSを取得。デフォルトはグレー
                        }

        weekly_rows = [
            {"hour": hour, "cells": weekly_grid[hour]} for hour in hours
        ]  # 時間帯ごとの行データを作成

        context["children"] = children
        context["selected_child"] = selected_child
        context["week_start"] = week_start
        context["week_end"] = week_end
        context["week_dates"] = week_dates
        context["week_weekdays"] = week_weekdays
        context["weekly_rows"] = weekly_rows
        context["month_label"] = f"{display_month.month}がつ"  # 月の表示ラベル（例: "5がつ"）
        context["display_month_query"] = (
            f"{display_month.year}-{display_month.month:02d}"  # クエリパラメータ用の月の文字列（例: "2026-05"）
        )
        context["month_weekdays"] = self.MONTH_WEEKDAYS
        context["month_weeks"] = month_weeks
        context["prev_month_query"] = (
            f"month={prev_month_year}-{prev_month_month:02d}"  # クエリパラメータ用の前月の文字列（例: "2026-04"）
        )
        context["next_month_query"] = (
            f"month={next_month_year}-{next_month_month:02d}"  # クエリパラメータ用の次月の文字列（例: "2026-06"）
        )
        context["selected_date"] = selected_date
        return context


class ScheduleListView(LoginRequiredMixin, ListView):
    template_name = "kids_board/schedule_list.html"
    model = Schedule
    context_object_name = "schedules"

    COLOR_CSS_MAP = {
        Schedule.ColorType.RED: "var(--red-400)",
        Schedule.ColorType.YELLOW: "var(--yellow-200)",
        Schedule.ColorType.GREEN: "var(--green-300)",
        Schedule.ColorType.EMERALD_GREEN: "var(--teal-400)",
        Schedule.ColorType.SKY_BLUE: "var(--cyan-300)",
        Schedule.ColorType.BLUE: "var(--blue-400)",
        Schedule.ColorType.PURPLE: "var(--indigo-300)",
        Schedule.ColorType.PINK: "var(--pink-300)",
        Schedule.ColorType.ORANGE: "var(--orange-300)",
        Schedule.ColorType.WHITE: "var(--gray-100)",
    }

    def get_queryset(self):
        child_id = self.kwargs.get("child_id")
        selected_child = get_object_or_404(
            Child,
            id=child_id,
            parent=self.request.user,
            deleted_at__isnull=True,
        )
        return Schedule.objects.filter(
            child__parent=self.request.user, child=selected_child
        ).order_by(
            "-schedule_date"
        )  # ログインユーザーのスケジュールだけを取得するようにクエリセットを返す

    # 追加のコンテキストでヘッダーの子供をテンプレートに渡す
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        child_id = self.kwargs.get("child_id")
        selected_child = get_object_or_404(
            Child,
            id=child_id,
            parent=self.request.user,
            deleted_at__isnull=True,
        )
        context["schedule_color_choices"] = [
            {
                "value": color.value,
                "label": color.label,
                "css": self.COLOR_CSS_MAP[color],
            }
            for color in Schedule.ColorType
        ]
        context["schedule_form"] = ScheduleForm()
        context["selected_child"] = selected_child
        return context


class CreateScheduleView(LoginRequiredMixin, CreateView):
    template_name = "kids_board/create_schedule.html"

    COLOR_CSS_MAP = {
        Schedule.ColorType.RED: "var(--red-400)",
        Schedule.ColorType.YELLOW: "var(--yellow-200)",
        Schedule.ColorType.GREEN: "var(--green-300)",
        Schedule.ColorType.EMERALD_GREEN: "var(--teal-400)",
        Schedule.ColorType.SKY_BLUE: "var(--cyan-300)",
        Schedule.ColorType.BLUE: "var(--blue-400)",
        Schedule.ColorType.PURPLE: "var(--indigo-300)",
        Schedule.ColorType.PINK: "var(--pink-300)",
        Schedule.ColorType.ORANGE: "var(--orange-300)",
        Schedule.ColorType.WHITE: "var(--gray-100)",
    }

    form_class = ScheduleForm

    def get_initial(self):
        initial = super().get_initial()
        initial["color"] = Schedule.ColorType.RED
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        child_id = self.kwargs.get("child_id")
        selected_child = get_object_or_404(
            Child,
            id=child_id,
            parent=self.request.user,
            deleted_at__isnull=True,
        )
        context["selected_child"] = selected_child
        context["schedule_color_choices"] = [
            {
                "value": color.value,
                "label": color.label,
                "css": self.COLOR_CSS_MAP[color],
            }
            for color in Schedule.ColorType
        ]
        context["schedule"] = {
            "colors": [
                {
                    "value": color.value,
                    "label": color.label,
                    "css": self.COLOR_CSS_MAP[color],
                    "checked": False,
                }
                for color in Schedule.ColorType
            ],
        }
        return context

    def form_valid(self, form):
        child = get_object_or_404(
            Child,
            id=self.kwargs.get("child_id"),
            parent=self.request.user,
            deleted_at__isnull=True,
        )
        form.instance.child = child
        return super().form_valid(form)

    # フォームの入力が無効な場合にエラーメッセージ。スケジュール作成画面を再表示。
    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        context["error_message"] = "入力内容を確認してください。"
        return render(self.request, self.template_name, context, status=400)

    # CreateViewのform_validが成功した後、スケジュールの保存後にスケジュール一覧画面にリダイレクトするようにする。
    def get_success_url(self):
        return reverse_lazy("schedule_list", kwargs={"child_id": self.kwargs.get("child_id")})


@login_required
def schedule_delete_view(request, child_id, schedule_id):
    if request.method == "POST":
        schedule = get_object_or_404(
            Schedule,
            id=schedule_id,
            child_id=child_id,
            child__parent=request.user,
            child__deleted_at__isnull=True,
        )
        schedule.delete()

    return redirect("schedule_list", child_id=child_id)


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = "kids_board/settings.html"
