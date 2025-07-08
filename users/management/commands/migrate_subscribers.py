import csv
from typing import Any

from django.core.management.base import BaseCommand

from users.models import Client, Subscriber, SubscriberSMS, User


class Command(BaseCommand):
    help = "Migrate subscribers and subscriber SMS data to User model"

    def handle(self, *args, **options):
        self.migrate_subscribers()
        self.migrate_subscribers_sms()

    def migrate_subscribers(self):
        client_with_duplicated_phones = {}
        subscriber_conflicts = []
        new_users = []

        for subscriber in Subscriber.objects.all().iterator(chunk_size=1000):
            user = User.objects.filter(email=subscriber.email)

            if not user.exists():
                client = Client.objects.filter(email=subscriber.email).first()

                if client:
                    clients_with_same_phone = list(
                        Client.objects.filter(phone=client.phone).values_list(
                            "id", "phone"
                        )
                    )
                    if len(clients_with_same_phone) > 1:
                        client_with_duplicated_phones.update(
                            dict(clients_with_same_phone)
                        )
                        continue

                    existing_user = (
                        User.objects.filter(phone=client.phone)
                        .exclude(email=client.email)
                        .first()
                    )
                    if not existing_user:
                        new_users.append(
                            User(
                                email=subscriber.email,
                                phone=client.phone,
                                gdpr_consent=subscriber.gdpr_consent,
                            )
                        )

                    if existing_user:
                        subscriber_conflicts.append((subscriber.id, subscriber.email))
                else:
                    new_users.append(
                        User(
                            email=subscriber.email, gdpr_consent=subscriber.gdpr_consent
                        )
                    )

        User.objects.bulk_create(new_users, batch_size=1000)

        self._save_to_csv(
            "clients_with_duplicated_phones.csv",
            ["client_id", "phone"],
            list(client_with_duplicated_phones.items()),
        )
        self._save_to_csv(
            "subscriber_conflicts.csv", ["subscriber_id", "email"], subscriber_conflicts
        )

    def migrate_subscribers_sms(self):
        subscriber_sms_conflicts = []
        new_users = []

        for subscriber_sms in SubscriberSMS.objects.all().iterator(chunk_size=1000):
            user = User.objects.filter(phone=subscriber_sms.phone)

            if not user.exists():
                client = Client.objects.filter(phone=subscriber_sms.phone).first()

                if client:
                    existing_user = (
                        User.objects.filter(email=client.email)
                        .exclude(phone=client.phone)
                        .first()
                    )
                    if not existing_user:
                        new_users.append(
                            User(
                                phone=subscriber_sms.phone,
                                email=client.email,
                                gdpr_consent=subscriber_sms.gdpr_consent,
                            )
                        )

                    if existing_user:
                        subscriber_sms_conflicts.append(
                            (subscriber_sms.id, subscriber_sms.phone)
                        )
                else:
                    new_users.append(
                        User(
                            phone=subscriber_sms.phone,
                            gdpr_consent=subscriber_sms.gdpr_consent,
                        )
                    )

        User.objects.bulk_create(new_users, batch_size=100)

        self._save_to_csv(
            "subscriber_sms_conflicts.csv",
            ["subscriber_sms_id", "phone"],
            subscriber_sms_conflicts,
        )

    @staticmethod
    def _save_to_csv(filename: str, header: list[str], data: list[tuple[Any, Any]]):
        with open(filename, "w") as f:
            csvwriter = csv.writer(f)
            csvwriter.writerow(header)

            for row in data:
                csvwriter.writerow(row)
