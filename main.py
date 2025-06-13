from classes import Student, Teacher, Parent, Admin, Schedule, Notification, Assignment, Grade
from utils import register_user, export_all

student1 = register_user(Student, 1, "Ali Valiyev", "ali@mail.com", "password123", grade="9-A", subjects={"Math": 2})
student2 = register_user(Student, 2, "Laylo Karimova", "laylo@mail.com", "password123", grade="9-A", subjects={"Math": 2})
teacher1 = register_user(Teacher, 3, "Dilshod Qodirov", "dilshod@mail.com", "password123", subjects=["Math"], classes=["9-A"])
parent1 = register_user(Parent, 4, "Ota Valiyev", "ota@mail.com", "password123", children=[student1._id])
admin1 = register_user(Admin, 5, "Admin", "admin@mail.com", "adminpass")

teacher1.create_assignment(
    title="Algebra HW",
    description="Solve equations",
    deadline="2025-06-20T23:59",
    subject="Math",
    class_id="9-A"
)

student1.submit_assignment(1, "My solution for algebra")
student2.submit_assignment(1, "Another solution")

teacher1.grade_assignment(1, student1._id, 5)
teacher1.grade_assignment(1, student2._id, 4)

print("Parent sees grades:", parent1.view_child_grades(student1._id))

schedule = Schedule(1, "9-A", "Monday")
schedule.add_lesson("09:00", "Math", teacher1._id)
print("Schedule for 9-A:", schedule.view_schedule())

for notif in student1.view_notifications():
    print("Student1 notification:", notif.message if hasattr(notif, "message") else notif)

users_data = [u.get_profile() for u in Student._students + Teacher._teachers + Parent._parents + Admin._admins]
assignments_data = [{
    "id": a.id,
    "title": a.title,
    "description": a.description,
    "deadline": a.deadline,
    "subject": a.subject,
    "teacher_id": a.teacher_id,
    "class_id": a.class_id
} for a in Assignment._assignments]
grades_data = [{
    "id": g.id,
    "student_id": g.student_id,
    "subject": g.subject,
    "value": g.value,
    "date": g.date,
    "teacher_id": g.teacher_id,
    "comment": g.comment
} for g in Grade._grades]

export_all(users_data, assignments_data, grades_data)