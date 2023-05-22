from django import forms
# from django.core.exceptions import ValidationError

from .models import *

class CodeForm(forms.Form):
    # title = forms.CharField(max_length=255, label="Название")
    content = forms.CharField(widget=forms.Textarea(attrs={
        'cols': 140, 'rows': 17, 'class':'form-control', 'id':'ta', 'required':False
    }), label='')
    plang = forms.ChoiceField(choices=LANG_CHOICES, label='') #widget=forms.Select(attrs={'class':'choiceField'}), label='')

class MyCodeForm(forms.Form):
    title = forms.CharField(max_length=255, label='Название')
    content = forms.CharField(widget=forms.Textarea(attrs={
        'cols': 120, 'rows': 17, 'class':'form-control', 'id':'ta', 'required':False
    }), label='Код')
    plang = forms.ChoiceField(choices=LANG_CHOICES, label='')

'''
class CreateTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'points', 'until', 'active', 'test']
'''

class CreateTaskForm(forms.Form):
    name = forms.CharField(max_length=255, label='Название задачи')
    description = forms.CharField(widget=forms.Textarea(attrs={
        'cols':50, 'rows':17, 'class':'form-control','required':False
    }), label='Описание задачи')
    points = forms.IntegerField(initial=10, label="Максимум очков")
    until = forms.DateField(widget=forms.SelectDateWidget(), label="Активна до")
    active = forms.BooleanField(initial=True, label="Активна?")

class CreateOlympiadForm(forms.Form):
    name = forms.CharField(max_length=255, label="Название олимпиады",
        widget=forms.TextInput(attrs={'width':'50%', 'class':'form-control'}))
    description = forms.CharField(widget=forms.Textarea(attrs={
        'cols':50, 'rows':7, 'class':'form-control', 'required':False
    }), label="Описание олимпиады")

class TestDataForm(forms.Form):
    input = forms.CharField()
    output = forms.CharField()