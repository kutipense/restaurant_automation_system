from django import forms
from .models import Musteri,Yorum


class UyeForm(forms.ModelForm):
    class Meta:
        model = Musteri
        fields = ('name', 'username', 'password','addr','telno')
        widgets = {
            'password': forms.PasswordInput(),
            'addr' : forms.Textarea(attrs={'cols': 30, 'rows': 4}),
        }


class DateForm(forms.Form):
    date = forms.DateTimeField(label="Tarih",input_formats=("%Y-%m-%dT%H:%M",),
    widget=forms.DateTimeInput(attrs={"type":"datetime-local"}))


class YorumForm(forms.ModelForm):
    class Meta:
        model = Yorum
        fields = ('comment', 'star')
        widgets = {
            'star': forms.NumberInput(attrs={'min': 1, 'max':5}),
            'comment' : forms.Textarea(attrs={'cols': 40, 'rows': 4}),
        }
