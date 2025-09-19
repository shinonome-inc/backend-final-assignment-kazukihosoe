from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class TestSignupView(TestCase):
    # serUpで準備
    def setUp(self):
        self.url = reverse("accounts:signup")

    # GETのテスト
    def test_success_get(self):
        # テスト用のクライアントを用いてself.urlにGETリクエストを送りそのresponseを取得
        response = self.client.get(self.url)
        # ステータスコードは200が帰ってくることを期待
        self.assertEqual(response.status_code, 200)
        # 使用されたtemplateがaccounts/signup.htmlであることを期待
        self.assertTemplateUsed(response, "accounts/signup.html")

    # POSTのテスト
    def test_success_post(self):
        # 送りたいデータをdict型で準備。キーはsignupformのフィールドと一致させる。
        valid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        # formにデータを打ち込んでPOSTを行った処理を再現。
        # テスト用のクライアントを使ってself.urlにvalid_dataをPOSTリクエストとして送りresponseを取得
        response = self.client.post(self.url, valid_data)

        # responseに対して想定通りのurlの表示と、リダイレクト、テンプレート表示成功のステータスコードをそれぞれ確認。
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        # 2の確認　ユーザーが作成されること
        # DBにユーザーが作成されていることをユニークな値（username）を用いて確認。存在すればTrueを返す。
        self.assertTrue(User.objects.filter(username=valid_data["username"]).exists())

        # 3の確認　ログイン状態になること
        # テスト用クライアントのセッションにログイン状態を示すキーが含まれているかを確認。
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_username(self):
        # 不正データ（usernameが空）を準備
        invalid_data = {
            "username": "",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        # テスト用のクライアントを用いてself.url, invalid_dataをPOSTしたときのresponseを取得。
        response = self.client.post(self.url, invalid_data)
        # responseからtemplateに渡されたフォームオブジェクトを取得。エラーの確認時に使う。
        form = response.context["form"]

        # テンプレートが正しく表示されていることを確認。
        self.assertEqual(response.status_code, 200)
        # invalid_dataのユーザーが作成されていないことを確認。
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        # formに入力した値がバリデーションを通過するか調べる。
        self.assertFalse(form.is_valid())
        # エラーメッセージを取得し、そこに特定のメッセージが含まれていることを確認。
        self.assertIn("このフィールドは必須です。", form.errors["username"])

    def test_failure_post_with_empty_form(self):
        invalid_data = {
            "username": "",
            "email": "",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["username"])
        self.assertIn("このフィールドは必須です。", form.errors["email"])
        self.assertIn("このフィールドは必須です。", form.errors["password1"])
        self.assertIn("このフィールドは必須です。", form.errors["password2"])
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())

    def test_failure_post_with_empty_email(self):
        invalid_data = {
            "username": "testuser",
            "email": "",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertIn("このフィールドは必須です。", form.errors["email"])
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())

    def test_failure_post_with_empty_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertIn("このフィールドは必須です。", form.errors["password1"])
        self.assertIn("このフィールドは必須です。", form.errors["password2"])
        self.assertFalse(User.objects.filter(username=invalid_data["username"]))

    def test_failure_post_with_duplicated_user(self):
        valid_data1 = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        valid_data2 = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        self.client.post(self.url, valid_data1)
        response = self.client.post(self.url, valid_data2)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertIn("同じユーザー名が既に登録済みです。", form.errors["username"])
        self.assertEqual(User.objects.filter(username=valid_data2["username"]).count(), 1)

    def test_failure_post_with_invalid_email(self):
        invalid_data = {
            "username": "testuser",
            "email": "test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertIn("有効なメールアドレスを入力してください。", form.errors["email"])
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())

    def test_failure_post_with_too_short_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "test",
            "password2": "test",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertIn("このパスワードは短すぎます。最低 8 文字以上必要です。", form.errors["password2"])
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())

    def test_failure_post_with_password_similar_to_username(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testuser123",  # ユーザー名に似ているパスワード
            "password2": "testuser123",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertIn("このパスワードは ユーザー名 と似すぎています。", form.errors["password2"])
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())

    def test_failure_post_with_only_numbers_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "12345678",
            "password2": "12345678",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertIn("このパスワードは数字しか使われていません。", form.errors["password2"])
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())

    def test_failure_post_with_mismatch_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpasswor",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertIn("確認用パスワードが一致しません。", form.errors["password2"])
        self.assertFalse(User.objects.filter(username=invalid_data["username"]))


