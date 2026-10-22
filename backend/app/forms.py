from django import forms
from .models import User


class RegisterForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'role',
            'password'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Normal users cannot register as Admin
        self.fields['role'].choices = [
            ('agent', 'Agent'),
            ('scrap_team', 'Scrap Team'),
        ]

    def clean(self):

        cleaned_data = super().clean() or {}

        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:

            if password != confirm_password:
                raise forms.ValidationError(
                    "Passwords do not match"
                )

        return cleaned_data


class AdminSetupForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password'
        ]

    def clean(self):

        cleaned_data = super().clean() or {}

        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:

            if password != confirm_password:
                raise forms.ValidationError(
                    "Passwords do not match"
                )

        return cleaned_data
