from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

# Create your models here.


class YearLevelSection(models.Model):
    year_levels = [
        ('Grade 1', 'Grade 1'),
        ('Grade 2', 'Grade 2'),
        ('Grade 3', 'Grade 3'),
        ('Grade 4', 'Grade 4'),
        ('Grade 5', 'Grade 5'),
        ('Grade 6', 'Grade 6'),
        ('Grade 7', 'Grade 7'),
        ('Grade 8', 'Grade 8'),
        ('Grade 9', 'Grade 9'),
        ('Grade 10', 'Grade 10'),
        ('Grade 11', 'Grade 11'),
        ('Grade 12', 'Grade 12'),
        ('1st Year', '1st Year'),
        ('2nd Year', '2nd Year'),
        ('3rd Year', '3rd Year'),
        ('4th Year', '4th Year'),
    ]
    year_level = models.CharField(max_length=10, choices=year_levels)
    section = models.CharField(max_length=10)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.year_level} - {self.section}"
    
    def save(self, *args, **kwargs):
        # Generate a unique slug before saving the object
        if not self.slug:
            self.slug = slugify(f"{self.year_level}: {self.section}")
        super().save(*args, **kwargs)
    
class Subject(models.Model):
    name = models.CharField(max_length=100)
    year_level_section = models.ForeignKey(YearLevelSection, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    day = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)


    def __str__(self):
        return f"{self.name} - {self.year_level_section.year_level}: {self.year_level_section.section}"
    
    def save(self, *args, **kwargs):
        # Generate a unique slug before saving the object
        if not self.slug:
            self.slug = slugify(f"{self.name} - {self.year_level_section.year_level}: {self.year_level_section.section}")
        super().save(*args, **kwargs)

class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subjects = models.ManyToManyField(Subject, related_name='instructor')

    def __str__(self):
        return f"{self.user.username} - {self.user.first_name} {self.user.last_name}"


