import json
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Max
from django.db import transaction
from django.contrib.auth.decorators import login_required
from mainapp.models import Usermodel, Profile, QuizResult, Feedback, Product, Cart, Wishlist, ProductImage

logger = logging.getLogger(__name__)

@login_required(login_url='login')
def dashboard(request):
    user = request.user 
    db_stars = QuizResult.objects.filter(user=user).aggregate(Sum('score'))['score__sum'] or 0
    recent_activity = QuizResult.objects.filter(user=user).order_by('-completed_at')[:5]

    categories = ['alphabets', 'numbers', 'colors', 'animals', 'fruits', 'shapes']
    cat_progress = {}
    for cat in categories:
        max_score = QuizResult.objects.filter(user=user, category=cat).aggregate(Max('score'))['score__max'] or 0
        cat_progress[cat] = max_score

    cart_count = Cart.objects.filter(user=user).aggregate(total=Sum('quantity'))['total'] or 0

    context = {
        'user': user,
        'db_stars': db_stars,
        'recent_activity': recent_activity,
        'cat_progress': cat_progress,
        'cart_count': cart_count,
    }
    return render(request, 'user_templates/dashboard.html', context)


@login_required(login_url='login')
def save_quiz_result(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user = request.user

        QuizResult.objects.create(
            user=user,
            category=data.get('category'),
            total_questions=data.get('total'),
            score=data.get('score')
        )
        return JsonResponse({'status': 'success', 'message': 'Quiz result saved successfully'})
    return JsonResponse({'status': 'invalid request'}, status=400)


@login_required(login_url='login')
def feedback(request):
    user = request.user

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            mood = data.get('mood', '').strip()
            comment = data.get('comment', '').strip()

            if not mood:
                return JsonResponse({'status': 'error', 'message': 'Mood rating is required.'}, status=400)

            rating_map = {"😍": 5, "😊": 4, "😐": 3, "😕": 2}
            stars = rating_map.get(mood, 5)

            with transaction.atomic():
                Feedback.objects.create(
                    user_details=user,    
                    mood_emoji=mood,
                    star_rating=stars,
                    star_feedback=comment
                )
            return JsonResponse({'status': 'success', 'message': 'Magic feedback saved!'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid payload format.'}, status=400)
        except Exception as e:
            logger.error(f"Production Feedback Save Error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'Server error.'}, status=500)

    db_stars = QuizResult.objects.filter(user=user).aggregate(Sum('score'))['score__sum'] or 0
    cart_count = Cart.objects.filter(user=user).aggregate(total=Sum('quantity'))['total'] or 0
    return render(request, 'user_templates/feedback.html', {'user': user, 'db_stars': db_stars, 'cart_count': cart_count})


@login_required(login_url='login')
def profile(request):
    user = request.user

    if request.method == "POST":
        new_username = request.POST.get('username', '').strip()
        new_email = request.POST.get('email', '').strip()
        new_phone = request.POST.get('phone', '').strip()

        if not new_username or not new_email or not new_phone:
            messages.error(request, "All fields are required to update your workspace.")
            return redirect('profile')

        if Usermodel.objects.filter(email=new_email).exclude(id=user.id).exists():
            messages.error(request, "This email address is already locked onto another account.")
            return redirect('profile')

        try:
            with transaction.atomic():
                user.username = new_username
                user.email = new_email
                user.phone = new_phone
                user.save()
            messages.success(request, "Your profile parameters have been updated smoothly! ✨")
            return redirect('profile')
        except Exception as e:
            logger.error(f"Production Profile Save Error: {str(e)}")
            messages.error(request, "A database failure occurred while updating properties.")
            return redirect('profile')
        
    db_stars = QuizResult.objects.filter(user=user).aggregate(Sum('score'))['score__sum'] or 0
    categories = ['alphabets', 'numbers', 'colors', 'animals', 'fruits', 'shapes']
    cat_progress = {}
    for cat in categories:
        max_score = QuizResult.objects.filter(user=user, category=cat).aggregate(Max('score'))['score__max'] or 0
        cat_progress[cat] = max_score

    cart_count = Cart.objects.filter(user=user).aggregate(total=Sum('quantity'))['total'] or 0

    context = {
        'user': user,
        'db_stars': db_stars,
        'cat_progress': cat_progress,
        'cart_count': cart_count,
    }
    return render(request, 'user_templates/profile.html', context)


@login_required(login_url='login')
def flashcards_user(request):
    user = request.user
    db_stars = QuizResult.objects.filter(user=user).aggregate(Sum('score'))['score__sum'] or 0
    cart_count = Cart.objects.filter(user=user).aggregate(total=Sum('quantity'))['total'] or 0
    return render(request, 'user_templates/flashcards_user.html', {'user': user, 'db_stars': db_stars, 'cart_count': cart_count})


def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        request.session['next_page'] = 'cart'  
        messages.info(request, "Please login or register to add items to your cart.")
        return redirect('login')

    user = request.user
    product = get_object_or_404(Product, id=product_id)
    finish = request.POST.get('selected_finish', 'glossy').lower()

    cart_item, created = Cart.objects.get_or_create(
        user=user,
        product=product,
        paper_finish=finish,
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"{product.name} ({finish.title()} Finish) added to your cart!")
    return redirect('cart')


@login_required(login_url='login')
def cart(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user).select_related('product')
    total_price = 0

    for item in cart_items:
        finish = item.paper_finish.lower()

        if finish == "glossy":
            current_price = item.product.glossy_price
        else:
            current_price = item.product.matte_price

        item.variant_price = current_price
        item.item_total = current_price * item.quantity

        total_price += item.item_total

    context = {
        'user': user,
        'cart_items': cart_items,
        'total_price': total_price,
        'cart_count': sum(item.quantity for item in cart_items),
    }
    return render(request, 'user_templates/cart.html', context)


@login_required(login_url='login')
def remove_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.delete()
    return redirect('cart')


@login_required(login_url='login')
def user_shop(request):
    user = request.user
    products = Product.objects.all()
    
    categories = Product.objects.exclude(category__isnull=True).exclude(category='').values_list('category', flat=True).distinct()
    cleaned_categories = sorted(list(set(cat.strip() for cat in categories)))
    
    db_stars = QuizResult.objects.filter(user=user).aggregate(Sum('score'))['score__sum'] or 0
    cart_count = Cart.objects.filter(user=user).aggregate(total=Sum('quantity'))['total'] or 0

    context = {
        'user': user,
        'products': products,
        'categories': cleaned_categories,
        'total_products': products.count(),
        'db_stars': db_stars,
        'cart_count': cart_count,
    }
    return render(request, 'user_templates/user_shop.html', context)


def toggle_wishlist(request, product_id):
    if not request.user.is_authenticated:
        request.session['next_page'] = 'wishlist'
        messages.info(request, "Please login or register to add items to your wishlist.")
        return redirect('login')
    
    user = request.user
    product = get_object_or_404(Product, id=product_id)
    wishlist_item = Wishlist.objects.filter(user=user, product=product)

    if wishlist_item.exists():
        wishlist_item.delete()  
        messages.success(request, f"{product.name} removed from your wishlist.")
    else:
        Wishlist.objects.create(user=user, product=product)  
        messages.success(request, f"{product.name} added to your wishlist! ❤️")
        
    return redirect(request.META.get('HTTP_REFERER', 'shop'))


@login_required(login_url='login')
def wishlist(request):
    user = request.user
    user_wishlist = Wishlist.objects.filter(user=user).select_related('product')

    db_stars = QuizResult.objects.filter(user=user).aggregate(Sum('score'))['score__sum'] or 0
    cart_count = Cart.objects.filter(user=user).aggregate(total=Sum('quantity'))['total'] or 0

    context = {
        'user': user,
        'user_wishlist': user_wishlist,
        'db_stars': db_stars,
        'cart_count': cart_count,
    }
    return render(request, 'user_templates/wishlist.html', context)


@login_required(login_url='login')
def increase_cart_qty(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('cart')
 
@login_required(login_url='login')
def decrease_cart_qty(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
        messages.success(request, f"{cart_item.product.name} removed from cart.")
    return redirect('cart')

@login_required(login_url="login")
def shops(request):

    user = request.user

    products = Product.objects.all()

    categories = (
        Product.objects
        .exclude(category__isnull=True)
        .exclude(category='')
        .values_list("category", flat=True)
        .distinct()
    )

    cleaned_categories = sorted(set(cat.strip() for cat in categories))

    db_stars = QuizResult.objects.filter(
        user=user
    ).aggregate(
        Sum("score")
    )["score__sum"] or 0

    cart_count = Cart.objects.filter(
        user=user
    ).aggregate(
        total=Sum("quantity")
    )["total"] or 0

    context = {
        "user": user,
        "products": products,
        "categories": cleaned_categories,
        "total_products": products.count(),
        "db_stars": db_stars,
        "cart_count": cart_count,
    }
    return render(request, "user_templates/shops.html", context)

