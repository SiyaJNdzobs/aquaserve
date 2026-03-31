from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('report/', views.report_issue, name='report'),
    path('track/', views.track_request, name='track'),
    path('account/', views.account, name='account'),
    path('payment/', views.payment, name='payment'),
    path('about/', views.about, name='about'),
]