from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, View

from .forms import CreateForm
from .models import Like, Tweet


class HomeView(LoginRequiredMixin, ListView):
    model = Tweet
    context_object_name = "tweets"
    template_name = "tweets/home.html"

    def get_queryset(self):
        return Tweet.objects.order_by("-created")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 各ツイートにいいね状態を追加
        tweets = context["tweets"]
        for tweet in tweets:
            tweet.user_has_liked = tweet.is_liked_by(self.request.user)
        return context


class TweetCreateView(LoginRequiredMixin, CreateView):
    template_name = "tweets/create.html"
    model = Tweet
    success_url = reverse_lazy("tweets:home")
    form_class = CreateForm

    def form_valid(self, form):
        form.instance.author = self.request.user  # ログイン中のユーザーをauthorに設定
        return super().form_valid(form)


class TweetDetailView(LoginRequiredMixin, DetailView):
    model = Tweet
    template_name = "tweets/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tweet = context["tweet"]
        tweet.user_has_liked = tweet.is_liked_by(self.request.user)
        return context


class TweetDeleteView(LoginRequiredMixin, DeleteView):
    model = Tweet
    success_url = reverse_lazy("tweets:home")
    template_name = "tweets/tweet_confirm_delete.html"

    def get_queryset(self):
        return super().get_queryset().filter(author=self.request.user)


class LikeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        tweet = get_object_or_404(Tweet, pk=pk)

        if tweet.is_liked_by(request.user):
            messages.warning(request, "既にいいねしています。")
        else:
            Like.objects.create(user=request.user, tweet=tweet)
            messages.success(request, f"{tweet.title}にいいねしました！")

        return redirect("tweets:detail", pk=tweet.pk)


class UnLikeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        tweet = get_object_or_404(Tweet, pk=pk)

        try:
            like = Like.objects.get(user=request.user, tweet=tweet)
            like.delete()
            messages.success(request, f"{tweet.title}のいいねを取り消しました。")
        except Like.DoesNotExist:
            messages.warning(request, "いいねしていません。")

        return redirect("tweets:detail", pk=tweet.pk)
