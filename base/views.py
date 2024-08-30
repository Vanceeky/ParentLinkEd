from collections import defaultdict
from django.shortcuts import render
from . models import *
# Create your views here.

def admin_dashboard(request):
    return render(request, 'base/admin/dashboard.html')


def instructor_page(request):
    return render(request, 'base/admin/instructor.html')

def subject_page(request):
    subjects = Subject.objects.all().prefetch_related('instructor')


    context = {
        'subjects': subjects
    }
    return render(request, 'base/admin/subjects.html', context)







def student_page(request):
    # Fetch all year levels and sections
    year_level_sections = YearLevelSection.objects.all().order_by('year_level', 'section')
    grouped_sections = {}
    for section in year_level_sections:
        year_level = section.year_level
        if year_level not in grouped_sections:
            grouped_sections[year_level] = []
        grouped_sections[year_level].append(section.section)

    context = {'grouped_sections': grouped_sections}
    
    return render(request, 'base/admin/students.html', context)


def section_tab(request):
    return render('base/admin/section_tab.html')

def view_section(request):

    context = {
        'section': section_tab,
    }    
    return render(request, 'base/admin/sections.html', context)





