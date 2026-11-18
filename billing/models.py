from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Service(models.Model):
    name = models.CharField(
        "Tên dịch vụ",
        max_length=150,
        unique=True,
    )

    description = models.TextField(
        "Mô tả",
        blank=True,
    )

    price = models.DecimalField(
        "Giá dịch vụ (VNĐ)",
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("0"))],
    )

    is_active = models.BooleanField(
        "Đang sử dụng",
        default=True,
    )

    class Meta:
        verbose_name = "Dịch vụ"
        verbose_name_plural = "Dịch vụ"
        ordering = ["name"]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gte=0),
                name="billing_service_price_nonnegative",
            ),
        ]

    def __str__(self):
        return self.name