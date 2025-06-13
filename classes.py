from abc import ABC, abstractmethod
from datetime import datetime

from utils import register_user

class AbstractRole(ABC):
    def __init__(self, _id, full_name, email, password_hash, created_at=None):
        self._id = _id
        self._full_name = full_name
        self._email = email
        self._password_hash = password_hash
        self._created_at = created_at or datetime.now().isoformat()

    @abstractmethod
    def get_profile(self):
        pass

    @abstractmethod
    def update_profile(self, **kwargs):
        pass


class User(AbstractRole):

    _users = []

    def __init__(self, _id, full_name, email, password_hash, role, created_at=None):
        super().__init__(_id, full_name, email, password_hash, created_at)
        self.role = role
        self._notifications = []
        User._users.append(self)

    def add_notification(self, message):
        self._notifications.append(message)

    def view_notifications(self):
        return self._notifications

    def delete_notification(self, index):
        if 0 <= index < len(self._notifications):
            del self._notifications[index]

    def get_profile(self):
        return {
            "id": self._id,
            "name": self._full_name,
            "email": self._email,
            "role": self.role,
            "created_at": self._created_at
        }

    def update_profile(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, f"_{key}"):
                setattr(self, f"_{key}", value)


class Teacher(User):

    _teachers = []

    def __init__(self, _id, full_name, email, password_hash, subjects=None, classes=None, created_at=None):
        super().__init__(_id, full_name, email, password_hash, "Teacher", created_at)
        self.subjects = subjects or []
        self.classes = classes or []
        self.assignments = {}
        Teacher._teachers.append(self)

    def create_assignment(self, title, description, deadline, subject, class_id):
        assignment = Assignment(title,description,deadline,subject,self._id, class_id)
        self.assignments[assignment.id] = assignment
        for student in Student._students:
            if subject in student.subjects:
                Notification("New assignment", student._id)

    def grade_assignment(self, assignment_id, student_id, grade):
        if assignment_id in self.assignments:
            grade = Grade(student_id, self.assignments[assignment_id].subject, grade, self._id)
            self.assignments[assignment_id].set_grade(student_id, grade)

    def view_student_progress(self, student_id):
        grades = []
        for assignment_id, assignment in self.assignments.items():
            if student_id in assignment.grades.keys():
                grades.append(assignment.grades[student_id])
        return grades


class Student(User):

    _students = []

    def __init__(self, _id, full_name, email, password_hash, grade, subjects=None, created_at=None):
        super().__init__(_id, full_name, email, password_hash, "Student")
        self.grade = grade
        self.subjects = subjects or {}  # {subject: teacher_id}
        self.assignments = {}   # {assignment_id: status}
        self.grades = {}   # {subject: [grade1, grade2, ...]}
        Student._students.append(self)

    def submit_assignment(self, assignment_id, content):
        if len(content)>500:
            raise KeyError("The content of submission must be less than 500.")
        self.assignments[assignment_id] = True
        Assignment.add_submission_(assignment_id, self._id, content)

    def view_grades(self, subject=None):
        if subject:
            return self.grades.get(subject, [])
        return self.grades

    def calculate_average_grade(self):
        total, count = 0, 0
        for grades in self.grades.values():
            total += sum(grades)
            count += len(grades)
        return total / count if count else 0


class Parent(User):

    _parents = []

    def __init__(self, _id, full_name, email, password_hash, children=None, created_at=None):
        super().__init__(_id, full_name, email, password_hash, "Parent")
        self.children = children or []
        Parent._parents.append(self)

    def view_child_grades(self, child_id):
        for student in Student._students:
            if student._id == child_id:
                return student.view_grades()

    def view_child_assignments(self, child_id):
        for student in Student._students:
            if student._id == child_id:
                return student.assignments()

    def receive_child_notification(self, child_id):
        for student in Student._students:
            if student._id == child_id:
                return student._notifications()


class Admin(User):

    _admins = []

    def __init__(self, _id, full_name, email, password_hash, permissions=None, created_at=None):
        super().__init__(_id, full_name, email, password_hash, "Admin")
        self.permissions = permissions or []
        Admin._admins.append(self)

    def add_user(self, user):
        pass

    def remove_user(self, user_id):
        pass

    def generate_report(self):
        pass


class Assignment:

    _count_of_assignments = 0
    _assignments = []

    def __init__(self, title, description, deadline, subject, teacher_id, class_id):
        Assignment._count_of_assignments += 1
        self.id = Assignment._count_of_assignments
        self.title = title
        self.description = description
        self.deadline = deadline  # str format (ISO)
        self.subject = subject
        self.teacher_id = teacher_id
        self.class_id = class_id
        self.submissions = {}  # {student_id: content}
        self.grades = {}  # {student_id: grade}
        Assignment._assignments.append(self)


    def add_submission(self, student_id, content):
        self.submissions[student_id] = content
        if datetime.fromisoformat(self.deadline) < datetime.now():
            Notification("You submitted late.")
    
    @classmethod
    def add_submission_(cls, assignment_id, student_id, content):
        for assignment in Assignment._assignments:
            if assignment.id == assignment_id:
                assignment.add_submission(student_id, content)

    def set_grade(self, student_id, grade):
        self.grades[student_id] = grade
        for student in Student._students:
            if student._id == student_id:
                if self.subject in student.grades.keys():
                    student.grades[self.subject].append(grade)
                else:
                    student.grades[self.subject] = [grade]

    def get_status(self):
        return {
            "submitted": list(self.submissions.keys()),
            "graded": list(self.grades.keys())
        }


class Grade:

    _count_of_grades = 0
    _grades = []

    def __init__(self, student_id, subject, value, teacher_id, date=None, comment=None):
        Grade._count_of_grades += 1
        self.id = Grade._count_of_grades
        self.student_id = student_id
        self.subject = subject
        self.value = value  # int, 1-5
        self.date = date or datetime.now().isoformat()   # ISO format
        self.teacher_id = teacher_id
        self.comment = comment
        Grade._grades.append(self)

    def update_grade(self, value, comment=None):
        self.value = value
        self.comment = comment

    def get_grade_info(self):
        return {
            "student_id": self.student_id,
            "subject": self.subject,
            "grade": self.value,
            "date": self.date,
            "comment": self.comment
        }


class Notification:

    _count_of_notifications = 0
    _notifications = []

    def __init__(self, message, recipient_id, created_at=None, priority="normal"):
        Notification._count_of_notifications += 1
        self.id = Notification._count_of_notifications
        self.message = message
        self.recipient_id = recipient_id
        self.created_at = created_at or datetime.now().isoformat()
        self.is_read = False
        self.priority = priority  # e.g., "low", "normal", "high"
        self.send()
        Notification._notifications.append(self)

    def send(self):
        for user in User._users:
            if user._id==self.recipient_id:
                user._notifications.append(self)
        return f"Notification sent to user {self.recipient_id}: {self.message}"

    def mark_as_read(self):
        self.is_read = True


class Schedule:

    def __init__(self, id, group_id, day):
        self.id = id
        self.group = group_id
        self.day = day
        self.lessons = {}  # {time: {"subject": ..., "teacher_id": ...}}

    def add_lesson(self, time, subject, teacher_id):
        if time not in self.lessons:
            self.lessons[time] = {"subject": subject, "teacher_id": teacher_id}

    def remove_lesson(self, time):
        if time in self.lessons:
            del self.lessons[time]

    def view_schedule(self):
        return self.lessons
