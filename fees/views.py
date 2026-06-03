import io
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from students.models import Student, AcademicYear, SchoolClass
from .models import FeeRecord, FeeStructure
from .forms import FeeRecordForm, FeeStructureForm
from .decorators import admin_required


@login_required
def dashboard(request):
    year = AcademicYear.get_current()
    today = date.today()
    month = int(request.GET.get('month', today.month))

    total_students = Student.objects.filter(academic_year=year, is_active=True).count()
    paid_ids = FeeRecord.objects.filter(academic_year=year, month=month).values_list('student_id', flat=True)
    paid_count = len(paid_ids)
    pending_count = total_students - paid_count

    today_collections = FeeRecord.objects.filter(
        academic_year=year, collection_date=today
    ).select_related('student', 'student__school_class')

    total_today = sum(r.total_paid for r in today_collections)
    total_month = sum(
        r.total_paid for r in FeeRecord.objects.filter(academic_year=year, month=month)
    )

    months = FeeRecord.MONTH_CHOICES
    return render(request, 'fees/dashboard.html', {
        'year': year, 'month': month, 'months': months,
        'total_students': total_students, 'paid_count': paid_count,
        'pending_count': pending_count, 'today_collections': today_collections,
        'total_today': total_today, 'total_month': total_month,
    })


@login_required
def fee_entry_select(request):
    year = AcademicYear.get_current()
    students = Student.objects.filter(academic_year=year, is_active=True).select_related('school_class')

    q = request.GET.get('q', '').strip()
    class_filter = request.GET.get('class_id', '')
    serial_filter = request.GET.get('serial', '').strip()
    if q:
        students = students.filter(name__icontains=q)
    if class_filter:
        students = students.filter(school_class_id=class_filter)
    if serial_filter:
        students = students.filter(serial_number=serial_filter)

    classes = SchoolClass.objects.all()
    return render(request, 'fees/fee_entry_select.html', {
        'students': students, 'q': q, 'classes': classes,
        'selected_class': class_filter, 'serial_filter': serial_filter, 'year': year,
    })


@login_required
def fee_entry(request, student_pk):
    student = get_object_or_404(Student, pk=student_pk)
    year = student.academic_year

    # Check if this is the first fee payment in this session (for annual fee logic)
    existing_records = FeeRecord.objects.filter(student=student, academic_year=year).order_by('-month')
    annual_already_paid = existing_records.filter(annual_compulsory__gt=0).exists()
    is_first_payment = student.is_new() and not existing_records.exists()

    # Pre-fill with fee structure defaults
    try:
        structure = FeeStructure.objects.get(academic_year=year, school_class=student.school_class)
        initial = {
            'tuition_fee': structure.tuition_fee,
            'dearness_fee': structure.dearness_fee,
            'miscellaneous_dues': structure.miscellaneous_fee,
            # Annual fee only pre-fills if not yet paid this session
            'annual_compulsory': 0 if annual_already_paid else structure.annual_compulsory,
            'collection_date': date.today(),
        }
    except FeeStructure.DoesNotExist:
        initial = {
            'annual_compulsory': 0 if annual_already_paid else 0,
            'collection_date': date.today(),
        }

    form = FeeRecordForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        record = form.save(commit=False)
        record.student = student
        record.academic_year = year
        record.collected_by = request.user
        record.save()
        messages.success(request, f'Fee recorded. Receipt: {record.receipt_number}')
        return redirect('fees:receipt_html', pk=record.pk)

    return render(request, 'fees/fee_entry.html', {
        'form': form, 'student': student, 'year': year,
        'existing_records': existing_records,
        'is_new_student': student.is_new(),
        'is_first_payment': is_first_payment,
        'annual_already_paid': annual_already_paid,
    })


@login_required
def fee_record_detail(request, pk):
    record = get_object_or_404(FeeRecord, pk=pk)
    return render(request, 'fees/record_detail.html', {'record': record})


@login_required
def receipt_html(request, pk):
    record = get_object_or_404(FeeRecord, pk=pk)
    return render(request, 'fees/receipt.html', {
        'record': record,
        'copy_labels': ['School Copy', "Parent's Copy"],
    })


@login_required
def receipt_pdf(request, pk):
    record = get_object_or_404(FeeRecord, pk=pk)
    html_string = render_to_string('fees/receipt.html', {
        'record': record, 'pdf_mode': True,
        'copy_labels': ['School Copy', "Parent's Copy"],
    })
    buffer = io.BytesIO()
    pisa.CreatePDF(html_string, dest=buffer)
    pdf = buffer.getvalue()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="receipt-{record.receipt_number}.pdf"'
    return response


