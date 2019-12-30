from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User
# Create your models here.
sections=(
    ('A','A'),
    ('B','B'),
    ('C','C')
)

class Courses(models.Model):
    Course=models.CharField(max_length=30,primary_key=True);

courses=[];
for course in Courses.objects.all():
    courses.append((course.Course, course.Course));


class Teacher(models.Model):
    User=models.OneToOneField(User,on_delete=models.CASCADE, primary_key=True);
    Course=models.ForeignKey(Courses, on_delete=models.CASCADE);
    Active = models.BooleanField(default=False);

class Student(models.Model):
    User=models.OneToOneField(User,primary_key=True, on_delete=models.CASCADE);
    Dob = models.DateField()
    Course=models.ForeignKey(Courses, on_delete=models.CASCADE);
    Section = models.CharField(max_length=1,choices=sections,default=sections[0]);
    Semester = models.IntegerField()
    Active = models.BooleanField(default=False)

class Course_Subject_Semester(models.Model):
    class Meta:
        unique_together=(('Course','Subject'),)
    Course=models.ForeignKey(Courses,on_delete=models.CASCADE);
    Subject=models.CharField(max_length=50);
    Semester=models.IntegerField();

class Teacher_Subject(models.Model):
    class Meta:
        unique_together=(('Teacher','Course'),)
    Teacher=models.ForeignKey(Teacher,on_delete=models.CASCADE);
    Course=models.ForeignKey(Course_Subject_Semester,on_delete=models.CASCADE)

class Portal(models.Model):
    Teacher=models.OneToOneField(Teacher,on_delete=models.CASCADE,primary_key=True)
    Course=models.ForeignKey(Course_Subject_Semester,on_delete=models.CASCADE)
    Section = models.CharField(max_length=1)
    Students = JSONField(default=dict)
    Lectures=models.IntegerField(default=1);
    Open=models.BooleanField(default=True);

class Total_Lectures(models.Model):
    class meta:
        unique_together=(('Course','Section'),)
    Course=models.ForeignKey(Course_Subject_Semester, on_delete=models.CASCADE);
    Section=models.CharField(max_length=1);
    Month=JSONField(default=dict);

class Student_Attendance(models.Model):
    class meta:
        unique_together=(('Student','Course_Subject'),)
    Student=models.ForeignKey(Student, on_delete=models.CASCADE)
    Course_Subject=models.ForeignKey(Course_Subject_Semester, on_delete=models.CASCADE)
    Section=models.CharField(max_length=1);
    Month=JSONField(default=dict);