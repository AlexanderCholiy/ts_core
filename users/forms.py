from django import forms
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate

from .models import PendingUser, User
from .constants import MIN_USER_PASSWORD_LEN


class UserRegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'minlength': MIN_USER_PASSWORD_LEN,
            'autocomplete': 'new-password',
        }),
        help_text=(
            f'Пароль должен содержать минимум {MIN_USER_PASSWORD_LEN} '
            'символов, не может быть полностью числовым, '
            'не должен быть похож на имя пользователя и '
            'не должен быть слишком простым.'
        ),
        strip=True,
    )
    password2 = forms.CharField(
        label='Повторите пароль',
        widget=forms.PasswordInput(attrs={
            'minlength': MIN_USER_PASSWORD_LEN,
            'autocomplete': 'new-password',
        }),
        strip=True,
    )

    class Meta:
        model = PendingUser
        fields = ('username', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'autocomplete': 'username'}),
            'email': forms.EmailInput(attrs={'autocomplete': 'email'}),
        }

    def clean_username(self) -> str:
        username: str = self.cleaned_data.get('username', '').strip()
        return username

    def clean_email(self) -> str:
        email: str = self.cleaned_data.get('email', '').strip()
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            try:
                validate_password(password1)
            except ValidationError as error:
                self.add_error('password1', error)
        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', ('Пароли не совпадают.'))

        return cleaned_data

    def save(self, commit: bool = True) -> PendingUser:
        instance = super().save(commit=False)
        raw_password = self.cleaned_data['password1']
        instance.password = make_password(raw_password)
        if commit:
            instance.save()
        return instance


class AuthForm(AuthenticationForm):
    username = forms.CharField(
        label='Имя пользователя или email',
        strip=True,
        required=True
    )

    error_messages = {
        'invalid_login': (
            "Пожалуйста, введите правильные имя пользователя/email и пароль. "
            "Оба поля могут быть чувствительны к регистру."
        ),
        'inactive': "Этот аккаунт неактивен.",
    }

    def clean_username(self):
        username_or_email = self.cleaned_data['username']

        user = None
        if '@' in username_or_email:
            try:
                user = User.objects.get(email=username_or_email)
            except User.DoesNotExist:
                pass
        else:
            try:
                user = User.objects.get(username=username_or_email)
            except User.DoesNotExist:
                pass

        if not user:
            return username_or_email

        return user.email

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

        if user is None:
            raise forms.ValidationError(
                self.error_messages['invalid_login'],
                code='invalid_login',
            )


class ChangeEmailForm(forms.ModelForm):
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'minlength': MIN_USER_PASSWORD_LEN,
            'autocomplete': 'new-password',
        }),
        strip=True,
    )

    class Meta:
        model = User
        fields = ('email',)
        widgets = {
            'email': forms.EmailInput(attrs={'autocomplete': 'email'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        user: User = self.instance

        if not authenticate(username=user.username, password=password):
            raise ValidationError('Неверный пароль')

        return cleaned_data
