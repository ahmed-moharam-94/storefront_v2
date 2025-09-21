from uuid import uuid4
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Customer(models.Model):
    # assign the user to the customer
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    birth_date = models.DateField(null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    second_phone_number = models.CharField(
        unique=True, blank=True, null=True, max_length=15
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    class Meta:
        ordering = ["user__first_name", "user__last_name"]


class CustomerImage(models.Model):
    image = models.ImageField(upload_to="store/images/customers")
    customer = models.OneToOneField(
        Customer, on_delete=models.CASCADE, related_name="image"
    )


class Category(models.Model):
    title = models.CharField(max_length=255, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title"]


class Product(models.Model):
    title = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    slug = models.SlugField()
    price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(999999),
        ],
    )
    inventory = models.IntegerField(validators=[MinValueValidator(0)])
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    image = models.ImageField(upload_to="store/images/products")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )


class Review(models.Model):
    rate = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    description = models.TextField(null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.description} rate: {self.rate}"

    class Meta:
        # only one review for a customer on the same product
        unique_together = [
            ["customer", "product"],
        ]


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    # customer can be null because cart is created for anonymous users
    # and after the user is authenticated it will be updated
    customer = models.OneToOneField(
        Customer, on_delete=models.CASCADE, null=True, blank=True
    )


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        # make sure cart only have one instance from a product
        unique_together = [["cart", "product"]]

    
class Order(models.Model):
    PENDING_PAYMENT_STATUS = 'P'
    COMPLETED_PAYMENT_STATUS = 'C'
    FAILED_PAYMENT_STATUS = 'F'
    PAYMENT_STATUS_CHOICES = [
        (PENDING_PAYMENT_STATUS, 'Pending'),
        (COMPLETED_PAYMENT_STATUS, 'Completed'),
        (FAILED_PAYMENT_STATUS, 'Failed'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='orders')
    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1,
        choices=PAYMENT_STATUS_CHOICES,
        default=PENDING_PAYMENT_STATUS,
    )

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.SmallIntegerField(validators=[MinValueValidator(1)])
    current_price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(1), MaxValueValidator(999999)],
    )

