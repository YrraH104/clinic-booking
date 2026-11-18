from datetime import datetime, timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class DoctorSchedule(models.Model):
    """Một khung giờ làm việc của bác sĩ (mỗi dòng = 1 slot có thể đặt)."""

    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Bác sĩ",
        on_delete=models.CASCADE,
        related_name="schedules",
    )
    date = models.DateField("Ngày")
    start_time = models.TimeField("Giờ bắt đầu")
    end_time = models.TimeField("Giờ kết thúc")
    is_active = models.BooleanField("Đang mở đặt", default=True)

    class Meta:
        verbose_name = "Lịch làm việc"
        verbose_name_plural = "Lịch làm việc"
        ordering = ["date", "start_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "date", "start_time"],
                name="appointments_unique_doctor_slot",
            ),
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")),
                name="appointments_slot_end_after_start",
            ),
        ]

    @property
    def start_datetime(self):
        return timezone.make_aware(datetime.combine(self.date, self.start_time))

    def __str__(self):
        return f"{self.doctor} - {self.date} {self.start_time:%H:%M}"


class Appointment(models.Model):
    """Lịch hẹn khám của bệnh nhân."""

    class Status(models.TextChoices):
        PENDING = "pending", "Chờ xác nhận"
        CONFIRMED = "confirmed", "Đã xác nhận"
        CHECKED_IN = "checked_in", "Đã check-in"
        COMPLETED = "completed", "Hoàn thành"
        CANCELLED = "cancelled", "Đã hủy"

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Bệnh nhân",
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    schedule = models.ForeignKey(
        DoctorSchedule,
        verbose_name="Khung giờ",
        on_delete=models.PROTECT,
        related_name="appointments",
    )
    status = models.CharField(
        "Trạng thái",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    reason = models.TextField("Lý do khám", blank=True)
    reminder_sent = models.BooleanField("Đã gửi nhắc lịch", default=False)
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)
    updated_at = models.DateTimeField("Ngày cập nhật", auto_now=True)

    class Meta:
        verbose_name = "Lịch hẹn"
        verbose_name_plural = "Lịch hẹn"
        ordering = ["-created_at"]
        constraints = [
            # Chống trùng lịch: 1 khung giờ chỉ có 1 lịch hẹn chưa bị hủy.
            models.UniqueConstraint(
                fields=["schedule"],
                condition=~models.Q(status="cancelled"),
                name="appointments_one_active_per_slot",
            ),
        ]

    @property
    def doctor(self):
        return self.schedule.doctor

    def can_change(self):
        """Chỉ được đổi/hủy nếu còn ít nhất 2 giờ trước giờ khám."""
        if self.status not in (self.Status.PENDING, self.Status.CONFIRMED):
            return False
        return self.schedule.start_datetime - timezone.now() >= timedelta(hours=2)

    def __str__(self):
        return f"Lịch hẹn #{self.pk} - {self.patient}"