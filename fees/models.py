from django.db import models
from students.models import Student, SchoolClass, AcademicYear
from accounts.models import CustomUser


class FeeStructure(models.Model):
    """Default fee amounts set by Admin per class per academic year."""
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='fee_structures')
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='fee_structures')
    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    dearness_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    miscellaneous_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    annual_compulsory = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = [('academic_year', 'school_class')]

    def __str__(self):
        return f"{self.school_class} | {self.academic_year}"


class FeeRecord(models.Model):
    MONTH_CHOICES = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December'),
    ]
    PAYMENT_CASH = 'cash'
    PAYMENT_CHEQUE = 'cheque'
    PAYMENT_UPI = 'upi'
    PAYMENT_BANK = 'bank'
    PAYMENT_CHOICES = [
        (PAYMENT_CASH, 'Cash'),
        (PAYMENT_CHEQUE, 'Cheque'),
        (PAYMENT_UPI, 'UPI'),
        (PAYMENT_BANK, 'Bank Transfer'),
    ]

    RECEIVER_SANGEETA = 'sangeeta'
    RECEIVER_NEELAM = 'neelam'
    RECEIVER_OTHER = 'other'
    RECEIVER_CHOICES = [
        (RECEIVER_SANGEETA, 'Mrs. Sangeeta Sahu (Treasurer, SMWS)'),
        (RECEIVER_NEELAM, 'Mrs. Neelam Gupta (Sr. Teacher)'),
        (RECEIVER_OTHER, 'Other'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_records')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name='fee_records')
    month = models.PositiveSmallIntegerField(choices=MONTH_CHOICES)

    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    dearness_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='New students only')
    miscellaneous_dues = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    admission_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='New students only')
    annual_compulsory = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    total_paid = models.DecimalField(max_digits=10, decimal_places=2)
    collection_date = models.DateField()
    payment_mode = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default=PAYMENT_CASH)
    cheque_number = models.CharField(max_length=30, blank=True, default='')
    collected_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='collected_fees')
    received_by = models.CharField(max_length=20, choices=RECEIVER_CHOICES, default=RECEIVER_SANGEETA)
    received_by_other = models.CharField(max_length=100, blank=True, default='')
    receipt_number = models.CharField(max_length=30, unique=True, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('student', 'academic_year', 'month')]
        ordering = ['-collection_date']

    def __str__(self):
        return f"{self.receipt_number} | {self.student.name} | {self.get_month_display()}"

    @property
    def receiver_name(self):
        if self.received_by == self.RECEIVER_OTHER:
            return self.received_by_other or 'Other'
        return self.get_received_by_display()

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            year_tag = self.academic_year.name.replace('-', '')[2:]  # "2627"
            month_tag = str(self.month).zfill(2)
            prefix = f"REC-{year_tag}-{month_tag}-"
            last = FeeRecord.objects.filter(receipt_number__startswith=prefix).order_by('receipt_number').last()
            if last:
                last_num = int(last.receipt_number.split('-')[-1])
                self.receipt_number = f"{prefix}{str(last_num + 1).zfill(3)}"
            else:
                self.receipt_number = f"{prefix}001"
        super().save(*args, **kwargs)
