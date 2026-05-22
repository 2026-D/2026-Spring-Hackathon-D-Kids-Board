# Create your views here.
from django.contrib.auth import (
    login,
    logout,
)  # 登録ユーザーをログイン状態にする # ログアウト状態にする
from django.shortcuts import render, redirect  # renderはHTML表示 #redirectは別ページ移動
from .forms import SignUpForm, LoginForm, ChildForm  # forms.pyからSignUpForm, LoginFormを読み込む
from django.views.generic import TemplateView, ListView
from django.urls import reverse_lazy
from .models import PrepItem, Child, PrepRule
from django.contrib.auth.mixins import LoginRequiredMixin  # ログイン必須のクラスを読み込む
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import date
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
    return redirect("login")  # ログアウト後にloginページへ移動する


@login_required
def child_create_view(request):  # 子ども追加処理
    if request.method == "POST":  # フォームの追加ボタンを押した時の処理
        form = ChildForm(request.POST)  # HTMLから送られた入力値を、forms.pyのChildFormに渡す

        if form.is_valid():  # 入力内容が正しいか確認
            child = form.save(commit=False)  # Childデータを作る、しかしDBには保存はしない
            child.parent = request.user  # ログインしているユーザーを、子どもの親として設定
            child.save()  # childrenテーブルに保存
            return redirect("home")  # home画面へ遷移


class HomeView(LoginRequiredMixin, ListView):
    model = Child
    template_name = "kids_board/home.html"
    context_object_name = "children"
    ordering = ["created_at"]  # 子供の表示順を作成日時順にするための指定
    print("children:", context_object_name)

    def get_queryset(self):
        # ログインしているユーザー（ファミリー）の子供だけを表示するためのクエリセットを返す
        return Child.objects.filter(parent=self.request.user, deleted_at__isnull=True)


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

    # 追加のコンテキストで今日の日付をテンプレートに渡す
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        WEEKDAY_JP = ["げつ", "か", "すい", "もく", "きん", "ど", "にち"]
        context["today"] = today
        context["weekday_jp"] = WEEKDAY_JP[today.weekday()]
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
        today = date.today()
        WEEKDAY_JP = ["げつ", "か", "すい", "もく", "きん", "ど", "にち"]
        context["today"] = today
        context["weekday_jp"] = WEEKDAY_JP[today.weekday()]
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
        today = date.today()
        WEEKDAY_JP = ["げつ", "か", "すい", "もく", "きん", "ど", "にち"]
        context["today"] = today
        context["weekday_jp"] = WEEKDAY_JP[today.weekday()]
        return context


class PrepItemsView(LoginRequiredMixin, ListView):
    template_name = "kids_board/prep_items.html"

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
        return context


# todo:DE編集を実装する段階で、UpdateViewを継承し、編集機能を実装する。
# todo:LoginRequiredMixinを追加
class PrepItemEditView(TemplateView):
    template_name = "kids_board/prep_items.html"
    model = PrepItem  # モデルを指定
    fields = [
        "name",
        "weekdays",
        "holiday",
        "special_date",
        "category_type",
        "children",
    ]  # 編集可能なフィールドを指定
    success_url = reverse_lazy("prep_items")  # 編集成功後のリダイレクト先を指定


class CustomItemsEditView(TemplateView):
    template_name = "kids_board/custom_items.html"

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


class NewItemsEditView(TemplateView):
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


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = "kids_board/settings.html"
