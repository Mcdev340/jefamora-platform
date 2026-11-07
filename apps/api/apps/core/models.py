import uuid

from django.db import models


class UUIDModel(models.Model):
    """Identifiant public UUID et dates communes.

    `prepare_save` aligne les champs dérivés avant le contrôle.
    `full_clean` refuse un enregistrement qui casse une règle métier.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def prepare_save(self):
        return None

    def after_save(self):
        return None

    def save(self, *args, **kwargs):
        if self.id is None:
            self.id = uuid.uuid4()
        self.prepare_save()
        self.full_clean()
        super().save(*args, **kwargs)
        self.after_save()
