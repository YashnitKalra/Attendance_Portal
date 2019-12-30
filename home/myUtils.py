import random, re
from .models import Portal, User, Courses
from django.core.mail import send_mail

def getPortalStatus(id):
    status='0'
    obj=Portal.objects.filter(Teacher__User_id=id)
    if obj.exists():
        obj=obj[0]
        if obj.Open:
            status='1'
        else:
            status='2'
    return status

def generateOTP():
    numbers=['0', '1', '2', '3', '4', '5', '6', '8', '7', '9']
    otp=[]
    for _ in range(6):
        otp.append(random.choice(numbers))
    return "".join(otp)

def sendMail(subject,message,to):
    fromMail="attendanceportal@noreply.com"
    send_mail(subject,message,fromMail,to)

def verifyUserDetails(firstname,lastname,username,email,password1,password2,course):
    messages=[]
    if not re.search("^[a-zA-Z\s]+$",firstname):
        messages.append("Error: Firstname can only have alphabets")
    if not re.search("^[a-zA-Z\s]+$",lastname):
        messages.append("Error: Lastname can only have alphabets")
    if re.search("\s",username):
        messages.append("Error: Spaces not allowed in Username")
    elif User.objects.filter(username=username).exists():
        messages.append("Error: Username already taken")
    if User.objects.filter(email=email).exists():
        messages.append('Error: Email already in use.')
    if password1!=password2:
        messages.append("Error: Passwords do not match")
    elif len(password1)<8:
        messages.append("Error: Minimum Password length should be 8 characters")
    if not Courses.objects.filter(Course=course).exists():
        messages.append('Error: Invalid Course')
    return messages