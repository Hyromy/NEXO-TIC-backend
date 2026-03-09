from django.contrib.auth.models import User
from rest_framework.viewsets import ModelViewSet

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

#   ///////////////////////////////////////////////////////////////////

#   Importacion de modelos y serializers reales

from apps.models.models import (
    Announcement, 
    Department,
    EmploymentHistory, 
    Incident, 
    IncidentJustification, 
    JobPosition, 
    Employee,
    ReportHistory,
    Role, 
    VacationPolicy, 
    VacationPeriod, 
    VacationRequest, 
    VacationDetail, 
    VacationApproval,
    EmployeeTermination
)
from .serializers import (
    UserSerializer,
    AnnouncementSerializer,
    DepartmentSerializer, 
    IncidentSerializer, 
    IncidentJustificationSerializer, 
    JobPositionSerializer, 
    EmployeeSerializer, 
    VacationPolicySerializer, 
    VacationPeriodSerializer, 
    VacationDetailSerializer, 
    VacationRequestSerializer, 
    VacationApprovalSerializer,
    EmploymentHistorySerializer,
    EmployeeTerminationSerializer,
    ReportHistorySerializer,
    RoleSerializer,
)
#   Departamento
class DepartmentViewSet(ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

#   Puesto
class JobPositionViewSet(ModelViewSet):
    queryset = JobPosition.objects.all()
    serializer_class = JobPositionSerializer

#   Empleado
class EmployeeViewSet(ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

#   Politica de Vacaciones
class VacationPolicyViewSet(ModelViewSet):
    queryset = VacationPolicy.objects.all()
    serializer_class = VacationPolicySerializer

#   Periodo Vacacional
class VacationPeriodViewSet(ModelViewSet):
    queryset = VacationPeriod.objects.all()
    serializer_class = VacationPeriodSerializer

#   Solicitud de vacaciones
class VacationRequestViewSet(ModelViewSet):
    queryset = VacationRequest.objects.all()
    serializer_class = VacationRequestSerializer

#   Detalle de vacaciones
class VacationDetailViewSet(ModelViewSet):
    queryset = VacationDetail.objects.all()
    serializer_class = VacationDetailSerializer

#   Aprovacion de Vacaciones
class VacationApprovalViewSet(ModelViewSet):
    queryset = VacationApproval.objects.all()
    serializer_class = VacationApprovalSerializer

#   Incidencias
class IncidentViewSet(ModelViewSet):
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer

#   Justificacion Incidencia
class IncidentJustificationViewSet(ModelViewSet):
    queryset = IncidentJustification.objects.all()
    serializer_class = IncidentJustificationSerializer

#   Anuncios
class AnnouncementViewSet(ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer

#   Historial de Empleos
class EmploymentHistoryViewSet(ModelViewSet):
    queryset = EmploymentHistory.objects.all()
    serializer_class = EmploymentHistorySerializer

#   Baja de Empleados
class EmployeeTerminationViewSet(ModelViewSet):
    queryset = EmployeeTermination.objects.all()
    serializer_class = EmployeeTerminationSerializer

#   Historial de Reportes
class ReportHistoryViewSet(ModelViewSet):
    queryset = ReportHistory.objects.all()
    serializer_class = ReportHistorySerializer

#   Roles del sistema
class RoleViewSet(ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
