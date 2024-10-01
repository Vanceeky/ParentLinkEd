

from base.models import Instructor, Subject, YearLevelSection, Student
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required






@login_required
def instructor_home(request):
    instructor = get_object_or_404(Instructor, user=request.user)


    year_level_sections = instructor.year_level_sections.all().select_related('instructor').prefetch_related('subjects')
    
    context = {
        'instructor': instructor,
        'year_level_sections': year_level_sections,
    }

    return render(request, 'base/instructor/home.html', context)



def subject_details(request, slug):

    subject = get_object_or_404(Subject, slug=slug)
    #year_level_sections = subject.year_level_sections.all()  # Get related year level sections

    # Get all YearLevelSections that have the subject
    year_level_sections = YearLevelSection.objects.filter(subjects=subject)

    # Prepare a dictionary of students for each year level section
    sections_with_students = []

    # Iterate through each year level section and get the students
    for section in year_level_sections:
        students = section.student_set.all()  # Get all students in this section
        sections_with_students.append((section, students))

    context = {
        'subject': subject,
        'sections_with_students': sections_with_students,  # Pass the list of tuples to the context
    }


    return render(request, 'base/instructor/subject_details.html', context)




def inbox_page(request):
    return render(request, 'base/instructor/inbox.html')


def instructor_students_list(request):
    instructor = get_object_or_404(Instructor, user=request.user)
    year_level_sections = instructor.year_level_sections.all()
    students = Student.objects.filter(year_level_section__in=year_level_sections)

    context = {
        'instructor': instructor,
        'students': students,
    }
    
    return render(request, 'base/instructor/student_list.html', context)

