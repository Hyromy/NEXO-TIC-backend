from django.contrib import admin
from .models import *

admin.site.register(Role)
admin.site.register(Department)
admin.site.register(JobPosition)
admin.site.register(Employee)
admin.site.register(VacationPolicy)
admin.site.register(VacationPeriod)
admin.site.register(VacationRequest)
admin.site.register(VacationDetail)
admin.site.register(VacationApproval)
admin.site.register(Incident)
admin.site.register(IncidentJustification)
admin.site.register(Announcement)
admin.site.register(EmploymentHistory)
admin.site.register(EmployeeTermination)
admin.site.register(ReportHistory)
