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

    list_display = ['id', 'first_name', 'last_name', 'phone_number']
    # define the related fields
    list_select_related = ['user']
    ordering = ['user__first_name', 'user__last_name']
    search_fields = ['user__first_name__istartswith', 'user__last_name__istartswith']


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    pass
