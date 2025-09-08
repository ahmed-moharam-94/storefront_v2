from django.db import models
from django.conf import settings



class Customer(models.Model):
    # assign the user to the customer
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    birth_date = models.DateField(null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    second_phone_number = models.CharField(unique=True, blank=True, null=True, max_length=15)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'
    

class CustomerImage(models.Model):
    image = models.ImageField(upload_to='store/images')
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='image')
    

