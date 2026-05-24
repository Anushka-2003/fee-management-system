from django import forms
from .models import Student, AcademicYear, SchoolClass


class AcademicYearForm(forms.ModelForm):
    class Meta:
        model = AcademicYear
        fields = ['name', 'start_date', 'end_date', 'is_current']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'e.g. 2026-2027'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control form-control-lg', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control form-control-lg', 'type': 'date'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ['name', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'e.g. Class 1A'}),
            'order': forms.NumberInput(attrs={'class': 'form-control form-control-lg'}),
        }


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'serial_number', 'name', 'school_class', 'enrollment_type',
            'gender', 'date_of_birth',
            'father_name', 'mother_name', 'date_of_admission', 'is_active',
        ]
        widgets = {
            'serial_number': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'name': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'school_class': forms.Select(attrs={'class': 'form-select form-select-lg'}),
            'enrollment_type': forms.Select(attrs={'class': 'form-select form-select-lg', 'id': 'id_enrollment_type'}),
            'gender': forms.Select(attrs={'class': 'form-select form-select-lg'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control form-control-lg', 'type': 'date'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'date_of_admission': forms.DateInput(attrs={'class': 'form-control form-control-lg', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
