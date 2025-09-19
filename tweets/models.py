from django.conf import settings
from django.db import models


class Tweet(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tweets",
        null=True,
        blank=True,
    )
    title = models.CharField(verbose_name='タイトル', max_length=30, null=False, blank=False)
    content = models.TextField(verbose_name='コンテンツ', max_length=50, null=False, blank=False)
    created = models.DateTimeField(verbose_name='作成日時', auto_now=True)
    updated = models.DateTimeField(verbose_name='更新日時', auto_now_add=True)

    def like_count(self):
        return self.likes.count()
    
    def is_liked_by(self, user):
        return self.likes.filter(user=user).exists()
    
    def __str__(self):
        return self.title


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'tweet')

    def __str__(self):
        return f"{self.user.username} likes {self.tweet.title}"