class TestLoginView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test",
            email="test@test.com",
            password="testpassword",
        )
        self.url = reverse("accounts:login")

    def test_success_get(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_success_post(self):
        valid_data = {"username": "test", "password": "testpassword"}
        response = self.client.post(self.url, valid_data)
        # print(response.context['form'].errors)
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )

    def test_failure_post_with_not_exists_user(self):
        invalid_data = {"username": "test1", "password": "testpassword"}
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "正しいユーザー名とパスワードを入力してください。どちらのフィールドも大文字と小文字は区別されます。",
            form.errors["__all__"],
        )
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_password(self):
        invalid_data = {"username": "test", "password": ""}
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertIn("このフィールドは必須です。", form.errors["password"])


class TestLogoutView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test",
            email="test@test.com",
            password="testpassword",
        )
        self.client.login(username="test", password="testpassword")
        self.url = reverse("accounts:logout")

    def test_success_post(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("accounts:login"), status_code=302, target_status_code=200)
        self.assertNotIn(SESSION_KEY, self.client.session)


# class TestUserProfileView(TestCase):
#     def test_success_get(self):


# class TestUserProfileEditView(TestCase):
#     def test_success_get(self):

#     def test_success_post(self):

#     def test_failure_post_with_not_exists_user(self):

#     def test_failure_post_with_incorrect_user(self):


class TestFollowView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="pass123")
        self.user2 = User.objects.create_user(username="user2", password="pass123")
        self.client.login(username="user1", password="pass123")
        self.url = reverse("accounts:follow", args=[self.user2.username])

    def test_success_post(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("accounts:user_profile", args=[self.user2.username]))
        # フォロー関係が作成されているか確認
        from .models import Connection

        connection = Connection.objects.get(user=self.user1)
        self.assertTrue(connection.following.filter(username=self.user2.username).exists())

    def test_failure_post_with_not_exist_user(self):
        invalid_url = reverse("accounts:follow", args=["nonexistent"])
        response = self.client.post(invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_failure_post_with_self(self):
        self_url = reverse("accounts:follow", args=[self.user1.username])
        response = self.client.post(self_url)
        self.assertRedirects(response, reverse("accounts:user_profile", args=[self.user1.username]))
        # フォロー関係が作成されていないことを確認
        from .models import Connection

        try:
            connection = Connection.objects.get(user=self.user1)
            self.assertFalse(connection.following.filter(username=self.user1.username).exists())
        except Connection.DoesNotExist:
            pass  # Connectionが作成されていないのが正常

    def test_success_post_toggle_follow(self):
        # 最初にフォロー
        response = self.client.post(self.url)
        from .models import Connection

        connection = Connection.objects.get(user=self.user1)
        self.assertTrue(connection.following.filter(username=self.user2.username).exists())

        # 再度POSTでフォロー解除
        response = self.client.post(self.url)
        self.assertFalse(connection.following.filter(username=self.user2.username).exists())


class TestUnfollowView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="pass123")
        self.user2 = User.objects.create_user(username="user2", password="pass123")
        self.client.login(username="user1", password="pass123")
        self.url = reverse("accounts:unfollow", args=[self.user2.username])

        # 事前にフォロー関係を作成
        from .models import Connection

        connection = Connection.objects.create(user=self.user1)
        connection.following.add(self.user2)

    def test_success_post(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("accounts:user_profile", args=[self.user2.username]))

        # フォロー関係が削除されているか確認
        from .models import Connection

        connection = Connection.objects.get(user=self.user1)
        self.assertFalse(connection.following.filter(username=self.user2.username).exists())

    def test_failure_post_with_not_exist_user(self):
        invalid_url = reverse("accounts:unfollow", args=["nonexistent"])
        response = self.client.post(invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_failure_post_with_not_following(self):
        # フォローしていない状態でアンフォローを試す
        user3 = User.objects.create_user(username="user3", password="pass123")
        url = reverse("accounts:unfollow", args=[user3.username])
        response = self.client.post(url)
        self.assertRedirects(response, reverse("accounts:user_profile", args=[user3.username]))

    def test_failure_post_with_self(self):
        self_url = reverse("accounts:unfollow", args=[self.user1.username])
        response = self.client.post(self_url)
        self.assertRedirects(response, reverse("accounts:user_profile", args=[self.user1.username]))


# class TestFollowingListView(TestCase):
#     def test_success_get(self):


# class TestFollowerListView(TestCase):
#     def test_success_get(self):
