from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

# get_user_modelはAUTH_USER_MODELを読み込んでいる。
User = get_user_model()  # 基本的にはget_user_modelはグローバル変数として扱う。


class SignupForm(UserCreationForm):
    class Meta:
        model = User  # modelを指定してDBに保存
        fields = ("username", "email")  # 入力する事項をカスタマイズ　ここではblankにできないもののみ指定
