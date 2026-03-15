from django.db import transaction
from django.contrib.auth.models import User
from rest_framework.serializers import CharField, EmailField, ModelSerializer
from rest_framework.exceptions import ValidationError
from utils.randomizer import generate_password

from apps.mail.mails import welcome as welcome_mail

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
    class Meta:
        model = JobPosition
        fields = "__all__"

#   Empleado
class EmployeeSerializer(ModelSerializer):
    email = EmailField(write_only=True, required=True)
    name = CharField(write_only=True, required=True)
    last_name = CharField(write_only=True, required=True)

    class Meta:
        model = Employee
        fields = "__all__"

    def validate(self, data):
        # Evitar error de integridad por email duplicado en auth_user.
        if User.objects.filter(email=data["email"]).exists():
            raise ValidationError({"email": "Este correo ya está registrado."})
        return data

    def create(self, validated_data):
        temp_password = generate_password(
            use_upper = True,
            use_numbers = True
        )

        name = validated_data.pop("name")
        last_name = validated_data.pop("last_name")
        email = validated_data.pop("email")

        with transaction.atomic():
            user = User.objects.create_user(
                username=email.split("@")[0],
                email=email,
                password=temp_password,
                first_name=name,
                last_name=last_name
            )
            
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

            welcome_mail(user=employee.user, tmp_pass=temp_password)
        
        return employee

#   Politica de Vacaciones
class VacationPolicySerializer(ModelSerializer):
    class Meta:
        model = VacationPolicy
        fields = "__all__"

#   Periodo Vcacional
class VacationPeriodSerializer(ModelSerializer):
    class Meta:
        model = VacationPeriod
        fields = "__all__"

#   Solicitud vacaciones 
class VacationRequestSerializer(ModelSerializer):
    class Meta:
        model = VacationRequest
        fields = "__all__"
        
#   Detalle Vacaciones
class VacationDetailSerializer(ModelSerializer):
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
    class Meta:
        model = Incident
        fields = "__all__"

#   Jusificacion Incidencia
class IncidentJustificationSerializer(ModelSerializer):
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
    class Meta:
        model = Announcement
        fields = "__all__"

#   Historial de Empleos
class EmploymentHistorySerializer(ModelSerializer):
    class Meta:
        model = EmploymentHistory
        fields = "__all__"

#   Baja Empleado
class EmployeeTerminationSerializer(ModelSerializer):
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
    class Meta:
        model = ReportHistory
        fields = "__all__"

#   Roles del sistema
class RoleSerializer(ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"