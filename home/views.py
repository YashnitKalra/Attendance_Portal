from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
import datetime, io
from .models import *
from django.http import HttpResponse, FileResponse
import json
from django.contrib.auth.models import User, auth
from django.contrib import messages as msgs
from .myUtils import generateOTP, getPortalStatus, sendMail, verifyUserDetails
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from django.urls import reverse

def home(request):
    if 'isTeacher' in request.session:
        if request.session['isTeacher']:
            request.session['portalOpen']=getPortalStatus(request.session['id'])
            request.session['userActive']=Teacher.objects.get(User__id=int(request.session['id'])).Active
            return redirect('/teacherDashboard')
        else:
            request.session['userActive']=Student.objects.get(User__id=int(request.session['id'])).Active
            return redirect('/studentDashboard')
    return render(request,"home.html",{'courses':courses, 'sections':sections})

def logout(request):
    try:
        del(request.session['isTeacher'])
        del(request.session['name'])
        del(request.session['userActive'])
        del(request.session['id'])
        del(request.session['course'])
    except:
        pass
    try:
        del(request.session['portalOpen'])
    except:
        pass
    try:
        del(request.session['sections'])
    except:
        pass
    auth.logout(request);
    return redirect("/")

def loginTeacher(request):
    if request.method=="POST":
        username=request.POST['username']
        password=request.POST['password']
        try:
            teacher=Teacher.objects.get(User__username=username)
        except:
            return render(request,"message.html",{"messages":["Error: User Not Found"]})
        user=auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request,user)
            request.session['isTeacher']=True
            request.session['name']="{} {}".format(user.first_name,user.last_name)
            request.session['userActive']=teacher.Active
            request.session['id']=teacher.User.id
            request.session['course']=teacher.Course.Course
            request.session['portalOpen']=getPortalStatus(teacher.User.id)
            return render(request,"teacherDashboard.html")
        else:
            return render(request,"message.html",{"messages":["Error: Password Does Not Match"]})
    else:
        if 'isTeacher' in request.session:
            request.session['userActive']=Teacher.objects.get(User__id=int(request.session['id'])).Active
            request.session['portalOpen']=getPortalStatus(request.session['id'])
            return render(request,"teacherDashboard.html")
        return render(request,"message.html",{"messages":["Error"]})

def loginStudent(request):
    if request.method=="POST":
        username=request.POST['username']
        password=request.POST['password']
        try:
            student=Student.objects.get(User__username=username)
        except:
            return render(request,"message.html",{"messages":["Error: User Not Found"]})
        user=auth.authenticate(username=username, password=password)
        if user is not None:
            request.session['isTeacher']=False
            request.session['name']="{} {}".format(user.first_name,user.last_name)
            request.session['course']=student.Course.Course
            request.session['userActive']=student.Active
            request.session['id']=user.id
            request.session['section']=student.Section
            return render(request,"studentDashboard.html")
        else:
            return render(request,"message.html",{"messages":["Error: Password Does Not Match"]})
    else:
        if 'isTeacher' in request.session:
            request.session['userActive']=Student.objects.get(User__id=int(request.session['id'])).Active
            return render(request,"studentDashboard.html")
        return render(request,"message.html",{"messages":["Error"]})

def registerTeacher(request):
    if request.method=="POST":
        firstname,course,email=request.POST['firstname'].strip(),request.POST['course'].strip(),request.POST['email'].strip()
        lastname,username=request.POST['lastname'],request.POST['username']
        password1,password2=request.POST['password1'],request.POST['password2']
        messages=verifyUserDetails(firstname,lastname,username,email,password1,password2,course)    
        if(len(messages)>0):
            return render(request,"message.html",{"messages":messages})
        otp=generateOTP()
        sendMail("Attendance Portal One Time Password","OTP for registration is {}.".format(otp),[email])
        return render(request,'otpVerification.html',{
            "firstname":firstname, "lastname":lastname, "username":username, "otp":make_password(otp),
            "password":make_password(password1), "course":course, 'userType':'teacher', "email":email
        })

def registerStudent(request):
    if request.method=="POST":
        firstname,lastname,username=request.POST['firstname'].strip(),request.POST['lastname'].strip(),request.POST['username'].strip()
        course,email=request.POST['course'].strip(),request.POST['email'].strip()
        dob,section,semester=request.POST['dob'],request.POST['section'],int(request.POST['semester'])
        password1,password2=request.POST['password1'],request.POST['password2']
        messages=verifyUserDetails(firstname,lastname,username,email,password1,password2,course)
        try:
            datetime.datetime.strptime(dob,"%Y-%m-%d").date()
        except:
            messages.append("Error: Invalid DOB")
        if(len(messages)>0):
            return render(request,"message.html",{"messages":messages})
        otp=generateOTP()
        sendMail("Attendance Portal One Time Password","OTP for registration is {}.".format(otp),[email])
        return render(request,'otpVerification.html',{
            "firstname":firstname, "lastname":lastname, "username":username, "otp":make_password(otp), "email":email, "dob":dob,
            "password":make_password(password1), "course":course, "section":section, "semester":semester, 'userType':'student'
        })

