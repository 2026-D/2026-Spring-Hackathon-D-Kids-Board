from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Child


class SignUpForm(UserCreationForm):  # UserCreationFormを継承
    email = forms.EmailField(  # メールアドレス入力欄を作る
        required=True,  # 項目は必須入力
        label="Eメール",  # ラベルを追加
        widget=forms.EmailInput(  # <input type="email">
            attrs={  # HTMLの追加設定
                "class": "form-control",  # Bootstrap用のCSSクラス
            }
        ),
    )

    class Meta:
        # 標準Userを使う
        model = User
        # フォーム表示の入力項目を指定
        fields = ("username", "email", "password1", "password2")
        widgets = {
            "username": forms.TextInput(  # 文字入力欄
                attrs={
                    "class": "form-control",
                }
            ),
        }

        labels = {
            "username": "ユーザー名",
        }

    def __init__(self, *args, **kwargs):  # フォーム完成後の微調整をする
        super().__init__(*args, **kwargs)  # 親クラスを初期化処理

        self.label_suffix = ""  # フォームのlabelの最後につく文字を空にする

        self.fields["username"].help_text = ""  # 説明文を空文字にする
        self.fields["password1"].help_text = ""
        self.fields["password2"].help_text = ""

        self.fields["password1"].label = "パスワード"  # 画面の表示名を日本語にする
        self.fields["password2"].label = "パスワード確認用"

        self.fields["password1"].widget.attrs.update(  # <input> のclassやplaceholderを設定する
            {
                "class": "form-control",
            }
        )

        self.fields["password2"].widget.attrs.update(
            {
                "class": "form-control",
            }
        )


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.label_suffix = ""  # フォームのlabelの最後につく文字を空にする

        self.fields["username"].label = "ユーザー名"  # 画面の表示名を日本語にする
        self.fields["password"].label = "パスワード"

        self.fields["username"].widget.attrs.update(
            {
                "class": "form-control",
            }
        )

        self.fields["password"].widget.attrs.update(
            {
                "class": "form-control",
            }
        )


class ChildForm(forms.ModelForm):  # Childモデルと連動するフォーム
    class Meta:  # フォームの設定を書く場所
        model = Child  # Childテーブル用
        fields = ("child_name", "child_icon")  # フォームの入力項目
        labels = {
            "child_name": "子どもの名前",  # 画面に表示するラベル名
            "child_icon": "アイコン",
        }
        widgets = {
            "child_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),  # HTMLの入力欄の見た目を指定
            "child_icon": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()  # フォームの基本的なバリデーションを実行

        child_name = cleaned_data.get("child_name")  # 入力された子どもの名前を取得

        if child_name:
            # 同じユーザーが同名の子どもを登録していないか確認
            if (
                Child.objects.filter(
                    parent=self.instance.parent,
                    child_name=child_name,
                    deleted_at__isnull=True,
                )
                .exclude(id=self.instance.id)
                .exists()
            ):
                self.add_error("child_name", "同じ名前の子どもは既に登録されています。")

        return cleaned_data
