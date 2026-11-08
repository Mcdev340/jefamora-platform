from django.db import models

from apps.clients.validators import validate_client_user
from apps.core.models import UUIDModel


class ClientProfile(UUIDModel):
    user = models.OneToOneField(
        "identity.User",
        verbose_name="compte",
        on_delete=models.PROTECT,
        related_name="client_profile",
    )
    company_name = models.CharField(
        "raison sociale",
        max_length=180,
        blank=True,
        help_text="Renseigné lorsque le client est une entreprise.",
    )

    class Meta:
        verbose_name = "profil client"
        verbose_name_plural = "profils clients"

    def __str__(self):
        return self.company_name or self.user.email

    def clean(self):
        super().clean()
        if self.user_id:
            validate_client_user(self.user)

