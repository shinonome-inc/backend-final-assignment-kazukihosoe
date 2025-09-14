from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import SignupForm


class SignupView(CreateView):
    # クラス変数（アトリビュート）
    form_class = SignupForm
    # クラスベースビューではこの行によってクラス属性でフォームクラスを指定している。
    # これにより自動でsignupformを使ってフォームを作成し、テンプレートに渡す。
    template_name = "accounts/signup.html"
    # success_url には実URLが必要なため URL 名を reverse して設定する
    success_url = reverse_lazy("tweets:home")

    def form_valid(self, form):
        response = super().form_valid(form)
        # form_validはデータを保存してurlを返す。つまり今response=HttpResponseRedirect(self.get_success_url())
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password1"]
        # バリデーション済みのデータの中から抜き出している。
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return response


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context
