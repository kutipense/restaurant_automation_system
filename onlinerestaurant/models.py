from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Musteri(User):
    name = models.CharField("Isim",max_length=50, blank=False)
    addr = models.CharField("Adres",max_length=250, blank=False)
    telno = models.IntegerField("Telefon Numarasi",blank=False,unique=True)
    puan = models.IntegerField("Sistem Puani",blank=False,default=5)


class Yemek(models.Model):
    types = (
        (0, "Ana Yemek"),
        (1, "Ara Sicak"),
        (2, "Tatli"),
        (3, "Icecek")
    )

    edibletype = models.IntegerField("Tur",choices=types)
    name = models.CharField("Yemek Ismi",max_length=50)
    price = models.DecimalField("Ucret",decimal_places=1,max_digits=6)
    preptime = models.IntegerField("Hazirlanma Suresi (dk)")

    def __str__(self):
        return "{} | Ucret: {}TL Hazirlanma Suresi: {}dk".format(self.name,self.price,self.preptime)


class SiparisHavuzu(models.Model):
    musteri = models.ForeignKey(Musteri, on_delete=models.CASCADE)
    orderdate = models.DateTimeField("Siparis Tarihi", auto_now_add=True)
    ispayed = models.BooleanField("Odendi",default=False)
    onay = models.BooleanField("Onay",default=False)

    def __str__(self):
        return " || ".join(list(map(lambda x: str(x).split('|')[0],YemekSiparisi.objects.filter(siparis=self))))


class YemekSiparisi(models.Model):
    siparis = models.ForeignKey(SiparisHavuzu, on_delete=models.CASCADE)
    yemek = models.ForeignKey(Yemek, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.yemek)


class Rezervasyon(models.Model):
    musteri = models.ForeignKey(Musteri,on_delete=models.CASCADE)
    date = models.DateTimeField("Rezervasyon Tarihi")


class Masa(models.Model):
    no = models.IntegerField("Masa No",primary_key=True)


class MasaSecimi(models.Model):
    masa = models.ForeignKey(Masa,on_delete=models.CASCADE)
    rezervasyon = models.ForeignKey(Rezervasyon,on_delete=models.CASCADE)


class Yorum(models.Model):
    orderdate = models.DateTimeField("Siparis Tarihi")
    comment = models.CharField("Yorum", max_length=500,blank = False)
    star = models.IntegerField("Yildiz")

    def __str__(self):
        return self.comment