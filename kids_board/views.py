# Create your views here.
from django.contrib.auth import login  # 登録ユーザーをログイン状態にする
from django.shortcuts import render, redirect  # renderはHTML表示 #redirectは別ページ移動
from .forms import SignUpForm, LoginForm  # forms.pyからSignUpForm, LoginFormを読み込む
from django.views.generic import TemplateView


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


# todo:LoginRequiredMixinを追加
class HomeView(TemplateView):
    template_name = "/home.html"


# todo:LoginRequiredMixinを追加
class KidsBoardView(TemplateView):
    template_name = "kids_board/kids_board.html"

    # kids_board.htmlに渡すデータ（context)を作るメソッドを定義（花丸表示用）。
    def get_context_data(self, **kwargs):
        # 親クラス(TemplateView)が用意する基本のcontextを取得し、context変数に格納.
        context = super().get_context_data(**kwargs)
        # 花丸を表示する場合はTrueにする。
        # 子供のタスク達成状況などに応じてTrue/Falseを切り替える想定。
        context["show_badge"] = False
        return context


# todo:LoginRequiredMixinを追加
class PrepItemsMornView(TemplateView):
    template_name = "kids_board/prep_items_morn.html"


# todo:LoginRequiredMixinを追加
class PrepItemsView(TemplateView):
    template_name = "kids_board/prep_items.html"


# todo:LoginRequiredMixinを追加
class ScheduleView(TemplateView):
    template_name = "kids_board/schedule.html"
