from datetime import date

from django import forms
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import check_password

from .models import PendingUser, User
from .validators import validate_user_email
from .constants import (
    MIN_USER_PASSWORD_LEN,
    MAX_USER_USERNAME_DISPLAY_LEN,
    MIN_USER_AGE,
    MAX_USER_AGE,
)


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
        """
        Данная проверка нужна, т.к. мы используем temporary username при смене
        email.
        """
        username: str = self.cleaned_data.get('username', '').strip()
        if len(username) > MAX_USER_USERNAME_DISPLAY_LEN:
            raise ValidationError(
                f'Имя пользователя должно быть не длиннее '
                f'{MAX_USER_USERNAME_DISPLAY_LEN} символов'
            )
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
        new_email = cleaned_data.get('email')

        if not check_password(password, user.password):
            raise ValidationError('Неверный пароль')

        if new_email and new_email == user.email:
            raise ValidationError('Вы уже используете эту почту.')

        if new_email:
            validate_user_email(new_email, user)

        return cleaned_data


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('avatar', 'date_of_birth', 'first_name', 'last_name',)
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={
                'class': 'avatar-input',
                'accept': 'image/*',
            }),
            'date_of_birth': forms.DateInput(
                attrs={
                    'type': 'date',
                    'max': str(date.today().replace(
                        year=date.today().year - MIN_USER_AGE)),
                    'min': str(date.today().replace(
                        year=date.today().year - MAX_USER_AGE))
                }
            )
        }

    def clean_date_of_birth(self):
        value: date = self.cleaned_data.get('date_of_birth')
        if not value:
            return value

        today = date.today()
        age = (
            today.year - value.year
            - ((today.month, today.day) < (value.month, value.day))
        )

        if age < MIN_USER_AGE:
            raise ValidationError(
                f'Пользователь должен быть старше {MIN_USER_AGE}'
            )
        if age > MAX_USER_AGE:
            raise ValidationError(
                f'Пользователь должен быть младше {MAX_USER_AGE}'
            )

        return value

    def save(self, commit=True):
        user = super().save(commit=False)

        if self.cleaned_data.get('avatar-clear'):
            if user.avatar:
                user.avatar.delete(save=False)
            user.avatar = None

        if commit:
            user.save()

        return user
