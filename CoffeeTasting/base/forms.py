from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile, Bean, Tasting


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Gebruikersnaam'
        self.fields['password1'].label = 'Wachtwoord'
        self.fields['password2'].label = 'Wachtwoord bevestigen'


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        labels = {
            'first_name': 'Voornaam',
            'last_name': 'Achternaam',
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['city', 'date_of_birth', 'favorite_method']
        labels = {
            'city': 'Woonplaats',
            'date_of_birth': 'Geboortedatum',
            'favorite_method': 'Favoriete zetmethode',
        }
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }


class BeanForm(forms.ModelForm):
    class Meta:
        model = Bean
        fields = ['name', 'country_of_origin', 'roaster', 'harvest_season', 'in_season']
        labels = {
            'name': 'Naam',
            'country_of_origin': 'Land van herkomst',
            'roaster': 'Brander / merk',
            'harvest_season': 'Oogstseizoen',
            'in_season': 'Momenteel leverbaar',
        }


class TastingForm(forms.ModelForm):
    class Meta:
        model = Tasting
        fields = ['bean', 'date', 'description']
        labels = {
            'bean': 'Koffieboon',
            'date': 'Datum',
            'description': 'Beschrijving',
        }
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['bean'].queryset = Bean.objects.filter(approved=True).order_by('name')