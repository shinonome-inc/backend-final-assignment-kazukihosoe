from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from tweets.models import Tweet

User = get_user_model()


class TestHomeView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="testpassword")
        self.client.login(username="tester", password="testpassword")
        self.url = reverse("tweets:home")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(list(response.context['tweets']), [])

        # データ作成（created の降順で Third, Second, First になる想定）
        Tweet.objects.create(title="First", content="c1")
        Tweet.objects.create(title="Second", content="c2")
        Tweet.objects.create(title="Third", content="c3")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        context_qs = list(response.context['tweets'])
        db_qs = list(Tweet.objects.order_by('-created'))
        # PK 順（並び順）一致
        self.assertEqual([t.pk for t in context_qs], [t.pk for t in db_qs])
        # タイトル集合一致
        self.assertEqual({t.title for t in context_qs}, {t.title for t in db_qs})


class TestTweetCreateView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", password="testpassword")
        self.client.login(username="test", password="testpassword")
        self.url = reverse('tweets:create')

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tweets/create.html')

    def test_success_post(self):
        valid_data = {
            'title': 'test',
            'content': 'testtext'
        }
        response = self.client.post(self.url, valid_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse('tweets:home'),
            status_code=302,
            target_status_code=200
        )
        self.assertTrue(Tweet.objects.filter(title='test', content='testtext').exists())

    def test_failure_post_with_empty_content(self):
        invalid_data = {
            'title': 'test',
            'content': ''
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context['form']
        self.assertEqual(response.status_code, 200)
        self.assertIn('このフィールドは必須です。', form.errors['content'])
        self.assertFalse(Tweet.objects.filter(title='test', content='').exists())

    def test_failure_post_with_too_long_content(self):
        # content max_length=100 を超える 101 文字
        long_content = 'x' * 101
        invalid_data = {
            'title': 'test',
            'content': long_content
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context['form']
        self.assertEqual(response.status_code, 200)
        self.assertIn('content', form.errors)
        self.assertFalse(Tweet.objects.filter(title='test').exists())


class TestTweetDetailView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="viewer", password="pass12345")
        self.client.login(username="viewer", password="pass12345")
        # 詳細表示対象のツイートを作成（author を設定）
        self.tweet = Tweet.objects.create(title="Detail Title", content="Detail Content")
        self.url = reverse('tweets:detail', args=[self.tweet.pk])

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tweets/detail.html')
        # コンテキストのオブジェクト一致（DetailView の既定: context_object_name は 'tweet'）
        self.assertEqual(response.context['tweet'].pk, self.tweet.pk)
        self.assertContains(response, self.tweet.title)
        self.assertContains(response, self.tweet.content)

    
class TestTweetDeleteView(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='testpassword')
        self.other = User.objects.create_user(username='other', password='testpassword')
        # owner が作成
        self.tweet = Tweet.objects.create(title='deletetitle', content='deletecontent', author=self.owner)
        self.url = reverse('tweets:delete', args=[self.tweet.pk])

    # def test_get_confirm_page(self):
    #     self.client.login(username='owner', password='testpassword')
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'tweets/tweet_confirm_delete.html')
    #     self.assertContains(response, self.tweet.title)

    def test_success_post(self):
        self.client.login(username='owner', password='testpassword')
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('tweets:home'))
        self.assertFalse(Tweet.objects.filter(pk=self.tweet.pk).exists())
    
    # def test_failure_not_logged_in(self):
    #     response = self.client.post(self.url)
    #     self.assertEqual(response.status_code, 302)
    #     login_url = reverse('accounts:login')
    #     self.assertTrue(response.url.startswith(login_url))
    #     self.assertTrue(Tweet.objects.filter(pk=self.tweet.pk).exists())

    # def test_failure_other_user(self):
    #     self.client.login(username='other', password='testpassword')
    #     response = self.client.post(self.url)
    #     # 権限なし -> 404 (get_queryset でフィルタされ存在しない扱い)
    #     self.assertEqual(response.status_code, 404)
    #     self.assertTrue(Tweet.objects.filter(pk=self.tweet.pk).exists())

    # def test_failure_not_exist_pk(self):
    #     self.client.login(username='owner', password='testpassword')
    #     invalid_url = reverse('tweets:delete', args=[self.tweet.pk + 999])
    #     response = self.client.post(invalid_url)
    #     self.assertEqual(response.status_code, 404)

    def test_failure_post_with_not_exist_tweet(self):
        self.client.login(username='owner', password='testpassword')
        invalid_url = reverse('tweets:delete', args=[self.tweet.pk + 999])
        response = self.client.post(invalid_url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Tweet.objects.filter(pk=self.tweet.pk).exists())

    def test_failure_post_with_incorrect_user(self):
        self.client.login(username='other', password='testpassword')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Tweet.objects.filter(pk=self.tweet.pk).exists())


