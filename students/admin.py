from django.contrib import admin
from .models import AcademicYear, SchoolClass, Student


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_current']


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    ordering = ['order']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['serial_number', 'name', 'school_class', 'enrollment_type', 'academic_year', 'is_active']
    list_filter = ['academic_year', 'school_class', 'enrollment_type', 'is_active']
    search_fields = ['name', 'serial_number', 'father_name', 'mother_name']
