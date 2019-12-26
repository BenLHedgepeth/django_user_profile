from django import forms
from .models import Profile
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.forms.widgets import EmailInput


from .validate import validate_bio, validate_date


class UserAccountCreationForm(UserCreationForm):

    verify_email = forms.EmailField(label="Verify your email")

    class Meta:
        model = get_user_model()
        fields = (
            'username', 'first_name', 'last_name', 'email', 'verify_email'
        )

    def __init__(self, *args, **kwargs):
        '''Note: A user defined field needs a label argument
        passed to the field constructor in order for a placeholder
        to render properly in HTML'''

        super().__init__(*args, **kwargs)
        for form_field in self.fields.values():
            form_field.widget.attrs.update(placeholder=form_field.label)

    def clean_verify_email(self):
        my_email = self.cleaned_data['email']
        verify_email = self.cleaned_data['verify_email']

        if my_email != verify_email:
            msg = "Email doesn't match the previously entered email."
            raise ValidationError(msg)


class ProfileForm(forms.ModelForm):

    birth = forms.DateField(label="Date of birth", validators=[validate_date])
    bio = forms.CharField(label="Your bio...", validators=[validate_bio])

    class Meta:
        model = Profile
        fields = ('birth', 'bio', 'avatar')


class EditUserForm(forms.ModelForm):

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form_field in self.fields.values():
            form_field.widget.attrs.update(placeholder=form_field.label)

    def clean_verify_email(self):
        my_email = self.cleaned_data['email']
        verify_email = self.cleaned_data['verify_email']

        if my_email != verify_email:
            msg = "Email doesn't match the previously entered email."
            raise ValidationError(msg)