def register(request):
    if request.method=='POST':
        firstname,lastname,username=request.POST['firstname'],request.POST['lastname'],request.POST['username']
        email,password,otp,userOtp=request.POST['email'],request.POST['password'],request.POST['token'],request.POST['otp']
        userType,course=request.POST['userType'],request.POST['course']
        messages=verifyUserDetails(firstname,lastname,username,email,password,password,course)
        if not check_password(userOtp,otp):
            messages.append("Invalid OTP")
        if(len(messages)>0):
            return render(request,"message.html",{"messages":messages})
        try:
            if userType=='student':
                section,semester,dob=request.POST['section'],request.POST['semester'],request.POST['dob']
                dob=datetime.datetime.strptime(dob,"%Y-%m-%d").date()
                user=User.objects.create(first_name=firstname,last_name=lastname,username=username,email=email,password=password)
                user.save()
                student=Student.objects.create(User=user,Course=Courses.objects.get(Course=course),Dob=dob,
                Section=section,Semester=semester)
                student.save()
                msgs.info(request,"Successful Registeration, Wait for Activation")
                return redirect(home,permanent=True)
            elif userType=='teacher':
                user=User.objects.create(first_name=firstname,last_name=lastname,username=username,email=email,password=password)
                user.save()
                teacher=Teacher.objects.create(User=user,Course=Courses.objects.get(Course=course))
                teacher.save()
                msgs.info(request,"Successful Registeration, Wait for Activation")
                return redirect(home,permanent=True)
        except:
            user = User.objects.filter(username=username)
            if user.exists():
                for u in user:
                    u.delete()
            return render(request,"message.html",{"messages":["Error"]})

def forgotUsername(request):
    if request.method=='GET':
        return render(request,"forgotUsername.html")
    elif request.method=='POST':
        email=request.POST['email']
        try:
            username=User.objects.get(email=email).username
        except:
            msgs.info(request,"Error: Email not registered")
            return render(request,"forgotUsername.html")
        msg="Your username is '{}'.".format(username)
        sendMail("Attendance Portal Username",msg,[email])
        msgs.info(request,"Username sent to "+email)
        return render(request,"forgotUsername.html")

def forgotPassword(request):
    if request.is_ajax():
        if request.method=='GET':
            try:
                email=request.GET['email']
                try:
                    username=User.objects.get(email=email).username
                except:
                    return HttpResponse('Error: Email not registered')
                otp=generateOTP()
                msg="Your OTP is '{}'".format(otp)
                sendMail("Attendance Portal Forgot Password",msg,[email])
                m={"token_u":make_password(username), "token_o":make_password(otp)}
                m=json.dumps(m)
                return HttpResponse(m)
            except:
                return HttpResponse('Error')
        elif request.method=='POST':
            try:
                email,otp,password1=request.POST['email'],request.POST['otp'],request.POST['password1']
                username_token,otp_token,password2=request.POST['token_u'],request.POST['token_o'],request.POST['password2']
                if password1!=password2:
                    return HttpResponse("Error: Passwords Do no match.")
                elif len(password1)<8:
                    return HttpResponse("Error: Minimum Password Length should be 8.")
                else:
                    user=User.objects.get(email=email)
                    if not check_password(user.username, username_token):
                        return HttpResponse("Error")
                    if not check_password(otp, otp_token):
                        return HttpResponse("Error: OTP Does not match.")
                    user.set_password(password1)
                    user.save()
                    return HttpResponse(reverse(home))
            except:
                return HttpResponse('Error')
    elif request.method=='GET':
        return render(request,"forgotPassword.html")

def teacherSubjects(request):
    if(request.is_ajax()):
        id=int(request.POST['Teacher_Id'])
        subjects=Teacher_Subject.objects.filter(Teacher__User__id=id).values_list('Course__Subject')
        jSubjects=json.dumps({'subjects':list(subjects)})
        return HttpResponse(str(jSubjects))

