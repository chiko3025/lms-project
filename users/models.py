from django.contrib.auth.models import User
from django.db import models

class UserDevice(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    device_id = models.CharField(max_length=200, blank=True)

    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username