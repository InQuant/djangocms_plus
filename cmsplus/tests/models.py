from django.db import models


class Test(models.Model):
    message = models.CharField(max_length=255, default="Hello World")
