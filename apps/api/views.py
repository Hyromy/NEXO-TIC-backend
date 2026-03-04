from django.contrib.auth.models import User
from rest_framework.viewsets import ModelViewSet

from .serializers import (
    UserSerializer,
)

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

#   ///////////////////////////////////////////////////////////////////

#   Importacion de modelos y serializers reales

from apps.models.models import Department, JobPosition, Employee, VacationPolicy, VacationPeriod, VacationRequest, VacationDetail, VacationApproval
from .serializers import DepartmentSerializer, JobPositionSerializer, EmployeeSerializer, VacationPolicySerializer, VacationPeriodSerializer, VacationDetailSerializer, VacationRequestSerializer, VacationApprovalSerializer

#   Departamento
class DepartmentViewSet(ModelViewSet):
    """
    Este ViewSet crea automáticamente:

    GET     /api/departments/
    POST    /api/departments/
    GET     /api/departments/{id}/
    PUT     /api/departments/{id}/
    DELETE  /api/departments/{id}/

    Sin escribir más código.
    """

    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

#   Puesto
class JobPositionViewSet(ModelViewSet):
    """
    CRUD automático para puestos de trabajo.

    Endpoints:
    GET     /job-positions/
    POST    /job-positions/
    GET     /job-positions/{id}/
    PUT     /job-positions/{id}/
    DELETE  /job-positions/{id}/
    """

    queryset = JobPosition.objects.all()
    serializer_class = JobPositionSerializer

#   Empleado
class EmployeeViewSet(ModelViewSet):
    """
    CRUD automático para empleados.

    Endpoints generados:

    GET     /employees/
    POST    /employees/
    GET     /employees/{id}/
    PUT     /employees/{id}/
    DELETE  /employees/{id}/
    """

    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

#   Politica de Vacaciones
class VacationPolicyViewSet(ModelViewSet):
    """
    CRUD para políticas de vacaciones.
    """

    queryset = VacationPolicy.objects.all()
    serializer_class = VacationPolicySerializer

#   Periodo Vacacional
class VacationPeriodViewSet(ModelViewSet):
    """
    CRUD para periodos de vacaciones.
    """

    queryset = VacationPeriod.objects.all()
    serializer_class = VacationPeriodSerializer

#   Solicitud de vacaciones
class VacationRequestViewSet(ModelViewSet):
    """
    CRUD para solicitudes de vacaciones.
    """

    queryset = VacationRequest.objects.all()
    serializer_class = VacationRequestSerializer

#   Detalle de vacaciones
class VacationDetailViewSet(ModelViewSet):
    """
    CRUD para los días seleccionados de una solicitud.
    """

    queryset = VacationDetail.objects.all()
    serializer_class = VacationDetailSerializer

#   Aprovacion de Vacaciones
class VacationApprovalViewSet(ModelViewSet):
    """
    CRUD para decisiones de aprobación de vacaciones.
    """

    queryset = VacationApproval.objects.all()
    serializer_class = VacationApprovalSerializer