from django.contrib import admin
from home.models import *
from django.utils.html import format_html
from django.contrib.auth.models import Group,User
from django.urls import path
from django.shortcuts import render
from django.middleware import csrf
from django.http import HttpResponse
import json
# Register your models here.

class StudentAdmin(admin.ModelAdmin):
    list_display=('Student_Id','Name','Username','Email','Dob','course','Semester','Section','Active')
    list_filter=[("Active"), ("Course__Course"), ("Semester"), ("Section")]
    actions=("activate",)

    def Student_Id(self,obj):
        return obj.User.id
    def Name(self,obj):
        return "{} {}".format(obj.User.first_name, obj.User.last_name)
    def Username(self,obj):
        return obj.User.username
    def Email(self,obj):
        return obj.User.email
    def course(self,obj):
        return obj.Course.Course

    def activate(self, request, queryset):
        count=queryset.update(Active=True)
        self.message_user(request,"{} students activated successfully.".format(count))
    activate.short_description="Activate Selected Students"


class SubjectFilter(admin.SimpleListFilter):
    title="Subjects"
    parameter_name="Subjects"
    def lookups(self,request,model_admin):
        return (
            ("0","Not Assigned"),
            (">0","Assigned")
        )
    def queryset(self,request,queryset):
        objs=Teacher_Subject.objects.all().values_list('Teacher__User__id',flat=True)
        assigned=set()
        for obj in objs:
            assigned.add(obj)
        if self.value() == '0':
            return queryset.exclude(User__id__in=assigned)
        elif self.value()==">0":
            return queryset.filter(User__id__in=assigned)

class TeacherAdmin(admin.ModelAdmin):
    list_display=("Teacher_Id",'Name','Username','Email','course','Active',"Subjects",'Edit_Subjects')
    list_filter=(("Active"), ("Course__Course"), SubjectFilter)
    actions=("activate",)
    
    def activate(self, request, queryset):
        count=queryset.update(Active=True)
        self.message_user(request,"{} teachers activated successfully.".format(count))
    activate.short_description="Activate Selected Teachers"

    def Edit_Subjects(self, obj):
        return format_html(
            "<a href='editSubjects/?Teacher_Id={}&Course={}&Name={}' class='button'>Edit Subject(s)</a>",
            obj.User.id,
            obj.Course.Course,
            "{} {}".format(obj.User.first_name,obj.User.last_name)
        )
    
    def Teacher_Id(self,obj):
        return obj.User.id
    def Name(self,obj):
        return "{} {}".format(obj.User.first_name, obj.User.last_name)
    def Username(self,obj):
        return obj.User.username
    def Email(self,obj):
        return obj.User.email
    def course(self,obj):
        return obj.Course.Course

    def Subjects(self,obj):
        teacher_objs=Teacher_Subject.objects.filter(Teacher__User__id=obj.User.id)
        return ", ".join([obj.Course.Subject for obj in teacher_objs])
    
    def get_urls(self):
        urls=super().get_urls()
        custom_urls=[
            path('editSubjects/',self.admin_site.admin_view(self.editSubjectsView)),
            path('editSubjects/addSubject',self.admin_site.admin_view(self.addSubjectView)),
            path('editSubjects/removeSubject',self.admin_site.admin_view(self.removeSubjectView)),
            path('editSubjects/leftSubjects',self.admin_site.admin_view(self.leftSubjectsView)),
            path('editSubjects/teacherSubjects',self.admin_site.admin_view(self.teacherSubjectsView)),
        ]
        return custom_urls + urls
    
    def editSubjectsView(self,request):
        Teacher_Id=request.GET['Teacher_Id']
        Course=request.GET['Course']
        Name=request.GET['Name']
        return render(request,'editSubjectsAdmin.html',{'Teacher_Id':Teacher_Id, 'Course':Course, 'Name':Name})

    def addSubjectView(self,request):
        if(request.is_ajax()):
            try:
                sub=request.POST['Subject']
                teacher_id=request.POST['Teacher_Id']
                course=request.POST['Course']
                course_sub_obj=Course_Subject_Semester.objects.get(Subject=sub)
                teacher_obj=Teacher.objects.get(User__id=teacher_id, Course__Course=course)
                obj=Teacher_Subject.objects.create(
                    Teacher=teacher_obj,
                    Course=course_sub_obj
                )
                obj.save()
                return HttpResponse("Success")
            except:
                return HttpResponse("Error")

    def removeSubjectView(self,request):
        if(request.is_ajax()):
            try:
                sub=request.POST['Subject']
                teacher_id=request.POST['Teacher_Id']
                Teacher_Subject.objects.filter(Teacher__User__id=teacher_id, Course__Subject=sub).delete()
                return HttpResponse("Success")
            except:
                return HttpResponse("Error")

    def leftSubjectsView(self,request):
        if(request.is_ajax()):
            course=request.POST['Course']
            # getting teacher id's within same course
            sameCourseTeacherIds=Teacher.objects.filter(Course__Course=course).values_list('User__id',flat=True)
            # subjects assigned to above teachers
            assignedSubjects=Teacher_Subject.objects.filter(Teacher__User__id__in=sameCourseTeacherIds).values_list('Course__Subject',flat=True)
            # filtering left subjects in the course
            leftSubjects=Course_Subject_Semester.objects.filter(Course__Course=course).values_list('Subject', flat=True).exclude(Subject__in=assignedSubjects)
            jSubjects=json.dumps({'subjects':list(leftSubjects)})
            return HttpResponse(str(jSubjects))
    
    def teacherSubjectsView(self,request):
        if(request.is_ajax()):
            id=request.POST['Teacher_Id']
            subjects=Teacher_Subject.objects.filter(Teacher__User__id=id).values_list('Course__Subject',flat=True)
            jSubjects=json.dumps({'subjects':list(subjects)})
            return HttpResponse(str(jSubjects))

