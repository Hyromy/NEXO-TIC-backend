from django.test import TestCase
from datetime import date, datetime
from django.db.utils import IntegrityError
from django.utils import timezone
from django.contrib.auth.models import User

from apps.models.models import (
    Announcement,
    VacationRequest,
    VacationPolicy,
    CustomUser,
    Department,
    Employee,
    EmployeeTermination,
    EmploymentHistory,
    Incident,
    IncidentJustification,
    JobPosition,
    ReportHistory,
    Role,
    VacationApproval,
    VacationDetail,
    VacationPeriod,
)


def create_employee_for_tests(
    *,
    first_name,
    last_name,
    phone,
    job_position,
    username,
    email,
    join_date=None,
):
    user = User.objects.create_user(
        username=username,
        email=email,
        password="TestPass123",
        first_name=first_name,
        last_name=last_name,
    )
    return Employee.objects.create(
        user=user,
        join_date=join_date or date.today(),
        phone=phone,
        job_position=job_position,
    )

class RoleModelTestCase(TestCase):
    """Role model test cases"""
    
    def test_create_role(self):
        """Check that a Role can be created"""

        role = Role.objects.create(
            name = "Admin",
            description = "Administrator role"
        )
        self.assertEqual(role.name, "Admin")
        self.assertTrue(role.enabled)
    
    def test_role_str(self):
        """Check the string representation of Role"""

        role = Role.objects.create(
            name = "Manager",
            description = "Manager role"
        )
        self.assertEqual(str(role), "Manager")
    
    def test_role_unique_name(self):
        """Check that Role name is unique"""

        Role.objects.create(
            name = "Admin",
            description = "First"
        )
        
        with self.assertRaises(Exception):
            Role.objects.create(
                name = "Admin",
                description = "Second"
            )

class DepartmentModelTestCase(TestCase):
    """Department model test cases"""
    
    def test_create_department(self):
        """Check that a Department can be created"""
        
        dept = Department.objects.create(
            name = "IT",
            description = "Information Technology"
        )
        self.assertEqual(dept.name, "IT")
        self.assertTrue(dept.enabled)
    
    def test_department_str(self):
        """Check the string representation of Department"""
        
        dept = Department.objects.create(
            name = "HR",
            description = "Human Resources"
        )
        self.assertEqual(str(dept), "HR")
    
    def test_department_unique_name(self):
        """Check that Department name is unique"""
        
        Department.objects.create(
            name = "Engineering",
            description = "First"
        )
        
        with self.assertRaises(Exception):
            Department.objects.create(
                name = "Engineering",
                description = "Second"
            )

class VacationPolicyModelTestCase(TestCase):
    """VacationPolicy model test cases"""
    
    def test_create_vacation_policy(self):
        """Check that a VacationPolicy can be created"""
        
        policy = VacationPolicy.objects.create(
            seniority_years = 5,
            vacation_days = 15
        )
        self.assertEqual(policy.seniority_years, 5)
        self.assertEqual(policy.vacation_days, 15)
        self.assertTrue(policy.enabled)
    
    def test_vacation_policy_str(self):
        """Check the string representation of VacationPolicy"""
        
        policy = VacationPolicy.objects.create(
            seniority_years = 3,
            vacation_days = 10
        )
        self.assertEqual(str(policy), "3 years - 10 days")

