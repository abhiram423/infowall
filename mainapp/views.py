import token
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
import os
from .models import Usermodel, Quiz
import re
from django.db import IntegrityError
import phonenumbers
from django.core.mail import send_mail
import uuid
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password


def index(request):
    return render(request, 'main_templates/index.htm')

def flashcards(request):
    return render(request, 'main_templates/flashcards.html')

def about(request):
    return render(request, 'main_templates/about.html')

def contact(request):
    return render(request, 'main_templates/contact.html')

def services(request):
    return render(request, 'main_templates/services.html')

def arwall_page(request):
    return render(request, 'main_templates/arwall_page.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        country_code = request.POST.get('country_code')
        phone = request.POST.get('phone')
        pwd = request.POST.get('password')
        cpwd = request.POST.get('confirm_password')

        full_phone = country_code + phone

        if pwd != cpwd:
            messages.error(request, "Passwords do not match.")
            return redirect('register')
        if Usermodel.objects.filter(email=email).exists():
            messages.warning(request, "This email is already registered.")
            return redirect('register')
        
        try:
            parsed_number = phonenumbers.parse(full_phone)

            if not phonenumbers.is_valid_number(parsed_number):
                messages.error(request, "Invalid phone number. Please enter a valid number.")
                return redirect('register')
        except:
            messages.error(request, "Invalid phone number format. Please enter a valid number.")
            return redirect('register')
        
        if Usermodel.objects.filter(phone=full_phone).exists():
            messages.warning(request, "This phone number is already registered.")
            return redirect('register')
        
        try:
            new_user = Usermodel.objects.create(
                username=username,
                email=email,
                phone=full_phone,
                password=make_password(pwd)
            )
            messages.success(request, "Registration successful! Please login.")
            return redirect('login')
        except Exception as e:
            messages.error(request, "An error occurred. Please try again.")
    return render(request, 'main_templates/register.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
       
        user_exists = Usermodel.objects.filter(email=email).first()

        if user_exists and check_password(password, user_exists.password):
            request.session['user_id'] = user_exists.id
            request.session['username'] = user_exists.username
            messages.success(request, f"Welcome back, {user_exists.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid email or password")
            return redirect('login')    
    
    return render(request, 'main_templates/login.html')

def forget_password(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        try:
            user = Usermodel.objects.get(email=email)

            token = str(uuid.uuid4())
            user.password_reset_token = token 
            user.save()

            reset_link = request.build_absolute_uri(
                reverse('reset_password', args=[token])
            )
            print(reset_link)
            
            subject = "Password Reset Request - Infowall"
            message = f"Click the link below to reset your password:\n{reset_link}"
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

            messages.success(request, "Reset link sent to your email!")
            return redirect('login')
        
        except Usermodel.DoesNotExist:
            messages.error(request, "Email not registered.")

    return render(request, 'main_templates/forget_password.html')

def reset_password(request, token):
    user = get_object_or_404(Usermodel, password_reset_token=token)

    if request.method  == "POST":
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if new_password == confirm_password:
            user.password = make_password(new_password)
            user.password_reset_token = None
            user.save()
            messages.success(request, "Password updated successfully!")
            return redirect('login')
        else:
            messages.error(request, "Passwords do not match.")

    return render(request, 'main_templates/reset_password.html', {'token': token})

def shop(request):
    return render(request, 'main_templates/shop.html')