from django.db import models, transaction

# Create your models here.
# from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.core.validators import MinValueValidator
from accounts.models import UserAddress

User = settings.AUTH_USER_MODEL


class Refill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(UserAddress, on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=9,
        validators=[
            MinValueValidator(float('10.00'))
        ]
    )
    date_deposited = models.DateTimeField(auto_now_add=True)
    current_balance = models.DecimalField(
        null=True,
        blank=True,
        decimal_places=2,
        max_digits=9,
        validators=[MinValueValidator(float('10.00'))])
    previous_balance = models.DecimalField(
        null=True,
        blank=True,
        decimal_places=2,
        max_digits=9,
        validators=[
            MinValueValidator(float('10.00'))
        ]
    )

    def __str__(self):
        return f'{self.user} Refill {self.pk}'

    def get_absolute_url(self):
        return reverse('bank:refill')

    def save(self, *args, **kwargs):
        with transaction.atomic():
            balance = self.user.user_balance.get()
            self.previous_balance = balance.balance
            balance.balance += self.amount
            self.current_balance = balance.balance
            balance.save(force_update=True)
            super().save(*args, **kwargs)

    class Meta:
        ordering = ['-date_deposited']
        # unique_together = ['user', 'message']


class CashCall(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(UserAddress, on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=9,
        validators=[
            MinValueValidator(float('10.00'))
        ]
    )
    date_deposited = models.DateTimeField(auto_now_add=True)
    current_balance = models.DecimalField(
        null=True,
        blank=True,
        decimal_places=2,
        max_digits=9,
        validators=[MinValueValidator(float('10.00'))])
    previous_balance = models.DecimalField(
        null=True,
        blank=True,
        decimal_places=2,
        max_digits=9,
        validators=[MinValueValidator(float('10.00'))])

    def __str__(self):
        return f'{self.user} Cash Call {self.pk}'

    def get_absolute_url(self):
        return reverse('bank:cash_call')

    def save(self, *args, **kwargs):
        with transaction.atomic():
            balance = self.user.user_balance.get()
            self.previous_balance = balance.balance
            balance.balance -= self.amount
            balance.update()
            self.current_balance = balance.balance
            super().save(*args, **kwargs)

    class Meta:
        ordering = ['-date_deposited']
