from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    # create user using phone_number & password
    def create_user(self, phone_number, password, **extra_fields):
        # check if the phone_number is None or empty string
        if not phone_number:
            raise ValueError('The phone number must be set')
        # create a user model with phone_number and pass the extra_fields
        user = self.model(phone_number=phone_number, **extra_fields)
        # set the password to user
        user.set_password(password)
        # save the user (specify the database using self._db)
        user.save(using=self._db)
        return user
    

    # create superuser using email & password
    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)





class User(AbstractBaseUser, PermissionsMixin):
    # A) when extending AbstractBaseUser you should explicitly define: 
    # 1- all fields including is_active & is_staff
    # 2- USERNAME_FIELD = ''
    # 3- REQUIRED_FIELDS = []
    
    # B) you should also extend PermissionsMixin to define:
    # 1- has_perm
    # 2- has_module_perm

    # C) override objects manager to define:
    # 1- create_user
    # 2- create_superuser


    phone_number = models.CharField(unique=True, blank=False, max_length=15)
    email = models.EmailField()
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)   
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    # override objects manager
    objects = CustomUserManager()

    # change username to phone_number to authenticate with phone_number instead of username
    USERNAME_FIELD = 'phone_number'
    # REQUIRED_FIELDS is only used for superusers not normal users
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    # superuser can do anything
    def has_perm(self, perm, obj = None):
        return self.is_superuser
    
    # superuser can see all modules
    def has_module_perms(self, app_label):
        return self.is_superuser


