from django.db import models
from django.conf import settings
from datetime import date


class AcademicYear(models.Model):
    name = models.CharField(max_length=20, unique=True)  # e.g. "2026-2027"
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Only one year can be current at a time
        if self.is_current:
            AcademicYear.objects.exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_current(cls):
        return cls.objects.filter(is_current=True).first()


class SchoolClass(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g. "Class 1", "Class 5A"
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Student(models.Model):
    ENROLL_NEW = 'new'
    ENROLL_RE = 're'
    ENROLL_CHOICES = [
        (ENROLL_NEW, 'New'),
        (ENROLL_RE, 'Re-Enrolment'),
    ]

    GENDER_MALE = 'M'
    GENDER_FEMALE = 'F'
    GENDER_OTHER = 'O'
    GENDER_CHOICES = [
        (GENDER_MALE, 'Male'),
        (GENDER_FEMALE, 'Female'),
        (GENDER_OTHER, 'Other'),
    ]

    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name='students')
    serial_number = models.CharField(max_length=20)
    name = models.CharField(max_length=150)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.PROTECT, related_name='students')
    enrollment_type = models.CharField(max_length=3, choices=ENROLL_CHOICES, default=ENROLL_NEW)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default=GENDER_MALE)
    date_of_birth = models.DateField(null=True, blank=True)
    father_name = models.CharField(max_length=150)
    mother_name = models.CharField(max_length=150)
    date_of_admission = models.DateField()
    is_active = models.BooleanField(default=True)

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='students_created'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='students_updated'
    )

    class Meta:
        ordering = ['school_class__order', 'serial_number']
        unique_together = [('academic_year', 'serial_number')]

    def __str__(self):
        return f"{self.serial_number} - {self.name} ({self.school_class})"

    def is_new(self):
        return self.enrollment_type == self.ENROLL_NEW

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = date.today()
        d = self.date_of_birth
        return today.year - d.year - ((today.month, today.day) < (d.month, d.day))