class JobPositionModelTestCase(TestCase):
    """JobPosition model test cases"""
    
    def setUp(self):
        """Create a Department for use in all tests"""
        
        self.department = Department.objects.create(
            name = "Engineering",
            description = "Engineering Department"
        )
    
    def test_create_job_position(self):
        """Check that a JobPosition can be created"""
        
        position = JobPosition.objects.create(
            name = "Developer",
            description = "Software Developer",
            department = self.department
        )
        self.assertEqual(position.name, "Developer")
        self.assertEqual(position.department, self.department)
        self.assertTrue(position.enabled)
    
    def test_job_position_str(self):
        """Check the string representation of JobPosition"""
        
        position = JobPosition.objects.create(
            name = "Designer",
            description = "UI/UX Designer",
            department = self.department
        )
        self.assertEqual(str(position), "Designer")
    
    def test_delete_department_deletes_positions(self):
        """Check that deleting a Department deletes its JobPositions (CASCADE)"""
        
        position = JobPosition.objects.create(
            name = "Tester",
            description = "QA Tester",
            department = self.department
        )
        
        self.department.delete()
        
        self.assertFalse(
            JobPosition.objects.filter(id = position.id).exists()
        )

class EmployeeModelTestCase(TestCase):
    """Employee model test cases"""
    
    def setUp(self):
        """Create necessary data for Employee"""
        
        self.department = Department.objects.create(
            name = "Sales",
            description = "Sales Department"
        )
        self.position = JobPosition.objects.create(
            name = "Sales Rep",
            description = "Sales Representative",
            department = self.department
        )
    
    def test_create_employee(self):
        """Check that an Employee can be created"""

        employee = create_employee_for_tests(
            first_name="Juan",
            last_name="Pérez",
            phone="555-1234",
            job_position=self.position,
            username="juan.perez",
            email="juan.perez@company.com",
            join_date=date(2024, 1, 15),
        )
        self.assertEqual(employee.user.first_name, "Juan")
        self.assertEqual(employee.user.email, "juan.perez@company.com")
        self.assertTrue(employee.enabled)
    
    def test_employee_str(self):
        """Check the string representation of Employee"""

        employee = create_employee_for_tests(
            first_name="María",
            last_name="García",
            phone="555-5678",
            job_position=self.position,
            username="maria.garcia",
            email="maria.garcia@company.com",
            join_date=date(2024, 2, 1),
        )
        expected = "María García - Sales Rep"
        self.assertEqual(str(employee), expected)
    
    def test_employee_phone_unique(self):
        """Check that Employee phone is unique"""

        create_employee_for_tests(
            first_name="Carlos",
            last_name="López",
            phone="555-1111",
            job_position=self.position,
            username="carlos.lopez",
            email="carlos@company.com",
            join_date=date(2024, 1, 1),
        )

        with self.assertRaises(IntegrityError):
            Employee.objects.create(
                phone="555-1111",
                job_position=self.position,
            )
    
    def test_employee_user_optional(self):
        """Check that user relation is optional"""

        employee = Employee.objects.create(
            join_date=date(2024, 3, 1),
            phone="555-9999",
            job_position=self.position,
        )
        self.assertIsNone(employee.user)

class CustomUserModelTestCase(TestCase):
    """CustomUser model test cases"""
    
    def setUp(self):
        """Create necessary data for CustomUser"""
        
        self.department = Department.objects.create(
            name = "IT",
            description = "Information Technology"
        )
        self.position = JobPosition.objects.create(
            name = "Developer",
            description = "Software Developer",
            department = self.department
        )
        self.employee = create_employee_for_tests(
            first_name="Luis",
            last_name="Ramírez",
            phone="555-0001",
            job_position=self.position,
            username="luis.ramirez",
            email="luis.ramirez@company.com",
            join_date=date(2023, 1, 1),
        )
        self.role = Role.objects.create(
            name = "User",
            description = "Regular user"
        )
    
    def test_create_custom_user(self):
        """Check that a CustomUser can be created"""
        
        user = CustomUser.objects.create(
            username = "lramirez",
            password = "hashed_password",
            employee = self.employee,
            role = self.role
        )
        self.assertEqual(user.username, "lramirez")
        self.assertEqual(user.employee, self.employee)
        self.assertEqual(user.role, self.role)
        self.assertTrue(user.enabled)
    
    def test_custom_user_str(self):
        """Check the string representation of CustomUser"""
        
        user = CustomUser.objects.create(
            username = "lramirez",
            password = "hashed_password",
            employee = self.employee,
            role = self.role
        )
        expected = "lramirez - Luis Ramírez"
        self.assertEqual(str(user), expected)
    
    def test_custom_user_created_at(self):
        """Check that created_at is auto-generated"""
        
        user = CustomUser.objects.create(
            username = "testuser",
            password = "password",
            employee = self.employee,
            role = self.role
        )
        self.assertIsNotNone(user.created_at)

