from collections import defaultdict
from django.shortcuts import render, get_object_or_404, redirect
from . models import *
from django.db.models import Q
from django.http import JsonResponse
from django.db import IntegrityError, DatabaseError
from django.db.models import Count
from django.utils import timezone
from datetime import datetime, timedelta
import random
import string
from django.core.mail import send_mail
from django.db import transaction, IntegrityError
from django.contrib.auth.models import Group 
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.views.decorators.csrf import csrf_exempt
import json
# Create your views here.

from django.conf import settings
def manifest(request):
    return JsonResponse(settings.PWA_MANIFEST)

def offline(request):
    return render(request, 'offline.html')

def index(request):
    return render(request, 'index.html')


def feed(request):
    posts = Feed.objects.all()
    context = {
        'posts': posts
    }
    return render(request, 'base/feed.html', context)


def add_feed(request):
    try:
        if request.method == 'POST':
            title = request.POST.get('title')
            content = request.POST.get('description')
            images = request.FILES.getlist('images')  # Get list of uploaded files
            
            # Create the feed object
            feed = Feed(author=request.user.instructor, title=title, content=content)
            feed.save()
            
            # Save associated images
            for image in images:
                FeedImage.objects.create(feed=feed, image=image)

            # Prepare success response
            response_data = {
                'success': True,
                'message': 'Feed created successfully!'
            }
        return JsonResponse(response_data)

    except Exception as e:
        # Prepare error response
        response_data = {
            'success': False,
            'message': f'Error creating feed: {str(e)}'
        }
        return JsonResponse(response_data, status=400)


