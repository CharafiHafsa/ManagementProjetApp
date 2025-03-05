from django.urls import path
from . import views

urlpatterns = [    
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_user, name='logout'),
    path('forget_password/', views.forget_password, name='forget_password'),
    path('update_password/', views.update_password, name='update_password'),
]
