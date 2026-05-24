from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Student, AcademicYear, SchoolClass
from .forms import StudentForm, AcademicYearForm, SchoolClassForm
from fees.decorators import admin_required


@login_required
def student_list(request):
    year = AcademicYear.get_current()
    students = Student.objects.filter(academic_year=year).select_related('school_class')

    q = request.GET.get('q', '').strip()
    class_filter = request.GET.get('class_id', '')
    if q:
        students = students.filter(name__icontains=q)
    if class_filter:
        students = students.filter(school_class_id=class_filter)

    classes = SchoolClass.objects.all()
    return render(request, 'students/student_list.html', {
        'students': students, 'q': q, 'classes': classes,
        'selected_class': class_filter, 'year': year,
    })


@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    fee_records = student.fee_records.select_related('academic_year').order_by('-academic_year__start_date', '-month')
    return render(request, 'students/student_detail.html', {
        'student': student, 'fee_records': fee_records,
    })


@login_required
def student_add(request):
    year = AcademicYear.get_current()
    form = StudentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        student = form.save(commit=False)
        student.academic_year = year
        student.created_by = request.user
        student.updated_by = request.user
        student.save()
        messages.success(request, f'Student "{student.name}" added. Please record their first fee payment.')
        return redirect('fees:fee_entry', student_pk=student.pk)
    return render(request, 'students/student_form.html', {'form': form, 'title': 'Add Student', 'year': year})


@login_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    form = StudentForm(request.POST or None, instance=student)
    if request.method == 'POST' and form.is_valid():
        student = form.save(commit=False)
        student.updated_by = request.user
        student.save()
        messages.success(request, 'Student updated successfully.')
        return redirect('students:detail', pk=student.pk)
    return render(request, 'students/student_form.html', {
        'form': form, 'title': 'Edit Student', 'obj': student, 'year': student.academic_year,
    })


@login_required
@admin_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        name = student.name
        student.delete()
        messages.success(request, f'Student "{name}" has been deleted.')
        return redirect('students:list')
    return render(request, 'students/student_confirm_delete.html', {'student': student})


# ── Academic Year ──────────────────────────────────────────────────────────────

@login_required
@admin_required
def year_list(request):
    years = AcademicYear.objects.all()
    return render(request, 'students/year_list.html', {'years': years})


@login_required
@admin_required
def year_add(request):
    form = AcademicYearForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Academic year created.')
        return redirect('students:year_list')
    return render(request, 'students/year_form.html', {'form': form, 'title': 'Add Academic Year'})


@login_required
@admin_required
def year_set_current(request, pk):
    year = get_object_or_404(AcademicYear, pk=pk)
    year.is_current = True
    year.save()
    messages.success(request, f'{year.name} is now the current academic year.')
    return redirect('students:year_list')


@login_required
@admin_required
def year_carry_forward(request, pk):
    """Carry all active students from a given year into the current year."""
    source_year = get_object_or_404(AcademicYear, pk=pk)
    current_year = AcademicYear.get_current()
    if source_year == current_year:
        messages.error(request, 'Cannot carry forward from the current year to itself.')
        return redirect('students:year_list')

    if request.method == 'POST':
        carried = 0
        skipped = 0
        for student in source_year.students.filter(is_active=True):
            exists = Student.objects.filter(
                academic_year=current_year, serial_number=student.serial_number
            ).exists()
            if not exists:
                Student.objects.create(
                    academic_year=current_year,
                    serial_number=student.serial_number,
                    name=student.name,
                    school_class=student.school_class,
                    enrollment_type=Student.ENROLL_RE,
                    gender=student.gender,
                    date_of_birth=student.date_of_birth,
                    father_name=student.father_name,
                    mother_name=student.mother_name,
                    date_of_admission=student.date_of_admission,
                    created_by=request.user,
                    updated_by=request.user,
                )
                carried += 1
            else:
                skipped += 1
        messages.success(request, f'Carried forward {carried} students. {skipped} already existed.')
        return redirect('students:year_list')

    return render(request, 'students/year_carry_forward.html', {
        'source_year': source_year, 'current_year': current_year,
    })


# ── School Classes ─────────────────────────────────────────────────────────────

@login_required
@admin_required
def class_list(request):
    classes = SchoolClass.objects.all()
    return render(request, 'students/class_list.html', {'classes': classes})


@login_required
@admin_required
def class_add(request):
    form = SchoolClassForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Class added.')
        return redirect('students:class_list')
    return render(request, 'students/class_form.html', {'form': form, 'title': 'Add Class'})
