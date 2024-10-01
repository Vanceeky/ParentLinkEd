from django.urls import path
from . import views

urlpatterns = [

    path('accounts/login/', views.accounts_login, name="accounts-login"),
    path('login/', views.login_account, name="login-account"),
    path('register/', views.register_page, name="register-page"),
    path('logout/', views.logout_account, name="logout-account"),
]
