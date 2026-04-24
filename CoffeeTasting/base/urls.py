from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/wachtwoord/', views.change_password, name='change_password'),
    path('profile/<str:username>/', views.public_profile, name='public_profile'),
    path('bonen/', views.bean_list, name='bean_list'),
    path('bonen/toevoegen/', views.bean_add, name='bean_add'),
    path('beheer/bonen/', views.beheer_bonen, name='beheer_bonen'),
    path('beheer/bonen/toevoegen/', views.beheer_boon_toevoegen, name='beheer_boon_toevoegen'),
    path('beheer/bonen/<int:pk>/goedkeuren/', views.beheer_boon_goedkeuren, name='beheer_boon_goedkeuren'),
    path('beheer/bonen/<int:pk>/afwijzen/', views.beheer_boon_afwijzen, name='beheer_boon_afwijzen'),
]
