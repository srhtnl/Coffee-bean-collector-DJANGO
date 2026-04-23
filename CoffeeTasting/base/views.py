from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import RegisterForm, ProfileUpdateForm, UserUpdateForm


def home(request):
    return render(request, "base/home.html")


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        from .models import Profile
        Profile.objects.get_or_create(user=user)
        login(request, user)
        messages.success(request, 'Registratie geslaagd! Welkom, {}!'.format(user.username))
        return redirect('profile')
    return render(request, 'base/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')
        messages.error(request, 'Ongeldige gebruikersnaam of wachtwoord.')
    return render(request, 'base/login.html')


def user_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
    return redirect('home')


@login_required(login_url='/login/')
def profile(request):
    return render(request, 'base/profile.html')


@login_required(login_url='/login/')
def profile_edit(request):
    from .models import Profile
    user_profile, _ = Profile.objects.get_or_create(user=request.user)

    user_form = UserUpdateForm(request.POST or None, instance=request.user)
    profile_form = ProfileUpdateForm(request.POST or None, instance=user_profile)
    if request.method == 'POST' and user_form.is_valid() and profile_form.is_valid():
        user_form.save()
        profile_form.save()
        messages.success(request, 'Profiel bijgewerkt!')
        return redirect('profile')
    return render(request, 'base/profile_edit.html', {'user_form': user_form, 'profile_form': profile_form})
