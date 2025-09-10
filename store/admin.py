from django.contrib import admin

from . import models
from .models import Customer, Product


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    # in list_display you can't use related fields such as user__first_name
    # so you have to define related fields and decorate with @admin.display()
    @admin.display(ordering="user__first_name", description="First Name")
    def first_name(self, customer: Customer):
        return customer.user.first_name

    @admin.display(ordering="user__last_name", description="Last Name")
    def last_name(self, customer: Customer):
        return customer.user.last_name

    @admin.display(ordering="user__phone_number", description="Phone Number")
    def phone_number(self, customer: Customer):
        return customer.user.phone_number

    list_display = ["id", "first_name", "last_name", "phone_number"]
    # define the related fields
    list_select_related = ["user"]
    ordering = ["user__first_name", "user__last_name"]
    search_fields = ["user__first_name__istartswith", "user__last_name__istartswith"]


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    # TODO: define a field that show the number of products on every category
    list_display = ["id", "title"]


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    
    # Changelist View fields
    @admin.display(ordering="category__title")
    def category_title(self, product: Product):
        return product.category.title
    
    # TODO: show image
    list_display = ["id", "category_title", "title", "price", "inventory"]
    # note: that category_title will be added 
    ordering = ['id', 'title', 'price']
    list_filter = ["category"]
    search_fields = ["title", "description", "price"]
    list_editable = ["price"]
    
    # Add/Edit Form View fields
    autocomplete_fields = ['category']
