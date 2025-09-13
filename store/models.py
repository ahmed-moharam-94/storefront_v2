from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Customer(models.Model):
    # assign the user to the customer
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    birth_date = models.DateField(null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    second_phone_number = models.CharField(
        unique=True, blank=True, null=True, max_length=15)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'


class CustomerImage(models.Model):
    image = models.ImageField(upload_to='store/images/customers')
    customer = models.OneToOneField(
        Customer, on_delete=models.CASCADE, related_name='image')
    


class Category(models.Model):
    title = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return self.title
    
    

class Product(models.Model):
    title = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    slug = models.SlugField()
    price = models.DecimalField(max_digits=5, decimal_places=2, validators=[
        MinValueValidator(1), MaxValueValidator(999999),
    ],
    )
    inventory = models.IntegerField(validators=[MinValueValidator(0)])
    category = models.ForeignKey(Category, on_delete=models.PROTECT)


class ProductImage(models.Model):
    image = models.ImageField(upload_to='store/images/products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    


#TODO: 
# 1) Implement Order, OrderItem models
# 2) Implement Cart, CartItem models
# 3) Implement Like as a content_type
# 4) Implement Reviews
# 5) Add ordering to Products, Customer models