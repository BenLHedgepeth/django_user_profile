from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from ..models import Profile
from ..forms import ProfileForm


class RequestSignUpView(TestCase):

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
            reverse("accounts:profile", kwargs={'user_id': 1}),
            follow=True
        )
        self.assertRedirects(
            response, '/accounts/sign_in/?next=/accounts/profile/1/'
        )
    #     # self.assertIn('/accounts/sign_in', response.url)
    #     # self.assertEqual(response.status_code, 302)

    def test_redirect_to_login_from_edit_profile_view(self):
        response = self.client.get(
            reverse("accounts:edit_profile", kwargs={'user_id': 1}),

        )
        self.assertRedirects(
            response, '/accounts/sign_in/?next=/accounts/profile_edit/1/'
        )


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
                kwargs={'user_id': 1}), data=self.profile_data
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
                "accounts:edit_profile", kwargs={'user_id': 1}
            ),
            data=self.mock_post_data, follow=True
        )
        self.assertTemplateUsed(response, 'accounts/profile.html')
        self.assertRedirects(response, '/accounts/profile/1/')
        self.assertContains(response, 'Lorem ipsum dolor sit amet')


class UpdatePasswordTestCase(TestCase):
    '''Verify that a User receives a message telling them
    that a new password cannot contain their username, first name,
    or last name.'''

    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(
            "test_user", password="Secret*#7_code!",
            first_name='Fn', last_name='Ln'
        )
        cls.new_password = cls.test_user.get_full_name()

        cls.passwords = {
            'old_password': "Secret*#7_code!",
            'new_password1': f"{cls.new_password}-{cls.test_user}$8",
            'new_password2': f"{cls.new_password}-{cls.test_user}$8"
        }

    def test_password_update_fail(self):
        self.client.force_login(self.test_user)
        response = self.client.post(
            reverse("accounts:change_password", kwargs={'user_id': 1}),
            data=self.passwords,
            follow=True
        )
        self.assertTemplateUsed(response, 'accounts/change_password.html')
        self.assertContains(
            response,
            "Password cannot contain: Username; First Name; Last Name"
        )


class UpdatePasswordTestCase(TestCase):
    '''Verify that a User receives a message telling them
    that their password has changed.'''

    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(
            "test_user", password="Secret*#7_code!",
            first_name='Fn', last_name='Ln'
        )
        cls.new_password = cls.test_user.get_full_name()

        cls.passwords = {
            'old_password': "Secret*#7_code!",
            'new_password1': "SeCretPa$$word6*",
            'new_password2': "SeCretPa$$word6*"
        }

    def test_password_update_fail(self):
        self.client.force_login(self.test_user)
        response = self.client.post(
            reverse("accounts:change_password", kwargs={'user_id': 1}),
            data=self.passwords,
            follow=True
        )
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, "Your password is updated!")
