

from base.models import Instructor, Subject, YearLevelSection, Student, User, Reminder, Announcement, Attendance, Grade
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
import datetime
from chat.models import ChatGroup
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError


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

        if not last_message:
            continue
        
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


def instructor_subjects(user):

    instructor = get_object_or_404(Instructor, user=user)
    
    year_level_sections = instructor.year_level_sections.all().select_related('instructor').prefetch_related('subjects')

    return year_level_sections


    
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
    groups_info = get_user_chat_groups(request.user)  # Calling the reusable function
    instructor_subjects_ = instructor_subjects(request.user)

    context = {
        'subject': subject,
        'sections_with_students': sections_with_students,
        'announcements': announcements,
        'attendance': attendance,
        'groups_info': groups_info,

        'year_level_sections': instructor_subjects_

    }


    return render(request, 'base/instructor/subject_details.html', context)




def inbox_page(request):
    return render(request, 'base/instructor/inbox.html')


def instructor_students_list(request):
    instructor = get_object_or_404(Instructor, user=request.user)
    year_level_sections = instructor.year_level_sections.all()
    students = Student.objects.filter(year_level_section__in=year_level_sections)
    groups_info = get_user_chat_groups(request.user)  # Calling the reusable function
    instructor_subjects_ = instructor_subjects(request.user)


    context = {
        'instructor': instructor,
        'students': students,
        'groups_info': groups_info,
        'year_level_sections': instructor_subjects_,
    
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

def complete_reminder(request, reminder_id):
    reminder = get_object_or_404(Reminder, id=reminder_id)
    reminder.is_completed = True
    reminder.save()

    return JsonResponse({'success': True})


def student_profile(request, student_id):
   
    student = get_object_or_404(Student, student_id=student_id)
   
    guardians = student.guardians.all()  
    attendance = Attendance.objects.filter(student=student) 


    grades = Grade.objects.filter(student=student).select_related('subject')


    year_level_section = student.year_level_section
    subjects = year_level_section.subjects.all()  
  
    subjects_with_grades = {grade.subject.id for grade in grades}
    subjects_without_grades = subjects.exclude(id__in=subjects_with_grades)
    groups_info = get_user_chat_groups(request.user)  # Calling the reusable function

    context = {
        'student': student,
        'guardians': guardians,
        'attendance': attendance,
        'grades': grades,
        'subjects': subjects,
        'subjects_without_grades': subjects_without_grades,  # Ne 
        'groups_info': groups_info
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


def update_grade(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        subject_id = request.POST.get('subject_id')
        quarter_1 = request.POST.get('1st')
        quarter_2 = request.POST.get('2nd')
        quarter_3 = request.POST.get('3rd')
        quarter_4 = request.POST.get('4th')

        try:
            # Retrieve the Grade instance for the student and subject
            grade = Grade.objects.get(student_id=student_id, subject_id=subject_id)

            # Ensure each quarter is filled sequentially
            if quarter_2 and not grade.quarter_1:
                return JsonResponse({'success': False, 'message': "Please enter a grade for the 1st Quarter before adding the 2nd Quarter."}, status=400)
            if quarter_3 and not grade.quarter_2:
                return JsonResponse({'success': False, 'message': "Please enter a grade for the 2nd Quarter before adding the 3rd Quarter."}, status=400)
            if quarter_4 and not grade.quarter_3:
                return JsonResponse({'success': False, 'message': "Please enter a grade for the 3rd Quarter before adding the 4th Quarter."}, status=400)

            # Update grades if present in the request
            grade.quarter_1 = float(quarter_1) if quarter_1 else grade.quarter_1
            grade.quarter_2 = float(quarter_2) if quarter_2 else grade.quarter_2
            grade.quarter_3 = float(quarter_3) if quarter_3 else grade.quarter_3
            grade.quarter_4 = float(quarter_4) if quarter_4 else grade.quarter_4
            grade.save()

            return JsonResponse({'success': True, 'message': "Grade updated successfully."})

        except ValueError as ve:
            return JsonResponse({'success': False, 'message': "Invalid grade value: " + str(ve)}, status=400)
        except Grade.DoesNotExist:
            return JsonResponse({'success': False, 'message': "Grade record not found for the specified student and subject."}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': "An error occurred while updating the grade: " + str(e)}, status=500)

    return JsonResponse({'success': False, 'message': "Invalid request method."}, status=400)



def get_user_groups(user):
    groups_with_last_message = []

    # Retrieve all groups where the user is a member
    user_groups = ChatGroup.objects.filter(members=user)

    for group in user_groups:
        # Get the last message for each group
        last_message = group.chat_messages.first()  # Since messages are ordered by "-created_at"

        # If there is no message in the group, skip this group
        if not last_message:
            continue

        # Prepare the message display
        if last_message.author == user:
            message_preview = f"You: {last_message.body[:25]}"  # Show only the first 25 characters with "You:"
        else:
            message_preview = last_message.body[:25]  # Show the first 25 characters of the message

        # If the message is longer than 25 characters, append "..." to indicate truncation
        if len(last_message.body) > 25:
            message_preview += "..."

        # Get the other members in the group (excluding the current user)
        other_members = group.members.exclude(id=user.id)

        # Create a list of other members' names (first and last)
        other_usernames = ', '.join([
            f"{member.first_name} {member.last_name}" for member in other_members
        ])

        # Add group, last message info, and other members' names to the list
        groups_with_last_message.append({
            'group_name': group.group_name,
            'last_message': message_preview,
            'message_time': last_message.created_at,
            'other_members': other_usernames  # Add the names of other users
        })

    return groups_with_last_message





def profile(request):
    acc = Instructor.objects.get(user=request.user)

    groups_info = get_user_chat_groups(request.user)  

    year_level_sections = acc.year_level_sections.all().select_related('instructor').prefetch_related('subjects')

    context = {
        'groups_info': groups_info,
        'acc': acc,
        'year_level_sections': year_level_sections
    }
    return render(request, 'base/instructor/profile.html', context)

def update_profile(request):
    if request.method == 'POST':
        try:
            instructor_id = request.POST.get('instructor')
            email = request.POST.get('email')
            contact_number = request.POST.get('contact_number')
            address = request.POST.get('address')
            avatar = request.FILES.get('avatar')

       
            acc = Instructor.objects.get(id=instructor_id)

        
          # Check for email duplication
            if email and email != acc.user.email:
                if User.objects.filter(email=email).exclude(id=acc.user.id).exists():
                    return JsonResponse({'success': False, 'error': 'Email already exists'}, status=400)

       
            acc.user.email = email if email else acc.user.email
            # Update Instructor fields
            acc.contact_number = contact_number if contact_number else acc.contact_number
            acc.address = address if address else acc.address


           
            if avatar:
                acc.avatar = avatar

            # Save changes
            acc.user.save()
            acc.save()

            return JsonResponse({'success': True})

        except ObjectDoesNotExist:
            return JsonResponse({'success': False, 'error': 'Instructor not found'}, status=404)
        except IntegrityError:
            return JsonResponse({'success': False, 'error': 'Failed to update profile due to database error'}, status=500)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

