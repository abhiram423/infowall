from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings

class Usermodel(AbstractUser):
    phone = PhoneNumberField(unique=True, region=None, null=True, blank=True)
    country_code = models.CharField(max_length=10, default="+91")
    password_reset_token = models.CharField(max_length=100, unique=True, blank=True, null=True)
    password_reset_token_created = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.username
    

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class QuizResult(models.Model):
    user = models.ForeignKey(Usermodel, on_delete=models.CASCADE)
    category = models.CharField(max_length=50)
    total_questions = models.IntegerField()
    score = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.category}"


class Profile(models.Model):
    user = models.OneToOneField(Usermodel, on_delete=models.CASCADE, related_name='profile')

    def __str__(self):
        return f"Profile of {self.user.username}"


class Product(models.Model):
    name = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, null=True, blank=True, default="Educational Flash Cards Set")
    description = models.TextField(null=True, blank=True, default="Premium interactive flashcards designed to help early development.")
    glossy_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    matte_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.FileField(upload_to='products/', null=True, blank=True)
    category = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_images', null=True, blank=True)
    image = models.FileField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Gallery Image for {self.product.name if self.product else 'Unassigned Product'}"
    

class Cart(models.Model):
    user = models.ForeignKey(Usermodel, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    paper_finish = models.CharField(max_length=50, default='glossy') # 🌟 Stores user selection dynamic states ('glossy' / 'matte')
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.paper_finish})"


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product') # 🌟 Prevents dual rows instantiation for same instances mapping

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Feedback(models.Model):
    feed_id = models.AutoField(primary_key=True)
    user_details = models.ForeignKey(Usermodel, on_delete=models.CASCADE)
    mood_emoji = models.CharField(max_length=10, null=True, blank=True)
    star_rating = models.IntegerField(default=5)
    star_feedback = models.TextField(max_length=500, default="", blank=True)
    star_Date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"Feedback from {self.user_details.username} - {self.star_rating} stars"