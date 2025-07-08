from django.core.management.base import BaseCommand

from users.models import Subscriber, SubscriberSMS, User


class Command(BaseCommand):
    def handle(self, *args, **options):
        for user in User.objects.filter(
            email__isnull=False, phone__isnull=False
        ).iterator(1000):

            subscriber = Subscriber.objects.filter(email=user.email).first()
            subscriber_sms = SubscriberSMS.objects.filter(phone=user.phone).first()

            if (
                subscriber.create_date > user.create_date
                or subscriber_sms.create_date > user.create_date
            ):
                if subscriber.create_date > subscriber_sms.create_date:
                    user.gdpr_consent = subscriber.gdpr_consent
                else:
                    user.gdpr_consent = subscriber_sms.gdpr_consent
                user.save()
