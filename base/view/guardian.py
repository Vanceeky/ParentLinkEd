from django.shortcuts import render, get_object_or_404, redirect
from base.models import Guardian, Student, Attendance, Grade, Announcement

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.db.models import Q

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

@csrf_exempt  # Only use @csrf_exempt if you are not using CSRF tokens via headers
def update_avatar(request, student_id):
    if request.method == 'POST':
        try:
            avatar = request.FILES.get('avatar')
            if not avatar:
                return JsonResponse({'success': False, 'error': 'No avatar provided'}, status=400)

            student = Student.objects.get(id=student_id)
            student.avatar = avatar
            student.save()
            
            return JsonResponse({'success': True})
        except Student.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Student not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


def guardian_profile(request):
    guardian = get_object_or_404(Guardian, user=request.user)

    context = {
        'guardian': guardian
    }

    return render(request, 'base/guardian/profile.html', context)


def update_guardian(request):
    if request.method == 'POST':
        try:
            guardian_id = request.POST.get('guardian_id')
            email = request.POST.get('email')
            contact_number = request.POST.get('contact_number')
            address = request.POST.get('address')
            avatar = request.FILES.get('avatar')

       
            acc = Guardian.objects.get(id=guardian_id)

        
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
            return JsonResponse({'success': False, 'error': 'Guardian not found'}, status=404)
        except IntegrityError:
            return JsonResponse({'success': False, 'error': 'Failed to update profile due to database error'}, status=500)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)




def guardian_announcements(request):
    guardian = Guardian.objects.get(user=request.user)  # Get the logged-in guardian
    students = guardian.student.all()  # Get the students associated with this guardian

    # Fetch announcements for all students or selected students of this guardian
    announcements = Announcement.objects.filter(
        Q(all_students=True) | Q(selected_students__in=students)
    ).distinct()
    
    context = {
        'announcements': announcements,
        'students': students,
    }
    return render(request, 'base/guardian/announcements.html', context)