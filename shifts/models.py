from django.db import models
from datetime import datetime, date, timedelta


class Shift(models.Model):
    SHIFT_CHOICES = [
        ("M", "Morning"),
        ("E", "Evening"),
        ("N", "Night"),
    ]

    name = models.CharField(max_length=1, choices=SHIFT_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return self.get_name_display()

    def duration_hours(self):
        start = datetime.combine(date.today(), self.start_time)
        end = datetime.combine(date.today(), self.end_time)

        # Cross-midnight safe
        if end <= start:
            end += timedelta(days=1)

        return round((end - start).total_seconds() / 3600, 2)