class IncidentModelTestCase(TestCase):
    """Incident model test cases"""
    
    def setUp(self):
        """Create necessary data for Incident"""
        
        self.department = Department.objects.create(
            name = "HR",
            description = "Human Resources"
        )
        self.position = JobPosition.objects.create(
            name = "HR Manager",
            description = "Human Resources Manager",
            department = self.department
        )
        self.employee = create_employee_for_tests(
            first_name="Pedro",
            last_name="Sánchez",
            phone="555-0002",
            job_position=self.position,
            username="pedro.sanchez",
            email="pedro.sanchez@company.com",
            join_date=date(2023, 5, 1),
        )
    
    def test_create_incident(self):
        """Check that an Incident can be created"""
        
        incident = Incident.objects.create(
            type = "Tardiness",
            justified = "No",
            notes = "Arrived 30 minutes late",
            employee = self.employee
        )
        self.assertEqual(incident.type, "Tardiness")
        self.assertEqual(incident.employee, self.employee)
        self.assertTrue(incident.enabled)
    
    def test_incident_str(self):
        """Check the string representation of Incident"""
        
        incident = Incident.objects.create(
            type = "Absence",
            justified = "Yes",
            notes = "Medical appointment",
            employee = self.employee
        )
        expected = "Absence - Pedro Sánchez"
        self.assertEqual(str(incident), expected)
    
    def test_incident_date_auto(self):
        """Check that date is auto-generated"""
        
        incident = Incident.objects.create(
            type = "Leave",
            justified = "Yes",
            notes = "Personal leave",
            employee = self.employee
        )
        self.assertIsNotNone(incident.date)

class EmploymentHistoryModelTestCase(TestCase):
    """EmploymentHistory model test cases"""
    
    def setUp(self):
        """Create necessary data for EmploymentHistory"""
        
        self.department = Department.objects.create(
            name = "Operations",
            description = "Operations Department"
        )
        self.position1 = JobPosition.objects.create(
            name = "Junior Analyst",
            description = "Junior level analyst",
            department = self.department
        )
        self.position2 = JobPosition.objects.create(
            name = "Senior Analyst",
            description = "Senior level analyst",
            department = self.department
        )
        self.employee = create_employee_for_tests(
            first_name="Sofia",
            last_name="Hernández",
            phone="555-0003",
            job_position=self.position2,
            username="sofia.hernandez",
            email="sofia.hernandez@company.com",
            join_date=date(2022, 1, 1),
        )
    
    def test_create_employment_history(self):
        """Check that an EmploymentHistory can be created"""
        
        history = EmploymentHistory.objects.create(
            description = "Promoted to Senior Analyst",
            employee = self.employee,
            last_job_position = self.position1,
            new_job_position = self.position2
        )
        self.assertEqual(history.employee, self.employee)
        self.assertEqual(history.last_job_position, self.position1)
        self.assertEqual(history.new_job_position, self.position2)
        self.assertTrue(history.enabled)
    
    def test_employment_history_str(self):
        """Check the string representation of EmploymentHistory"""
        
        history = EmploymentHistory.objects.create(
            description = "Position change",
            employee = self.employee,
            last_job_position = self.position1,
            new_job_position = self.position2
        )
        expected = "Sofia Hernández - Junior Analyst to Senior Analyst"
        self.assertEqual(str(history), expected)

