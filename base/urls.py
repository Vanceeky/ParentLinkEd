from django.urls import path


from . import views
from django.conf import settings
from django.conf.urls.static import static


from base.view.instructor import *
from base.view.guardian import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('feed/', views.feed, name='feed'),
    path('add-feed/', views.add_feed, name='add_feed'),

    path('upcoming-events/', views.upcoming_events, name='upcoming_events'),
    path('add-event/', views.add_event, name='add_event'),
    path('update-event/<int:event_id>/', views.update_event, name='update_event'),
    path('delete-event/<int:event_id>/', views.delete_event, name='delete_event'),

    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),


    path('add-instructor/', views.add_instructor, name='add_instructor'),
    path('instructors/', views.instructor_page, name='instructor_page'),
    path('instructor-info/<str:instructor_id>/', views.instructor_detail, name='instructor_detail'),



    path('sections/', views.subject_page, name='subject_page'),
    path('add-subject/', views.add_subject, name='add_subject'),
    path('update-subject/', views.update_subject, name='update_subject'),



    path('students/', views.student_page, name='student_page'),
    path('update_student_section/', views.update_student_section, name='update_student_section'),
    path('student/profile/<student_id>/', views.student_profile, name='student_profile'),

    path('add-student/', views.add_student, name='add_student'),

    path('section/<slug:section_slug>/', views.section_detail, name='section_detail'),
    path('add-section/', views.add_section, name="add_section"),


    path('search-instructor/', views.instructor_autocomplete, name='search-instructor'),
    path('assign-adviser/', views.assign_instructor, name='assign_adviser'),



    # INTRUCTORS URLS
    path('instructor/', profile, name="instructor_profile"),
    path('instructor/edit-profile/', update_profile, name="update_profile"),
    path('instructor/home/', instructor_home, name="instructor_home"),
    path('instructor/teaching-subject/<slug:slug>/', subject_details, name="subject_details"),
    path('instructor/inbox/', inbox_page, name="inbox_page"),
    path('instructor/students/', instructor_students_list, name="instructor_students_list"),
    path('add-new-reminder/', add_new_reminder, name="add_new_reminder"),
    path('instructor/student/profile/<student_id>/', student_profile, name='instructor_student_profile'),

    path('instructor/create-announcement/', create_announcement, name="create_announcement"),
    path('instructor/record-attendance/', record_attendance, name="record_attendance"),
    path('add-grade/', add_grade, name='add_grade'),
    path('update-grade/', update_grade, name="update_grade"),
    path('complete-reminder/<int:reminder_id>/', complete_reminder, name="complete_reminder"),
 
    
    # GUARDIAN URLS
    path('guardian/home/', guardian_home, name="guardian_home"),
    path('guardian/profile/', guardian_profile, name="guardian_profile"),
    path('guardian/student/<student_id>/', guardian_student_profile, name="guardian_student_profile"),
    path('guardian/update-avatar/<student_id>/', update_avatar, name="update_avatar"),
    path('guardian/update-info/', update_guardian, name="update_guardian"),
    path('announcements/', guardian_announcements, name="guardian_announcements"),


    path('offline/', views.offline, name='offline'),
    path('manifest.json', views.manifest, name='manifest'),
    # other URL patterns

        # Password reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
