from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

app_name = 'college'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('students/', views.student_list, name='student_list'),
    path('courses/', views.course_list, name='course_list'),
    path('staff/', views.staff_list, name='staff_list'),
    path('attendance/students/', views.student_attendance_list, name='student_attendance'),
    path('attendance/staff/', views.staff_attendance_list, name='staff_attendance'),
    path('location/', views.location_detail, name='location'),
    path('location/edit/', views.edit_location, name='edit_location'),
    path('gallery/<slug:block>/', views.block_gallery, name='block_gallery'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # ─── AJAX API endpoints (Module 6) ───
    path('api/students/', views.api_students, name='api_students'),
    path('api/students/add/', views.api_add_student, name='api_add_student'),
    path('api/students/<int:pk>/', views.api_student_detail, name='api_student_detail'),
    path('api/students/<int:pk>/update/', views.api_update_student, name='api_update_student'),
    path('api/students/<int:pk>/delete/', views.api_delete_student, name='api_delete_student'),
    path('api/staff/', views.api_staff, name='api_staff'),
    # ─── Module 6.2 AJAX endpoints ───
    path('api/attendance/toggle/', views.api_toggle_attendance, name='api_toggle_attendance'),
    path('api/attendance/today/', views.api_attendance_today, name='api_attendance_today'),
    path('api/marks/', views.api_marks, name='api_marks'),
    path('api/marks/grid/', views.api_marks_grid, name='api_marks_grid'),
    path('api/marks/add/', views.api_add_mark, name='api_add_mark'),
    path('api/marks/<int:pk>/update/', views.api_update_mark, name='api_update_mark'),
    path('api/guestbook/', views.api_guestbook, name='api_guestbook'),
    path('api/guestbook/add/', views.api_add_guestbook_entry, name='api_add_guestbook_entry'),
    path('api/status/', views.api_status, name='api_status'),
    # ─── Module 6.2 Pages ───
    path('guestbook/', views.guestbook_page, name='guestbook'),
    path('attendance/grid/', views.attendance_grid_page, name='attendance_grid'),
    path('marks/sheet/', views.marks_sheet_page, name='marks_sheet'),
    path('status/', views.status_poll_page, name='status_poll'),
]
