from django.urls import path
from .views import form, dashboard, students, courses, visiting, JoiningStudents, fees, update_status
from .import views

urlpatterns = [
    path("", form, name="form"),
    path("dashboard/", dashboard, name="dashboard"),
    path("students/", students, name="students"),
    path("courses/", courses, name="courses"),
    path("visiting/", visiting, name="visiting"),
    path("JoiningStudents/", JoiningStudents, name="JoiningStudents"),
    path("fees/", fees, name="fees"),
    path('update-status/<int:id>/', update_status, name='update_status'),

    path('student/view/<int:id>/', views.student_view, name='student_view'),
    path('student/edit/<int:id>/', views.student_edit, name='student_edit'),
    path('fees-discussion/<int:id>/', views.fees_discussion, name='fees_discussion'),

    path('receipt/<int:id>/', views.generate_receipt, name='generate_receipt'),
    path("payment-history/<int:id>/", views.payment_history, name="payment_history"),
    path('add-followup/<int:id>/', views.add_followup, name='add_followup'),
    path("followup/<int:id>/", views.followup_details, name="followup_details"),
    path('letter/<int:student_id>/<str:letter_type>/', views.generate_letter, name='generate_letter'),
]

