from django.shortcuts import render, get_object_or_404, redirect, Http404
from django.http import HttpResponse
from django.views.generic import TemplateView, View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.utils import timezone
# Create your views here.
from django.db.models import Q,QuerySet
from .models import Masa,Yemek,Rezervasyon,MasaSecimi,Musteri,SiparisHavuzu,YemekSiparisi,Yorum
from .forms import UyeForm, DateForm, YorumForm

from datetime import timedelta

class Index(TemplateView):
    template_name = "onlinerestaurant/base.html"

    def post(self,request):
        rez = request.POST.get("rez")
        puan = request.POST.get("puan")
        siparis = request.POST.getlist("siparis")
        yemek = request.POST.getlist("yemek")
        if rez:
            rezervasyon = Rezervasyon.objects.filter(id=int(rez))
            rezervasyon.delete()
        if siparis:
            if(request.POST.get("sil")):
                for i in siparis:
                    s = SiparisHavuzu.objects.get(id=int(i))
                    s.delete()
            elif request.POST.get("onayla"):
                for i in siparis:
                    s = SiparisHavuzu.objects.get(id=int(i))
                    s.onay = True
                    s.save()
        if yemek:
            if(request.POST.get("sil")):
                for i in yemek:
                    y = YemekSiparisi.objects.get(Q(id=int(i)))
                    s = y.siparis
                    if len(YemekSiparisi.objects.filter(siparis = s))==1:
                        s.delete()
                    if y:
                        y.delete()
        if puan:
            m = Musteri.objects.get(username=request.user.username)
            m.puan = int(puan)
            m.save()
        return redirect("/")

    def get(self,request):
        yemek = SiparisHavuzu.objects.filter(Q(musteri=request.user) & Q(onay=False))
        yemek_list = []
        for i in yemek:
            yemek_list.append([i,])
            y = YemekSiparisi.objects.filter(siparis=i)
            yemek_list[-1].append(y)

        m = Musteri.objects.get(username=request.user.username)
        rez = Rezervasyon.objects.filter(musteri=m)
        masalar = []
        for i in rez:
            masalar.append(MasaSecimi.objects.get(rezervasyon = i))

        mlist= Musteri.objects.all()
        puan = sum([i.puan for i in mlist])/len(mlist)
        return render(request,self.template_name,{"rez":list(zip(rez,masalar)),"yemekler":yemek_list,"ort_puan":puan})

    def dispatch(self,request,*args,**kwargs):
        if not request.user.is_authenticated:
            return redirect("/giris")
        return super(TemplateView, self).dispatch(request, *args, **kwargs)


class YorumYap(TemplateView):
    template_name = "onlinerestaurant/yorum.html"

    def post(self,request):
        form = YorumForm(request.POST)
        siparis = request.POST.get("yolla")
        if form.is_valid() and siparis:
            s = SiparisHavuzu.objects.get(id=int(siparis))
            y = Yorum()
            y.orderdate = s.orderdate
            y.comment = form.cleaned_data["comment"]
            y.star = form.cleaned_data["star"]
            y.save()
            s.delete()
        return redirect("/yorum/")

    def get(self,request):
        m = Musteri.objects.get(username=request.user.username)
        siparisler = SiparisHavuzu.objects.filter(musteri = m)
        form = YorumForm()
        yorumlar = Yorum.objects.all()
        return render(request,self.template_name,{"siparisler":siparisler,"form":form, "yorumlar":yorumlar})

    def dispatch(self,request,*args,**kwargs):
        if not request.user.is_authenticated:
            return redirect("/giris")
        return super(TemplateView, self).dispatch(request, *args, **kwargs)


