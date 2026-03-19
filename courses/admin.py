from django.contrib import admin
from .models import Course, Video, Purchase, VideoProgress


class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "price")


class VideoAdmin(admin.ModelAdmin):
    list_display = ("title", "course")


class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("user", "course")


admin.site.register(Course, CourseAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(Purchase, PurchaseAdmin)
admin.site.register(VideoProgress)