from django.db import models
from django.contrib.auth.models import User


class Bean(models.Model):
    name = models.CharField(max_length=255)
    country_of_origin = models.CharField(max_length=255)
    roaster = models.CharField(max_length=255, blank=True, default='')
    harvest_season = models.CharField(max_length=255)
    in_season = models.BooleanField(default=True)
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_beans'
    )

    def __str__(self):
        return self.name


class Profile(models.Model):
    BREWING_METHODS = [
        ('espresso', 'Espresso'),
        ('filter', 'Filter'),
        ('french_press', 'French Press'),
        ('pour_over', 'Pour Over'),
        ('aeropress', 'AeroPress'),
        ('moka_pot', 'Moka Pot'),
        ('cold_brew', 'Cold Brew'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    favorite_method = models.CharField(max_length=50, choices=BREWING_METHODS, blank=True, default='')
    city = models.CharField(max_length=255, blank=True, default='')
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.user}"
