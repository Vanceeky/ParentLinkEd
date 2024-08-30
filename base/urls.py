from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('instructors/', views.instructor_page, name='instructor_page'),
    path('subjects/', views.subject_page, name='subject_page'),
    path('students/', views.student_page, name='student_page'),

    path('view-section/slug/', views.view_section, name='view_section'),
]
