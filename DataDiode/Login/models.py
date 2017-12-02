from django.db import models
from django.contrib.auth.models import (
    UserManager, AbstractUser
)

class UserManager(UserManager):
    def create_user(self, username, password,passWordHashed,isStaff):
        if not username:
            raise ValueError('Users must have a username address')

        user = self.model(
            username=username,
            passWordHashed=passWordHashed,
            is_staff=isStaff,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

class UserReceiver(AbstractUser):
    username = models.CharField(
        verbose_name='username',
        max_length=255,
        unique=True,
    )
    passWordHashed=models.CharField(
        verbose_name='passHashed',
        max_length=255,
        null=True,
    )
    # notice the absence of a "Password field", that's built in.

    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['passWordHashed'] # Email & Password are required by default.