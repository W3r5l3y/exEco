from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.conf import settings


class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        if not email:
            raise ValueError("The Email field must not be empty")
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None):
        user = self.create_user(email, first_name, last_name, password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


class UserPoints(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True
    )
    bingame_points = models.IntegerField(default=0)
    qrscanner_points = models.IntegerField(default=0)
    transport_points = models.IntegerField(default=0)

    @property
    def total_points(self):
        return self.bingame_points + self.qrscanner_points + self.transport_points

    def add_points(self, points=1, category="bingame"):
        # Check if the users points wont go below 0. If they do return False. If true perform the add and return true.
        if category == "bingame" and self.bingame_points + points >= 0:
            self.bingame_points += points
        elif category == "qr" and self.qrscanner_points + points >= 0:
            self.qrscanner_points += points
        elif category == "transport" and self.transport_points + points >= 0:
            self.transport_points += points
        else:
            return False
        
        self.save()
        return True 
    
    def __str__(self):
        # Example: "john@example.com - Total: 20 (bingame=5, qr=10, transport=5)"
        return (
            f"{self.user.id} - Total: {self.total_points} "
            f"(bingame={self.bingame_points}, "
            f"qr={self.qrscanner_points}, "
            f"transport={self.transport_points})"
        )

    def add_bingame_points(self, points=1):
        self.bingame_points += points
        self.save()

    def add_qrscanner_points(self, points=1):
        self.qrscanner_points += points
        self.save()

    def add_transport_points(self, points=1):
        self.transport_points += points
        self.save()
        
class UserCoins(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True
    )
    coins = models.IntegerField(default=0)

    def add_coins(self, coins=1):
        self.coins += coins
        self.save()

    def spend_coins(self, coins=1):
        if self.coins >= coins:
            self.coins -= coins
            self.save()
            return True
        return False

    def __str__(self):
        return f"{self.user.id} - {self.coins} coins"
