from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    staff = models.ForeignKey('Staff', on_delete=models.SET_NULL, null=True, related_name='courses')

    def __str__(self):
        return f"{self.code} - {self.title}"


class Staff(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='staff_members')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Student(models.Model):
    roll = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='students')
    courses = models.ManyToManyField(Course, related_name='students', blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.roll} - {self.name}"


class StudentAttendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Leave', 'Leave'),
    ]

    date = models.DateField()
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_attendance')
    marked_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='marked_student_attendance')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ('date', 'student')

    def __str__(self):
        return f"{self.date} {self.student} {self.status}"


class StaffAttendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Leave', 'Leave'),
    ]

    date = models.DateField()
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='staff_attendance')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ('date', 'staff')

    def __str__(self):
        return f"{self.date} {self.staff} {self.status}"


class StudentMark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marks')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='marks')
    marks = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=2, blank=True)
    status = models.CharField(max_length=20, default='Pending')

    class Meta:
        unique_together = ('student', 'course')

    def save(self, *args, **kwargs):
        if self.marks >= 90:
            self.grade = 'A'
        elif self.marks >= 75:
            self.grade = 'B'
        elif self.marks >= 60:
            self.grade = 'C'
        elif self.marks >= 50:
            self.grade = 'D'
        else:
            self.grade = 'F'
        self.status = 'Pass' if self.marks >= 50 else 'Fail'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.course}: {self.marks} ({self.grade})"


class GuestbookEntry(models.Model):
    name = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}: {self.message[:50]}"


class CollegeLocation(models.Model):
    name = models.CharField(max_length=200, default='MOTHER THERESA DEGREE COLLEGE')
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return self.name