@csrf_exempt
def update_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            event.title = data.get('title', event.title)
            event.description = data.get('description', event.description)
            event.save()
            return JsonResponse({'message': 'Event updated successfully'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'DELETE':
        event.delete()
        return JsonResponse({'message': 'Event deleted successfully'}, status=204)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

def upcoming_events(request):
    # Get the current date
    today = timezone.now().date()
    
    # Define the end date (e.g., 3 months from today)
    end_date = today + timedelta(days=90)

    # Filter events that are happening from today up to the end date
    events = Event.objects.filter(date__range=[today, end_date]).order_by('date')

    # Check if the request is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Prepare the event data
        event_data = [
            {
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'date': event.date.strftime('%Y-%m-%d')  # Format the date as a string
            } for event in events
        ]
        return JsonResponse(event_data, safe=False)

    return render(request, 'base/upcoming_events.html')

def add_event(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        date = request.POST.get('date')

        # Check if an event with the same title and date already exists
        if Event.objects.filter(title=title, date=date).exists():
            return JsonResponse({'status': 'error', 'message': 'Event with the same title and date already exists.'})

        # Create the event since no duplicate was found
        event = Event.objects.create(
            title=title,
            description=description,
            date=date
        )
        event.save()

        # Return success response
        return JsonResponse({'status': 'success', 'message': 'Event added successfully!'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


@login_required
def admin_dashboard(request):
    instructors = Instructor.objects.all()
    students = Student.objects.all()
    guardians = Guardian.objects.all()
    subjects = Subject.objects.all()
    grouped_sections = get_grouped_sections()

    context = {
        'instructors': instructors,
        'students': students,
        'guardians': guardians,
        'subjects': subjects, 
        'grouped_sections': grouped_sections
    }
    return render(request, 'base/admin/dashboard.html', context)

@login_required
def instructor_page(request):
    
    instructors = Instructor.objects.prefetch_related('year_level_sections__subjects').all()

    grouped_sections = get_grouped_sections()
    
    context = {
        'instructors': instructors,
        'grouped_sections': grouped_sections
    }

    return render(request, 'base/admin/instructor.html', context)

@login_required
def instructor_detail(request, instructor_id):


    instructor = Instructor.objects.get(employee_id=instructor_id)

    year_level_sections = instructor.year_level_sections.all().select_related('instructor').prefetch_related('subjects')
    
    context = {
        'instructor': instructor,
        'year_level_sections': year_level_sections,
    }
    return render(request, 'base/admin/instructor_detail.html', context)



# Subject Views
@login_required
def subject_page(request):
    #subjects = Subject.objects.all().prefetch_related('year_level_sections__instructor')
    year_level_section = YearLevelSection.objects.all()
    context = {
       # 'subjects': subjects,
        'year_level_section': year_level_section
    }
    return render(request, 'base/admin/subjects.html', context)


#to revisedef 
@login_required
def add_subject(request):
    if request.method == 'POST':
        try:
            year_section_id = request.POST.get('year_section')
            subject_name = request.POST.get('subject_name')
            day = request.POST.get('day')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            description = request.POST.get('description')

            # Retrieve YearLevelSection instance
            year_section = get_object_or_404(YearLevelSection, id=year_section_id)

            # Normalize the subject name to lowercase for case-insensitive comparison
            normalized_subject_name = subject_name.strip().lower()

            # Check if the subject already exists in the given year level and section
            existing_subject = Subject.objects.filter(
                name__iexact=normalized_subject_name,
                year_level_sections=year_section  # Updated to use the ManyToMany relationship
            ).exists()

            if existing_subject:
                return JsonResponse({'success': False, 'message': 'Subject already exists in the specified year level and section.'})

            # Create and save the new subject
            subject = Subject.objects.create(
                name=subject_name,
                day=day,
                start_time=start_time,
                end_time=end_time,
                description=description,
            )

            # Add the subject to the YearLevelSection
            year_section.subjects.add(subject)  # Add the subject to the ManyToMany relationship

            return JsonResponse({'success': True})

        except IntegrityError as e:
            return JsonResponse({'success': False, 'message': 'Database integrity error: ' + str(e)})

        except Exception as e:
            return JsonResponse({'success': False, 'message': 'An unexpected error occurred: ' + str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method. Only POST requests are allowed.'})
#to revise
@login_required
def update_subject(request):
    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        section_id = request.POST.get('section_id')
        subject_name = request.POST.get('subject_name')
        
        try:
            # Fetch the subject and year level section
            subject = get_object_or_404(Subject, pk=subject_id)
            year_level_section = get_object_or_404(YearLevelSection, pk=section_id)
            
            # Check if there is already a subject with the same name in the section
            existing_subject = year_level_section.subjects.filter(name=subject_name).exclude(id=subject_id).first()
            
            if existing_subject:
                return JsonResponse({"success": False, "error": "A subject with this name already exists in the section"}, status=400)
            
            # Update the subject instance with POST data
            subject.name = subject_name
            subject.day = request.POST.get('day')
            subject.start_time = request.POST.get('start_time')
            subject.end_time = request.POST.get('end_time')
            subject.description = request.POST.get('description')
            subject.save()
            
            # Add the subject to the year level section if not already present
            if subject not in year_level_section.subjects.all():
                year_level_section.subjects.add(subject)
            
            # Return a success response
            return JsonResponse({"success": True, "message": "Subject updated and added to section successfully"})
        except Subject.DoesNotExist:
            return JsonResponse({"success": False, "error": "Subject not found"}, status=404)
        except YearLevelSection.DoesNotExist:
            return JsonResponse({"success": False, "error": "YearLevelSection not found"}, status=404)
        except IntegrityError:
            return JsonResponse({"success": False, "error": "Database integrity error"}, status=500)
        except Exception as e:
            return JsonResponse({"success": False, "error": f"An error occurred: {str(e)}"}, status=500)
    else:
        return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)
    


def get_grouped_sections():
    year_level_sections = YearLevelSection.objects.annotate(student_count=Count('student')).order_by('id', 'section')
    
    # Group sections by year level
    grouped_sections = {}
    for section in year_level_sections:
        year_level = section.year_level
        if year_level not in grouped_sections:
            grouped_sections[year_level] = []
        grouped_sections[year_level].append(section)  

    return grouped_sections



@login_required
def student_page(request):
    students = Student.objects.all()
    
    year_level_section = YearLevelSection.objects.all()

    grouped_sections = get_grouped_sections()
    
    context = {
        'grouped_sections': grouped_sections,
        
        'students': students,
        'year_level_section': year_level_section
    }
    
    return render(request, 'base/admin/students.html', context)


def student_profile(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    guardians = student.guardians.all()  # Get the related guardians

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
    return render(request, 'base/admin/student_profile.html', context)
def add_student(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        student_id = request.POST.get('student_id')
        avatar = request.FILES.get('avatar')  
        gender = request.POST.get('gender')
        age = request.POST.get('age')
        year_level_section_id = request.POST.get('year_level_section')

        try:
            # Validate required fields
            if not firstname or not lastname or not student_id:
                return JsonResponse({'status': 'error', 'message': 'Firstname, lastname, and student ID are required.'}, status=400)

            year_level_section = YearLevelSection.objects.get(id=year_level_section_id)
            
            # Create a new student instance
            student = Student(
                firstname=firstname,
                lastname=lastname,
                student_id=student_id,
                gender=gender,
                age=age,
                year_level_section=year_level_section
            )
            
            # Only set avatar if it exists
            if avatar:
                student.avatar = avatar
            
            student.save()

            return JsonResponse({'status': 'success', 'message': 'Student added successfully!'})

        except YearLevelSection.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Year level section does not exist.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # If it's a GET request, render the form page
    return render(request, 'base/admin/students.html')

@login_required
def section_detail(request, section_slug):
    # Fetch the YearLevelSection object based on the slug
    year_level_section = get_object_or_404(YearLevelSection, slug=section_slug)
    subjects = year_level_section.subjects.all()
    students = year_level_section.student_set.all()
    
    grouped_sections = get_grouped_sections()
    
    context = {
        'year_level_section': year_level_section,
        'subjects': subjects,
        'students': students,
        'grouped_sections': grouped_sections
    }
    return render(request, 'base/admin/sections.html', context)


def add_section(request):
    if request.method == 'POST':
        year_level = request.POST.get('year')
        section = request.POST.get('section')

        # Check if the combination of year_level and section already exists
        if YearLevelSection.objects.filter(year_level=year_level, section=section).exists():
            return JsonResponse({'status': 'error', 'message': f'The section {section} for {year_level} already exists.'}, status=400)

        # Create the YearLevelSection instance
        yls = YearLevelSection.objects.create(
            year_level=year_level,
            section=section
        )

        yls.save()
        print(f"Created YearLevelSection: {yls} with slug: {yls.slug}")


        return JsonResponse({'status': 'success', 'message': f'Successfully added section {section} for {year_level}.', 'slug': yls.slug})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)



def assign_instructor(request):
    if request.method == 'POST':
        section_id = request.POST.get('section_id')
        instructor_id = request.POST.get('instructor_id')

        try:
            # Retrieve the YearLevelSection and Instructor instances
            section = get_object_or_404(YearLevelSection, pk=section_id)
            instructor = get_object_or_404(Instructor, pk=instructor_id)

            # Assign the instructor to the section
            section.instructor = instructor
            section.save()  # Save the changes to the database
            
            return JsonResponse({'success': True})

        except IntegrityError:
            return JsonResponse({'success': False, 'message': 'Database integrity error occurred.'})
        except DatabaseError as e:
            return JsonResponse({'success': False, 'message': 'Database error: ' + str(e)})
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'An unexpected error occurred: ' + str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method. Only POST requests are allowed.'})

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def instructor_autocomplete(request):
    if is_ajax(request):
        term = request.GET.get('term', '')

        results = Instructor.objects.filter(
            Q(user__username__icontains=term) | Q(user__first_name__icontains=term) | Q(user__last_name__icontains=term)
        ).values('user__username', 'user__first_name', 'user__last_name', 'id')
        
        suggestions = [
            {
                'name': f"{result['user__first_name']} {result['user__last_name']}",
                'id': result['id']
            }
            for result in results
        ]

        return JsonResponse(suggestions, safe=False)
    else:
        return JsonResponse({'message': 'Not a valid request'}, status=400, safe=False)






# INSTRUCTORS VIEWS

def generate_password(length=10):
    """Generate a random password with a specified length, no special characters."""
    characters = string.ascii_letters + string.digits  # Letters and digits only
    return ''.join(random.choice(characters) for _ in range(length))

@transaction.atomic
def add_instructor(request):
    if request.method == 'POST':
        try:
            # Fetch form data
            firstname = request.POST.get('firstname')
            lastname = request.POST.get('lastname')
            email = request.POST.get('email')
            employee_id = request.POST.get('employee_id')
            contact_number = request.POST.get('contact_number')
            address = request.POST.get('address')

            # Create a new User instance
            username = employee_id
            password = generate_password()  # Generate password

            # Start atomic transaction
            with transaction.atomic():
                # Create the User and set password
                user = User.objects.create(username=username, email=email, first_name=firstname, last_name=lastname)
                user.set_password(password)
                user.save()

                instructor_group = Group.objects.get(name='instructor')  # Ensure this group exists
                user.groups.add(instructor_group)

                # Create the Instructor
                instructor = Instructor(
                    user=user,
                    employee_id=employee_id,
                    contact_number=contact_number,
                    address=address,
                )
                instructor.save()

            # Send email notification
            send_mail(
                subject='Welcome to ParentLinkED: Your Instructor Account Details',
                message=(
                    f"Dear {firstname} {lastname},\n\n"
                    "Welcome to ParentLinkED! We are pleased to inform you that your instructor account has been successfully created.\n\n"
                    "Here are your account details:\n"
                    f"Username (Employee ID): {employee_id}\n"
                    f"Temporary Password: {password}\n\n"
                    "For security reasons, we recommend that you change your password upon your first login. To change your password, please visit your account settings.\n\n"
                    "If you have any questions or need assistance, feel free to reach out to our support team.\n\n"
                    "Thank you for being a part of the ParentLinkED community!\n\n"
                    "Best regards,\n"
                    "The ParentLinkED Team\n"
                ),
                from_email='noreply@parentlinked.com',
                recipient_list=[user.email],
                fail_silently=False,
            )

            # Success response
            return JsonResponse({'message': 'Instructor added successfully and email sent!'}, status=201)

        except Exception as e:
            # If there's any error, the atomic block will roll back the transaction
            print(f"Error: {e}")
            return JsonResponse({'error': 'An error occurred while adding the instructor. Please try again.'}, status=500)

    # Handle non-POST requests
    return JsonResponse({'error': 'Invalid request method. Please use POST.'}, status=400)