def changePassword(request):
    if request.is_ajax():
        id=request.session['id']
        oldPassword=request.POST['oldPassword']
        password1=request.POST['password1']
        password2=request.POST['password2']
        user=User.objects.get(id=id)
        if auth.authenticate(username=user.username, password=oldPassword) is not None:
            if password1!=password2:
                return HttpResponse("Passwords do not match")
            elif len(password1)<8:
                return HttpResponse("Minimum Password Length should be 8")
            else:
                user.set_password(password1)
                user.save()
                return HttpResponse("Successful")
        else:
            return HttpResponse("Wrong Old Password")

def openPortal(request):
    if request.is_ajax():
        id, subject=int(request.POST['Teacher_Id']), request.POST['Subject']
        section, lectures=request.POST['Section'], int(request.POST['Lectures'])
        try:
            obj=Teacher_Subject.objects.get(Teacher__User__id=id, Course__Subject=subject)
        except:
            return HttpResponse("Invalid Subject")
        try:
            obj=Portal.objects.create(Teacher=obj.Teacher,Course=obj.Course,Lectures=lectures,Section=section)
            obj.save()
            return HttpResponse("Portal Opened")
        except:
            return HttpResponse("Error")

def closePortal(request):
    if(request.is_ajax()):
        id=int(request.POST['Teacher_Id'])
        try:
            Portal.objects.filter(Teacher__User__id=id).update(Open=False)
            return HttpResponse("Portal Closed")
        except:
            return HttpResponse("Error")

def getPortalData(request):
    if(request.is_ajax()):
        id=int(request.POST['Teacher_Id'])
        try:
            obj=Portal.objects.get(Teacher__User__id=id)
            data=json.dumps({
                'subject':obj.Course.Subject,
                'section':obj.Section,
                'lectures':obj.Lectures,
                'students':len(obj.Students)
            })
            return HttpResponse(str(data))
        except:
            return HttpResponse("Error")

def getStudentPortals(request):
    if request.is_ajax():
        try:
            course=request.POST['Course']
            section=request.POST['Section']
            s_id=request.POST['Student_Id']
            semester=Student.objects.get(User__id=s_id).Semester
            obj=Portal.objects.filter(Course__Course=course, Section=section,Course__Semester=semester, Open=True)
            data={}
            for ob in obj:
                data[ob.Teacher.User.id]=[ob.Course.Subject, s_id in ob.Students]
            return HttpResponse(str(json.dumps(data)))
        except:
            return HttpResponse('Error')

def markAttendance(request):
    if request.is_ajax():
        try:
            t_id=int(request.POST['Teacher_Id'])
            s_id=request.POST['Student_Id']
            s_name=request.POST['Student_Name']
            obj=Portal.objects.get(Teacher__User__id=t_id, Open=True)
            if s_id in obj.Students:
                return HttpResponse('Already Marked')
            obj.Students[s_id]=s_name
            obj.save()
            return HttpResponse('Attendance Marked')
        except:   
            return HttpResponse('Error')

def getPortalStudents(request):
    if request.is_ajax():
        try:
            t_id=int(request.POST['Teacher_Id'])
            obj=Portal.objects.get(Teacher__User__id=t_id)
            return HttpResponse(str(json.dumps(obj.Students)))
        except:
            return HttpResponse('Error')

def deletePortal(request):
    if request.is_ajax():
        try:
            t_id=int(request.POST['Teacher_Id'])
            Portal.objects.get(Teacher__User__id=t_id).delete()
            return HttpResponse('Success')
        except:
            return HttpResponse('Error')

def reopenPortal(request):
    if request.is_ajax():
        try:
            t_id=int(request.POST['Teacher_Id'])
            obj=Portal.objects.get(Teacher__User__id=t_id)
            obj.Open=True
            obj.save()
            return HttpResponse('Portal Re-opened')
        except:
            return HttpResponse('Error')

def uploadAttendance(request):
    if request.is_ajax():
        try:
            months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
            t_id=int(request.POST['Teacher_Id'])
            s_ids=request.POST['Student_Ids'].split(',')
            portal=Portal.objects.get(Teacher__User__id=t_id)
            course_obj=portal.Course
            section=portal.Section
            lectures=int(portal.Lectures)
            month = months[datetime.datetime.now().month-1]
            try:
                total=Total_Lectures.objects.get(Course=course_obj, Section=section)
            except:
                total=Total_Lectures.objects.create(Course=course_obj, Section=section)
            total.Month[month]=total.Month.get(month,0)+lectures
            total.save()
            if s_ids[0]!='':
                for s_id in s_ids:
                    try:
                        student=Student_Attendance.objects.get(
                            Student__User__id=int(s_id),
                            Course_Subject=course_obj,
                            Section=section
                        )
                    except:
                        stud=Student.objects.get(User__id=int(s_id))
                        student=Student_Attendance.objects.create(Student=stud, Course_Subject=course_obj, Section=section)
                    student.Month[month]=student.Month.get(month,0)+lectures
                    student.save()
            portal.delete()
            return HttpResponse('Uploaded')
        except:
            return HttpResponse('Error')

