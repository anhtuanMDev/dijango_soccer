from django.db import models

class Player(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length= 100)
    club = models.CharField(max_length=50, default="Unknown")
    position = models.CharField(max_length=50)
    likes = models.IntegerField(default=0)
