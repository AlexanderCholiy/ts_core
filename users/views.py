from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
from django.utils.encoding import force_str
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView
from django.core.exceptions import ValidationError

from .utils import send_activation_email, send_confirm_email, role_required
from .forms import UserRegisterForm, ChangeEmailForm
from .models import User, PendingUser
from .validators import validate_pending_email


class CustomPasswordResetView(PasswordResetView):
    def get_initial(self):
        initial = super().get_initial()
        email = self.request.GET.get('email')
        if email:
            initial['email'] = email
        return initial


@login_required
@role_required()
def index(request: HttpRequest) -> HttpResponse:
    template_name = 'homepage/index.html'
    return render(request, template_name)


def register(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            pending_user = form.save()
            send_activation_email(pending_user, request)
            return render(request, 'registration/email_confirmation_sent.html')
    else:
        form = UserRegisterForm()

    context = {'form': form}
    return render(request, 'registration/register.html', context)


def activate(request: HttpRequest, uidb64: str, token: str) -> HttpResponse:
    pending_user = None
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        pending_user = PendingUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        pass

    if (
        pending_user
        and default_token_generator.check_token(pending_user, token)
    ):
        pending_user.delete()
        User.objects.create(
            username=pending_user.username,
            email=pending_user.email,
            password=pending_user.password,  # hashed
            is_active=True
        )
        return render(request, 'registration/activation_success.html')
    return render(request, 'registration/activation_invalid.html')


@login_required
@role_required()
def change_email(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = ChangeEmailForm(request.POST)
        if form.is_valid():
            new_email = form.cleaned_data['email']
            if request.user.email == new_email:
                messages.info(
                    request,
                    'Вы уже используете эту почту.'
                )
                return redirect('users:change_email')

            try:
                validate_pending_email(new_email, instance=None)
            except ValidationError as e:
                messages.error(request, e.message)
                return redirect('users:change_email')

            pending_user = PendingUser.objects.create(
                username=request.user.username,
                email=new_email,
                password=request.user.password,
            )
            send_confirm_email(pending_user, request)
            return render(request, 'registration/email_confirmation_sent.html')
    else:
        form = ChangeEmailForm(instance=request.user)

    context = {'form': form}
    return render(request, 'registration/email_change_form.html', context)


@login_required
@role_required()
def confirm_email_change(
    request: HttpRequest, uidb64: str, token: str
) -> HttpResponse:
    pending_user = None
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        pending_user = PendingUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        pass

    if (
        pending_user
        and default_token_generator.check_token(pending_user, token)
    ):
        user = User.objects.get(username=pending_user.username)
        user.email = pending_user.email
        user.save()
        pending_user.delete()
        messages.success(
            request,
            'Ваш email был успешно изменен и подтвержден.'
        )
        return redirect('users:change_email')
    messages.error(
        request,
        'Ссылка для подтверждения недействительна или устарела. '
        'Пожалуйста, запросите смену email еще раз.'
    )
    return redirect('users:change_email')
