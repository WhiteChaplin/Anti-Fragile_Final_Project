from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import random
import uuid

class MyAccountManager(BaseUserManager):
    # 일반 user 생성, username 이 userID를 의미함
    def create_user(self, email, username, password, birth_date):
        if not email:
            raise ValueError("Users must have an email address.")
        if not username:
            raise ValueError("Users must have an name.")
        if not password:
            raise ValueError("Users must have an password")
        user = self.model(
            email = self.normalize_email(email),
            username = username,
            birth_date = birth_date
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    # 관리자 User 생성
    def create_superuser(self, email, username, password):
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            password=password,
            birth_date=None
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


# Create your models here.
class Account(AbstractBaseUser): 
    uid = models.UUIDField(verbose_name="uid", primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    username = models.CharField(verbose_name = 'name',max_length=40, null=False, blank=False, unique=True)
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="회원가입 날짜")
    birth_date = models.DateField(null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    

    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    object = MyAccountManager()
    
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    
    def has_module_perms(self, app_label):
        return True
    
    class Meta:
        db_table = "users"
        verbose_name = "user"
        verbose_name_plural = "Acoount_user"
    