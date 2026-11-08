from datetime import time, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.bookings.models import Booking
from apps.catalog.models import Category, Specialty, Trade
from apps.clients.models import ClientProfile
from apps.messaging.models import Conversation, Message
from apps.users.models import User
from apps.locations.models import Zone
from apps.portfolio.models import PortfolioItem
from apps.professionals.models import Availability, ProfessionalProfile, ProfessionalService
from apps.quotes.models import Quote
from apps.quotes.services import QuoteDecisionError, accept_quote
from apps.reviews.models import Review
from apps.service_requests.models import RequestRecipient, ServiceRequest


class MissionRulesTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Bâtiment")
        self.trade = Trade.objects.create(category=self.category, name="Plomberie")
        self.specialty = Specialty.objects.create(trade=self.trade, name="Fuite")
        self.zone = Zone.objects.create(region="Dakar", city="Dakar", district="Plateau")

        self.client_user = User.objects.create_user(
            "awa@example.com",
            "motdepasse123",
            role=User.Role.CLIENT,
            first_name="Awa",
            last_name="Diop",
        )
        self.client = ClientProfile.objects.create(user=self.client_user)
        self.pro_user_a = User.objects.create_user(
            "moussa@example.com",
            "motdepasse123",
            role=User.Role.PROFESSIONAL,
            first_name="Moussa",
        )
        self.pro_user_b = User.objects.create_user(
            "ibrahima@example.com",
            "motdepasse123",
            role=User.Role.PROFESSIONAL,
            first_name="Ibrahima",
        )
        self.pro_a = ProfessionalProfile.objects.create(
            user=self.pro_user_a,
            business_name="Moussa Plomberie",
        )
        self.pro_b = ProfessionalProfile.objects.create(
            user=self.pro_user_b,
            business_name="Ibrahima Services",
        )
        self.pro_a.zones.add(self.zone)
        self.pro_b.zones.add(self.zone)
        ProfessionalService.objects.create(
            profile=self.pro_a,
            trade=self.trade,
            specialty=self.specialty,
            title="Débouchage",
            starting_price=Decimal("15000"),
        )

        self.request = ServiceRequest.objects.create(
            client=self.client,
            zone=self.zone,
            title="Fuite sous l'évier",
            description="L'eau coule depuis hier.",
            status=ServiceRequest.Status.OPEN,
            desired_date=timezone.now() + timedelta(days=2),
        )
        self.recipient_a = RequestRecipient.objects.create(
            service_request=self.request,
            professional=self.pro_a,
            status=RequestRecipient.Status.QUOTED,
        )
        self.recipient_b = RequestRecipient.objects.create(
            service_request=self.request,
            professional=self.pro_b,
            status=RequestRecipient.Status.QUOTED,
        )
        self.quote_a = Quote.objects.create(
            recipient=self.recipient_a,
            total_amount=Decimal("25000"),
            status=Quote.Status.SENT,
            expires_at=timezone.now() + timedelta(days=3),
        )
        self.quote_b = Quote.objects.create(
            recipient=self.recipient_b,
            total_amount=Decimal("30000"),
            status=Quote.Status.SENT,
            expires_at=timezone.now() + timedelta(days=3),
        )

    def test_one_accepted_quote_becomes_the_booking_and_opens_the_chat(self):
        booking = accept_quote(quote=self.quote_a, client_user=self.client_user)

        self.quote_a.refresh_from_db()
        self.quote_b.refresh_from_db()
        self.recipient_a.refresh_from_db()
        self.recipient_b.refresh_from_db()
        self.request.refresh_from_db()

        self.assertEqual(self.quote_a.status, Quote.Status.ACCEPTED)
        self.assertEqual(self.quote_b.status, Quote.Status.REFUSED)
        self.assertEqual(self.recipient_a.status, RequestRecipient.Status.ACCEPTED)
        self.assertEqual(self.recipient_b.status, RequestRecipient.Status.REFUSED)
        self.assertEqual(self.request.status, ServiceRequest.Status.BOOKED)
        self.assertEqual(booking.quote_id, self.quote_a.id)
        self.assertEqual(booking.service_request_id, self.request.id)
        self.assertEqual(booking.client_id, self.client.id)
        self.assertEqual(booking.professional_id, self.pro_a.id)
        self.assertEqual(Booking.objects.count(), 1)
        self.assertTrue(Conversation.objects.filter(booking=booking).exists())

        with self.assertRaises(QuoteDecisionError):
            accept_quote(quote=self.quote_b, client_user=self.client_user)
        self.assertEqual(Booking.objects.count(), 1)

    def test_sent_quote_cannot_become_a_booking_on_its_own(self):
        with self.assertRaises(ValidationError):
            Booking.objects.create(quote=self.quote_a)
        self.assertEqual(Booking.objects.count(), 0)
        self.assertEqual(Conversation.objects.count(), 0)

    def test_service_and_portfolio_must_use_the_catalog(self):
        electricity = Trade.objects.create(category=self.category, name="Électricité")
        panel = Specialty.objects.create(trade=electricity, name="Tableau")

        with self.assertRaises(ValidationError):
            ProfessionalService.objects.create(
                profile=self.pro_a,
                trade=self.trade,
                specialty=panel,
                title="Mauvais rattachement",
            )
        with self.assertRaises(ValidationError):
            PortfolioItem.objects.create(
                profile=self.pro_a,
                trade=self.trade,
                specialty=panel,
                title="Photo trompeuse",
            )

        item = PortfolioItem.objects.create(
            profile=self.pro_a,
            trade=self.trade,
            specialty=self.specialty,
            zone=self.zone,
            title="Salle de bain",
        )
        self.assertEqual(item.trade_id, self.trade.id)
        self.assertEqual(item.zone_id, self.zone.id)

    def test_zones_come_from_one_active_list(self):
        self.assertIn(self.zone, self.pro_a.zones.all())
        self.assertEqual(self.request.zone_id, self.zone.id)

        closed = Zone.objects.create(
            region="Dakar",
            city="Dakar",
            district="Gueule Tapée",
            is_active=False,
        )
        with self.assertRaises(ValidationError):
            self.pro_a.assign_zones([closed])
        self.assertEqual(list(self.pro_a.zones.all()), [self.zone])
        with self.assertRaises(ValidationError):
            ServiceRequest.objects.create(
                client=self.client,
                zone=closed,
                title="Demande hors zone",
                description="Ne doit pas passer.",
                status=ServiceRequest.Status.OPEN,
            )

    def test_one_review_after_the_client_confirms(self):
        booking = accept_quote(quote=self.quote_a, client_user=self.client_user)
        with self.assertRaises(ValidationError):
            Review.objects.create(booking=booking, rating=5, comment="Trop tôt")

        booking.status = Booking.Status.CONFIRMED_BY_CLIENT
        booking.save()
        review = Review.objects.create(booking=booking, rating=5, comment="Travail soigné")

        self.assertEqual(review.author_id, self.client_user.id)
        self.assertGreater(review.editable_until, timezone.now() + timedelta(hours=47))
        self.pro_a.refresh_from_db()
        self.assertEqual(self.pro_a.average_rating, Decimal("5.00"))
        with self.assertRaises(ValidationError):
            Review.objects.create(booking=booking, rating=4, comment="Un second avis")

        Message.objects.create(
            conversation=booking.conversation,
            sender=self.client_user,
            content="Merci",
        )
        outsider = User.objects.create_user(
            "visiteur@example.com",
            "motdepasse123",
            role=User.Role.CLIENT,
        )
        with self.assertRaises(ValidationError):
            Message.objects.create(
                conversation=booking.conversation,
                sender=outsider,
                content="Je m'incruste",
            )

    def test_client_cannot_edit_a_review_after_48_hours(self):
        booking = accept_quote(quote=self.quote_a, client_user=self.client_user)
        booking.status = Booking.Status.CONFIRMED_BY_CLIENT
        booking.save()
        review = Review.objects.create(booking=booking, rating=4, comment="Bien")
        Review.objects.filter(pk=review.pk).update(
            editable_until=timezone.now() - timedelta(hours=1)
        )
        review.refresh_from_db()
        review.comment = "Je change d'avis"
        with self.assertRaises(ValidationError):
            review.save()

        review.refresh_from_db()
        review.professional_reply = "Merci Awa"
        review.save()
        review.refresh_from_db()
        self.assertEqual(review.professional_reply, "Merci Awa")
        self.assertEqual(review.comment, "Bien")

    def test_profile_follows_the_account_role(self):
        with self.assertRaises(ValidationError):
            ClientProfile.objects.create(user=self.pro_user_a)

    def test_availability_must_end_after_it_starts(self):
        with self.assertRaises(ValidationError):
            Availability.objects.create(
                profile=self.pro_a,
                weekday=Availability.Weekday.MONDAY,
                start_time=time(18, 0),
                end_time=time(8, 0),
            )
