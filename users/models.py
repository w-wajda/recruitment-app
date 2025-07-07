from django.db import models
from django.utils import timezone


class Subscriber(models.Model):
    create_date = models.DateTimeField(default=timezone.now)
    email = models.EmailField(unique=True, max_length=255)
    gdpr_consent = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Subscriber"
        verbose_name_plural = "Subscribers"

    def __str__(self):
        return self.email


class SubscriberSMS(models.Model):
    create_date = models.DateTimeField(default=timezone.now)
    phone = models.CharField(unique=True, max_length=20)
    gdpr_consent = models.BooleanField(default=False)

    class Meta:
        verbose_name = "SMS Subscriber"
        verbose_name_plural = "SMS Subscribers"

    def __str__(self):
        return self.phone


class Client(models.Model):
    create_date = models.DateTimeField(default=timezone.now)
    email = models.EmailField(unique=True, max_length=255)
    phone = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return f"{self.email} ({self.phone or 'No Phone'})"


class User(models.Model):
    create_date = models.DateTimeField(default=timezone.now)
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    gdpr_consent = models.BooleanField(default=False)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"User: {self.email or 'N/A'} / {self.phone or 'N/A'}"