class TestLikeView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.other_user = User.objects.create_user(username='otheruser', password='testpassword')
        self.tweet = Tweet.objects.create(
            title='Test Tweet',
            content='Test Content',
            author=self.user
        )
        self.client.login(username='testuser', password='testpassword')
        self.url = reverse('tweets:like', args=[self.tweet.pk])

    def test_success_post(self):
        """いいね成功テスト"""
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('tweets:detail', args=[self.tweet.pk]))
        
        # いいねが作成されているか確認
        from .models import Like
        self.assertTrue(Like.objects.filter(user=self.user, tweet=self.tweet).exists())
        self.assertEqual(self.tweet.like_count(), 1)

    def test_failure_post_with_not_exist_tweet(self):
        """存在しないツイートへのいいねテスト"""
        invalid_url = reverse('tweets:like', args=[self.tweet.pk + 999])
        response = self.client.post(invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_failure_post_with_liked_tweet(self):
        """既にいいね済みのツイートへのいいねテスト"""
        from .models import Like

        # 事前にいいねを作成
        Like.objects.create(user=self.user, tweet=self.tweet)
        
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('tweets:detail', args=[self.tweet.pk]))
        
        # いいねが重複作成されていないことを確認
        self.assertEqual(Like.objects.filter(user=self.user, tweet=self.tweet).count(), 1)

    def test_login_required(self):
        """ログイン必須テスト"""
        self.client.logout()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        login_url = reverse('accounts:login')
        self.assertTrue(response.url.startswith(login_url))


class TestUnLikeView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.other_user = User.objects.create_user(username='otheruser', password='testpassword')
        self.tweet = Tweet.objects.create(
            title='Test Tweet',
            content='Test Content',
            author=self.user
        )
        self.client.login(username='testuser', password='testpassword')
        self.url = reverse('tweets:unlike', args=[self.tweet.pk])

    def test_success_post(self):
        """いいね取り消し成功テスト"""
        from .models import Like

        # 事前にいいねを作成
        Like.objects.create(user=self.user, tweet=self.tweet)
        
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('tweets:detail', args=[self.tweet.pk]))
        
        # いいねが削除されているか確認
        self.assertFalse(Like.objects.filter(user=self.user, tweet=self.tweet).exists())
        self.assertEqual(self.tweet.like_count(), 0)

    def test_failure_post_with_not_exist_tweet(self):
        """存在しないツイートへのいいね取り消しテスト"""
        invalid_url = reverse('tweets:unlike', args=[self.tweet.pk + 999])
        response = self.client.post(invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_failure_post_with_unliked_tweet(self):
        """いいねしていないツイートへのいいね取り消しテスト"""
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('tweets:detail', args=[self.tweet.pk]))
        
        # いいねが存在しないことを確認
        from .models import Like
        self.assertFalse(Like.objects.filter(user=self.user, tweet=self.tweet).exists())

    def test_login_required(self):
        """ログイン必須テスト"""
        self.client.logout()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        login_url = reverse('accounts:login')
        self.assertTrue(response.url.startswith(login_url))
