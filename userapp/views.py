import email
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from mainapp.models import Usermodel, Profile, QuizResult, Feedback
from django.http import JsonResponse
import json
from django.db.models import Sum, Max
from django.db import transaction
import json
import logging
logger = logging.getLogger(__name__)


def dashboard(request):
    user_id = request.session.get('user_id')
    if not user_id: 
        return redirect('login')
    
    user = get_object_or_404(Usermodel, id=user_id)
    db_stars = QuizResult.objects.filter(user=user).aggregate(Sum('score'))['score__sum'] or 0

    recent_activity = QuizResult.objects.filter(user=user).order_by('-completed_at')[:5]
    
    categories= ['alphabets', 'numbers', 'colors', 'animals', 'fruits', 'shapes']
    cat_progress = {}
    for cat in categories:
        max_score = QuizResult.objects.filter(user=user, category=cat).aggregate(Max('score'))['score__max'] or 0
        cat_progress[cat] = max_score

    context = {
        'user': user,
        'db_stars': db_stars,
        'recent_activity': recent_activity,
        'cat_progress': cat_progress,
    }

    return render(request, 'user_templates/dashboard.html', context)


def save_quiz_result(request):
    if request.method ==  "POST":
        data = json.loads(request.body)
        user_id = request.session.get('user_id')
        user = Usermodel.objects.get(id=user_id)


        QuizResult.objects.create(
            user=user,
            category=data.get('category'),
            total_questions=data.get('total'),
            score=data.get('score')
        )
        return JsonResponse({'status': 'success', 'message': 'Quiz result saved successfully'})
    return JsonResponse({'status': 'invalid request'}, status=400)

def feedback(request):
    user_id = request.session.get('user_id')
    if not user_id:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)
        messages.error(request, "Please log in to submit your feedback.")
        return redirect('login')

    user = get_object_or_404(Usermodel, id=user_id)

    # 2. Handle AJAX POST request from Frontend
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            mood = data.get('mood', '').strip()
            comment = data.get('comment', '').strip()

            if not mood:
                return JsonResponse({'status': 'error', 'message': 'Mood rating is required.'}, status=400)

            # Map the clean front-end UI emojis directly to star integers for DB metrics
            rating_map = {"😍": 5, "😊": 4, "😐": 3, "😕": 2}
            stars = rating_map.get(mood, 5) # Default to 5 if something went wrong

            # Atomic database transaction control for safe writes
            with transaction.atomic():
                Feedback.objects.create(
                    user_details=user,    # Automatically links the logged-in User ID
                    mood_emoji=mood,
                    star_rating=stars,
                    star_feedback=comment
                )

            return JsonResponse({'status': 'success', 'message': 'Magic feedback saved!'})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid payload format.'}, status=400)
        except Exception as e:
            logger.error(f"Production Feedback Save Error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'Server error. Please try again later.'}, status=500)

    # 3. Handle standard GET request to load the page layout
    db_stars = QuizResult.objects.filter(user=user).aggregate(Sum('score'))['score__sum'] or 0
    return render(request, 'user_templates/feedback.html', {'user': user, 'db_stars': db_stars})

def profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in to manage your profile.")
        return redirect('login')

    user = get_object_or_404(Usermodel, id=user_id)

    # 2. Handle Form Profile Updates
    if request.method == "POST":
        new_username = request.POST.get('username', '').strip()
        new_email = request.POST.get('email', '').strip()
        new_phone = request.POST.get('phone', '').strip()

        # Input Validations
        if not new_username or not new_email or not new_phone:
            messages.error(request, "All fields are required to update your workspace.")
            return redirect('profile')

        # Business Logic Safety: Prevent choosing an email owned by another user id
        if Usermodel.objects.filter(email=new_email).exclude(id=user.id).exists():
            messages.error(request, "This email address is already locked onto another account.")
            return redirect('profile')

        try:
            with transaction.atomic():
                # Update properties
                user.username = new_username
                user.email = new_email
                user.phone = new_phone
                user.save()

            # Crucial: Update active session variables instantly so navigation headers update flawlessly
            request.session['username'] = user.username
            
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
        
    context = {
        'user': user,
        'db_stars': db_stars,
        'cat_progress': cat_progress,
    }
    return render(request, 'user_templates/profile.html', context)

def flashcards_user(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    user = get_object_or_404(Usermodel, id=user_id)
    db_stars = QuizResult.objects.filter(user=user).aggregate(Sum('score'))['score__sum'] or 0
    return render(request, 'user_templates/flashcards_user.html', {'user': user, 'db_stars': db_stars})

