from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from ckeditor.fields import RichTextField

# Create your models here.

class Subject(models.Model):
    name = models.CharField(max_length=100)
    subject_code = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    day = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)


    def __str__(self):
        return f"{self.name} - {self.day} {self.start_time} - {self.end_time}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.subject_code} - {self.name}")
        super().save(*args, **kwargs)


class Instructor(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    employee_id = models.CharField(max_length=100, null = True, blank = True)

    contact_number = models.CharField(max_length=11, null = True, blank = True)

    address = models.CharField(max_length=255, null = True, blank = True)

    avatar = models.ImageField(upload_to='avatars/', default = '/default_avatar.png', null = True, blank = True)


    date_created = models.DateTimeField(auto_now_add=True, null = True, blank = True)

    def __str__(self):
        return f"{self.employee_id} - {self.user.first_name} {self.user.last_name}"




class YearLevelSection(models.Model):
    year_levels = [
        ('Grade 1', 'Grade 1'),
        ('Grade 2', 'Grade 2'),
        ('Grade 3', 'Grade 3'),
        ('Grade 4', 'Grade 4'),
        ('Grade 5', 'Grade 5'),
        ('Grade 6', 'Grade 6'),
    ]
    year_level = models.CharField(max_length=10, choices=year_levels)

    section = models.CharField(max_length=10)
    
    subjects = models.ManyToManyField(Subject, null=True, blank=True, related_name='year_level_sections')

    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, related_name='year_level_sections', null = True, blank = True)


    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)




    def __str__(self):
        return f"{self.year_level} - {self.section}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.year_level}: {self.section}")
        super().save(*args, **kwargs)
    
    



    

class Student(models.Model):
    
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    student_id = models.CharField(max_length=100, null = True, blank = True)
    avatar = models.ImageField(upload_to='avatars/', default = '/default_avatar.png', null = True, blank = True)

    gender = models.CharField(max_length=10, null = True, blank = True)
    age = models.IntegerField(null = True, blank = True)

    year_level_section = models.ForeignKey(YearLevelSection, on_delete=models.CASCADE)

    date_created = models.DateTimeField(auto_now_add=True, null = True, blank = True)

    def __str__(self):
        return f"{self.firstname} {self.lastname} - {self.year_level_section.year_level}: {self.year_level_section.section}"
    

class Guardian(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    student = models.ManyToManyField(Student, related_name='guardians')

    age = models.IntegerField(null = True, blank = True)
    address = models.CharField(max_length=100, null = True, blank = True)
    contact_number = models.CharField(max_length=11, null = True, blank = True)
    gender = models.CharField(max_length=10, null = True, blank = True)

    avatar = models.ImageField(upload_to='avatars/', default = '/default_avatar.png', null = True, blank = True)
    relationship = models.CharField(max_length=100, null = True, blank = True)


    
    date_created = models.DateTimeField(auto_now_add=True, null = True, blank = True)


    def __str__(self):
        return f"{self.user.username} - {self.user.first_name} {self.user.last_name}"





class Reminder(models.Model):

    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)

    is_completed = models.BooleanField(default=False)

    title = models.CharField(max_length=100)
    description= models.TextField(blank=True, null=True)
    date = models.DateTimeField(null=True, blank=True)

    date_created = models.DateTimeField(auto_now_add=True, null = True, blank = True)


    def __str__(self):
        return f"Reminder: { self.instructor.user.username} - {self.title} - {self.date_created}"



class Announcement(models.Model):

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null = True, blank = True)
    content = RichTextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Announcement can be for all students or selected students
    all_students = models.BooleanField(default=False)

    selected_students = models.ManyToManyField('Student', blank=True, related_name='announcements')


    instructor = models.ForeignKey('Instructor', on_delete=models.CASCADE, related_name='announcements')



    def __str__(self):
        return f"{self.subject} - {self.created_at}"

    def get_recipients(self):
        """
        Return a queryset of the students who should receive this announcement.
        If `all_students` is True, return all students, otherwise return the selected students.
        """

        if self.all_students:
            return Student.objects.all()
        return self.selected_students.all()
    
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[('present', 'Present'), ('absent', 'Absent')])

    class Meta:
        unique_together = ('student', 'subject', 'date')  # Ensure no duplicate records for the same day

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.date} - {self.status}"