from django import forms
from django.forms.widgets import NumberInput
from datetime import datetime
# from django.core.exceptions import ValidationError

from .models import *
from .langs import prog_langs

class CodeForm(forms.Form):
    # title = forms.CharField(max_length=255, label="Название")
    content = forms.CharField(widget=forms.Textarea(attrs={
        'cols': 140, 'rows': 17, 'class':'form-control', 'id':'ta', 'required':False
    }), label='')
    plang = forms.ChoiceField(choices=prog_langs.choices(), label='') #widget=forms.Select(attrs={'class':'choiceField'}), label='')

class MyCodeForm(forms.Form):
    #title = forms.CharField(max_length=255, label='Название')
    content = forms.CharField(widget=forms.Textarea(attrs={
        'cols': 120, 'rows': 17, 'class':'form-control', 'id':'ta', 'required':False
    }), label='Код')
    plang = forms.ChoiceField(choices=prog_langs.choices(), label='')

'''
class CreateTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'points', 'until', 'active', 'test']
'''

class CreateTaskForm(forms.Form):
    name = forms.CharField(max_length=255, label='Название задачи')
    short_description = forms.CharField(widget=forms.Textarea(attrs={
        'cols':50, 'rows':5, 'class':'form-control','required':False
    }), label='Краткое описание задачи')
    description = forms.CharField(widget=forms.Textarea(attrs={
        'cols':50, 'rows':17, 'class':'form-control','required':False
    }), label='Описание задачи и требования')
    points = forms.IntegerField(initial=10, label="Количество очков")
    since = forms.DateTimeField(
        initial = datetime.now(),
        widget = NumberInput(attrs={'type': 'datetime-local'}),
        label = "Активна с")
    until = forms.DateTimeField(
        initial = datetime.now(),
        widget = NumberInput(attrs={'type': 'datetime-local'}),
        label="Активна до")
    tasktype = forms.ChoiceField(
        label = 'Тип задачи',
        required = True,
        choices = TaskType.choices
    )
    #active = forms.BooleanField(initial=True, label="Активна?")

class EditStaskForm(forms.ModelForm):
    class Meta:
        model = StandaloneTask
        fields = ('name', 'description', 'since')

class SimpleCodeTestDataForm(forms.Form):
    input = forms.CharField()
    output = forms.CharField()

class CreateTaskForm2(forms.Form):
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