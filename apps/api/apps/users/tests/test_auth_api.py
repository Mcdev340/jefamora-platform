from django.core import mail
from django.test import TestCase
from rest_framework.test import APIClient


class AuthApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def _register(self, email="awa@example.com", role="client", **extra):
        payload = {
            "email": email,
            "password": "Phrase-solide-2026",
            "first_name": "Awa",
            "last_name": "Diop",
            "role": role,
            "accept_terms": True,
        }
        payload.update(extra)
        return self.client.post("/api/v1/users/register/", payload, format="json")

    def test_register_requires_terms(self):
        response = self.client.post(
            "/api/v1/users/register/",
            {
                "email": "awa@example.com",
                "password": "Phrase-solide-2026",
                "role": "client",
                "accept_terms": False,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["code"], "consent_required")

    def test_login_waits_for_email_verification(self):
        with self.captureOnCommitCallbacks(execute=True):
            created = self._register()
        self.assertEqual(created.status_code, 201)
        self.assertEqual(len(mail.outbox), 1)
        code = mail.outbox[0].body.split("Votre code de vérification Jefamora :")[1].split()[0]

        blocked = self.client.post(
            "/api/v1/users/login/",
            {"email": "awa@example.com", "password": "Phrase-solide-2026"},
            format="json",
        )
        self.assertEqual(blocked.status_code, 403)
        self.assertEqual(blocked.json()["code"], "email_unverified")

        verified = self.client.post(
            "/api/v1/users/verify-email/",
            {"email": "awa@example.com", "code": code},
            format="json",
        )
        self.assertEqual(verified.status_code, 200)
        self.assertIn("access", verified.json())

        me = self.client.get(
            "/api/v1/users/me/",
            HTTP_AUTHORIZATION=f"Bearer {verified.json()['access']}",
        )
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.json()["role"], "client")
        self.assertTrue(me.json()["is_verified"])

    def test_public_registration_cannot_create_a_super_admin(self):
        response = self._register(email="admin@example.com", role="super_admin")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["code"], "validation_error")

    def test_inactive_modules_stay_closed(self):
        response = self.client.get("/api/v1/payments/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["code"], "module_inactive")

    def test_health(self):
        response = self.client.get("/api/v1/core/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
