from datetime import timedelta
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from users.models import Client, Subscriber, SubscriberSMS, User


class MigrateSubscribersTestCase(TestCase):
    def test_migrate_subscribers_creates_users(self):
        Client.objects.create(email="client@example.com", phone="123")
        Subscriber.objects.create(email="client@example.com", gdpr_consent=True)
        Subscriber.objects.create(email="new@example.com", gdpr_consent=False)

        call_command("migrate_subscribers")

        self.assertTrue(
            User.objects.filter(email="client@example.com", phone="123").exists()
        )
        self.assertTrue(User.objects.filter(email="new@example.com").exists())

    @patch("users.management.commands.migrate_subscribers.Command._save_to_csv")
    def test_migrate_subscribers_with_duplicated_phones(self, mock_save_to_csv):
        c1 = Client.objects.create(email="a@example.com", phone="555")
        c2 = Client.objects.create(email="b@example.com", phone="555")
        Subscriber.objects.create(email="a@example.com", gdpr_consent=True)
        Subscriber.objects.create(email="b@example.com", gdpr_consent=True)

        call_command("migrate_subscribers")

        mock_save_to_csv.assert_any_call(
            "clients_with_duplicated_phones.csv",
            ["client_id", "phone"],
            [(c1.id, "555"), (c2.id, "555")],
        )

    @patch("users.management.commands.migrate_subscribers.Command._save_to_csv")
    def test_migrate_subscribers_with_conflicts(self, mock_save_to_csv):
        Client.objects.create(email="c@example.com", phone="999")
        Subscriber.objects.create(email="c@example.com", gdpr_consent=True)
        User.objects.create(email="other@example.com", phone="999")
        Subscriber.objects.create(email="d@example.com", gdpr_consent=True)

        call_command("migrate_subscribers")

        mock_save_to_csv.assert_any_call(
            "subscriber_conflicts.csv",
            ["subscriber_id", "email"],
            [(Subscriber.objects.get(email="c@example.com").id, "c@example.com")],
        )


class MigrateSubscribersSMSTestCase(TestCase):
    def test_migrate_subscribers_sms_creates_users(self):
        Client.objects.create(email="sms@example.com", phone="888")
        SubscriberSMS.objects.create(phone="888", gdpr_consent=True)
        SubscriberSMS.objects.create(phone="777", gdpr_consent=False)

        call_command("migrate_subscribers")

        self.assertTrue(
            User.objects.filter(phone="888", email="sms@example.com").exists()
        )
        self.assertTrue(User.objects.filter(phone="777").exists())

    @patch("users.management.commands.migrate_subscribers.Command._save_to_csv")
    def test_migrate_subscribers_sms_with_conflicts(self, mock_save_to_csv):
        Client.objects.create(email="sms2@example.com", phone="333")
        SubscriberSMS.objects.create(phone="333", gdpr_consent=True)
        User.objects.create(email="sms2@example.com", phone="444")
        SubscriberSMS.objects.create(phone="555", gdpr_consent=True)

        call_command("migrate_subscribers")

        mock_save_to_csv.assert_any_call(
            "subscriber_sms_conflicts.csv",
            ["subscriber_sms_id", "phone"],
            [(SubscriberSMS.objects.get(phone="333").id, "333")],
        )


class MigrateGdprConsentsTestCase(TestCase):
    def test_update_gdpr_consent_from_subscriber(self):
        user = User.objects.create(
            email="a@a.com", phone="123", gdpr_consent=False, create_date=timezone.now()
        )
        Subscriber.objects.create(
            email="a@a.com",
            gdpr_consent=True,
            create_date=timezone.now() + timedelta(days=1),
        )
        SubscriberSMS.objects.create(
            phone="123", gdpr_consent=False, create_date=timezone.now()
        )

        call_command("migrate_gdpr_consents")
        user.refresh_from_db()
        self.assertTrue(user.gdpr_consent)

    def test_update_gdpr_consent_from_subscriber_sms(self):
        user = User.objects.create(
            email="b@b.com", phone="456", gdpr_consent=False, create_date=timezone.now()
        )
        Subscriber.objects.create(
            email="b@b.com", gdpr_consent=False, create_date=timezone.now()
        )
        SubscriberSMS.objects.create(
            phone="456",
            gdpr_consent=True,
            create_date=timezone.now() + timedelta(days=2),
        )

        call_command("migrate_gdpr_consents")
        user.refresh_from_db()
        self.assertTrue(user.gdpr_consent)

    def test_no_update_if_user_is_newest(self):
        user = User.objects.create(
            email="c@c.com",
            phone="789",
            gdpr_consent=False,
            create_date=timezone.now() + timedelta(days=3),
        )
        Subscriber.objects.create(
            email="c@c.com", gdpr_consent=True, create_date=timezone.now()
        )
        SubscriberSMS.objects.create(
            phone="789", gdpr_consent=True, create_date=timezone.now()
        )

        call_command("migrate_gdpr_consents")
        user.refresh_from_db()
        self.assertFalse(user.gdpr_consent)

    def test_update_prefers_newer_of_subscriber_and_sms(self):
        user = User.objects.create(
            email="d@d.com", phone="111", gdpr_consent=False, create_date=timezone.now()
        )
        Subscriber.objects.create(
            email="d@d.com",
            gdpr_consent=True,
            create_date=timezone.now() + timedelta(days=1),
        )
        SubscriberSMS.objects.create(
            phone="111",
            gdpr_consent=False,
            create_date=timezone.now() + timedelta(days=2),
        )

        call_command("migrate_gdpr_consents")
        user.refresh_from_db()
        self.assertFalse(user.gdpr_consent)