class ReportHistoryModelTestCase(TestCase):
    """ReportHistory model test cases"""
    
    def setUp(self):
        """Create necessary data for ReportHistory"""
        
        self.department = Department.objects.create(
            name = "Finance",
            description = "Finance Department"
        )
        self.position = JobPosition.objects.create(
            name = "Accountant",
            description = "Financial Accountant",
            department = self.department
        )
        self.employee = create_employee_for_tests(
            first_name="Diego",
            last_name="Morales",
            phone="555-0004",
            job_position=self.position,
            username="diego.morales",
            email="diego.morales@company.com",
            join_date=date(2023, 3, 1),
        )
    
    def test_create_report_history(self):
        """Check that a ReportHistory can be created"""
        
        report = ReportHistory.objects.create(
            type = "Overtime",
            start_at = timezone.make_aware(datetime(2024, 11, 1, 8, 0)),
            end_at = timezone.make_aware(datetime(2024, 11, 30, 18, 0)),
            notes = "Monthly overtime report",
            employee = self.employee
        )
        self.assertEqual(report.type, "Overtime")
        self.assertEqual(report.employee, self.employee)
        self.assertTrue(report.enabled)
    
    def test_report_history_str(self):
        """Check the string representation of ReportHistory"""
        
        report = ReportHistory.objects.create(
            type = "Attendance",
            start_at = timezone.make_aware(datetime(2024, 11, 1, 8, 0)),
            end_at = timezone.make_aware(datetime(2024, 11, 30, 18, 0)),
            notes = "Monthly attendance",
            employee = self.employee
        )
        expected = "Attendance - Diego Morales"
        self.assertEqual(str(report), expected)

class VacationPeriodModelTestCase(TestCase):
    """VacationPeriod model test cases"""
    
    def setUp(self):
        """Create necessary data for VacationPeriod"""
        
        self.department = Department.objects.create(
            name = "Marketing",
            description = "Marketing Department"
        )
        self.position = JobPosition.objects.create(
            name = "Marketing Specialist",
            description = "Marketing professional",
            department = self.department
        )
        self.employee = create_employee_for_tests(
            first_name="Carmen",
            last_name="Ruiz",
            phone="555-0005",
            job_position=self.position,
            username="carmen.ruiz",
            email="carmen.ruiz@company.com",
            join_date=date(2021, 1, 1),
        )
    
    def test_create_vacation_period(self):
        """Check that a VacationPeriod can be created"""
        
        period = VacationPeriod.objects.create(
            year = 2024,
            days_assigned = 15,
            days_used = 5,
            days_remaining = 10,
            employee = self.employee
        )
        self.assertEqual(period.year, 2024)
        self.assertEqual(period.days_remaining, 10)
        self.assertTrue(period.enabled)
    
    def test_vacation_period_str(self):
        """Check the string representation of VacationPeriod"""
        
        period = VacationPeriod.objects.create(
            year = 2024,
            days_assigned = 15,
            days_used = 5,
            days_remaining = 10,
            employee = self.employee
        )
        expected = "2024 - Carmen Ruiz"
        self.assertEqual(str(period), expected)

class EmployeeTerminationModelTestCase(TestCase):
    """EmployeeTermination model test cases"""
    
    def setUp(self):
        """Create necessary data for EmployeeTermination"""
        
        self.department = Department.objects.create(
            name = "Legal",
            description = "Legal Department"
        )
        self.position = JobPosition.objects.create(
            name = "Lawyer",
            description = "Corporate Lawyer",
            department = self.department
        )
        self.employee = create_employee_for_tests(
            first_name="Roberto",
            last_name="Díaz",
            phone="555-0006",
            job_position=self.position,
            username="roberto.diaz",
            email="roberto.diaz@company.com",
            join_date=date(2020, 6, 1),
        )
    
    def test_create_employee_termination(self):
        """Check that an EmployeeTermination can be created"""
        
        termination = EmployeeTermination.objects.create(
            type = "Resignation",
            reason = "Better opportunity",
            employee = self.employee
        )
        self.assertEqual(termination.type, "Resignation")
        self.assertEqual(termination.employee, self.employee)
        self.assertTrue(termination.enabled)
    
    def test_employee_termination_str(self):
        """Check the string representation of EmployeeTermination"""
        
        termination = EmployeeTermination.objects.create(
            type = "Layoff",
            reason = "Company restructuring",
            employee = self.employee
        )
        expected = "Layoff - Roberto Díaz"
        self.assertEqual(str(termination), expected)

