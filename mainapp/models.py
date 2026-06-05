from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField


class Usermodel(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    country_code = models.CharField(max_length=10, default="+91")
    phone = PhoneNumberField(unique=True, region=None)
    password_reset_token = models.CharField(max_length=100, unique=True, blank=True, null=True)

    def __str__(self):
        return self.username
    
class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Feedback(models.Model):
    feed_id = models.AutoField(primary_key=True)
    user_details = models.ForeignKey(User, on_delete=models.CASCADE)
    mood_emoji = models.CharField(max_length=10, null=True, blank=True)
    star_rating = models.IntegerField(default=5)
    star_feedback = models.TextField(max_length=500, default="", blank=True)
    star_Date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"Feedback from {self.user_details.username} - {self.star_rating} stars"
    
class QuizResult(models.Model):
    user = models.ForeignKey(Usermodel, on_delete=models.CASCADE)
    category = models.CharField(max_length=50)
    total_questions = models.IntegerField()
    score = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.category}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    def __str__(self):
        return f"Profile of {self.user.username}"

    