@login_required
def monthly_report(request):
    year = AcademicYear.get_current()
    today = date.today()
    month = int(request.GET.get('month', today.month))
    year_id = request.GET.get('year_id', '')
    if year_id:
        year = get_object_or_404(AcademicYear, pk=year_id)

    records = FeeRecord.objects.filter(
        academic_year=year, month=month
    ).select_related('student', 'student__school_class', 'collected_by').order_by(
        'student__school_class__order', 'student__serial_number'
    )
    total = sum(r.total_paid for r in records)
    total_tuition = sum(r.tuition_fee for r in records)
    total_dearness = sum(r.dearness_fee for r in records)
    total_misc = sum(r.miscellaneous_dues for r in records)
    total_annual = sum(r.annual_compulsory for r in records)
    total_registration = sum(r.registration_fee for r in records)
    total_admission = sum(r.admission_fee for r in records)
    all_years = AcademicYear.objects.all()
    return render(request, 'fees/monthly_report.html', {
        'records': records, 'month': month, 'year': year,
        'total': total,
        'total_tuition': total_tuition, 'total_dearness': total_dearness,
        'total_misc': total_misc, 'total_annual': total_annual,
        'total_registration': total_registration, 'total_admission': total_admission,
        'all_years': all_years,
        'months': FeeRecord.MONTH_CHOICES,
    })


@login_required
def total_collection(request):
    year = AcademicYear.get_current()
    year_id = request.GET.get('year_id', '')
    if year_id:
        year = get_object_or_404(AcademicYear, pk=year_id)

    selected_months = request.GET.getlist('months')
    selected_months = [int(m) for m in selected_months if m.isdigit()]
    generated = 'months' in request.GET

    records = list(FeeRecord.objects.filter(
        academic_year=year, month__in=selected_months
    ))

    totals = {
        'tuition':      sum(r.tuition_fee for r in records),
        'dearness':     sum(r.dearness_fee for r in records),
        'misc':         sum(r.miscellaneous_dues for r in records),
        'annual':       sum(r.annual_compulsory for r in records),
        'registration': sum(r.registration_fee for r in records),
        'admission':    sum(r.admission_fee for r in records),
    }
    totals['grand'] = sum(totals.values())

    # Per-month breakdown
    month_name_map = dict(FeeRecord.MONTH_CHOICES)
    month_breakdown = []
    for m in selected_months:
        month_records = [r for r in records if r.month == m]
        if not month_records:
            continue
        month_total = sum(r.total_paid for r in month_records)
        month_breakdown.append({
            'name': month_name_map.get(m, str(m)),
            'count': len(month_records),
            'tuition':      sum(r.tuition_fee for r in month_records),
            'dearness':     sum(r.dearness_fee for r in month_records),
            'misc':         sum(r.miscellaneous_dues for r in month_records),
            'annual':       sum(r.annual_compulsory for r in month_records),
            'registration': sum(r.registration_fee for r in month_records),
            'admission':    sum(r.admission_fee for r in month_records),
            'total':        month_total,
        })

    all_years = AcademicYear.objects.all()
    return render(request, 'fees/total_collection.html', {
        'year': year,
        'all_years': all_years,
        'selected_months': selected_months,
        'months': FeeRecord.MONTH_CHOICES,
        'totals': totals,
        'record_count': len(records),
        'month_breakdown': month_breakdown,
        'generated': generated,
    })


@login_required
def defaulters(request):
    year = AcademicYear.get_current()
    today = date.today()
    month = int(request.GET.get('month', today.month))
    class_filter = request.GET.get('class_id', '')

    paid_ids = FeeRecord.objects.filter(
        academic_year=year, month=month
    ).values_list('student_id', flat=True)

    defaulter_qs = Student.objects.filter(
        academic_year=year, is_active=True
    ).exclude(pk__in=paid_ids).select_related('school_class')

    if class_filter:
        defaulter_qs = defaulter_qs.filter(school_class_id=class_filter)

    classes = SchoolClass.objects.all()
    return render(request, 'fees/defaulters.html', {
        'defaulters': defaulter_qs, 'month': month, 'year': year,
        'months': FeeRecord.MONTH_CHOICES, 'classes': classes,
        'selected_class': class_filter,
    })


@login_required
@admin_required
def fee_structure_list(request):
    year = AcademicYear.get_current()
    year_id = request.GET.get('year_id', '')
    if year_id:
        year = get_object_or_404(AcademicYear, pk=year_id)

    classes = SchoolClass.objects.all()
    structures = {s.school_class_id: s for s in FeeStructure.objects.filter(academic_year=year)}
    all_years = AcademicYear.objects.all()
    return render(request, 'fees/structure_list.html', {
        'classes': classes, 'structures': structures, 'year': year, 'all_years': all_years,
    })


@login_required
@admin_required
def fee_structure_edit(request, year_pk, class_pk):
    year = get_object_or_404(AcademicYear, pk=year_pk)
    school_class = get_object_or_404(SchoolClass, pk=class_pk)
    instance, _ = FeeStructure.objects.get_or_create(academic_year=year, school_class=school_class)
    form = FeeStructureForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Fee structure for {school_class} updated.')
        return redirect('fees:structure_list')
    return render(request, 'fees/structure_edit.html', {
        'form': form, 'year': year, 'school_class': school_class,
    })


def api_fee_structure(request):
    """JSON endpoint: returns fee structure for a class+year (used by fee entry JS)."""
    year_id = request.GET.get('year_id')
    class_id = request.GET.get('class_id')
    try:
        structure = FeeStructure.objects.get(academic_year_id=year_id, school_class_id=class_id)
        data = {
            'tuition_fee': str(structure.tuition_fee),
            'dearness_fee': str(structure.dearness_fee),
            'annual_compulsory': str(structure.annual_compulsory),
        }
    except FeeStructure.DoesNotExist:
        data = {}
    return JsonResponse(data)
