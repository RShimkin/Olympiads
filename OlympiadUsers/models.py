from enum import Enum
from django.db import models
from djongo import models as dmodels
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

LOCATION_CHOICES = (
    ('Russia, Moscow', 'Russia, Moscow'),
    ('Russia, Voronezh', 'Russia, Voronezh'),
    ('UK, London', 'UK, London')
)

class UserType(Enum):

    ADMIN = "ADMIN"
    CREATOR = "CREATOR"
    PARTICIPANT = "PARTICIPANT"

    @classmethod
    def choices(cls):
        #print(tuple((i.name, i.value) for i in cls))
        return tuple((i.name, i.value) for i in cls)

    @classmethod
    def choices_safe(cls):
        return tuple((i.name, i.value) for i in cls if i.value != 'ADMIN')
    
class SchoolYears(Enum):

    SCHOOL5 = "SCHOOL5"
    SCHOOL9= "SCHOOL9"
    SCHOOL11= "SCHOOL11"
    UNI1 = "UNI1"
    UNI4 = "UNI4"
    NO = "NO"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)

class Profile(dmodels.Model):
    user = dmodels.OneToOneField(User, on_delete=dmodels.CASCADE, verbose_name="Пользователь")
    user_type = dmodels.CharField(max_length=20, choices=UserType.choices())
    birth_date = dmodels.DateField(blank=True, default=None)
    location = dmodels.CharField(max_length=255, blank = True)
    year = dmodels.CharField(max_length=20, choices=SchoolYears.choices())

    objects = dmodels.DjongoManager()

    class Meta:
        indexes = [
            models.Index(fields=['user'])
        ]

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()