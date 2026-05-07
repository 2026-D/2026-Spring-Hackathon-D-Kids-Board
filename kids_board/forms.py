from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):  # UserCreationFormを継承
    email = forms.EmailField(  # メールアドレス入力欄を作る
        required=True,  # 項目は必須入力
        widget=forms.EmailInput(  # <input type="email">
            attrs={  # HTMLの追加設定
                "class": "form-control",  # Bootstrap用のCSSクラス
                "placeholder": "メールアドレス",  # プレースホルダー
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
                    "placeholder": "ユーザー名",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # 親クラス UserCreationForm の初期化処理

        self.fields["username"].help_text = ""  # 説明文を空文字にする
        self.fields["password1"].help_text = ""
        self.fields["password2"].help_text = ""

        self.fields["password1"].widget.attrs.update(  # <input> のclassやplaceholderを設定する
            {
                "class": "form-control",
                "placeholder": "パスワード",
            }
        )

        self.fields["password2"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "パスワード確認",
            }
        )
