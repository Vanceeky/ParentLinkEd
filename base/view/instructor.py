

from base.models import Instructor, Subject, YearLevelSection, Student, User, Reminder
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import datetime
from chat.models import ChatGroup



def get_user_chat_groups(user):
    """
    Function to retrieve chat group information for a given user.
    It includes other members, the last message, and whether the last message was sent by the user.
    """
    chat_groups = ChatGroup.objects.filter(is_private=True, members=user)

    groups_info = []
    for group in chat_groups:
        last_message = group.chat_messages.first()  # Get the most recent message
        other_members = group.members.exclude(id=user.id)  # Exclude the current user
        
        # Determine if the last message was sent by the user
        if last_message and last_message.author == user:
            last_message_text = f"You: {last_message.body}"
        else:
            last_message_text = last_message.body if last_message else "No messages yet"

        # Append the group info to the list
        groups_info.append({
            'group': group,
            'other_members': other_members,
            'last_message': last_message_text,
        })

    return groups_info 


@login_required
def instructor_home(request):
    instructor = get_object_or_404(Instructor, user=request.user)
    groups_info = get_user_chat_groups(request.user)  # Calling the reusable function
    
    
    reminders = Reminder.objects.filter(instructor=instructor, is_completed=False, date__lt=datetime.datetime.now())

    year_level_sections = instructor.year_level_sections.all().select_related('instructor').prefetch_related('subjects')
    
    context = {
        'instructor': instructor,
        'year_level_sections': year_level_sections,
        'reminders': reminders,
        'groups_info': groups_info,
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


def add_new_reminder(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        title = request.POST.get('title')
        description = request.POST.get('description')
        date_time = request.POST.get('date_time')

        user = get_object_or_404(User, id=user_id)

        instructor = get_object_or_404(Instructor, user=user_id)


        new_reminder = Reminder(
            title=title,
            description=description,
            date=date_time,
            instructor=instructor
        )

        new_reminder.save()

        return JsonResponse({'success': True})

    return JsonResponse({'success': False})



def student_profile(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    guardians = student.guardians.all()  # Get the related guardians

    context = {
        'student': student,
        'guardians': guardians
    }

    return render(request, 'base/instructor/student_profile.html', context)



