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
admin.site.register(Grade)
admin.site.register(Event)


class FeedImageInline(admin.TabularInline):
    model = FeedImage
    extra = 1  

@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ('author', 'title', 'created_at')
    inlines = [FeedImageInline]


