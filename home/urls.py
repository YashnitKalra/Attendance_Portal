from django.urls import path
from . import views

urlpatterns=[
    path("",views.home),    # home
    path("teacherDashboard",views.loginTeacher),    # teacher dashboard
    path("studentDashboard",views.loginStudent),    # student dashboard
    path("registerTeacher",views.registerTeacher),  # teacher registration
    path("registerStudent",views.registerStudent),  # student registration
    path("register",views.register),    # after otp verification
    path("logout",views.logout),    # logout user
    path("forgotUsername",views.forgotUsername),
    path("forgotPassword",views.forgotPassword),
    path("getTeacherSubjects",views.teacherSubjects),   # fetch teacher subjects
    path("changePassword",views.changePassword),    # change user password
    path("openPortal",views.openPortal),    # portal opened by teacher
    path("closePortal",views.closePortal),  # portal closed by teacher
    path('getPortalData',views.getPortalData),  # data about portal like course, subject, lectures...
    path('getStudentPortals',views.getStudentPortals), # get opened portals for students
    path('markAttendance',views.markAttendance),    # students mark their attendance in portal
    path('getPortalStudents',views.getPortalStudents),  # get students who marked their attendance in a specific portal
    path('deletePortal',views.deletePortal),    # delete portal without uploading attendance
    path('reopenPortal',views.reopenPortal),    # reopen closed portal
    path('uploadAttendance',views.uploadAttendance),    # upload attendance and delete portal
    path('checkStudentAttendance', views.checkStudentAttendance),   # student check attendance page
    path('getAttendance',views.getAttendance),  # students check their attendance according to subject
    path('viewStudentsAttendance',views.viewStudentsAttendance),    # teacher checks attedance of the subjects he/she teaches
    path('getAttendances',views.getAttendances),    # teacher gets attendance of all students according subject
    path('generatePDF',views.generatePDF),  # generates students attendance pdf for teachers
]