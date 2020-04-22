from django.db import models

# Create your models here.
class Ham(models.Model):
    IMEI = models.CharField(max_length=32, unique=True)
    username = models.CharField(max_length=10, unique=True)
    sex = models.BooleanField(default=True)
    is_running = models.BooleanField(default=False)
    recent_result = models.BooleanField(default=True)