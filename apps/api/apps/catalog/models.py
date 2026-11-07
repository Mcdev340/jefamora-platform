from django.db import models
from django.utils.text import slugify

from apps.core.models import UUIDModel


def fill_slug(instance):
    if not instance.slug and instance.name:
        instance.slug = slugify(instance.name)


class Category(UUIDModel):
    name = models.CharField("nom", max_length=150, unique=True)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    is_active = models.BooleanField("active", default=True)

    class Meta:
        verbose_name = "catégorie"
        verbose_name_plural = "catégories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def prepare_save(self):
        fill_slug(self)


class Trade(UUIDModel):
    """Métier du catalogue. Les services et les réalisations pointent ici."""

    category = models.ForeignKey(
        Category,
        verbose_name="catégorie",
        on_delete=models.PROTECT,
        related_name="trades",
    )
    name = models.CharField("nom", max_length=150)
    slug = models.SlugField(max_length=180, blank=True)
    is_active = models.BooleanField("actif", default=True)

    class Meta:
        verbose_name = "métier"
        verbose_name_plural = "métiers"
        ordering = ["category__name", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["category", "name"],
                name="unique_trade_name_per_category",
            ),
            models.UniqueConstraint(
                fields=["category", "slug"],
                name="unique_trade_slug_per_category",
            ),
        ]

    def __str__(self):
        return self.name

    def prepare_save(self):
        fill_slug(self)


class Specialty(UUIDModel):
    trade = models.ForeignKey(
        Trade,
        verbose_name="métier",
        on_delete=models.PROTECT,
        related_name="specialties",
    )
    name = models.CharField("nom", max_length=150)
    slug = models.SlugField(max_length=180, blank=True)
    is_active = models.BooleanField("active", default=True)

    class Meta:
        verbose_name = "spécialité"
        verbose_name_plural = "spécialités"
        ordering = ["trade__name", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["trade", "name"],
                name="unique_specialty_name_per_trade",
            ),
            models.UniqueConstraint(
                fields=["trade", "slug"],
                name="unique_specialty_slug_per_trade",
            ),
        ]

    def __str__(self):
        return self.name

    def prepare_save(self):
        fill_slug(self)