class AnnouncementModelTestCase(TestCase):
    """Announcement model test cases"""
    
    def setUp(self):
        """Create necessary data for Announcement"""
        
        self.department = Department.objects.create(
            name = "Admin",
            description = "Administration"
        )
        self.position = JobPosition.objects.create(
            name = "CEO",
            description = "Chief Executive Officer",
            department = self.department
        )
        self.author = create_employee_for_tests(
            first_name="Elena",
            last_name="Vargas",
            phone="555-0007",
            job_position=self.position,
            username="elena.vargas",
            email="elena.vargas@company.com",
            join_date=date(2018, 1, 1),
        )
    
    def test_create_announcement(self):
        """Check that an Announcement can be created"""
        
        announcement = Announcement.objects.create(
            title = "Company Meeting",
            content = "There will be a company-wide meeting next Monday",
            priority = "High",
            author = self.author
        )
        self.assertEqual(announcement.title, "Company Meeting")
        self.assertEqual(announcement.author, self.author)
        self.assertTrue(announcement.enabled)
    
    def test_announcement_str(self):
        """Check the string representation of Announcement"""
        
        announcement = Announcement.objects.create(
            title = "Holiday Notice",
            content = "Office will be closed on Friday",
            priority = "Medium",
            author = self.author
        )
        self.assertEqual(str(announcement), "Holiday Notice")

class VacationRequestModelTestCase(TestCase):
    """VacationRequest model test cases"""
    
    def setUp(self):
        """Create necessary data for VacationRequest"""
        
        self.department = Department.objects.create(
            name = "Support",
            description = "Customer Support"
        )
        self.position = JobPosition.objects.create(
            name = "Support Agent",
            description = "Customer Support Agent",
            department = self.department
        )
        self.employee = create_employee_for_tests(
            first_name="Miguel",
            last_name="Castro",
            phone="555-0008",
            job_position=self.position,
            username="miguel.castro",
            email="miguel.castro@company.com",
            join_date=date(2022, 8, 1),
        )
    
    def test_create_vacation_request(self):
        """Check that a VacationRequest can be created"""
        
        request = VacationRequest.objects.create(
            status = "Pending",
            employee = self.employee
        )
        self.assertEqual(request.status, "Pending")
        self.assertEqual(request.employee, self.employee)
        self.assertTrue(request.enabled)
    
    def test_vacation_request_str(self):
        """Check the string representation of VacationRequest"""
        
        request = VacationRequest.objects.create(
            status = "Approved",
            employee = self.employee
        )
        expected = "Vacation Request - Miguel Castro - Approved"
        self.assertEqual(str(request), expected)

class IncidentJustificationModelTestCase(TestCase):
    """IncidentJustification model test cases"""
    
    def setUp(self):
        """Create necessary data for IncidentJustification"""
        
        self.department = Department.objects.create(
            name = "Logistics",
            description = "Logistics Department"
        )
        self.position = JobPosition.objects.create(
            name = "Driver",
            description = "Delivery Driver",
            department = self.department
        )
        self.employee = create_employee_for_tests(
            first_name="Jorge",
            last_name="Méndez",
            phone="555-0009",
            job_position=self.position,
            username="jorge.mendez",
            email="jorge.mendez@company.com",
            join_date=date(2023, 2, 1),
        )
        self.incident = Incident.objects.create(
            type = "Late Arrival",
            justified = "Pending",
            notes = "Arrived 1 hour late",
            employee = self.employee
        )
    
    def test_create_incident_justification(self):
        """Check that an IncidentJustification can be created"""
        
        justification = IncidentJustification.objects.create(
            reason = "Traffic accident on highway",
            evidence = "Police report attached",
            status = "Under Review",
            notes = "Valid justification",
            incident = self.incident
        )
        self.assertEqual(justification.reason, "Traffic accident on highway")
        self.assertEqual(justification.incident, self.incident)
        self.assertTrue(justification.enabled)

