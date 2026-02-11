from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

def require_fields(required_fields: str | list[str] | tuple[str, type] | list[tuple[str, type]]):
    """
    Check fields in request.data decorator.
    
    Args:
        required_fields (str | list[str] | tuple[str, type] | list[tuple[str, type]]): Field or list of fields to check in request.data.
 
    Returns:
        function: Decorator function that checks for required fields in the request data.

    Examples:
    ```python
        @require_fields("username")
        def my_simple_view(request):
            pass

        @require_fields(("superuser", bool))
        def my_typed_view(request):
            pass

        @require_fields(["username", "email"])
        def my_multiple_view(request):
            pass

        @require_fields([("age", int), ("is_active", bool)])
        def my_complex_view(request):
            pass
    ```
    """

    normalized_fields: list[tuple[str, type]] = []

    if isinstance(required_fields, str):
        normalized_fields = [(required_fields, object)]
    elif isinstance(required_fields, tuple) and len(required_fields) == 2:
        normalized_fields = [required_fields]
    elif isinstance(required_fields, list):
        if isinstance(required_fields[0], str):
            normalized_fields = [(field, object) for field in required_fields if isinstance(field, str)]
        else:
            normalized_fields = required_fields
    else:
        raise ValueError("Invalid format for required_fields parameter.")

    def decorator(func):
        def wrapper(request: Request, *args, **kwargs) -> Response:
            data = request.data
            errors = {}

            for field_name, field_type in normalized_fields:
                field_errors = []

                if field_name not in data:
                    field_errors.append("This field is required.")
                
                elif field_type is not object and not isinstance(data[field_name], field_type):
                    field_errors.append(
                        f"Incorrect type (expected {field_type.__name__}, received {type(data[field_name]).__name__})"
                    )

                if field_errors:
                    errors[field_name] = field_errors

            if errors:
                return Response(
                    errors,
                    status = status.HTTP_400_BAD_REQUEST
                )

            return func(request, *args, **kwargs)
        return wrapper
    return decorator
