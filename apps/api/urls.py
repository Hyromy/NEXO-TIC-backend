from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import dashboard

from .views import (
    RoleViewSet,
    UserViewSet,
    # MODELOS
    DepartmentViewSet,
    JobPositionViewSet,
    EmployeeViewSet,
    VacationApprovalViewSet,
    VacationDetailViewSet,
    VacationPeriodViewSet,
    VacationPolicyViewSet,
    VacationRequestViewSet,
    IncidentJustificationViewSet,
    IncidentViewSet,    
    AnnouncementViewSet,
    EmployeeTerminationViewSet,
    EmploymentHistoryViewSet,
    ReportHistoryViewSet,
    me,
)

router = DefaultRouter()
router.register(r'users', UserViewSet)

# MODELOS
router.register(r'departments', DepartmentViewSet)
router.register(r'job-positions', JobPositionViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'vacation-policies', VacationPolicyViewSet)
router.register(r'vacation-periods', VacationPeriodViewSet)
router.register(r'vacation-requests', VacationRequestViewSet)
router.register(r'vacation-details', VacationDetailViewSet)
router.register(r'vacation-approvals', VacationApprovalViewSet)
router.register(r'incidents', IncidentViewSet)
router.register(r'incident-justifications', IncidentJustificationViewSet)
router.register(r'announcements', AnnouncementViewSet)
router.register(r'employment-history', EmploymentHistoryViewSet)
router.register(r'employee-terminations', EmployeeTerminationViewSet)
router.register(r'report-history', ReportHistoryViewSet)
router.register(r'roles', RoleViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path("me/", me),
    path("dashboard/", dashboard),
]
