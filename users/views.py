from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from core.logger import email_logger

from .forms import ChangeEmailForm, UserForm, UserRegisterForm
from .models import PendingUser, User
from .utils import role_required, send_activation_email, send_confirm_email


class CustomPasswordResetView(PasswordResetView):
    def get_initial(self):
        initial = super().get_initial()
        email = self.request.GET.get('email')
        if email:
            initial['email'] = email
        return initial


def register(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            pending_user = form.save()
            if send_activation_email(pending_user, request):
                return render(
                    request, 'users/email_confirmation_sent.html')
    else:
        form = UserRegisterForm()

    context = {'form': form}
    return render(request, 'registration/register.html', context)


def activate(request: HttpRequest, uidb64: str, token: str) -> HttpResponse:
    pending_user = None
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        pending_user = PendingUser.objects.get(pk=uid)
    except (
        TypeError,
        ValueError,
        OverflowError,
        PendingUser.DoesNotExist,
    ) as e:
        email_logger.exception(e)

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
        form = ChangeEmailForm(request.POST, instance=request.user)
        if form.is_valid():
            new_email = form.cleaned_data['email']
            user: User = request.user
            pending_user = PendingUser.objects.create(
                username=user.temporary_username,
                email=new_email,
                password=user.password,
            )
            if send_confirm_email(pending_user, request):
                return render(request, 'users/email_confirmation_sent.html')
        else:
            for name, errors in form.errors.items():
                if name == '__all__':
                    for error in set(errors):
                        messages.error(request, error)
    else:
        form = ChangeEmailForm(instance=request.user)

    context = {'form': form}
    return render(request, 'users/email_change_form.html', context)


@login_required
@role_required()
def confirm_email_change(
    request: HttpRequest, uidb64: str, token: str
) -> HttpResponse:
    pending_user = None
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        pending_user = PendingUser.objects.get(pk=uid)
    except (
        TypeError,
        ValueError,
        OverflowError,
        PendingUser.DoesNotExist,
    ) as e:
        email_logger.exception(e)

    if (
        pending_user
        and default_token_generator.check_token(pending_user, token)
    ):
        user = User.objects.get(username=pending_user.original_username)
        pending_user.delete()
        user.email = pending_user.email
        user.save()
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


@login_required
@role_required()
def profile(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлён')
            return redirect('users:profile')
        else:
            for name, errors in form.errors.items():
                if name == '__all__':
                    for error in set(errors):
                        messages.error(request, error)
    else:
        form = UserForm(instance=request.user)

    context = {'form': form}
    return render(request, 'users/profile_form.html', context)
