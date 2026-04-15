from django.contrib import admin
from . models import *
from .models import LetterTemplate
# Register your models here.


admin.site.register(Student)
admin.site.register(QualificationOption)
admin.site.register(BranchOption)
admin.site.register(PassingYearOption)
admin.site.register(TechnologyOption)
admin.site.register(Course)

# admin.py


admin.site.register(LetterTemplate)
# Dear {{name}},

# We are pleased to inform you that {{pronoun}} have been selected for the {{course}}.

# {{pronoun_cap}} will start from {{date}}.

# Best Regards,
# Institute