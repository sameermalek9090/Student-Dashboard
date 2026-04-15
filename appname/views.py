from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Student,Installment, FollowUp
from django.db.models import Count
from datetime import datetime, timedelta
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils.timezone import now
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
import os
import io
from .models import Course
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import QualificationOption, BranchOption, PassingYearOption, TechnologyOption


# ✅ STUDENT REGISTRATION FORM

def form(request):

    qualifications = QualificationOption.objects.all()
    branches = BranchOption.objects.all()
    years = PassingYearOption.objects.all()
    technologies = TechnologyOption.objects.all()

    if request.method == "POST":

        fname = request.POST.get("FNAME")
        lname = request.POST.get("LNAME")

        Student.objects.create(
            FNAME=fname,
            LNAME=lname,
            BIRTHDAY=request.POST.get("BIRTHDAY"),
            GENDER=request.POST.get("GENDER"),
            EMAIL=request.POST.get("EMAIL"),
            PHONE=request.POST.get("PHONE"),  
            ADDRESS=request.POST.get("ADDRESS"),
            CITY=request.POST.get("CITY"),
            COLLEGENAME=request.POST.get("COLLEGENAME"),
            QUALIFICATION=request.POST.get("QUALIFICATION"),
            BRANCH=request.POST.get("BRANCH"),
            PASSING_YEAR=request.POST.get("PASSING_YEAR"),
            TECHNOLOGY=request.POST.get("TECHNOLOGY"),
        )

        messages.success(request, f"Welcome {fname} {lname}! Registration Successful 🎉")
        return redirect("form")

    return render(request, "form.html", {
        "qualifications": qualifications,
        "branches": branches,
        "years": years,
        "technologies": technologies
    })




# ✅ ADMIN DASHBOARD ONLY
@login_required
def dashboard(request):

     # 🔹 Top cards
    students = Student.objects.all()

    # ===== TOP CARDS =====
    total_students = students.count()
    total_courses = students.values('TECHNOLOGY').distinct().count()
    total_videos = total_courses * 5
    total_earning = total_students * 999

    # ===== SAFE CHART DATA (NO DB DATE DEPENDENCY) =====
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    counts = [
        total_students // 7,
        total_students // 6,
        total_students // 5,
        total_students // 4,
        total_students // 3,
        total_students // 2,
        total_students,
    ]

    years = ["2021", "2022", "2023", "2024", "2025"]
    analysis = [
        students.filter(PASSING_YEAR=y).count() for y in years
    ]

    # ===== CITY DATA =====
    city_data = students.values('CITY').annotate(total=Count('CITY'))
    cities = [c['CITY'] for c in city_data]
    city_counts = [c['total'] for c in city_data]

    # ===== TECHNOLOGY DATA =====
    tech_data = students.values('TECHNOLOGY').annotate(total=Count('TECHNOLOGY'))
    tech_labels = [t['TECHNOLOGY'] for t in tech_data]
    tech_counts = [t['total'] for t in tech_data]

    context = {
        'students': students,
        'total': total_students,
        'total_courses': total_courses,
        'total_videos': total_videos,
        'total_earning': total_earning,
        'days': days,
        'counts': counts,
        'years': years,
        'analysis': analysis,
        'cities': cities,
        'city_counts': city_counts,
        'tech_labels': tech_labels,
        'tech_counts': tech_counts,
    }
    # ✅ Block normal users
    if not request.user.is_superuser:
        return redirect("/")

    students = Student.objects.all().order_by("-id")
    total = students.count()

    # TECHNOLOGY DATA
    technology_data = Student.objects.values("TECHNOLOGY").annotate(total=Count("TECHNOLOGY"))
    tech_labels = [t["TECHNOLOGY"] for t in technology_data]
    tech_counts = [t["total"] for t in technology_data]

    # ✅ CITY DATA
    city_data = Student.objects.values("CITY").annotate(total=Count("CITY"))
    cities = [c["CITY"] for c in city_data]
    city_counts = [c["total"] for c in city_data]

    # ✅ REGISTRATION GROWTH (last 7 days)
    today = datetime.today()
    days = []
    counts = []

    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        days.append(d.strftime("%a"))
        counts.append(
            Student.objects.filter(BIRTHDAY__lte=today).count()
        )

    installments = Installment.objects.select_related('student').order_by('-payment_date')

    return render(request, "dashboard.html", {
        "students": students,
        "total": total,
        "cities": cities,
        "city_counts": city_counts,
        "days": days,
        "counts": counts,
        "counts": counts,
        "tech_labels": tech_labels,
        "tech_counts": tech_counts,
        "installments": installments
        
    })


@login_required
def students(request):
    students = Student.objects.all().order_by('-id')
    total = students.count()
    return render(request, 'students.html', {
        'students': students,
        'total': total
    })


def courses(request):
    return render(request,'courses.html')