class RezervasyonView(TemplateView):
    template_name = "onlinerestaurant/rezervasyon.html"

    def post(self,request):
        musait_masalar = []
        form = DateForm(request.POST)
        masa = request.POST.get("masa")
        if form.is_valid():
            date = form.cleaned_data["date"]
            if date>timezone.now():
                rez_list = Rezervasyon.objects.exclude(
                    Q(date__lte=date-timedelta(hours=2)) | Q(date__gte=date+timedelta(hours=2))
                )
                namusait_masalar = []
                for rez in rez_list:
                    namusait_masalar.append(MasaSecimi.objects.get(rezervasyon = rez).masa.no)
                musait_masalar = Masa.objects.exclude(no__in=namusait_masalar)

                if masa and (int(masa) in [m.no for m in musait_masalar]):
                    masasecimi = MasaSecimi()
                    rezervasyon = Rezervasyon()
                    rezervasyon.musteri = Musteri.objects.get(username = request.user.username)
                    rezervasyon.date = date
                    rezervasyon.save()
                    masasecimi.masa = Masa.objects.get(no=masa)
                    masasecimi.rezervasyon = rezervasyon
                    masasecimi.save()

                    messages.success(request, 'Rezervasyon Yapildi.')
                    return redirect("/")
        return render(request, self.template_name, {'form':form, 'masalar': musait_masalar})

    def get(self,request):
        form = DateForm()
        return render(request, self.template_name, {'form': form})
    
    def dispatch(self,request,*args,**kwargs):
        if not request.user.is_authenticated:
            return redirect("/")
        return super(TemplateView, self).dispatch(request, *args, **kwargs)


class SiparisView(TemplateView):
    template_name = "onlinerestaurant/siparis.html"
    musteri = None

    @classmethod
    def get_yemek(cls):
        y = Yemek.objects.all()
        yemekler = [
            ["Ana Yemek",[]],
            ["Ara Sicak",[]],
            ["Tatli",[]],
            ["Icecek",[]]
        ]
        for i in y:
            yemekler[i.edibletype][1].append(i)
        return yemekler

    def post(self,request):
        yemekler = request.POST.getlist("yemek")
        if(yemekler):
            sh = SiparisHavuzu()
            sh.musteri = self.musteri
            sh.orderdate = timezone.now()
            sh.ispayed = False
            if request.POST.get("card"):
                sh.ispayed = True
            sh.save()
            for i in yemekler:
                ys = YemekSiparisi()
                ys.siparis = sh
                ys.yemek = Yemek.objects.get(id=int(i))
                ys.save()
            messages.success(request, 'Siparis Verildi.')
            return redirect("/")
        return render(request, self.template_name, {'yemekler': self.get_yemek()})

    def get(self,request):
        return render(request, self.template_name, {'yemekler': self.get_yemek()})
    
    def dispatch(self,request,*args,**kwargs):
        if not request.user.is_authenticated:
            return redirect("/")
        self.musteri = Musteri.objects.get(username=request.user.username)
        return super(TemplateView, self).dispatch(request, *args, **kwargs)


class Uyeol(TemplateView):
    template_name = "onlinerestaurant/uyeol.html"

    def post(self,request):
        form = UyeForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            userid = form.cleaned_data["username"]
            userpw = form.cleaned_data["password"]
            user.set_password(userpw)
            user.save()

            user = authenticate(username = userid, password = userpw)

            if user is not None:
                if user.is_active:
                    login(request,user)
                    return redirect("/")
        raise Http404("Uye olamadiniz!")

    def get(self,request):
        form = UyeForm()
        return render(request, self.template_name, {'form': form})
    
    def dispatch(self,request,*args,**kwargs):
        if request.user.is_authenticated:
            return redirect("/")
        return super(TemplateView, self).dispatch(request, *args, **kwargs)


class Login(LoginView):
    template_name = "onlinerestaurant/giris.html"
    
    def dispatch(self,request,*args,**kwargs):
        if request.user.is_authenticated:
            return redirect("/")
        return super(LoginView, self).dispatch(request, *args, **kwargs)


class Logout(LogoutView):
    template_name = "onlinerestaurant/cikis.html"

def handler404(request, exception, template_name='404.html'):
    return redirect("/")