from django.db import models
from djongo import models as dmodels
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
#import bson

from OlympiadUsers.models import Profile

LANG_CHOICES = (
    ('C#', 'C#'),
    ('C++', 'C++'),
    ('PYTHON', 'Python')
)

class TaskType(models.TextChoices):
    SIMPLECHOICE = 'SCH', _('choose one')
    MULTIPLECHOICE = 'MCH', _('choose several')
    FULLANSWER = 'FUL', _('full answer')
    CODESIMPLETEST = 'CST', _('code with output comparison')
    CODEDOUBLETEST = 'CDT', _('code with output test')

'''class TestChoice(dmodels.Model):
    text = dmodels.CharField(max_length=255, default=None)
    correct = dmodels.BooleanField(default=False)

    objects = dmodels.DjongoManager()

    class Meta:
        managed = False
        #abstract = False'''


class TestData(dmodels.Model):
    type = dmodels.CharField(max_length=3, choices=TaskType.choices, default=TaskType.CODESIMPLETEST, verbose_name="Тип задачи")
    question = dmodels.TextField(max_length=1000, default=None, verbose_name="Вопрос задачи")
    #choices = dmodels.ArrayField(model_container=TestChoice, verbose_name="Тестовые варианты")
    testinput = dmodels.CharField(max_length=1000, primary_key=True, default=None, verbose_name="Текстовый ввод")
    testoutput = dmodels.CharField(max_length=1000, verbose_name="Текстовый вывод")

    objects = dmodels.DjongoManager()

    def __str__(self):
        return f"{self.testinput} -> {self.testoutput}"

    def __getitem__(self, name):
       return getattr(self, name)
    
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

class StandaloneTaskResult(dmodels.Model):
    _id = dmodels.ObjectIdField(primary_key=True)
    user = dmodels.ForeignKey(User, on_delete=dmodels.DO_NOTHING, default=None, verbose_name="Чей результат")
    username = dmodels.CharField(max_length=255, verbose_name="Чей результат (имя пользователя)")
    taskname = dmodels.CharField(max_length=255, verbose_name="Для какой задачи (название)")
    points = dmodels.PositiveIntegerField(verbose_name='Вес в очках')
    started = dmodels.DateTimeField(auto_now_add=False, default=None, verbose_name='Время начала выполнения')
    finished = dmodels.DateTimeField(auto_now_add=False, default=None, verbose_name='Время начала выполнения')
    attempts = dmodels.PositiveIntegerField(verbose_name='количество попыток')
    inner_attempts = dmodels.PositiveIntegerField(verbose_name='количество внутренних отправлений')
    success = dmodels.BooleanField(verbose_name='статус выполнения')

    objects = dmodels.DjongoManager()

    class Meta:
        verbose_name = 'Пользовательский результат по задаче'
        verbose_name_plural = 'результаты'
        ordering = ['-points']
        indexes = [
            #models.Index(fields=['guid']),
            #models.Index(fields=['slug'], name='task_slug_idx'),
        ]

class StandaloneTask(dmodels.Model):
    _id = dmodels.ObjectIdField(primary_key=True)
    guid = dmodels.TextField(default=None)          # delete
    name = dmodels.CharField(max_length=255, unique=True, verbose_name="Название задачи")
    short_description = dmodels.TextField(max_length=500, verbose_name="Краткое описание задачи")
    description = dmodels.TextField(max_length=10000, verbose_name='Полное описание задачи')
    points = dmodels.PositiveIntegerField(verbose_name='Вес в очках')
    active = dmodels.BooleanField(default=True)
    creator = dmodels.ForeignKey(User, on_delete=dmodels.DO_NOTHING, default=None, verbose_name="Создатель задачи")
    tests = dmodels.ArrayField(model_container=TestData, default=None, verbose_name="Тесты")
    created = dmodels.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    since = dmodels.DateTimeField(default=None, verbose_name="Активна с")
    until = dmodels.DateTimeField(default=None, verbose_name="Активна до")
    results = dmodels.ArrayReferenceField(to=TaskResult, default=None, on_delete=models.DO_NOTHING, verbose_name="Результаты пользователей")
    hidden = dmodels.BooleanField(default=False, verbose_name="Закрытый доступ")
    tasktype = dmodels.CharField(max_length=3, choices=TaskType.choices, default=TaskType.CODESIMPLETEST)
    #choices = dmodels.ArrayField(model_container=TestChoice, default=None, verbose_name="Тестовые варианты")

    objects = dmodels.DjongoManager()

    def get_view_url(self):
        return reverse('viewstask', kwargs={'task_oid': str(self._id)})
    
    def get_edit_url(self):
        return reverse('editstask', kwargs={'task_oid': str(self._id)})

    def __str__(self):
        return f"stask #{str(self._id)}"

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['created']
        indexes = [
            models.Index(fields=['guid']),
            #models.Index(fields=['slug'], name='task_slug_idx'),
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

class UserStats(dmodels.Model):
    user = dmodels.OneToOneField(User, on_delete=dmodels.CASCADE, verbose_name="Пользователь")
    tasks_results = dmodels.ArrayReferenceField(TaskResult, verbose_name="Результаты задач")
    olympiads_results = dmodels.ArrayReferenceField(OlympiadResult, verbose_name="Результаты олимпиад")

    class Meta:
        indexes = [
            models.Index(fields=['user'])
        ]

class TestJson(dmodels.Model):
    content = dmodels.JSONField()
    text = dmodels.TextField(default=None)
    profileref = dmodels.OneToOneField(Profile, on_delete=dmodels.DO_NOTHING, default=None)
    taskref = dmodels.OneToOneField(Task, on_delete=dmodels.DO_NOTHING, default=None)
    #taskref = dmodels.GenericObjectIdField()

    objects = dmodels.DjongoManager()

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

class StandaloneTaskViewModel():
    def __init__(self, task):
        self.view_url = task.get_view_url()
        self.edit_url = task.get_edit_url()
        self.name = task.name
        #self.count = len(task.results.all())
        self.creator = task.creator.username if task.creator != None else ''
        self.created = task.created
