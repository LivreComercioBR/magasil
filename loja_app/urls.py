from django.urls import path
from .views import *
from django.contrib.auth import views


urlpatterns = [
    # auth/cadastrar
    path('cadastro/', cadastro, name='cadastro'),
    path('logar/', logar, name='logar'),
    path('sair/', sair, name='sair'),

    path('minha_conta/', minha_conta, name='minha_conta'),
    path('meus_pedidos/', meus_pedidos, name='meus_pedidos'),
    path('alterar_senha/', alterar_senha, name='alterar_senha'),
    # resetar senha
    path("password_change/", views.PasswordChangeView.as_view(),
         name="password_change"),
    path("password_change/done/", views.PasswordChangeDoneView.as_view(),
         name="password_change_done"),
    # quando o usuário esquece a senha
    path("password_reset/", views.PasswordResetView.as_view(), name="password_reset"),
    # instruções para redefinição de senha
    path("password_reset/done/", views.PasswordResetDoneView.as_view(),
         name="password_reset_done"),
    # token com código de segurança para refefinição da senha
    path("reset/<uidb64>/<token>/", views.PasswordResetConfirmView.as_view(),
         name="password_reset_confirm"),
    # informações que a senha foi resetada
    path("reset/done/", views.PasswordResetCompleteView.as_view(),
         name="password_reset_complete"),

    # políticas da empresa
    path('politica_privacidade/', politica_privacidade,
         name='politica_privacidade'),
    path('termos_de_uso/', termos_de_uso,
         name='termos_de_uso'),
    path('quem_somos/', quem_somos,
         name='quem_somos'),

]
