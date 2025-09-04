from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models



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

    # change username to phone_number to authenticate with phone_number instead of username
    USERNAME_FIELD = 'phone_number'
    # REQUIRED_FIELDS is only used for superusers not normal users
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f'{self.first_name} {self.las}'

    # superuser can do anything
    def has_perm(self, perm, obj = ...):
        return self.is_superuser
    
    # superuser can see all modules
    def has_module_perms(self, app_label):
        return self.is_superuser


