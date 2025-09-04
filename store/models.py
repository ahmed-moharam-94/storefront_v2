from django.db import models
from django.conf import settings


class Customer(models.Model):
    # assign the user to the customer
    user = models.OneToOneField(
        settings.Auth_USER_MODEL, on_delete=models.CASCADE)
    birth_data = models.DateField(null=True, blank=True)
    location = models.TextField()
    second_phone_number = models.CharField(unique=True, blank=True, null=True, max_length=15)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'
    