def visiting(request):
    students = Student.objects.filter(status='visiting').order_by('-visiting_at')
    total = students.count()
    return render(request, 'visiting.html', {
        'students': students,
        'total': total
    })


def JoiningStudents(request):
    students = Student.objects.filter(status='adjoining')  # ✅ NO .values()
    total = students.count()
    return render(request, 'JoiningStudents.html', {
        'students': students,
        'total': total
    })




@login_required
def fees(request):

    # ✅ ONLY JOINING STUDENTS (adjoining)
    students = Student.objects.filter(status='adjoining')

    # ===== TOP CARDS =====
    total_students = students.count()

    total_fees = students.aggregate(
        total=Sum('total_fees')
    )['total'] or 0

    collected = students.aggregate(
        total=Sum('paid_fees')
    )['total'] or 0

    remaining = students.aggregate(
        total=Sum('remaining_fees')
    )['total'] or 0

    # ===== PAYMENT STATUS COUNT =====
    paid = students.filter(remaining_fees=0).count()

    partial = students.filter(
        paid_fees__gt=0,
        remaining_fees__gt=0
    ).count()

    pending = students.filter(paid_fees=0).count()

    # ===== MONTHLY COLLECTION (LAST 6 MONTHS) =====
    labels = []
    values = []

    for i in range(5, -1, -1):
        date = timezone.now() - timedelta(days=30*i)

        month_total = students.filter(
            joining_at__month=date.month
        ).aggregate(
            total=Sum('paid_fees')
        )['total'] or 0

        labels.append(date.strftime("%b"))
        values.append(month_total)

    context = {
        'students': students,
        'total_students': total_students,
        'total_fees': total_fees,
        'collected': collected,
        'remaining': remaining,
        'paid': paid,
        'partial': partial,
        'pending': pending,
        'chart_labels': labels,
        'chart_values': values,
    }

    return render(request, 'fees.html', context)


def update_status(request, id):
    student = get_object_or_404(Student, id=id)

    if request.method == "POST":
        new_status = request.POST.get("status")

        if new_status == "adjoining":
            student.course = request.POST.get("course")
            student.total_fees = int(request.POST.get("total_fees", 0))
            student.paid_fees = int(request.POST.get("paid_fees", 0))
            student.remaining_fees = student.total_fees - student.paid_fees
            student.joining_at = timezone.now()

        student.status = new_status
        student.save()

    return redirect('/JoiningStudents/')

def student_view(request, id):
    student = get_object_or_404(Student, id=id)
    return render(request, 'student_view.html', {'s': student})





def student_edit(request, id):
    student = get_object_or_404(Student, id=id)

    if request.method == "POST":

        student.course = request.POST.get("course")

        total_fees = request.POST.get("total_fees")
        if total_fees:
            student.total_fees = int(total_fees)

        installment = request.POST.get("installment")
        installment = int(installment) if installment else 0

        if installment > 0:
            Installment.objects.create(
                student=student,
                amount=installment
            )

            student.paid_fees = (student.paid_fees or 0) + installment
            student.remaining_fees = student.total_fees - student.paid_fees

        student.save()

        # LETTER CHECKBOXES
        if request.POST.get("joining_letter"):
            return generate_letter(student, "joining")

        if request.POST.get("offer_letter"):
            return generate_letter(student, "offer")

        if request.POST.get("definition_letter"):
            return generate_letter(student, "definition")

        return redirect("student_edit", id=student.id)

    installments = student.installments.all().order_by("-payment_date")

    return render(request, "student_edit.html", {
        "s": student,
        "installments": installments
    })







def fees_discussion(request, id):

    student = get_object_or_404(Student, id=id)
    courses = Course.objects.all()

    if request.method == "POST":

        course_id = request.POST.get("course")
        paid = request.POST.get("paid_fees")

        course = Course.objects.get(id=course_id)

        paid = int(paid) if paid else 0

        student.course = course.name
        student.total_fees = course.fees
        student.paid_fees = paid
        student.remaining_fees = course.fees - paid
        student.status = "adjoining"
        student.joining_at = timezone.now()

        student.save()

        if paid > 0:
            Installment.objects.create(
                student=student,
                amount=paid
            )

        return redirect("JoiningStudents")

    return render(request,"fees_discussion.html",{
        "student":student,
        "courses":courses
    })


def payment_history(request, id):
    student = get_object_or_404(Student, id=id)
    installments = student.installments.all().order_by("-payment_date")

    return render(request, "payment_history.html", {
        "student": student,
        "installments": installments
    })






