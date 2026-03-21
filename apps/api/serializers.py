from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer
import rest_framework.serializers as serializers
from rest_framework.exceptions import ValidationError
from utils.randomizer import generate_password

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user

# /////////////////////////////////////////////////////////////////

#   Importacion de modelos reales
from datetime import date
from apps.models.models import (
    Announcement, 
    Department,
    EmployeeTermination,
    EmploymentHistory, 
    IncidentJustification,
    ReportHistory,
    Role, 
    VacationApproval, 
    VacationDetail, 
    VacationPeriod, 
    VacationPolicy, 
    Employee, 
    JobPosition, 
    VacationRequest, 
    Incident,
) 

#   Departamento
class DepartmentSerializer(ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"

#   Puesto
class JobPositionSerializer(ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source='department',
        write_only=True
    )
    class Meta:
        model = JobPosition
        fields = "__all__"

#   Empleado
class EmployeeSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)
    job_position = JobPositionSerializer(read_only=True)
    job_position_id = serializers.PrimaryKeyRelatedField(
        queryset=JobPosition.objects.all(),
        source='job_position',
        write_only=True
    )
    class Meta:
        model = Employee
        fields = "__all__"

    def create(self, validated_data):

        email = validated_data["email"]

        # generar contraseña temporal
        temp_password = generate_password()

        # crear usuario de Django
        user = User.objects.create_user(
            username=email,
            email=email,
            password=temp_password
        )

        # crear empleado
        employee = Employee.objects.create(
            user=user,
            **validated_data
        )

        # calcular antigüedad
        today = date.today()
        years = today.year - employee.join_date.year

        policy = VacationPolicy.objects.filter(
            seniority_years__lte=years,
            enabled=True
        ).order_by('-seniority_years').first()

        if policy:
            VacationPeriod.objects.create(
                year=today.year,
                days_assigned=policy.vacation_days,
                days_used=0,
                days_remaining=policy.vacation_days,
                employee=employee
            )

        return employee

#   Politica de Vacaciones
class VacationPolicySerializer(ModelSerializer):
    class Meta:
        model = VacationPolicy
        fields = "__all__"

#   Periodo Vcacional
class VacationPeriodSerializer(ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source='employee',
        write_only=True
    )
    class Meta:
        model = VacationPeriod
        fields = "__all__"

#   Solicitud vacaciones 
class VacationRequestSerializer(ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source='employee',
        write_only=True
    )
    class Meta:
        model = VacationRequest
        fields = "__all__"
        
#   Detalle Vacaciones
class VacationDetailSerializer(ModelSerializer):
    vacation_request = VacationRequestSerializer(read_only=True)
    vacation_request_id = serializers.PrimaryKeyRelatedField(
        queryset=VacationRequest.objects.all(),
        source='vacation_request',
        write_only=True
    )
    class Meta:
        model = VacationDetail
        fields = "__all__"

    def validate(self, data):

        request = data["vacation_request"]
        employee = request.employee
        selected_day = data["selected_day"]

        # evitar dias duplicados
        if VacationDetail.objects.filter(
            vacation_request=request,
            selected_day=selected_day
        ).exists():
            raise ValidationError("Este día ya fue solicitado.")

        # contar dias solicitados actualmente
        existing_days = VacationDetail.objects.filter(
            vacation_request=request
        ).count()

        # buscar periodo
        period = VacationPeriod.objects.filter(
            employee=employee
        ).first()

        if period and existing_days + 1 > period.days_remaining:
            raise ValidationError("No tiene suficientes días disponibles.")

        return data

#   Aprobacion Vacaciones 
class VacationApprovalSerializer(ModelSerializer):
    vacation_request = VacationRequestSerializer(read_only=True)
    vacation_request_id = serializers.PrimaryKeyRelatedField(
        queryset=VacationRequest.objects.all(),
        source='vacation_request',
        write_only=True
    )

    approver = EmployeeSerializer(read_only=True)
    approver_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source='approver',
        write_only=True
    )
    class Meta:
        model = VacationApproval
        fields = "__all__"

    def create(self, validated_data):
        if VacationApproval.objects.filter(
            vacation_request=validated_data["vacation_request"]
        ).exists():
            raise ValidationError("Esta solicitud ya fue procesada.")
        
        approval = super().create(validated_data)

        # Si se aprueba la solicitud
        if approval.decision == "APPROVED":

            request = approval.vacation_request
            employee = request.employee

            # Contar días solicitados
            days_requested = VacationDetail.objects.filter(
                vacation_request=request
            ).count()

            # Buscar periodo del empleado
            period = VacationPeriod.objects.filter(
                employee=employee
            ).first()

            if period:
                period.days_used += days_requested
                period.days_remaining -= days_requested
                period.save()

            # Actualizar estatus de solicitud
            request.status = "APPROVED"
            request.save()

        return approval

#   Incidencias
class IncidentSerializer(ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source='employee',
        write_only=True
    )
    class Meta:
        model = Incident
        fields = "__all__"

#   Jusificacion Incidencia
class IncidentJustificationSerializer(ModelSerializer):
    incident = IncidentSerializer(read_only=True)
    incident_id = serializers.PrimaryKeyRelatedField(
        queryset=Incident.objects.all(),
        source='incident',
        write_only=True
    )
    class Meta:
        model = IncidentJustification
        fields = "__all__"

    def validate(self, data):

        incident = data["incident"]

        if IncidentJustification.objects.filter(
            incident=incident
        ).exists():
            raise ValidationError("Esta incidencia ya fue justificada.")

        return data

#   Anuncios
class AnnouncementSerializer(ModelSerializer):
    author = EmployeeSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source='author',
        write_only=True
    )
    class Meta:
        model = Announcement
        fields = "__all__"

#   Historial de Empleos
class EmploymentHistorySerializer(ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source='employee',
        write_only=True
    )

    last_job_position = JobPositionSerializer(read_only=True)
    last_job_position_id = serializers.PrimaryKeyRelatedField(
        queryset=JobPosition.objects.all(),
        source='last_job_position',
        write_only=True
    )

    new_job_position = JobPositionSerializer(read_only=True)
    new_job_position_id = serializers.PrimaryKeyRelatedField(
        queryset=JobPosition.objects.all(),
        source='new_job_position',
        write_only=True
    )

    class Meta:
        model = EmploymentHistory
        fields = "__all__"

#   Baja Empleado
class EmployeeTerminationSerializer(ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source='employee',
        write_only=True
    )
    class Meta:
        model = EmployeeTermination
        fields = "__all__"

    def create(self, validated_data):

        termination = super().create(validated_data)

        employee = termination.employee
        employee.enabled = False
        employee.save()

        return termination

#   Historial de reportes
class ReportHistorySerializer(ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source='employee',
        write_only=True
    )
    class Meta:
        model = ReportHistory
        fields = "__all__"

#   Roles del sistema
class RoleSerializer(ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"