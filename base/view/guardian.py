from django.shortcuts import render, get_object_or_404, redirect
from base.models import Guardian, Student, Attendance, Grade


def guardian_home(request):
    guardian = get_object_or_404(Guardian, user=request.user)
    students = guardian.student.all()

    context = {
        'guardian': guardian,
        'students': students
    }


    return render(request, 'base/guardian/home.html', context)


def guardian_student_profile(request, student_id):   
    student = get_object_or_404(Student, student_id=student_id)

    year_level_section = student.year_level_section
    subjects = year_level_section.subjects.all()  
    attendance = Attendance.objects.filter(student=student)
    grades = Grade.objects.filter(student=student).select_related('subject')

    subjects_with_grades = {grade.subject.id for grade in grades}
    subjects_without_grades = subjects.exclude(id__in=subjects_with_grades)

    context = {
        'student': student,
        'attendance': attendance,
        'yls': year_level_section,
        'grades': grades,
        'subjects': subjects,
        'subjects_without_grades': subjects_without_grades,  # Ne 
    }

    return render(request, 'base/guardian/student_profile.html', context)

