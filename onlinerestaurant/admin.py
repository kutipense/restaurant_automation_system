from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Yemek)

admin.site.register(Masa)

admin.site.register(YemekSiparisi)

admin.site.register(SiparisHavuzu)

admin.site.register(Musteri)

admin.site.register(Rezervasyon)

admin.site.register(MasaSecimi)

admin.site.register(Yorum)




