from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):  # UserCreationFormを継承
    class Meta:
        # 標準Userを使う
        model = User
        # フォーム表示の入力項目を指定
        fields = ("username", "email", "password1", "password2")
