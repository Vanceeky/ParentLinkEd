

from base.models import Instructor, Subject, YearLevelSection, Student, User, Reminder, Announcement, Attendance, Grade
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
import datetime
from chat.models import ChatGroup
from django.contrib import messages


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


    announcements = Announcement.objects.filter(subject=subject)

    attendance = Attendance.objects.filter(subject=subject)


    context = {
        'subject': subject,
        'sections_with_students': sections_with_students,
        'announcements': announcements,
        'attendance': attendance
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
   
    guardians = student.guardians.all()  
    attendance = Attendance.objects.filter(student=student) 


    grades = Grade.objects.filter(student=student).select_related('subject')


    year_level_section = student.year_level_section
    subjects = year_level_section.subjects.all()  
  
    subjects_with_grades = {grade.subject.id for grade in grades}
    subjects_without_grades = subjects.exclude(id__in=subjects_with_grades)
  
    context = {
        'student': student,
        'guardians': guardians,
        'attendance': attendance,
        'grades': grades,
        'subjects': subjects,
        'subjects_without_grades': subjects_without_grades,  # Ne 
    }


    return render(request, 'base/instructor/student_profile.html', context)



def create_announcement(request):
    if request.method == "POST":
        subject_id = request.POST.get('subject_id')
        content = request.POST.get('content')
        all_students = request.POST.get('all_students') == 'on'  # Checkbox
        selected_students_ids = request.POST.get('selected_students', '').split(',')

        subject = get_object_or_404(Subject, id=subject_id)

        # Check if content is empty
        if not content.strip():  # Use strip() to check for whitespace
            return JsonResponse({'status': 'error', 'message': 'Announcement cannot be empty.'})

        # Create the announcement
        announcement = Announcement.objects.create(
            subject=subject,
            content=content,
            all_students=all_students,
            instructor=request.user.instructor  # Assuming user is authenticated and has an instructor profile
        )

        # Link selected students
        if not all_students:
            for student_id in selected_students_ids:
                if student_id:
                    student = Student.objects.get(id=student_id)
                    announcement.selected_students.add(student)

        announcement.save()

        return JsonResponse({'status': 'success', 'message': 'Announcement created successfully!'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def record_attendance(request):
    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')  # Assuming you send the subject ID from the modal
        subject = Subject.objects.get(id=subject_id)

        # Loop through the posted attendance data
        for student_id in request.POST:
            if student_id.startswith('student_id_'):
                student_id = student_id.split('_')[2]
                attendance_status = request.POST.get(f'attendance_{student_id}')

                # Create or update attendance record
                Attendance.objects.update_or_create(
                    student_id=student_id,
                    subject=subject,
                    defaults={'status': attendance_status}
                )

        return JsonResponse({'success': True})  # Return success response
    return JsonResponse({'success': False}, status=400)  # Return error response


def add_grade(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        subject_id = request.POST.get('subject_id')
        quarter_1 = request.POST.get('1st')
        quarter_2 = request.POST.get('2nd', None)
        quarter_3 = request.POST.get('3rd', None)
        quarter_4 = request.POST.get('4th', None)

        try:
            if not quarter_1:
                return JsonResponse({'success': False, 'message': "1st Quarter is required."}, status=400)

            # Create a new Grade instance
            grade = Grade(
                student_id=student_id,
                subject_id=subject_id,
                quarter_1=float(quarter_1),  # Convert to float
                quarter_2=float(quarter_2) if quarter_2 else None,
                quarter_3=float(quarter_3) if quarter_3 else None,
                quarter_4=float(quarter_4) if quarter_4 else None,
                school_year="2023-2024"  # Set the school year as needed
            )

            grade.save()
            return JsonResponse({'success': True, 'message': "Grade added successfully."})

        except ValueError as ve:
            return JsonResponse({'success': False, 'message': str(ve)}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': "An error occurred while adding the grade: " + str(e)}, status=500)

    return JsonResponse({'success': False, 'message': "Invalid request method."}, status=400)