from django.contrib.auth.models import User
from rest_framework.viewsets import ModelViewSet

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

from django.db.models import Count
from datetime import timedelta
from django.utils import timezone

from .serializers import UserSerializer

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
    """

    queryset = JobPosition.objects.all()
    serializer_class = JobPositionSerializer

#   Empleado
class EmployeeViewSet(ModelViewSet):
    """
    CRUD automático para empleados.
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

#   Incidencias
class IncidentViewSet(ModelViewSet):
    """
    CRUD para incidencias de empleados.
    """

    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer

#   Justificacion Incidencia
class IncidentJustificationViewSet(ModelViewSet):
    """
    CRUD para justificaciones de incidencias.
    """

    queryset = IncidentJustification.objects.all()
    serializer_class = IncidentJustificationSerializer

#   Anuncios
class AnnouncementViewSet(ModelViewSet):
    """
    CRUD para avisos del sistema.
    """

    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer

#   Historial de Empleos
class EmploymentHistoryViewSet(ModelViewSet):
    """
    CRUD para historial laboral.
    """

    queryset = EmploymentHistory.objects.all()
    serializer_class = EmploymentHistorySerializer

#   Baja de Empleados
class EmployeeTerminationViewSet(ModelViewSet):
    """
    CRUD para bajas de empleados.
    """

    queryset = EmployeeTermination.objects.all()
    serializer_class = EmployeeTerminationSerializer

#   Historial de Reportes
class ReportHistoryViewSet(ModelViewSet):
    """
    CRUD para historial de reportes.
    """

    queryset = ReportHistory.objects.all()
    serializer_class = ReportHistorySerializer

#   Roles del sistema
class RoleViewSet(ModelViewSet):
    """
    CRUD para roles del sistema.
    """

    queryset = Role.objects.all()
    serializer_class = RoleSerializer

#   Identidad
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):

    user = request.user

    employee = Employee.objects.filter(user=user).first()

    if not employee:
        return Response({"error": "Empleado no encontrado"})

    data = {
        "user_id": user.id,
        "username": user.username,
        "employee": {
            "id": employee.id,
            "name": employee.name,
            "surname": employee.surname,
            "email": employee.email,
            "job_position": employee.job_position.name,
            "department": employee.job_position.department.name
        }
    }

    return Response(data)

#   Dashboard
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard(request):

    user = request.user
    employee = Employee.objects.filter(user=user).first()

    if not employee:
        return Response({"error": "Empleado no encontrado"})

    today = timezone.now()

    # avisos recientes
    announcements = Announcement.objects.filter(
        enabled=True
    ).order_by("-date")[:5]

    announcements_data = [
        {
            "title": a.title,
            "priority": a.priority,
            "date": a.date
        }
        for a in announcements
    ]

    # periodo vacacional actual
    period = VacationPeriod.objects.filter(
        employee=employee
    ).first()

    # solicitudes pendientes del usuario
    pending_requests = VacationRequest.objects.filter(
        employee=employee,
        status="PENDING"
    ).count()

    # incidencias últimos 15 días
    last_days = today - timedelta(days=15)

    incidents = Incident.objects.filter(
        employee=employee,
        date__gte=last_days
    ).count()

    data = {
        "employee": {
            "name": employee.name,
            "department": employee.job_position.department.name,
            "job_position": employee.job_position.name
        },

        "vacation": {
            "days_assigned": period.days_assigned if period else 0,
            "days_used": period.days_used if period else 0,
            "days_remaining": period.days_remaining if period else 0
        },

        "pending_requests": pending_requests,
        "recent_incidents": incidents,
        "announcements": announcements_data
    }

    return Response(data)