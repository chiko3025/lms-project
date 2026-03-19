from django.contrib.auth.models import User
from django.db import models
import re

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.IntegerField()
    image = models.ImageField(upload_to='course_images/', blank=True, null=True)

    def __str__(self):
        return self.title
        

class Video(models.Model):
    title = models.CharField(max_length=200)
    youtube_url = models.CharField(max_length=50)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        import re
        if "youtube.com" in self.youtube_url or "youtu.be" in self.youtube_url:
            match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", self.youtube_url)
            if match:
                self.youtube_url = match.group(1)
        super().save(*args, **kwargs)        
# Create your models here.

class Purchase(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    course = models.ForeignKey('Course',on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"


class VideoProgress(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    video = models.ForeignKey('Video', on_delete=models.CASCADE)

    watched_seconds = models.IntegerField(default=0)

    completed = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.video.title}"            