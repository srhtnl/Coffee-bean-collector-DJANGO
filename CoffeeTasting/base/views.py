from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib import messages

from .forms import RegisterForm, ProfileUpdateForm, UserUpdateForm, BeanForm, TastingForm, Tasting


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


def public_profile(request, username):
    from django.shortcuts import get_object_or_404
    from django.contrib.auth.models import User
    from .models import Profile
    profile_user = get_object_or_404(User, username=username)
    Profile.objects.get_or_create(user=profile_user)
    return render(request, 'base/public_profile.html', {'profile_user': profile_user})


@login_required(login_url='/login/')
def change_password(request):
    form = SetPasswordForm(request.user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Wachtwoord succesvol gewijzigd!')
        return redirect('profile')
    return render(request, 'base/change_password.html', {'form': form})


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


def bean_list(request):
    from .models import Bean
    beans = Bean.objects.filter(approved=True).order_by('name')
    pending_count = Bean.objects.filter(approved=False).count() if request.user.is_staff else 0
    return render(request, 'base/bean_list.html', {'beans': beans, 'pending_count': pending_count})


def bean_detail(request, pk):
    from django.shortcuts import get_object_or_404
    from .models import Bean
    bean = get_object_or_404(Bean, pk=pk, approved=True)
    return render(request, 'base/bean_detail.html', {'bean': bean})


@login_required(login_url='/login/')
def bean_add(request):
    form = BeanForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        bean = form.save(commit=False)
        if request.user.is_staff:
            bean.approved = True
            bean.approved_by = request.user
            bean.save()
            messages.success(request, 'Koffieboon toegevoegd en direct goedgekeurd.')
        else:
            bean.approved = False
            bean.save()
            messages.success(request, 'Koffieboon ingediend! Een admin keurt deze binnenkort goed.')
        return redirect('bean_list')
    return render(request, 'base/bean_add.html', {'form': form})


def staff_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/login/')
        if not request.user.is_staff:
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


@staff_required
def beheer_bonen(request):
    from .models import Bean
    pending = Bean.objects.filter(approved=False).order_by('name')
    return render(request, 'base/beheer_bonen.html', {'pending': pending})


@staff_required
def beheer_boon_goedkeuren(request, pk):
    from .models import Bean
    if request.method == 'POST':
        bean = Bean.objects.get(pk=pk)
        bean.approved = True
        bean.approved_by = request.user
        bean.save()
    return redirect('beheer_bonen')


@staff_required
def beheer_boon_afwijzen(request, pk):
    from .models import Bean
    if request.method == 'POST':
        Bean.objects.filter(pk=pk).delete()
    return redirect('beheer_bonen')


@staff_required
def beheer_boon_toevoegen(request):
    form = BeanForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        bean = form.save(commit=False)
        bean.approved = True
        bean.approved_by = request.user
        bean.save()
        messages.success(request, 'Koffieboon toegevoegd en direct goedgekeurd.')
        return redirect('beheer_bonen')
    return render(request, 'base/beheer_boon_toevoegen.html', {'form': form})

@login_required(login_url='/login/')
def tasting_add(request):
    form = TastingForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        tasting = form.save(commit=False)
        tasting.user = request.user 

        already_exists = Tasting.objects.filter(
            user=request.user,
            bean=tasting.bean,
            date=tasting.date).exists()
        
        if already_exists:
            messages.error(request, 'Je hebt deze koffie vandaag al geproefd!')
        else:
            tasting.save()
            messages.success(request, 'Proefsessie succesvol toegevoegd!')
            return redirect('profile') 
    return render(request, 'base/tasting_add.html', {'form': form})

@login_required(login_url='/login/')
def tasting_list(request):
    from .models import Tasting
    tastings = Tasting.objects.filter(user=request.user).order_by('-date')
    return render(request, 'base/tasting_list.html', {'tastings': tastings})

@login_required(login_url='/login/')
def tasting_edit(request, pk):
    from .models import Tasting

    tasting = Tasting.objects.get(pk=pk, user=request.user)

    form = TastingForm(request.POST or None, instance=tasting)

    if request.method == 'POST' and form.is_valid():
        already_tasted = Tasting.objects.filter(
            user=request.user, 
            bean=form.cleaned_data['bean'], 
            date=form.cleaned_data['date']
        ).exclude(pk=tasting.pk).exists()

        if already_tasted:
            messages.error(request, "Je hebt op deze datum al een andere proefsessie voor deze boon.")
        else:
            form.save()
            messages.success(request, 'Proefsessie succesvol bijgewerkt!')
            return redirect('tasting_list')
    
    return render(request, 'base/tasting_edit.html', {'form': form, 'tasting': tasting})

@login_required(login_url='/login/')
def tasting_delete(request, pk):
    from .models import Tasting
    tasting = Tasting.objects.get(pk=pk, user=request.user)
    
    if request.method == 'POST':
        tasting.delete()
        messages.success(request, 'Proefsessie verwijderd.')
        return redirect('tasting_list')
        
    return render(request, 'base/tasting_confirm_delete.html', {'tasting': tasting})
