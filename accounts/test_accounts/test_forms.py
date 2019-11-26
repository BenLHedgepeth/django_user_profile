from datetime import datetime
from os.path import join, dirname

from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from ..validate import validate_bio, validate_date
from .. import models
from ..forms import UserAccountCreationForm, ProfileForm


class FormFieldPlaceHolder(TestCase):
    '''Verify that each widget in UserAccountCreationForm
    has a placeholder attribute.'''
    
    @classmethod
    def setUpTestData(cls):
        cls.test_profile_form = UserAccountCreationForm()

    def test_field_widget_attrs(self):
        for field in self.test_profile_form.fields.values():
            widget = field.widget.attrs
            self.assertTrue('placeholder' in widget)


class ValidateFormUserEmail(TestCase):
    '''Verify that a validation error is raised 
    when a user enters a mismatching email address'''

    @classmethod
    def setUpTestData(cls):
        cls.user_form_data = {
            'username': 'testuser', 
            'first_name': 'test_fn',
            'last_name': 'test_ln', 
            'email': 'test@email.com',
            'verify_email': '', 
            'password1': 'secretcode',
            'password2': 'secretcode'
        }
        cls.test_accountform = UserAccountCreationForm(cls.user_form_data)
        cls.form_errors = cls.test_accountform.errors

    def test_invalid_email_error(self):
        self.assertTrue('verify_email' in self.form_errors)

class ValidateUserAccountForm(TestCase):
    '''Verify that a new User account is created when
    a User Account Creation page is submitted'''

    @classmethod
    def setUpTestData(cls):
        cls.user_form_data = {
            'username': 'testuser', 
            'first_name': 'test_fn',
            'last_name': 'test_ln', 
            'email': 'test@email.com',
            'verify_email': 'test@email.com', 
            'password1': 'secretcodecode8#A',
            'password2': 'secretcodecode8#A'
        }
        cls.test_accountform = UserAccountCreationForm(cls.user_form_data).save()

    def test_new_user_created(self):
        self.assertIsInstance(self.test_accountform, User)



class ValidateProfileForm(TestCase):
    '''Verify that a form field raises a validation 
    error when the data passed to the form is invalid.'''
    
    @classmethod
    def setUpTestData(cls):

        cls.image = open(join(dirname(__file__), 'images/test_image.jpg'), 'rb')

        cls.current_profile = {
            'birth': '1/1/39',
            'bio': 'About me.'
        }
        cls.current_files = {
            'avatar': SimpleUploadedFile(
                cls.image.name,
                cls.image.read(),
                content_type="image/jpeg"
            )
        }
        cls.test_profile_form = ProfileForm(data=cls.current_profile, files=cls.current_files)
        cls.profile_form_errors = cls.test_profile_form.errors

    def test_bio_field_invalid_length(self):
        with self.assertRaises(ValidationError) as error:
            validate_bio(self.current_profile['bio'])
        self.assertEqual(error.exception.message, "Add more detail to your bio.")

    def test_birth_field_invalid_date(self):
        with self.assertRaises(ValidationError) as error:
            validate_date(self.current_profile['birth'])
        self.assertIn('Invalid date format', error.exception.message)
    

class ValidateNewPasswordLength(TestCase):
    '''Verify that all password validators are raised when
    a new password does not meet any requirements'''

    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(
            username='test_user', 
            password='password'
        )
        cls.passwords = {
            'new_password1': 'secret',
            'new_password2': 'secret',
            'old_password': 'password'
        }

        cls.password_form = PasswordChangeForm(cls.test_user, cls.passwords)

    def test_new_password_change_length_fail(self):
        '''https://github.com/django/django/blob
        /master/django/contrib/auth/forms.py#L312'''

        '''Django is validating the new password against 
        all password validators in settings.AUTH_PASSWORD_VALIDATORS'''
        password_errors = self.password_form.errors.as_data()['new_password2']
        self.assertTrue(
            any(error.code == "password_too_short") 
            for error in password_errors
        )


class ValidatePasswordCharacters(TestCase):
    '''Verify that a submitted password that meets character 
    requirements is set as the user's new password.'''

    def setUp(self):
        self.test_user = User.objects.create_user(
            username='testuser',
            password='d8&3h2jv739841#'
        )
        self.new_password = {
            'old_password':  'd8&3h2jv739841#',
            'new_password1': 'k*$ug3E(dfbf^jyo',
            'new_password2': 'k*$ug3E(dfbf^jyo'
        }

    def test_character_requirements_pass(self):
        test_password_form = PasswordChangeForm(
            self.test_user, self.new_password
        )
        form_errors = test_password_form.errors.as_data()
        self.assertFalse(form_errors)

    def test_missing_uppercase(self):
        self.new_password.update(
            new_password1='djdfdfdfdfdfd8#',
            new_password2='djdfdfdfdfdfd8#'
        )

        test_password_form = PasswordChangeForm(
            self.test_user, self.new_password
        )
        form_errors = test_password_form.errors.as_data()['new_password2']
        uppercase_error = any("at least one uppercase letter" 
                                in error.message for error in form_errors)
        self.assertTrue(uppercase_error)

    def test_missing_lowercase(self):
        self.new_password.update(
            new_password1='DU8PISFIJ*DDJ@#',
            new_password2='DU8PISFIJ*DDJ@#'
        )

        test_password_form = PasswordChangeForm(
            self.test_user, self.new_password
        )
        form_errors = test_password_form.errors.as_data()['new_password2']
        lowercase_error = any(
            ("at least one lowercase letter"
                in error.message for error in form_errors)
        )
        self.assertTrue(lowercase_error)

    def test_missing_digit(self):
        self.new_password.update(
            new_password1='DUPISFIJ*DDJ@#',
            new_password2='DUPISFIJ*DDJ@#'
        )

        test_password_form = PasswordChangeForm(
            self.test_user, self.new_password
        )
        form_errors = test_password_form.errors.as_data()['new_password2']
        digit_error = any(
            "at least one digit" in error.message for error in form_errors
        )
        self.assertTrue(digit_error)
