from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


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

        self.fields["password1"].label = "パスワード"
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
