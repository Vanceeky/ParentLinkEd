from collections import defaultdict
from django.shortcuts import render, get_object_or_404
from . models import *
from django.db.models import Q
from django.http import JsonResponse
from django.db import IntegrityError, DatabaseError
from django.db.models import Count

import random
import string
from django.core.mail import send_mail
from django.db import transaction
from django.contrib.auth.models import Group 
from django.contrib.auth.decorators import login_required
# Create your views here.


def index(request):
    return render(request, 'base/index.html')


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
    
def upcoming_events(request):
    return render(request, 'base/upcoming_events.html')


@login_required
def admin_dashboard(request):
    instructors = Instructor.objects.all()
    students = Student.objects.all()
    guardians = Guardian.objects.all()
    subjects = Subject.objects.all()
    context = {
        'instructors': instructors,
        'students': students,
        'guardians': guardians,
        'subjects': subjects, 
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
    subjects = Subject.objects.all().prefetch_related('year_level_sections__instructor')
    year_level_section = YearLevelSection.objects.all()
    context = {
        'subjects': subjects,
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
    
    guardians = Guardian.objects.filter(student__in=students).distinct()

    grouped_sections = get_grouped_sections()
    
    context = {
        'grouped_sections': grouped_sections,
        
        'students': students,
        'guardians': guardians
    }
    
    return render(request, 'base/admin/students.html', context)


def student_profile(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    guardians = student.guardians.all()  # Get the related guardians

    context = {
        'student': student,
        'guardians': guardians
    }
    return render(request, 'base/admin/student_profile.html', context)





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