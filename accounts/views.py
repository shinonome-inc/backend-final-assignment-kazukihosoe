from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, View

from tweets.models import Tweet

from .forms import SignupForm
from .models import Connection

User = get_user_model()


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


class UserProfileView(LoginRequiredMixin, ListView):
    template_name = "accounts/profile.html"
    model = Tweet
    context_object_name = 'tweets'

    def get_queryset(self):
        username = self.kwargs['username']
        self.profile_user = get_object_or_404(User, username=username)
        return Tweet.objects.filter(author=self.profile_user).order_by('-created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_user'] = self.profile_user
        
        # フォロー状態の確認
        try:
            user_connection = Connection.objects.get(user=self.request.user)
            context['is_following'] = user_connection.following.filter(username=self.profile_user.username).exists()
        except Connection.DoesNotExist:
            context['is_following'] = False
        
        # フォロー数・フォロワー数
        try:
            profile_connection = Connection.objects.get(user=self.profile_user)
            context['following_count'] = profile_connection.following.count()
        except Connection.DoesNotExist:
            context['following_count'] = 0
        
        context['follower_count'] = Connection.objects.filter(following=self.profile_user).count()
        
        return context


class FollowView(LoginRequiredMixin, View):
    def post(self, request, username, *args, **kwargs):
        to_user = get_object_or_404(User, username=username)
        from_user = request.user

        if from_user == to_user:
            messages.error(request, "自分自身をフォローすることはできません。")
            return redirect('accounts:user_profile', username=to_user.username)
        
        from_user_connection, created = Connection.objects.get_or_create(user=from_user)
        is_following = from_user_connection.following.filter(username=to_user.username).exists()

        if is_following:
            from_user_connection.following.remove(to_user)
            messages.success(request, f"{to_user.username}さんのフォローを解除しました。")

        else:
            from_user_connection.following.add(to_user)
            messages.success(request, f"{to_user.username}さんをフォローしました。")

        return redirect('accounts:user_profile', username=to_user.username)


class UnFollowView(LoginRequiredMixin, View):
    def post(self, request, username, *args, **kwargs):
        to_user = get_object_or_404(User, username=username)
        from_user = request.user

        if from_user == to_user:
            messages.error(request, "自分自身をフォロー解除することはできません。")
            return redirect('accounts:user_profile', username=to_user.username)
        
        try:
            from_user_connection = Connection.objects.get(user=from_user)
            is_following = from_user_connection.following.filter(username=to_user.username).exists()
            
            if is_following:
                from_user_connection.following.remove(to_user)
                messages.success(request, f"{to_user.username}さんのフォローを解除しました。")
            else:
                messages.warning(request, f"{to_user.username}さんをフォローしていません。")
        except Connection.DoesNotExist:
            messages.warning(request, f"{to_user.username}さんをフォローしていません。")

        return redirect('accounts:user_profile', username=to_user.username)


class FollowingListView(LoginRequiredMixin, ListView):
    template_name = "accounts/following_list.html"
    context_object_name = 'following_users'

    def get_queryset(self):
        username = self.kwargs['username']
        self.profile_user = get_object_or_404(User, username=username)
        try:
            connection = Connection.objects.get(user=self.profile_user)
            return connection.following.all()
        except Connection.DoesNotExist:
            return User.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_user'] = self.profile_user
        return context


class FollowerListView(LoginRequiredMixin, ListView):
    template_name = "accounts/follower_list.html"
    context_object_name = 'follower_users'

    def get_queryset(self):
        username = self.kwargs['username']
        self.profile_user = get_object_or_404(User, username=username)
        # このユーザーをフォローしているConnection一覧を取得し、そのuserを取得
        connections = Connection.objects.filter(following=self.profile_user)
        return User.objects.filter(id__in=connections.values_list('user', flat=True))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_user'] = self.profile_user
        return context
