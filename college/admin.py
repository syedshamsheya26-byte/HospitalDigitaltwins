from django.contrib import admin
from .models import Student, Course, Staff, StudentAttendance, StaffAttendance, CollegeLocation


@admin.register(CollegeLocation)
class CollegeLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'latitude', 'longitude')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll', 'name', 'email', 'department', 'is_active')
    search_fields = ('name', 'email')
    list_filter = ('department', 'is_active')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'staff')
    search_fields = ('title', 'code')
    list_filter = ('staff',)


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'department', 'is_active')
    search_fields = ('name', 'email')
    list_filter = ('department', 'is_active')


@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'student', 'marked_by', 'status')
    search_fields = ('student__name', 'marked_by__name')
    list_filter = ('status', 'date')


@admin.register(StaffAttendance)
class StaffAttendanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'staff', 'status')
    search_fields = ('staff__name',)
    list_filter = ('status', 'date')
