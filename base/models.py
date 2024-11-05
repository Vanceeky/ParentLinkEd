from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from django.utils.crypto import get_random_string

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
    
    def get_unique_slug(self):
        # Generate a base slug
        base_slug = f"{self.subject_code} - {self.name}"
        unique_slug = slugify(base_slug)

        # Check if the generated slug already exists
        if Subject.objects.filter(slug=unique_slug).exists():
            # If it does, append a random string to make it unique
            unique_slug = f"{unique_slug}-{get_random_string(length=6)}"

        return unique_slug

    def save(self, *args, **kwargs):
        # If slug is not set, generate a unique slug
        if not self.slug:
            self.slug = self.get_unique_slug()

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

    def count_subjects(self):
        """Return the count of subjects associated with this year level section."""
        return self.subjects.count()

    def count_students(self):
        """Return the count of students associated with this year level section."""
        return Student.objects.filter(year_level_section=self).count()



    

class Student(models.Model):
    
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    student_id = models.CharField(max_length=100, null = True, blank = True)
    avatar = models.ImageField(upload_to='avatars/', default = '/default_avatar.png', null = True, blank = True)

    gender = models.CharField(max_length=10, null = True, blank = True)
    age = models.IntegerField(null = True, blank = True)

    year_level_section = models.ForeignKey(YearLevelSection, on_delete=models.CASCADE, null=True, blank=True)

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
        return f"{self.id } -{self.user.username} - {self.user.first_name} {self.user.last_name}"





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
    


class Feed(models.Model):
    author = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Author: {self.author} - {self.title} - {self.created_at}"
    
class FeedImage(models.Model):
    feed = models.ForeignKey(Feed, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='feed_images/')
    
    def __str__(self):
        return f"Image for {self.feed.title}"
    

class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='grades')
    school_year = models.CharField(max_length=9)  # e.g., "2023-2024"
    
    quarter_1 = models.FloatField(null=True, blank=True)
    quarter_2 = models.FloatField(null=True, blank=True)
    quarter_3 = models.FloatField(null=True, blank=True)
    quarter_4 = models.FloatField(null=True, blank=True)
    
    final_grade = models.FloatField(null=True, blank=True)  # This will be calculated
    remarks = models.CharField(max_length=10, choices=[('Passed', 'Passed'), ('Failed', 'Failed')], null=True, blank=True)

    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.subject} - Final Grade: {self.final_grade} ({self.remarks})"

    def save(self, *args, **kwargs):
        # Calculate the final grade and remarks before saving
        self.calculate_final_grade()
        super().save(*args, **kwargs)

    def calculate_final_grade(self):
        # Get the quarter grades
        quarters = [self.quarter_1, self.quarter_2, self.quarter_3, self.quarter_4]

        # Check if all quarters are provided (not None)
        if all(q is not None for q in quarters):
            # Calculate the final grade as the average of the four quarters
            self.final_grade = sum(quarters) / len(quarters)

            # Determine the remarks based on the final grade
            self.remarks = 'Passed' if self.final_grade >= 74.9 else 'Failed'
        else:
            # If any quarter is None, set final_grade and remarks to None
            self.final_grade = None
            self.remarks = None



class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()

    def __str__(self):
        return f"{self.title} - {self.date}"
    