from django.db import models
from django.contrib.auth.models import User


def _employee_display_name(employee):
    user = employee.user
    if not user:
        return "Unknown"
    full_name = f"{user.first_name} {user.last_name}".strip()
    return full_name or user.username

# -------------------------
#    first order models
# -------------------------
class Role(models.Model):
    name = models.CharField(max_length = 30, unique = True)
    description = models.CharField(max_length = 100)

    enabled = models.BooleanField(default = True)

    def __str__(self):
        return self.name
    
class Department(models.Model):
    name = models.CharField(max_length = 50, unique = True)
    description = models.CharField(max_length = 100)

    enabled = models.BooleanField(default = True)

    def __str__(self):
        return self.name

class VacationPolicy(models.Model):
    seniority_years = models.IntegerField()
    vacation_days = models.IntegerField()

    enabled = models.BooleanField(default = True)

    def __str__(self):
        return f"{self.seniority_years} years - {self.vacation_days} days"

# --------------------------
#    second order models
# --------------------------
class JobPosition(models.Model):
    name = models.CharField(max_length = 50, unique = True)
    description = models.CharField(max_length = 100)

    enabled = models.BooleanField(default = True)

    department = models.ForeignKey(Department, on_delete = models.CASCADE)

    def __str__(self):
        return self.name

# -------------------------
#    third order models
# -------------------------
class Employee(models.Model):
    user = models.OneToOneField(
        User,
        on_delete = models.CASCADE,
        null = True,
        blank = True    
    )
    join_date = models.DateField(auto_created = True)
    phone = models.CharField(max_length = 20, unique = True)

    enabled = models.BooleanField(default = True)

    job_position = models.ForeignKey(JobPosition, on_delete = models.CASCADE)

    def __str__(self):
        name = _employee_display_name(self)
        return f"{name} - {self.job_position.name}"



# --------------------------
#    fourth order models
# --------------------------
class CustomUser(models.Model):
    """
    Modelo legacy. Ya no se utiliza.
    Se mantiene solo por compatibilidad.
    """
    
    username = models.CharField(max_length = 50, unique = True)
    password = models.TextField()
    created_at = models.DateTimeField(auto_now_add = True)

    enabled = models.BooleanField(default = True)

    employee = models.OneToOneField(Employee, on_delete = models.CASCADE)
    role = models.ForeignKey(Role, on_delete = models.CASCADE)

    def __str__(self):
        return f"{self.username} - {_employee_display_name(self.employee)}"

class Incident(models.Model):
    type = models.CharField(max_length = 30)
    date = models.DateField(auto_now = True)
    justified = models.CharField(max_length = 20)
    notes = models.TextField()

    enabled = models.BooleanField(default = True)

    employee = models.ForeignKey(Employee, on_delete = models.CASCADE)

    def __str__(self):
        return f"{self.type} - {_employee_display_name(self.employee)}"

class EmploymentHistory(models.Model):
    update_at = models.DateTimeField(auto_now = True)
    description = models.TextField()

    enabled = models.BooleanField(default = True)

    employee = models.ForeignKey(Employee, on_delete = models.CASCADE)
    last_job_position = models.ForeignKey(JobPosition, on_delete = models.CASCADE, related_name = "last_job_position")
    new_job_position = models.ForeignKey(JobPosition, on_delete = models.CASCADE, related_name = "new_job_position")

    def __str__(self):
        employee_name = _employee_display_name(self.employee)
        return f"{employee_name} - {self.last_job_position.name} to {self.new_job_position.name}"

class ReportHistory(models.Model):
    type = models.CharField(max_length = 50)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    registered_at = models.DateTimeField(auto_now_add = True)
    notes = models.TextField()

    enabled = models.BooleanField(default = True)

    employee = models.ForeignKey(Employee, on_delete = models.CASCADE)

    def __str__(self):
        return f"{self.type} - {_employee_display_name(self.employee)}"

class VacationPeriod(models.Model):
    year = models.IntegerField()
    days_assigned = models.IntegerField()
    days_used = models.IntegerField()
    days_remaining = models.IntegerField()

    enabled = models.BooleanField(default = True)

    employee = models.ForeignKey(Employee, on_delete = models.CASCADE)

    def __str__(self):
        return f"{self.year} - {_employee_display_name(self.employee)}"

class EmployeeTermination(models.Model):
    date = models.DateField(auto_now = True)
    type = models.CharField(max_length = 30)
    reason = models.TextField()

    enabled = models.BooleanField(default = True)

    employee = models.ForeignKey(Employee, on_delete = models.CASCADE)

    def __str__(self):
        return f"{self.type} - {_employee_display_name(self.employee)}"

class Announcement(models.Model):
    title = models.CharField(max_length = 100)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add = True)
    priority = models.CharField(max_length = 20)

    enabled = models.BooleanField(default = True)

    author = models.ForeignKey(Employee, on_delete = models.CASCADE)

    def __str__(self):
        return self.title

class VacationRequest(models.Model):
    date = models.DateTimeField(auto_now_add = True)
    status = models.CharField(max_length = 20)

    enabled = models.BooleanField(default = True)

    employee = models.ForeignKey(Employee, on_delete = models.CASCADE)

    def __str__(self):
        return f"Vacation Request - {_employee_display_name(self.employee)} - {self.status}"

# -------------------------
#    fifth order models
# -------------------------
class IncidentJustification(models.Model):
    reason = models.TextField()
    evidence = models.TextField()
    date = models.DateTimeField(auto_now_add = True)
    status = models.CharField(max_length = 20)
    notes = models.TextField()

    enabled = models.BooleanField(default = True)

    incident = models.ForeignKey(Incident, on_delete = models.CASCADE)

class VacationDetail(models.Model):
    selected_day = models.DateField()

    enabled = models.BooleanField(default = True)

    vacation_request = models.ForeignKey(VacationRequest, on_delete = models.CASCADE)

    def __str__(self):
        employee_name = _employee_display_name(self.vacation_request.employee)
        return f"{self.selected_day} - {employee_name}"

class VacationApproval(models.Model):
    date = models.DateTimeField(auto_now_add = True)
    decision = models.CharField(max_length = 20)
    note = models.TextField()

    enabled = models.BooleanField(default = True)

    vacation_request = models.ForeignKey(VacationRequest, on_delete = models.CASCADE)
    approver = models.ForeignKey(Employee, on_delete = models.CASCADE)

    def __str__(self):
        request_employee_name = _employee_display_name(self.vacation_request.employee)
        approver_name = _employee_display_name(self.approver)
        return f"{self.decision} - {request_employee_name} - Approver: {approver_name}"
