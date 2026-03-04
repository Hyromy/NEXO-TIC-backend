from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer

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
from apps.models.models import Department, VacationApproval, VacationDetail, VacationPeriod, VacationPolicy, Employee, JobPosition, VacationRequest 

#   Departamento
class DepartmentSerializer(ModelSerializer):
    """
    Convierte el modelo Department en JSON y viceversa.
    Esto permite:
    - Crear departamentos
    - Listarlos
    - Editarlos
    - Eliminarlos
    """
    class Meta:
        model = Department
        fields = "__all__"

#   Puesto
class JobPositionSerializer(ModelSerializer):
    """
    Permite convertir JobPosition a JSON y viceversa.
    Incluye relación con Department.
    """
    class Meta:
        model = JobPosition
        fields = "__all__"

#   Empleado
class EmployeeSerializer(ModelSerializer):
    """
    Serializer para el modelo Employee.

    Permite:
    - Crear empleados
    - Listarlos
    - Editarlos
    - Eliminarlos (baja lógica recomendada)
    """

    class Meta:
        model = Employee
        fields = "__all__"

    def create(self, validated_data):
        """
        Cuando se crea un empleado:
        1. Se guarda el empleado
        2. Se calcula antigüedad
        3. Se busca política correspondiente
        4. Se crea VacationPeriod automáticamente
        """

        employee = super().create(validated_data)

        # Calcular años de antigüedad
        today = date.today()
        years = today.year - employee.join_date.year

        # Buscar política más cercana
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
    """
    Define cuántos días corresponden según años de antigüedad.
    """

    class Meta:
        model = VacationPolicy
        fields = "__all__"

#   Periodo Vcacional
class VacationPeriodSerializer(ModelSerializer):
    """
    Representa el saldo anual de vacaciones del empleado.
    """

    class Meta:
        model = VacationPeriod
        fields = "__all__"

#   Solicitud vacaciones 
class VacationRequestSerializer(ModelSerializer):
    """
    Representa la solicitud de vacaciones.
    """

    class Meta:
        model = VacationRequest
        fields = "__all__"
        
#   Detalle Vacaciones
class VacationDetailSerializer(ModelSerializer):
    """
    Representa un día específico dentro de una solicitud de vacaciones.
    """

    class Meta:
        model = VacationDetail
        fields = "__all__"

#   Aprovacion Vacaciones 
class VacationApprovalSerializer(ModelSerializer):
    """
    Representa la aprobación o rechazo de una solicitud de vacaciones.
    """

    class Meta:
        model = VacationApproval
        fields = "__all__"

    def create(self, validated_data):
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