from django.db import models
from django.utils import timezone

class Student(models.Model):
    FNAME = models.CharField(max_length=50)
    LNAME = models.CharField(max_length=50)
    BIRTHDAY = models.DateField(null=True, blank=True)
    GENDER = models.CharField(max_length=10, blank=True)
    EMAIL = models.EmailField(unique=False)
    PHONE = models.CharField(max_length=10, blank=True)
    ADDRESS = models.CharField(max_length=200, blank=True)
    CITY = models.CharField(max_length=50, blank=True)
    COLLEGENAME = models.CharField(max_length=100, blank=True)
    QUALIFICATION = models.CharField(max_length=50, blank=True, null=True)
    BRANCH = models.CharField(max_length=50, blank=True)
    PASSING_YEAR = models.CharField(max_length=10, blank=True)
    TECHNOLOGY = models.CharField(max_length=50, blank=True)

    STATUS_CHOICES = [
        ('visiting', 'visiting'),
        ('adjoining', 'Adjoining'),
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='visiting'
    )

    visiting_at = models.DateTimeField(auto_now_add=True)
    joining_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.FNAME
    
    COURSE_CHOICES = [
        ('python', 'Python'),
        ('django', 'Django'),
        ('fullstack', 'Full Stack'),
    ]

    course = models.CharField(
        max_length=50,
        choices=COURSE_CHOICES,
        null=True,
        blank=True
    )

    total_fees = models.IntegerField(null=True, blank=True)
    paid_fees = models.IntegerField(default=0)
    remaining_fees = models.IntegerField(null=True, blank=True)


class Installment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="installments")
    amount = models.IntegerField()
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.FNAME} - {self.amount}"




class FollowUp(models.Model):
    student = models.ForeignKey("Student", on_delete=models.CASCADE, related_name="followups")
    remark = models.TextField()
    status = models.CharField(max_length=50)
    followup_date = models.DateField()
    followup_time = models.TimeField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.student.FNAME} - {self.followup_date}"
    
class QualificationOption(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class BranchOption(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class PassingYearOption(models.Model):
    year = models.CharField(max_length=10)

    def __str__(self):
        return self.year


class TechnologyOption(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=100)
    fees = models.IntegerField()

    def __str__(self):
        return self.name


class LetterTemplate(models.Model):
    LETTER_TYPES = (
        ('joining', 'Joining Letter'),
        ('offer', 'Offer Letter'),
        ('definition', 'Definition Letter'),
    )

    title = models.CharField(max_length=100)
    letter_type = models.CharField(max_length=20, choices=LETTER_TYPES, unique=True)
    content = models.TextField()

    def __str__(self):
        return self.title