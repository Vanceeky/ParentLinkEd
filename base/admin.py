from django.contrib import admin
from . models import *
# Register your models here.



admin.site.register(YearLevelSection)
admin.site.register(Subject)
admin.site.register(Instructor)
admin.site.register(Student)
admin.site.register(Guardian)
admin.site.register(Reminder)
admin.site.register(Announcement)
admin.site.register(Attendance)