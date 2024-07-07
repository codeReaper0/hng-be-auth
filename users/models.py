from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid


class UserManager(BaseUserManager):
    def create_user(self, email, firstName, lastName, password, phone=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not firstName:
            raise ValueError('Users must have a first name')
        if not lastName:
            raise ValueError('Users must have a last name')
        if not password:
            raise ValueError('Password required')

        user = self.model(
            email=self.normalize_email(email),
            firstName=firstName,
            lastName=lastName,
            phone=phone,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, firstName, lastName, password, phone):
        user = self.create_user(
            email,
            firstName,
            lastName,
            password=password,
            phone=phone,
        )
        user.isAdmin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    userId = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    firstName = models.CharField(max_length=30)
    lastName = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    isActive = models.BooleanField(default=True)
    isAdmin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstName', 'lastName', 'password']

    def __str__(self):
        return f"{self.email}"

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return f"{self.isAdmin}"


class Organisation(models.Model):
    orgId = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    users = models.ManyToManyField(User, related_name='organisations')

    def __str__(self):
        return f"{self.name}"
