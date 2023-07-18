from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.

class Privilege(models.Model):
    id = models.AutoField(primary_key=True)
    pageallocation = models.ForeignKey(
        'PageAllocation',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='privileges'
    )
    is_active = models.BooleanField(default=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    assigned_users = models.ManyToManyField(
        User,
        related_name='assigned_privileges',
        related_query_name='assigned_privileges'
    )

    def __str__(self):
        return str(self.id)


class PageAllocation(models.Model):
    id = models.AutoField(primary_key=True)
    route = models.CharField(max_length=255, blank=True, default='')
    name = models.CharField(max_length=255, blank=True, default='')
    psection = models.CharField(max_length=255, blank=True, default='')
    ssection = models.CharField(max_length=255, blank=True, default='')
    pposition = models.IntegerField(default=0)
    sposition = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> int:
        return str(self.id)
    