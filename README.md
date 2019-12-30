# What it does:
It's an attendance system where students can mark their attendance for the subjects whose portal is opened by the teacher.
Teacher then closes portal, verifies attendance and uploads it. Teacher can also reopen the portal or cancel the attendance taken before it is uploaded, once attendance is uploaded it can't be modified. Only one portal can be opened by a teacher at a time.
Students can view their attendance subject-wise.
Teachers can view attendance of the subjects they are assigned and generate it's PDF.

It consists of 3 users: Admin, Teacher and Student.
After a teacher or a student registers, their data is added to database but their account is not activated.
A non-activated user cannot use the functionality provided on Dashboard.

# Admin Role:
1. He/She activates the user account.
2. He/She can add new courses and subjects to a course or edit them.
3. He/She assigns subjects to a teacher.
4. He/She has access to most of the data present in Database.

# Made Using:
Django, jQuery, JavaScript, Bootstrap 4, CSS, HTML, PostgreSQL

# Some Snapshots:
Home Page:
![](/snapshots/1.jpg)
![](/snapshots/2.jpg)
![](/snapshots/3.jpg)
![](/snapshots/4.jpg)
![](/snapshots/5.jpg)

Activating and Assigning Subject to teacher:
![](/snapshots/6.jpg)
![](/snapshots/7.jpg)

Opening Portal for Subject "Python"
![](/snapshots/8.jpg)

Student Marking Subject for "Python"
![](/snapshots/9.jpg)
![](/snapshots/10.jpg)

Closing Portal:
![](/snapshots/11.jpg)

Uploading Attendance:
![](/snapshots/12.jpg)

Teacher's Attendance Report
![](/snapshots/13.jpg)

Student Attendance:
![](/snapshots/14.jpg)
