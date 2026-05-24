from django.contrib import admin
from .models import FeeStructure, FeeRecord


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ['school_class', 'academic_year', 'tuition_fee', 'dearness_fee', 'annual_compulsory']
    list_filter = ['academic_year', 'school_class']


@admin.register(FeeRecord)
class FeeRecordAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'student', 'month', 'academic_year', 'total_paid', 'payment_mode', 'collection_date']
    list_filter = ['academic_year', 'month', 'payment_mode', 'student__school_class']
    search_fields = ['receipt_number', 'student__name', 'student__serial_number']
    readonly_fields = ['receipt_number']
