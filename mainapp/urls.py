from django.urls import path
from mainapp import views
from userapp import views as user_views

urlpatterns = [
    path('', views.index, name='index'),
    path('flashcards/', views.flashcards, name='flashcards'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('services/', views.services, name='services'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('arwall-page/', views.arwall_page, name='arwall_page'),
    path('forget-password/', views.forget_password, name='forget_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
    path('dashboard/', user_views.dashboard, name='dashboard'),
    path('feedback/', user_views.feedback, name='feedback'),
    path('profile/', user_views.profile, name='profile'),
    path('flashcards-user/', user_views.flashcards_user, name='flashcards_user'),
    path('save-quiz-result/', user_views.save_quiz_result, name='save_quiz_result'),
    path('shop/', views.shop, name='shop'),
    path('cart/', user_views.cart, name='cart'),
    path('add-to-cart/<int:product_id>/', user_views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:cart_id>/', user_views.remove_from_cart, name='remove_from_cart'),
    path('logout/', views.logout_view, name='logout'),
    path('wishlist/', user_views.wishlist, name='wishlist'),
    path('toggle-wishlist/<int:product_id>/', user_views.toggle_wishlist, name='toggle_wishlist'),
    path('shops/', user_views.shops, name='shops'),
    
]
