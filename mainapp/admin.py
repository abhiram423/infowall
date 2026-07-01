from django.contrib import admin
from .models import Product, Cart, ProductImage, Wishlist, Usermodel, Quiz, QuizResult, Feedback, Profile

class ProductImageAdmin(admin.TabularInline):
    model = ProductImage
    extra = 3 


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageAdmin] 
    list_display = ('name', 'price', 'category', 'subtitle') 
    search_fields = ('name', 'category')
    list_filter = ('category',)

admin.site.register(Cart)
admin.site.register(Wishlist)
admin.site.register(Usermodel)
admin.site.register(Quiz)
admin.site.register(QuizResult)
admin.site.register(Feedback)
admin.site.register(Profile)