from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from ..models import Profile
from ..forms import ProfileForm


class RequestSignUpView(TestCase):
    '''Verify that "GET" and "POST" requests'''

    @classmethod
    def setUpTestData(cls):
        cls.test_post_data = {
            'username': 'testuser',
            'first_name': 'test_fn',
            'last_name': 'test_ln',
            'email': 'test@email.com',
            'verify_email': 'test@email.com',
            'password1': 'efj8eE8*3jaaaaaa#',
            'password2': 'efj8eE8*3jaaaaaa#'
        }

    def test_get_sign_up_view(self):
        response = self.client.get(
            reverse("accounts:sign_up")
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/sign_up.html', count=1)

    def test_post_sign_up_view(self):
        response = self.client.post(
            reverse("accounts:sign_up"), data=self.test_post_data, follow=True
        )
        expected_url = response.request.get('PATH_INFO')
        self.assertRedirects(response, expected_url)


class RequestSignInView(TestCase):
    '''Verify that a registered user is redirected
    to their home page after successfully logging in'''

    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            'username': 'testuser',
            'password': '*Dh&M3h36v*$J*'
        }
        cls.test_user = User.objects.create_user(**cls.user_data)
        Profile.objects.create(
            user=cls.test_user,
            birth="2019-01-01",
            bio="A little info about me..."
        )

    def test_user_login_success(self):
        self.client.login(**self.user_data)
        '''Setting `follow=True` returns the endpoint for the response'''
        response = self.client.post(
            reverse('accounts:sign_in'), self.user_data, follow=True
        )
        self.assertRedirects(response, reverse('home'))
        self.assertContains(response, self.test_user)


class LoginRedirectRequest(TestCase):
    '''Verify that a user is redirected to
    a login page if they are not logged in.'''

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(
            username="testuser",
            password='*Dh&M3h36v*$J*'
        )

    def test_redirect_to_login_from_profile_view(self):
        response = self.client.get(
            reverse("accounts:profile", kwargs={'username': 'testuser'})
        )
        self.assertIn('/accounts/sign_in', response.url)
        self.assertEqual(response.status_code, 302)

    def test_redirect_to_login_from_edit_profile_view(self):
        response = self.client.get(
            reverse("accounts:edit_profile", kwargs={'username': 'testuser'})
        )
        self.assertIn('/accounts/sign_in', response.url)
        self.assertEqual(response.status_code, 302)


class CreateProfileView(TestCase):
    '''Verify that a profile is created when a user
    is required to provide data in a profile form'''
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(
            username="testuser",
            password='*Dh&M3h36v*$J*'
        )

        cls.profile_data = {
            'user': cls.test_user,
            'birth': '2019-01-01',
            'bio': 'A little about me...'
        }

    def test_find(self):
        self.client.force_login(self.test_user)
        response = self.client.post(
            reverse(
                'accounts:new_profile',
                kwargs={'username': self.test_user}), data=self.profile_data
        )
        profile = Profile.objects.filter(user=self.test_user).count()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(profile, 1)


class EditedProfileView(TestCase):
    '''Verify that any changes made to user's profile
    are saved when they click "Update Profile".'''

    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(
            username="testuser",
            password='*Dh&M3h36v*$J*'
        )
        Profile.objects.create(
            user=cls.test_user,
            birth="2019-01-01",
            bio="A little info about me..."
        )

        cls.test_user_data = {
            'username': cls.test_user.username,
            'first_name': 'test_fn',
            'last_name': 'test_ln',
            'email': 'test@email.com',
            'verify_email': 'test@email.com'
        }
        cls.updated_profile_data = {
            'birth': "2019-12-12",
            'bio': "Lorem ipsum dolor sit amet"
        }

        cls.mock_post_data = {
            **cls.test_user_data,
            **cls.updated_profile_data
        }

    def test_edited_profile_displays_new_profile(self):
        self.client.force_login(self.test_user)
        response = self.client.post(
            reverse(
                "accounts:edit_profile", kwargs={'username': self.test_user}
            ),
            data=self.mock_post_data, follow=True
        )
        print(response)
        self.assertTemplateUsed(response, 'accounts/profile.html')
        self.assertRedirects(response, '/accounts/profile/testuser/')
        self.assertContains(response, 'Lorem ipsum dolor sit amet')
