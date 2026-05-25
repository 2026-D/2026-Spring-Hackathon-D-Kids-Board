# Create your views here.
from django.contrib.auth import (
    login,
    logout,
)  # 登録ユーザーをログイン状態にする # ログアウト状態にする
from django.shortcuts import render, redirect  # renderはHTML表示 #redirectは別ページ移動
from .forms import SignUpForm, LoginForm, ChildForm  # forms.pyからSignUpForm, LoginFormを読み込む
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from .models import PrepItem
from django.contrib.auth.mixins import LoginRequiredMixin  # ログイン必須のクラスを読み込む
from django.contrib.auth.decorators import login_required
from .models import Child
from django.utils import timezone
from django.shortcuts import get_object_or_404


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


@login_required
def home_view(request):  # DBから子ども情報の一覧を取得、home画面表示

    children = Child.objects.filter(  # childrenテーブルから、表示する子どもの情報を取得
        parent=request.user,  # ログインしているユーザーの子どもを取得
        deleted_at__isnull=True,  # 削除されていない子どもだけを取得
    )

    return render(  # home.htmlを表示
        request,
        "kids_board/home.html",
        {
            "children": children,  # コンテキスト Python(view) → HTML(template)へ渡すデータ
        },
    )


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


# @login_required
# def kids_board_view(request): # kids_board.htmlを表示する

#     return render(
#         request,
#         "kids_board/kids_board.html",
#     )

# class HomeView(LoginRequiredMixin, TemplateView):
#     template_name = "/home.html"

# class HomeView(LoginRequiredMixin, TemplateView):
#     template_name = "kids_board/home.html"

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

#         context["children"] = Child.objects.filter(
#             parent=self.request.user,
#             deleted_at__isnull=True,
#         )

#         return context


class KidsBoardView(LoginRequiredMixin, TemplateView):
    template_name = "kids_board/kids_board.html"

    # kids_board.htmlに渡すデータ（context)を作るメソッドを定義（花丸表示用）。
    def get_context_data(self, **kwargs):
        # 親クラス(TemplateView)が用意する基本のcontextを取得し、context変数に格納.
        context = super().get_context_data(**kwargs)
        # 花丸を表示する場合はTrueにする。
        # 子供のタスク達成状況などに応じてTrue/Falseを切り替える想定。
        context["show_badge"] = False
        return context


class PrepItemsMornView(LoginRequiredMixin, TemplateView):
    template_name = "kids_board/prep_items_morn.html"


class PrepItemsView(LoginRequiredMixin, TemplateView):
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


# class SettingsView(LoginRequiredMixin, TemplateView):
#     template_name = "kids_board/settings.html"
