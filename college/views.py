import json

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_http_methods

from .forms import CollegeLocationForm
from .models import Student, Course, Staff, StudentMark, GuestbookEntry, StudentAttendance, StaffAttendance, CollegeLocation


def home(request):
    return redirect('college:login')


def about(request):
    stats = {
        'students': Student.objects.count(),
        'courses': Course.objects.count(),
        'staff': Staff.objects.count(),
    }
    return render(request, 'college/about.html', {'stats': stats})


def student_list(request):
    students = Student.objects.select_related('department').prefetch_related('courses').all()
    return render(request, 'college/students.html', {'students': students})


def course_list(request):
    courses = Course.objects.select_related('department', 'staff').all()
    return render(request, 'college/courses.html', {'courses': courses})


def staff_list(request):
    staff_members = Staff.objects.select_related('department').all()
    return render(request, 'college/staff.html', {'staff_members': staff_members})


def student_attendance_list(request):
    student_attendance = StudentAttendance.objects.select_related('student', 'marked_by').order_by('-date')[:50]
    return render(request, 'college/student_attendance.html', {'student_attendance': student_attendance})


def staff_attendance_list(request):
    staff_attendance = StaffAttendance.objects.select_related('staff').order_by('-date')[:50]
    return render(request, 'college/staff_attendance.html', {'staff_attendance': staff_attendance})


@staff_member_required
def edit_location(request):
    location, _ = CollegeLocation.objects.get_or_create(
        defaults={
            'name': 'MOTHER THERESA DEGREE COLLEGE',
            'address': 'degree block mother theresa institutions 219, national highway gangavaram melmoi andhra pradesh 517408',
            'latitude': 13.2442799,
            'longitude': 78.7299217,
        }
    )

    if request.method == 'POST':
        form = CollegeLocationForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            return redirect('college:location')
    else:
        form = CollegeLocationForm(instance=location)

    return render(request, 'college/edit_location.html', {'form': form, 'location': location})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('college:dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            next_url = request.GET.get('next')
            return redirect(next_url or 'college:dashboard')
    else:
        form = AuthenticationForm(request)
    return render(request, 'college/login.html', {'form': form})


@login_required
def dashboard(request):
    students = Student.objects.select_related('department').prefetch_related('courses').all()
    courses = Course.objects.select_related('department', 'staff').all()
    staff_members = Staff.objects.select_related('department').all()
    location = CollegeLocation.objects.first()
    return render(request, 'college/dashboard.html', {
        'students': students,
        'courses': courses,
        'staff_members': staff_members,
        'location': location,
    })


def location_detail(request):
    location, _ = CollegeLocation.objects.get_or_create(
        defaults={
            'name': 'MOTHER THERESA DEGREE COLLEGE',
            'address': 'degree block mother theresa institutions 219, national highway gangavaram melmoi andhra pradesh 517408',
            'latitude': 13.2442799,
            'longitude': 78.7299217,
        }
    )
    return render(request, 'college/location.html', {'location': location})


# ─── AJAX API Views (Module 6 — JsonResponse) ─────────────────────────

@require_http_methods(["GET"])
def api_students(request):
    q = request.GET.get("search", "").strip()
    qs = Student.objects.select_related("department")
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(roll__icontains=q))
    data = list(qs.values("id", "roll", "name", "department__name", "email"))
    return JsonResponse({"students": data, "count": len(data)})


@require_http_methods(["GET"])
def api_student_detail(request, pk):
    s = get_object_or_404(Student.objects.select_related("department"), pk=pk)
    return JsonResponse({
        "id": s.id, "roll": s.roll, "name": s.name,
        "email": s.email, "department": s.department.name,
    })


