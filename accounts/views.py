from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import (
    AuthenticationForm, UserCreationForm, PasswordChangeForm
)
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from .forms import UserAccountCreationForm, ProfileForm, EditUserForm
from .models import Profile


def sign_in(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            if form.user_cache is not None:
                user = form.user_cache
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(
                        reverse('home')  # TODO: go to profile
                    )
                else:
                    messages.error(
                        request,
                        "That user account has been disabled."
                    )
            else:
                messages.error(
                    request,
                    "Username or password is incorrect."
                )
    return render(request, 'accounts/sign_in.html', {'form': form})


def sign_up(request):
    form = UserAccountCreationForm()
    if request.method == 'POST':
        form = UserAccountCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
            )
            login(request, user)
            messages.success(
                request,
                "You're now a user! You've been signed in, too."
            )
            return HttpResponseRedirect(reverse('home'))  # TODO: go to profile
    return render(request, 'accounts/sign_up.html', {'form': form})


def sign_out(request):
    logout(request)
    messages.success(request, "You've been signed out. Come back soon!")
    return HttpResponseRedirect(reverse('home'))


@login_required(login_url="/accounts/sign_in/")
def profile(request, username):
    user = request.user
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        messages.info(request, "Provide more detail about yourself...")
        return HttpResponseRedirect(
            reverse("accounts:new_profile", kwargs={'username': username})
        )
    return render(request, 'accounts/profile.html', {'profile': profile})


@login_required(login_url="/accounts/sign_in/")
def new_profile(request, username):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            form.cleaned_data.update(user=user)
            Profile.objects.create(**form.cleaned_data)
            return HttpResponseRedirect(
                reverse("accounts:profile", kwargs={'username': username})
            )
    else:
        form = ProfileForm()
    return render(
        request, 'accounts/create_profile.html',
        {'form': form, 'user': request.user}
    )


@login_required(login_url="/accounts/sign_in")
def edit_profile(request, username):
    user = request.user
    user_data = model_to_dict(
        user,
        fields=['username', 'first_name', 'last_name', 'email', 'verify_email']
    )
    current_profile = Profile.objects.get(user=user)
    profile_data = model_to_dict(
        current_profile, fields=['birth', 'bio', 'avatar']
    )
    if request.method == "POST":
        user_form = EditUserForm(
            request.POST, initial=user_data, instance=user
        )
        profile_form = ProfileForm(
            request.POST, request.FILES,
            initial=profile_data, instance=current_profile
        )
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            if any(data.has_changed() for data in [profile_form, user_form]):
                messages.success(request, "Your profile is updated!")
            else:
                messages.success(request, "No profile changes applied...")
            return HttpResponseRedirect(
                reverse('accounts:profile', kwargs={'username': user})
            )
    else:
        profile_form = ProfileForm(initial=profile_data)
        user_form = EditUserForm(initial=user_data)
    return render(
        request, 'accounts/edit_profile.html',
        {'profile_form': profile_form,
            'user_form': user_form,
            'username': user}
    )


@login_required(login_url="/accounts/sign_in")
def change_password(request, username):
    user = request.user
    if request.method == 'POST':
        form = PasswordChangeForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password is updated!")
            return HttpResponse(reverse('accounts:home', username=user))
    form = PasswordChangeForm(user)
    return render(request, 'accounts/change_password.html', {'form': form})