class VacationDetailModelTestCase(TestCase):
    """VacationDetail model test cases"""
    
    def setUp(self):
        """Create necessary data for VacationDetail"""
        
        self.department = Department.objects.create(
            name = "Production",
            description = "Production Department"
        )
        self.position = JobPosition.objects.create(
            name = "Operator",
            description = "Machine Operator",
            department = self.department
        )
        self.employee = create_employee_for_tests(
            first_name="Isabel",
            last_name="Ramos",
            phone="555-0010",
            job_position=self.position,
            username="isabel.ramos",
            email="isabel.ramos@company.com",
            join_date=date(2021, 9, 1),
        )
        self.vacation_request = VacationRequest.objects.create(
            status = "Pending",
            employee = self.employee
        )
    
    def test_create_vacation_detail(self):
        """Check that a VacationDetail can be created"""
        
        detail = VacationDetail.objects.create(
            selected_day = date(2024, 12, 25),
            vacation_request = self.vacation_request
        )
        self.assertEqual(detail.selected_day, date(2024, 12, 25))
        self.assertEqual(detail.vacation_request, self.vacation_request)
        self.assertTrue(detail.enabled)
    
    def test_vacation_detail_str(self):
        """Check the string representation of VacationDetail"""
        
        detail = VacationDetail.objects.create(
            selected_day = date(2024, 12, 25),
            vacation_request = self.vacation_request
        )
        expected = "2024-12-25 - Isabel Ramos"
        self.assertEqual(str(detail), expected)

class VacationApprovalModelTestCase(TestCase):
    """VacationApproval model test cases"""
    
    def setUp(self):
        """Create necessary data for VacationApproval"""
        
        self.department = Department.objects.create(
            name = "Quality",
            description = "Quality Assurance"
        )
        self.position = JobPosition.objects.create(
            name = "QA Analyst",
            description = "Quality Analyst",
            department = self.department
        )
        self.manager_position = JobPosition.objects.create(
            name = "QA Manager",
            description = "Quality Manager",
            department = self.department
        )
        self.employee = create_employee_for_tests(
            first_name="Fernando",
            last_name="Ortiz",
            phone="555-0011",
            job_position=self.position,
            username="fernando.ortiz",
            email="fernando.ortiz@company.com",
            join_date=date(2023, 4, 1),
        )
        self.approver = create_employee_for_tests(
            first_name="Laura",
            last_name="Silva",
            phone="555-0012",
            job_position=self.manager_position,
            username="laura.silva",
            email="laura.silva@company.com",
            join_date=date(2019, 1, 1),
        )
        self.vacation_request = VacationRequest.objects.create(
            status = "Pending",
            employee = self.employee
        )
    
    def test_create_vacation_approval(self):
        """Check that a VacationApproval can be created"""
        
        approval = VacationApproval.objects.create(
            decision = "Approved",
            note = "Approved for the requested dates",
            vacation_request = self.vacation_request,
            approver = self.approver
        )
        self.assertEqual(approval.decision, "Approved")
        self.assertEqual(approval.approver, self.approver)
        self.assertTrue(approval.enabled)
    
    def test_vacation_approval_str(self):
        """Check the string representation of VacationApproval"""
        
        approval = VacationApproval.objects.create(
            decision = "Approved",
            note = "All good",
            vacation_request = self.vacation_request,
            approver = self.approver
        )
        expected = "Approved - Fernando Ortiz - Approver: Laura Silva"
        self.assertEqual(str(approval), expected)
