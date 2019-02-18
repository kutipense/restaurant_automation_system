from django.urls import path

from . import views

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('uyeol/', views.Uyeol.as_view(), name='uyeol'),
    path('rezervasyon/', views.RezervasyonView.as_view(), name='rezervasyon'),
    path('siparis/', views.SiparisView.as_view(), name='siparis'),
    path('yorum/', views.YorumYap.as_view(), name='yorum'),
    path('giris/', views.Login.as_view(), name='login'),
    path('cikis/', views.Logout.as_view(), name='cikis'),
]