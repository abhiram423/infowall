from django.contrib import admin
from .models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 4


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "category",
        "glossy_price",
        "matte_price",
    )

    search_fields = (
        "name",
        "category",
    )

    list_filter = (
        "category",
    )

    inlines = [
        ProductImageInline,
    ]
