from django.urls import path


from . import views
from django.conf import settings
from django.conf.urls.static import static


from base.view.instructor import *

urlpatterns = [
    path('', views.index, name='index'),


    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),


    path('add-instructor/', views.add_instructor, name='add_instructor'),
    path('instructors/', views.instructor_page, name='instructor_page'),
    path('instructor-info/<str:instructor_id>/', views.instructor_detail, name='instructor_detail'),



    path('subjects/', views.subject_page, name='subject_page'),
    path('add-subject/', views.add_subject, name='add_subject'),
    path('update-subject/', views.update_subject, name='update_subject'),



    path('students/', views.student_page, name='student_page'),
    path('student/profile/<student_id>/', views.student_profile, name='student_profile'),

    path('section/<slug:section_slug>/', views.section_detail, name='section_detail'),


    path('search-instructor/', views.instructor_autocomplete, name='search-instructor'),
    path('assign-adviser/', views.assign_instructor, name='assign_adviser'),



    # INTRUCTORS URLS
    path('instructor/home/', instructor_home, name="instructor_home"),
    path('instructor/teaching-subject/<slug:slug>/', subject_details, name="subject_details"),
    path('instructor/inbox/', inbox_page, name="inbox_page"),
    path('instructor/students/', instructor_students_list, name="instructor_students_list"),
    path('add-new-reminder/', add_new_reminder, name="add_new_reminder"),
    path('instructor/student/profile/<student_id>/', student_profile, name='instructor_student_profile'),

    path('instructor/create-announcement/', create_announcement, name="create_announcement"),
    path('instructor/record-attendance/', record_attendance, name="record_attendance"),
    
    
    # other URL patterns
]


urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
