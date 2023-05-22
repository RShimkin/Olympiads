from django.db import models
from djongo import models as dmodels
from django.urls import reverse
from django.contrib.auth.models import User
#import bson

LANG_CHOICES = (
    ('C#', 'C#'),
    ('C++', 'C++')
)

class TestData(dmodels.Model):
    testinput = dmodels.CharField(max_length=1000, primary_key=True, verbose_name="Текстовый ввод")
    testoutput = dmodels.CharField(max_length=1000, verbose_name="Текстовый вывод")

    objects = dmodels.DjongoManager()

    def __str__(self):
        return f"{self.testinput} -> {self.testoutput}"
    
    class Meta:
        managed = False

class TaskResult(dmodels.Model):
    #_id = dmodels.ObjectIdField(primary_key=True, default=bson.ObjectId(b'foo-bar-quux'))
    uname = dmodels.CharField(max_length=255, verbose_name="Имя пользователя")
    taskname = dmodels.CharField(max_length=255, verbose_name="Название задачи")
    points = dmodels.PositiveSmallIntegerField(verbose_name="Очки пользователя", default=0)
    time = dmodels.DateTimeField(auto_now_add=True)

    objects = dmodels.DjongoManager()

    def __str__(self):
        return f"{self.uname} scored {self.points} in task {self.taskname}"
    
    class Meta:
        indexes = [
            models.Index(fields=['uname'], name='res_name_idx'),
            models.Index(fields=['taskname'], name='res_task_idx')
        ]

class Task(dmodels.Model):
    _id = dmodels.ObjectIdField(primary_key=True)
    name = dmodels.CharField(max_length=255, db_index=True, unique=True, verbose_name="Название задачи")
    slug = dmodels.SlugField(max_length=255, verbose_name="slug", blank=True, unique=False) # unique=True
    description = dmodels.TextField(max_length=10000, verbose_name="Описание задачи")
    points = dmodels.PositiveSmallIntegerField(verbose_name="Очки", default=10)
    tests = dmodels.ArrayField(model_container=TestData, default=None, verbose_name="Тестовые данные")
    results = dmodels.ArrayReferenceField(to=TaskResult, default=None, on_delete=models.DO_NOTHING, verbose_name="Результаты пользователей")
    created = dmodels.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    until = dmodels.DateTimeField(default=None, verbose_name="Активна до")
    creator = dmodels.ForeignKey(User, on_delete=dmodels.DO_NOTHING, default=None, verbose_name="Создатель")
    active = dmodels.BooleanField(default=True)
    olympiadname = dmodels.CharField(max_length = 255, verbose_name="Олимпиада", default=None)

    objects = dmodels.DjongoManager()

    def get_absolute_url(self):
        return reverse('task', kwargs={'task_name': self.name})

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            #models.Index(fields=['slug'], name='task_slug_idx'),
        ]

class OlympiadResult(dmodels.Model):
    uname = dmodels.CharField(max_length=255, verbose_name="Имя пользователя")
    olympiad = dmodels.CharField(max_length=255, verbose_name="Название олимпиады")
    points = dmodels.PositiveSmallIntegerField(verbose_name="Очки пользователя", default=0)

    def __str__(self):
        return f"{self.uname} has {self.points} in {self.olympiad}"

    class Meta:
        indexes = [
            models.Index(fields=['uname'], name='olympres_name_idx'),
            models.Index(fields=['olympiad'], name='olympres_olymp_idx')
        ]

class Olympiad(dmodels.Model):
    name = dmodels.CharField(max_length=255, db_index=True, unique=True, verbose_name="Название задачи")
    slug = dmodels.SlugField(max_length=255, verbose_name="slug", blank=True, unique=False) # unique=True
    description = dmodels.TextField(max_length=10000, verbose_name="Описание задачи")
    results = dmodels.ArrayReferenceField(to=OlympiadResult, default=None, on_delete=models.DO_NOTHING, 
        verbose_name="Результаты пользователей", related_name="olympres")
    created = dmodels.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    creator = dmodels.ForeignKey(User, on_delete=dmodels.SET_NULL, default=None, null=True, verbose_name="Создатель")
    tasks = dmodels.ArrayReferenceField(to=Task, default=None, on_delete=models.DO_NOTHING, verbose_name="Результаты пользователей")

    objects = dmodels.DjongoManager()

    def get_absolute_url(self):
        return reverse('olympiad', kwargs={'olymp_name': self.name})

    def __str__(self):
        return f"olympiad {self.name}"

    class Meta:
        verbose_name = 'Олимпиада'
        verbose_name_plural = 'Олимпиады'
        ordering = ['created']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['created'], name='olymp_created_idx')
        ]

class Profile(dmodels.Model):
    user = dmodels.OneToOneField(User, on_delete=dmodels.CASCADE, verbose_name="Пользователь")
    birth_date = dmodels.DateField(blank=True, default=None)
    region = dmodels.CharField(max_length=1000, blank = True)
    # year = ?
    tasks_results = dmodels.ArrayReferenceField(TaskResult, verbose_name="Результаты задач")
    olympiads_results = dmodels.ArrayReferenceField(OlympiadResult, verbose_name="Результаты олимпиад")

    class Meta:
        indexes = [
            models.Index(fields=['user'])
        ]

class TestJson(dmodels.Model):
    content = dmodels.JSONField()

class OlympiadViewModel():
    def __init__(self, olymp):
        self.url = olymp.get_absolute_url()
        self.name = olymp.name
        self.count = len(olymp.results.all())
        self.creator = olymp.creator.username
        self.created = olymp.created

class TaskViewModel():
    def __init__(self, task):
        self.url = task.get_absolute_url()
        self.name = task.name
        self.count = len(task.results.all())
        self.creator = task.creator.username if task.creator != None else ''
        self.created = task.created