class Course_Subject_Semester_Admin(admin.ModelAdmin):
    list_display=("course","Subject","Semester")
    list_filter=(("Course__Course"),("Semester"))

    def course(self,obj):
        return obj.Course.Course

class Portal_Admin(admin.ModelAdmin):
    list_display=('Teacher_id','subject','Section','Students','Lectures','Open')
    def Teacher_id(self,obj):
        return obj.Teacher.User.id
    def subject(self,obj):
        return obj.Course.Subject

class Student_Attendace_Admin(admin.ModelAdmin):
    list_display=('ID','Name','course', 'Subject','Section', 'Month')
    list_filter=('Course_Subject__Course__Course','Course_Subject__Subject','Section')
    def ID(self,obj):
        return obj.Student.User.id
    def Name(self,obj):
        return "{} {}".format(obj.Student.User.first_name, obj.Student.User.last_name)
    def course(self,obj):
        return obj.Course_Subject.Course.Course
    def Subject(self,obj):
        return obj.Course_Subject.Subject

class Total_Lectures_Admin(admin.ModelAdmin):
    list_display=('course','Subject','Month')
    def course(self,obj):
        return obj.Course.Course.Course
    def Subject(self,obj):
        return obj.Course.Subject

class CoursesAdmin(admin.ModelAdmin):
    list_display=('Course',)

admin.site.site_header='Attendance Admin'
admin.site.site_title='Attendance Admin'
admin.site.index_title='Attendance Administration'

admin.site.register(Student,StudentAdmin)
admin.site.register(Teacher,TeacherAdmin)
admin.site.register(Courses,CoursesAdmin)
admin.site.register(Course_Subject_Semester,Course_Subject_Semester_Admin)
admin.site.register(Portal,Portal_Admin)
admin.site.register(Student_Attendance,Student_Attendace_Admin)
admin.site.register(Total_Lectures,Total_Lectures_Admin)
admin.site.unregister(Group)
admin.site.unregister(User)