def checkStudentAttendance(request):
    name=request.session['name']
    id=request.session['id']
    course=Student.objects.get(User__id=id).Course.Course
    subjects=list(Total_Lectures.objects.filter(Course__Course__Course=course).values_list('Course__Subject',flat=True))
    return render(request,'studentAttendance.html',{'subjects':subjects,'name':name})

def getAttendance(request):
    if request.is_ajax():
        try:
            subject=request.POST['subject']
            id=request.session['id']
            student=Student.objects.get(User__id=id)
            section, course=student.Section, student.Course
            if subject=='all':
                m={'subjects':{}}
                total_objs=Total_Lectures.objects.filter(Course__Course=course, Section=section)
                for obj in total_objs:
                    subject=obj.Course.Subject
                    m['subjects'][subject]={'total':obj.Month};
                    try:
                        attented=Student_Attendance.objects.get(Student__User__id=id, Course_Subject__Subject=subject).Month;
                        m['subjects'][subject]['attended']=attented;
                    except:
                        m['subjects'][subject]['attended']={};

            else:
                try:
                    month_attended=Student_Attendance.objects.get(Student__User__id=id, Course_Subject__Subject=subject).Month;
                except:
                    month_attended={}
                month_total=Total_Lectures.objects.get(Course__Course=course,Course__Subject=subject, Section=section).Month
                m={
                    'subjects':{
                        subject: {
                            'total':month_total,
                            'attended':month_attended
                        }
                    }
                }
            m=json.dumps(m)
            return HttpResponse(m)
        except:
            return HttpResponse('Error')

def viewStudentsAttendance(request):
    id=int(request.session['id'])
    subjects=Teacher_Subject.objects.filter(Teacher__User__id=id).values_list('Course__Subject', flat=True)
    return render(request,'studentsAttendance.html',{'subjects':subjects,'name':request.session['name']});

def getAttendances(request):
    if request.is_ajax():
        try:
            subject=request.POST['subject']
            course=request.session['course']
            section=request.POST['section']
            semester=Course_Subject_Semester.objects.get(Subject=subject,Course=course).Semester
            m,total={},0;
            try:
                total_month=Total_Lectures.objects.get(Course__Subject=subject,Course__Course__Course=course).Month;
                for month in total_month:
                    total+=total_month[month]
            except:
                total=0
            m['total']=total
            m['students']={};
            students=Student.objects.filter(Section=section, Course__Course=course, Semester=semester, Active=True)
            for student in students:
                s_id=student.User.id
                name="{} {}".format(student.User.first_name, student.User.last_name)
                m['students'][s_id]=[name]
                try:
                    attended_month=Student_Attendance.objects.get(Student__User__id=s_id, Course_Subject__Subject=subject).Month
                    attended=0;
                    for month in attended_month:
                        attended+=attended_month[month]
                except:
                    attended=0
                m['students'][s_id].append(attended)
            m=json.dumps(m);
            return HttpResponse(m)
        except:
            return HttpResponse('Error');

def generatePDF(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="attendance.pdf"'
    pdf=SimpleDocTemplate(response,pagesize=letter,title="Attendance Report")
    data1=[
        ['Teacher: ',request.session['name']],
        ['Subject: ',request.POST['subject']],
        ['Section: ',request.POST['section']],
    ]
    table1=Table(data1, hAlign='LEFT',spaceAfter=12)

    data2=[["Student ID","Name","Attended Lectures","Total Lectures"],]
    students_data=request.POST['students'].replace("_"," ").split(",")
    i=0;
    while i<len(students_data):
        student=[];
        for _ in range(4):
            student.append(students_data[i])
            i+=1;
        data2.append(student)

    table2=Table(data2)
    style=TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), colors.beige),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME',(0,0),(-1,0),'Courier-Bold'),
        ('FONTSIZE',(0,0),(-1,0),14),
        ('FONTSIZE',(0,1),(-1,-1),9),
        ('BOTTOMPADDING',(0,0),(-1,0),10),
        ('BOTTOMPADDING',(0,1),(-1,-1),3),
        ('GRID',(0,0),(-1,-1),1,colors.black)
    ])
    table2.setStyle(style)

    elems=[];
    elems.append(
        Paragraph(
            "Attendance Report",
            style=ParagraphStyle(
                name='normal',
                fontSize=20,
                alignment=TA_CENTER,
                spaceAfter=20
            )    
        )
    )
    elems.append(table1)
    elems.append(table2)
    pdf.build(elems)
    return response