@require_http_methods(["POST"])
def api_add_student(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    errors = {}
    roll = payload.get("roll", "").strip()
    name = payload.get("name", "").strip()
    email = payload.get("email", "").strip()

    if not roll: errors["roll"] = ["Roll number is required."]
    if not name: errors["name"] = ["Name is required."]
    if not email: errors["email"] = ["Email is required."]
    if errors:
        return JsonResponse({"errors": errors}, status=400)

    if Student.objects.filter(roll=roll).exists():
        return JsonResponse({"errors": {"roll": ["Roll already exists."]}}, status=400)

    student = Student.objects.create(roll=roll, name=name, email=email)
    return JsonResponse({
        "id": student.id, "roll": student.roll,
        "name": student.name, "email": student.email,
    }, status=201)


@require_http_methods(["PATCH"])
def api_update_student(request, pk):
    s = get_object_or_404(Student, pk=pk)
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    if "name" in payload:
        s.name = payload["name"].strip()
    if "email" in payload:
        s.email = payload["email"].strip()
    s.save()
    return JsonResponse({"id": s.id, "name": s.name, "email": s.email})


@require_http_methods(["DELETE"])
def api_delete_student(request, pk):
    s = get_object_or_404(Student, pk=pk)
    s.delete()
    return JsonResponse({}, status=204)


# ─── Attendance AJAX Toggle (Module 6.2) ──────────────────────────────

@require_http_methods(["POST"])
def api_toggle_attendance(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    student_id = payload.get("student_id")
    date_str = payload.get("date")
    status = payload.get("status", "Present")
    if not student_id or not date_str:
        return JsonResponse({"error": "student_id and date required"}, status=400)

    student = get_object_or_404(Student, pk=student_id)
    from datetime import datetime
    date = datetime.strptime(date_str, "%Y-%m-%d").date()

    att, created = StudentAttendance.objects.update_or_create(
        date=date, student=student,
        defaults={"status": status},
    )
    return JsonResponse({"id": att.id, "student": student.name, "status": att.status, "date": str(att.date)})


@require_http_methods(["GET"])
def api_attendance_today(request):
    from datetime import date
    today = date.today()
    students = Student.objects.select_related("department").all()
    rows = []
    for s in students:
        att = StudentAttendance.objects.filter(date=today, student=s).first()
        rows.append({
            "id": s.id, "roll": s.roll, "name": s.name,
            "department": s.department.name,
            "status": att.status if att else "—",
            "attendance_id": att.id if att else None,
        })
    return JsonResponse({"date": str(today), "students": rows, "count": len(rows)})


# ─── Marks AJAX (Module 6.2) ──────────────────────────────────────────

@require_http_methods(["GET"])
def api_marks(request):
    course_id = request.GET.get("course_id")
    qs = StudentMark.objects.select_related("student", "course")
    if course_id:
        qs = qs.filter(course_id=course_id)
    data = list(qs.values("id", "student__id", "student__name", "student__roll", "course__id", "course__code", "course__title", "marks", "grade", "status"))
    return JsonResponse({"marks": data, "count": len(data)})


@require_http_methods(["GET"])
def api_marks_grid(request):
    from datetime import date
    courses = Course.objects.all()
    students = Student.objects.select_related("department").all()
    marks_qs = StudentMark.objects.select_related("student", "course")
    marks_map = {}
    for m in marks_qs:
        marks_map[(m.student_id, m.course_id)] = {"id": m.id, "marks": float(m.marks), "grade": m.grade, "status": m.status}

    rows = []
    for s in students:
        row = {"student_id": s.id, "roll": s.roll, "name": s.name, "department": s.department.name, "courses": {}}
        for c in courses:
            entry = marks_map.get((s.id, c.id))
            row["courses"][str(c.id)] = {
                "mark_id": entry["id"] if entry else None,
                "marks": entry["marks"] if entry else None,
                "grade": entry["grade"] if entry else None,
                "status": entry["status"] if entry else "—",
            }
        rows.append(row)

    return JsonResponse({
        "courses": [{"id": c.id, "code": c.code, "title": c.title} for c in courses],
        "students": rows,
    })


@require_http_methods(["PATCH"])
def api_update_mark(request, pk):
    m = get_object_or_404(StudentMark, pk=pk)
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    if "marks" in payload:
        m.marks = float(payload["marks"])
        m.save()
    return JsonResponse({"id": m.id, "marks": float(m.marks), "grade": m.grade, "status": m.status})


@require_http_methods(["POST"])
def api_add_mark(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    student = get_object_or_404(Student, pk=payload.get("student_id"))
    course = get_object_or_404(Course, pk=payload.get("course_id"))
    m, created = StudentMark.objects.update_or_create(
        student=student, course=course,
        defaults={"marks": float(payload.get("marks", 0))},
    )
    return JsonResponse({"id": m.id, "marks": float(m.marks), "grade": m.grade, "status": m.status}, status=201)


# ─── Guestbook AJAX (Module 6.2 — reload-free) ────────────────────────

@require_http_methods(["GET"])
def api_guestbook(request):
    entries = GuestbookEntry.objects.order_by("-created_at")[:50]
    data = list(entries.values("id", "name", "message", "created_at"))
    return JsonResponse({"entries": data, "count": len(data)})


@require_http_methods(["POST"])
def api_add_guestbook_entry(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    name = payload.get("name", "").strip()
    message = payload.get("message", "").strip()
    if not name or not message:
        return JsonResponse({"error": "Name and message are required."}, status=400)
    entry = GuestbookEntry.objects.create(name=name, message=message)
    return JsonResponse({"id": entry.id, "name": entry.name, "message": entry.message, "created_at": entry.created_at.isoformat()}, status=201)


# ─── Status Polling Endpoint (Module 6.2 — setInterval + fetch) ──────

from datetime import datetime

@require_http_methods(["GET"])
def api_status(request):
    return JsonResponse({
        "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "student_count": Student.objects.count(),
        "course_count": Course.objects.count(),
        "staff_count": Staff.objects.count(),
        "attendance_today": StudentAttendance.objects.filter(date=datetime.now().date()).count(),
        "guestbook_entries": GuestbookEntry.objects.count(),
        "marks_count": StudentMark.objects.count(),
    })


# ─── Module 6.2 Pages ─────────────────────────────────────────────────

def guestbook_page(request):
    return render(request, 'college/guestbook.html')


def attendance_grid_page(request):
    from datetime import date
    today = date.today()
    students = Student.objects.select_related("department").all()
    courses = Course.objects.all()
    return render(request, 'college/attendance_grid.html', {
        'students': students,
        'courses': courses,
        'today': today,
    })


def marks_sheet_page(request):
    students = Student.objects.select_related("department").all()
    courses = Course.objects.all()
    return render(request, 'college/marks_sheet.html', {
        'students': students,
        'courses': courses,
    })


def status_poll_page(request):
    return render(request, 'college/status_poll.html')


# ─── Staff AJAX ───────────────────────────────────────────────────────

@require_http_methods(["GET"])
def api_staff(request):
    qs = Staff.objects.select_related("department")
    data = list(qs.values("id", "name", "email", "department__name"))
    return JsonResponse({"staff": data})


BLOCK_DATA = {
    'degree': {
        'title': 'Degree Block',
        'subtitle': 'B.Sc / B.Com / BCA / BBA Programs',
        'description': 'Our Degree Block offers a wide range of undergraduate programs including B.Sc (Computer Science, Chemistry, Botany, etc.), B.Com, BCA (Artificial Intelligence), and BBA — all affiliated to Sri Venkateswara University.',
        'color': '#6366f1',
        'badge': 'U.G. Programs',
        'badge_class': 'bg-primary',
        'images': [f'campus{i}.jpg' for i in [1,2,3,4,5,6]] + ['library1.jpg'],
    },
    'intermediate': {
        'title': 'Intermediate Block',
        'subtitle': 'Higher Secondary Education',
        'description': 'Our intermediate block provides foundation-level education preparing students for higher studies. Focus on core academics, personality development, and career guidance for pre-university students.',
        'color': '#f59e0b',
        'badge': 'Higher Secondary',
        'badge_class': 'bg-warning text-dark',
        'images': [f'campus{i}.jpg' for i in [9,10,13,14,15,16]],
    },
    'engineering': {
        'title': 'Engineering Block',
        'subtitle': 'B.Tech Programs',
        'description': 'Mother Theresa Institute of Engineering and Technology offers state-of-the-art B.Tech programs in Computer Science, AI & ML, Electronics, and Mechanical Engineering. Equipped with modern labs and industry partnerships.',
        'color': '#ec4899',
        'badge': 'B.Tech Programs',
        'badge_class': 'bg-danger',
        'images': [f'campus{i}.jpg' for i in [7,8,11,12,17,18]],
    },
    'masters': {
        'title': 'Masters Block',
        'subtitle': 'M.Tech / M.A Programs',
        'description': 'Advanced M.Tech and M.A programs fostering research, innovation, and specialization. Designed for aspiring researchers and industry leaders with access to advanced research facilities.',
        'color': '#10b981',
        'badge': 'M.Tech / M.A',
        'badge_class': 'bg-success',
        'images': [f'campus{i}.jpg' for i in [19,20,21,22,23]],
    },
}

def block_gallery(request, block):
    data = get_object_or_404(BLOCK_DATA, block)
    return render(request, 'college/block_gallery.html', {'campus': data, 'block_key': block})
