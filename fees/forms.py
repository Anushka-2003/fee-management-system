from django import forms
from .models import FeeRecord, FeeStructure
from students.models import SchoolClass, AcademicYear


class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ['tuition_fee', 'dearness_fee', 'miscellaneous_fee', 'annual_compulsory']
        widgets = {
            'tuition_fee': forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'step': '0.01'}),
            'dearness_fee': forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'step': '0.01'}),
            'miscellaneous_fee': forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'step': '0.01'}),
            'annual_compulsory': forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'step': '0.01'}),
        }


class FeeRecordForm(forms.ModelForm):
    class Meta:
        model = FeeRecord
        fields = [
            'month', 'tuition_fee', 'dearness_fee', 'registration_fee',
            'miscellaneous_dues', 'admission_fee', 'annual_compulsory',
            'total_paid', 'collection_date', 'payment_mode', 'cheque_number',
        ]
        widgets = {
            'month': forms.Select(attrs={'class': 'form-select form-select-lg'}),
            'tuition_fee': forms.NumberInput(attrs={'class': 'form-control form-control-lg fee-field', 'step': '0.01', 'min': '0'}),
            'dearness_fee': forms.NumberInput(attrs={'class': 'form-control form-control-lg fee-field', 'step': '0.01', 'min': '0'}),
            'registration_fee': forms.NumberInput(attrs={'class': 'form-control form-control-lg fee-field', 'step': '0.01', 'min': '0'}),
            'miscellaneous_dues': forms.NumberInput(attrs={'class': 'form-control form-control-lg fee-field', 'step': '0.01', 'min': '0'}),
            'admission_fee': forms.NumberInput(attrs={'class': 'form-control form-control-lg fee-field', 'step': '0.01', 'min': '0'}),
            'annual_compulsory': forms.NumberInput(attrs={'class': 'form-control form-control-lg fee-field', 'step': '0.01', 'min': '0'}),
            'total_paid': forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'step': '0.01', 'readonly': 'readonly', 'id': 'id_total_paid'}),
            'collection_date': forms.DateInput(attrs={'class': 'form-control form-control-lg', 'type': 'date'}),
            'payment_mode': forms.Select(attrs={'class': 'form-select form-select-lg', 'id': 'id_payment_mode'}),
            'cheque_number': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Cheque number'}),
        }

    def clean(self):
        cleaned = super().clean()
        mode = cleaned.get('payment_mode')
        cheque = cleaned.get('cheque_number', '').strip()
        if mode == FeeRecord.PAYMENT_CHEQUE and not cheque:
            self.add_error('cheque_number', 'Cheque number is required when payment mode is Cheque.')
        return cleaned
