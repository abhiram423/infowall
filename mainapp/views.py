import uuid
import phonenumbers
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login as auth_login, logout
from .models import Usermodel, Product

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
            Usermodel.objects.create_user(
                username=username,
                email=email,
                phone=full_phone,
                password=pwd
            )
            messages.success(request, "Registration successful! Please login.")
            return redirect('login')
        except Exception as e:
            messages.error(request, "An error occurred during registration. Please try again.")
            
    return render(request, 'main_templates/register.html')


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user_exists = Usermodel.objects.filter(email=email).first()

        if user_exists:
            user = authenticate(username=user_exists.username, password=password)
            if user is not None:
                auth_login(request, user) 
                messages.success(request, f"Welcome back, {user.username}!")

                next_page = request.session.pop('next_page', None)
                if next_page == 'cart':
                    return redirect('cart')
                elif next_page == 'wishlist':
                    return redirect('wishlist')
                
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid email or password")
        else:
            messages.error(request, "Invalid email or password")
            
    return render(request, 'main_templates/login.html')


from django.utils import timezone

def forget_password(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        try:
            user = Usermodel.objects.get(email=email)

            token = str(uuid.uuid4())
            user.password_reset_token = token
            user.password_reset_token_created = timezone.now()

            user.save()

            reset_link = request.build_absolute_uri(
                reverse('reset_password', args=[token])
            )
            
            subject = "Password Reset Request - Infowall"
            message = f"""
            Hello {user.username},

                We received a request to reset the password for your Infowall account.

                To create a new password, please click the secure link below:

                {reset_link}

                Important Security Information:
                • This password reset link is valid for only 10 minutes.
                • If the link expires, you can request another password reset email.
                • If you did not request this password reset, you can safely ignore this email. Your account will remain secure.

                Thank you,

                Infowall Team
                Interactive Learning Platform
                """

            send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False
                )

            messages.success(request, "Reset link sent to your email!")
            return redirect('login')
        
        except Usermodel.DoesNotExist:
            messages.error(request, "Email not registered.")

    return render(request, 'main_templates/forget_password.html')

from django.utils import timezone
from datetime import timedelta

def reset_password(request, token):
    user = get_object_or_404(Usermodel, password_reset_token=token)

    if (
        user.password_reset_token_created is None or
        timezone.now() > user.password_reset_token_created + timedelta(minutes=10)
    ):
        user.password_reset_token = None
        user.password_reset_token_created = None
        user.save()

        messages.error(
            request,
            "This password reset link has expired. Please request a new one."
        )
        return redirect("forget_password")

    if request.method == "POST":
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if new_password == confirm_password:
            user.password = make_password(new_password)
            user.password_reset_token = None
            user.password_reset_token_created = None
            user.save()
            messages.success(request, "Password updated successfully!")
            return redirect('login')
        else:
            messages.error(request, "Passwords do not match.")
 
    return render(request, 'main_templates/reset_password.html', {'token': token})


def shop(request):
    products = Product.objects.all()
    
    categories = Product.objects.exclude(
        category__isnull=True
    ).exclude(
        category=''
    ).values_list(
        'category', flat=True
    ).distinct()
    
    cleaned_categories = sorted(list(set(cat.strip() for cat in categories)))
    total_products = products.count()

    context = {
        'products': products,
        'categories': cleaned_categories,
        'total_products': total_products,
    }
    return render(request, 'main_templates/shop.html', context)


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out Successfully.")
    return redirect('index')