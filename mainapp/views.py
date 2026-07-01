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

# ── 1. INDEX / HOME VIEW ──
def index(request):
    return render(request, 'main_templates/index.htm')


# ── 2. PUBLIC FLASHCARDS INFO VIEW ──
def flashcards(request):
    return render(request, 'main_templates/flashcards.html')


# ── 3. ABOUT US VIEW ──
def about(request):
    return render(request, 'main_templates/about.html')


# ── 4. CONTACT VIEW ──
def contact(request):
    return render(request, 'main_templates/contact.html')


# ── 5. SERVICES VIEW ──
def services(request):
    return render(request, 'main_templates/services.html')


# ── 6. AR WALL VIEW ──
def arwall_page(request):
    return render(request, 'main_templates/arwall_page.html')


# ── 7. USER REGISTRATION PIPELINE ──
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
            # create_user వాడుతున్నాం కాబట్టి Django పాస్‌వర్డ్‌ను ఆటోమేటిక్‌గా హ్యాష్ చేస్తుంది
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


# ── 8. SECURE LOGIN WITH DYNAMIC REDIRECTION (`next_page` flow) ──
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

                # 🌟 నువ్వు అడిగినట్లు సెషన్ చెక్ చేసి కరెక్ట్ పేజీకి రీడైరెక్ట్ చేస్తుంది
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


# ── 9. FORGET PASSWORD REQUEST ENGINE ──
def forget_password(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        try:
            user = Usermodel.objects.get(email=email)

            # UUID టోకెన్ క్రియేట్ చేసి డేటాబేస్ లో సేవ్ చేస్తాం
            token = str(uuid.uuid4())
            user.password_reset_token = token 
            user.save()

            reset_link = request.build_absolute_uri(
                reverse('reset_password', args=[token])
            )
            
            subject = "Password Reset Request - Infowall"
            message = f"Click the link below to reset your password:\n{reset_link}"
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

            messages.success(request, "Reset link sent to your email!")
            return redirect('login')
        
        except Usermodel.DoesNotExist:
            messages.error(request, "Email not registered.")

    return render(request, 'main_templates/forget_password.html')


# ── 10. PASSWORD RESET PROCESS ENGINE ──
def reset_password(request, token):
    user = get_object_or_404(Usermodel, password_reset_token=token)

    if request.method == "POST":
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


# ── 11. PUBLIC STORE CATALOG VIEW ──
def shop(request):
    products = Product.objects.all()
    
    # అడ్మిన్ ప్యానెల్ లో కేటగిరీ ఖాళీగా లేని ప్రొడక్ట్స్ ని మాత్రమే ఫిల్టర్ చేస్తుంది
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


# ── 12. HIGH SECURITY LOGOUT PIPELINE ──
def logout_view(request):
    logout(request) # 
    messages.success(request, "You have been logged out Successfully.")
    return redirect('index')