def generate_receipt(request, id):
    student = get_object_or_404(Student, id=id)
    installments = student.installments.all().order_by("payment_date")

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=(595, 842),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph("<b>Student Full Payment Receipt</b>", styles["Title"]))
    elements.append(Spacer(1, 20))

    # Student Info
    info = [
        ["Student Name", f"{student.FNAME} {student.LNAME}"],
        ["Phone", student.PHONE],
        ["Course", student.course],
        ["Total Fees", f"₹ {student.total_fees}"],
        ["Paid Fees", f"₹ {student.paid_fees}"],
        ["Remaining", f"₹ {student.remaining_fees}"],
    ]

    table = Table(info, colWidths=[180, 330])
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (0,-1), colors.lightgrey),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 25))

    # Payment History
    elements.append(Paragraph("<b>Payment History</b>", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    data = [["No", "Date", "Amount"]]

    for i, inst in enumerate(installments, start=1):
        data.append([
            str(i),
            inst.payment_date.strftime("%d-%m-%Y %I:%M %p"),
            f"₹ {inst.amount}"
        ])

    pay_table = Table(data, colWidths=[60, 300, 150])
    pay_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#4F46E5")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ]))

    elements.append(pay_table)
    elements.append(Spacer(1, 25))

    # Status
    if student.remaining_fees == 0:
        status = "FULLY PAID"
    else:
        status = "PARTIAL PAYMENT"

    elements.append(Paragraph(f"<b>Status:</b> {status}", styles["Heading3"]))
    elements.append(Spacer(1, 30))

    elements.append(Paragraph(
        "This is a system generated receipt.",
        styles["Normal"]
    ))

    doc.build(elements)
    buffer.seek(0)

    return HttpResponse(buffer, content_type="application/pdf")


def generate_letter(student, letter_type):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=(595,842),
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    elements = []
    styles = getSampleStyleSheet()

    # 👉 Gender handling
    pronoun, pronoun_cap = get_pronoun(student.GENDER)

    # 👉 Logo
    logo_path = os.path.join("static/images/logo.png")
    try:
        logo = Image(logo_path, width=140, height=60)
        elements.append(logo)
    except:
        pass

    elements.append(Spacer(1,30))

    # 👉 LETTER CONTENT
    if letter_type == "joining":
        title = "Joining Letter"

        content = f"""
        Dear {student.FNAME} {student.LNAME},<br/><br/>

        We are pleased to welcome you to <b>Way To Web Training Institute</b>.

        {pronoun_cap} has successfully joined the <b>{student.course}</b> course.

        We wish {pronoun} success in {pronoun} learning journey.
        """

    elif letter_type == "offer":
        title = "Offer Letter"

        content = f"""
        Dear {student.FNAME} {student.LNAME},<br/><br/>

        Congratulations! {pronoun_cap} is offered admission in the 
        <b>{student.course}</b> program at Way To Web.

        Please confirm {pronoun} admission by completing the enrollment process.
        """

    else:
        title = "Definition Letter"

        content = f"""
        This letter certifies that <b>{student.FNAME} {student.LNAME}</b>
        is a student of <b>Way To Web Training Institute</b> and enrolled
        in the <b>{student.course}</b> program.

        {pronoun_cap} is currently pursuing the course successfully.
        """

    # 👉 Title Styling
    elements.append(Paragraph(f"<b>{title}</b>", styles["Title"]))
    elements.append(Spacer(1,30))

    # 👉 Content
    elements.append(Paragraph(content, styles["Normal"]))
    elements.append(Spacer(1,60))

    # 👉 Footer
    elements.append(Paragraph(
        "Authorized Signatory<br/>Way To Web",
        styles["Normal"]
    ))

    doc.build(elements)

    buffer.seek(0)

    return HttpResponse(buffer, content_type="application/pdf")


from .models import FollowUp
from django.utils import timezone

def add_followup(request, id):

    student = get_object_or_404(Student, id=id)

    if request.method == "POST":

        status = request.POST.get("status")

        # ✅ If adjoining → go to fees discussion
        if status == "adjoining":
            student.status = "adjoining"
            student.save()

            return redirect("fees_discussion", id=student.id)

        # ✅ Otherwise save followup
        followup_date = request.POST.get("date")
        followup_time = request.POST.get("time")
        remark = request.POST.get("remark")

        FollowUp.objects.create(
            student=student,
            status=status,
            remark=remark,
            followup_date=followup_date,
            followup_time=followup_time
        )

        # ❗ IMPORTANT
        # Do NOT change status from visiting
        student.status = "visiting"
        student.save()

    return redirect("visiting")




def followup_details(request, id):

    student = get_object_or_404(Student, id=id)

    followups = FollowUp.objects.filter(
        student=student
    ).order_by("-created_at")

    return render(request, "followup_details.html", {
        "student": student,
        "followups": followups
    })


def get_pronoun(gender):
    if gender.lower() == "male":
        return "he", "He"
    else:
        return "she", "She"
    



from django.shortcuts import render
from django.template import Template, Context
from .models import LetterTemplate

def generate_dynamic_letter(request, student, letter_type): 
    template_obj = LetterTemplate.objects.get(letter_type=letter_type)

    django_template = Template(template_obj.content)
    context = Context({
        'student_name': student.name,
        'course': student.course,
        'phone': student.phone,
    })

    final_content = django_template.render(context)

    return render(request, 'letter_template.html', {
        'content': final_content
    })