from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
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

urlpatterns = [
    path("", include(router.urls)),
]
