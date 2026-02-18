from django.contrib.auth.models import User
from django.test import TestCase

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, APITestCase

from apps.api.decorators import (
    require_fields,
)
from apps.api.serializers import UserSerializer

class RequireFieldsDecoratorTestCase(TestCase):
    """ Test for `require_fields` decorator """

    def setUp(self):
        """ Create an APIRequestFactory instance for testing """

        self.factory = APIRequestFactory()

    # ========================================== 
    # Single field tests (string)
    # ========================================== 
    
    def test_single_field_success(self):
        """ Test single required field with valid data """

        @api_view(['POST'])
        @permission_classes([AllowAny])
        @require_fields("username")
        def test_view(request):
            return Response({"ok": True}, status = status.HTTP_200_OK)

        request = self.factory.post('/test/', {'username': 'testuser'})
        response = test_view(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_single_field_missing(self):
        """ Test single required field when missing """

        @api_view(['POST'])
        @permission_classes([AllowAny])
        @require_fields("username")
        def test_view(request):
            return Response({"ok": True}, status = status.HTTP_200_OK)

        request = self.factory.post('/test/', {})
        response = test_view(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        self.assertIn("This field is required.", response.data["username"])

    # ========================================== 
    # Single field with type validation (tuple)
    # ========================================== 
    
    def test_typed_field_success_bool(self):
        """ Test typed field (bool) with correct type """

        @api_view(['POST'])
        @permission_classes([AllowAny])
        @require_fields(("is_active", bool))
        def test_view(request):
            return Response({"ok": True}, status = status.HTTP_200_OK)

        request = self.factory.post('/test/', {'is_active': True}, format = 'json')
        response = test_view(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_typed_field_success_int(self):
        """ Test typed field (int) with correct type """

        @api_view(['POST'])
        @permission_classes([AllowAny])
        @require_fields(("age", int))
        def test_view(request):
            return Response({"ok": True}, status = status.HTTP_200_OK)

        request = self.factory.post('/test/', {'age': 25}, format = 'json')
        response = test_view(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_typed_field_success_str(self):
        """ Test typed field (str) with correct type """

        @api_view(['POST'])
        @permission_classes([AllowAny])
        @require_fields(("name", str))
        def test_view(request):
            return Response({"ok": True}, status = status.HTTP_200_OK)

        request = self.factory.post('/test/', {'name': 'John'})
        response = test_view(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_typed_field_wrong_type(self):
        """ Test typed field with incorrect type """

        @api_view(['POST'])
        @permission_classes([AllowAny])
        @require_fields(("age", int))
        def test_view(request):
            return Response({"ok": True}, status = status.HTTP_200_OK)

        request = self.factory.post('/test/', {'age': 'twenty-five'})
        response = test_view(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("age", response.data)
        self.assertIn("Incorrect type", response.data["age"][0])
        self.assertIn("expected int", response.data["age"][0])
        self.assertIn("received str", response.data["age"][0])

    def test_typed_field_missing(self):
        """ Test typed field when missing """

        @api_view(['POST'])
        @permission_classes([AllowAny])
        @require_fields(("is_active", bool))
        def test_view(request):
            return Response({"ok": True}, status = status.HTTP_200_OK)

        request = self.factory.post('/test/', {})
        response = test_view(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("is_active", response.data)
        self.assertIn("This field is required.", response.data["is_active"])

    # ========================================== 
    # Multiple fields tests (list of strings)
    # ========================================== 
    
    def test_multiple_fields_success(self):
        """ Test multiple required fields with all present """

        @api_view(['POST'])
        @permission_classes([AllowAny])
        @require_fields(["username", "email"])
        def test_view(request):
            return Response({"ok": True}, status = status.HTTP_200_OK)

        request = self.factory.post('/test/', {
            'username': 'testuser',
            'email': 'test@example.com'
        })
        response = test_view(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_multiple_fields_one_missing(self):
        """ Test multiple required fields with one missing """

        @api_view(['POST'])
        @permission_classes([AllowAny])
        @require_fields(["username", "email"])
        def test_view(request):
            return Response({"ok": True}, status = status.HTTP_200_OK)

        request = self.factory.post('/test/', {'username': 'testuser'})
        response = test_view(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertIn("This field is required.", response.data["email"])

    def test_multiple_fields_all_missing(self):
        """ Test multiple required fields with all missing """

        @api_view(['POST'])
        @permission_classes([AllowAny])
        @require_fields(["username", "email"])
        def test_view(request):
            return Response({"ok": True}, status = status.HTTP_200_OK)

        request = self.factory.post('/test/', {})
        response = test_view(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        self.assertIn("email", response.data)

    # ========================================== 
    # Multiple fields with types (list of tuples)
    # ========================================== 
    
    def test_multiple_typed_fields_success(self):
        """ Test multiple typed fields with all correct """

        @api_view(['POST'])
        @permission_classes([AllowAny])
        @require_fields([("age", int), ("is_active", bool)])
        def test_view(request):
            return Response({"ok": True}, status = status.HTTP_200_OK)

        request = self.factory.post('/test/', {
            'age': 30,
            'is_active': True
        }, format = 'json')
        response = test_view(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_multiple_typed_fields_one_wrong_type(self):
        """ Test multiple typed fields with one incorrect type """

        @api_view(['POST'])
        @permission_classes([AllowAny])
        @require_fields([("age", int), ("is_active", bool)])
        def test_view(request):
            return Response({"ok": True}, status = status.HTTP_200_OK)

        request = self.factory.post('/test/', {
            'age': 'thirty',
            'is_active': True
        })
        response = test_view(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("age", response.data)
        self.assertIn("Incorrect type", response.data["age"][0])

    def test_multiple_typed_fields_one_missing(self):
        """ Test multiple typed fields with one missing """

        @api_view(['POST'])
        @permission_classes([AllowAny])
        @require_fields([("age", int), ("is_active", bool)])
        def test_view(request):
            return Response({"ok": True}, status = status.HTTP_200_OK)

        request = self.factory.post('/test/', {'age': 30})
        response = test_view(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("is_active", response.data)
        self.assertIn("This field is required.", response.data["is_active"])

    def test_multiple_typed_fields_complex(self):
        """ Test multiple typed fields with various types """

        @api_view(['POST'])
        @permission_classes([AllowAny])
        @require_fields([
            ("username", str),
            ("age", int),
            ("is_active", bool)
        ])
        def test_view(request):
            return Response({"ok": True}, status = status.HTTP_200_OK)

        request = self.factory.post('/test/', {
            'username': 'john_doe',
            'age': 25,
            'is_active': False
        }, format = 'json')
        response = test_view(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ========================================== 
    # Edge cases
    # ========================================== 
    
    def test_extra_fields_allowed(self):
        """ Test that extra fields don't cause errors """

        @api_view(['POST'])
        @permission_classes([AllowAny])
        @require_fields("username")
        def test_view(request):
            return Response({"ok": True}, status = status.HTTP_200_OK)

        request = self.factory.post('/test/', {
            'username': 'testuser',
            'extra_field': 'extra_value',
            'another_field': 123
        })
        response = test_view(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_field_value_none_with_type(self):
        """ Test that None value fails type validation """

        @api_view(['POST'])
        @permission_classes([AllowAny])
        @require_fields(("age", int))
        def test_view(request):
            return Response({"ok": True}, status = status.HTTP_200_OK)

        request = self.factory.post('/test/', {'age': None}, format = 'json')
        response = test_view(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("age", response.data)

    def test_field_value_empty_string(self):
        """ Test that empty string is accepted as valid field """

        @api_view(['POST'])
        @permission_classes([AllowAny])
        @require_fields("username")
        def test_view(request):
            return Response({"ok": True}, status = status.HTTP_200_OK)

        request = self.factory.post('/test/', {'username': ''})
        response = test_view(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_field_zero_value(self):
        """ Test that zero is accepted as valid integer """

        @api_view(['POST'])
        @permission_classes([AllowAny])
        @require_fields(("count", int))
        def test_view(request):
            return Response({"ok": True}, status = status.HTTP_200_OK)

        request = self.factory.post('/test/', {'count': 0}, format = 'json')
        response = test_view(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_field_false_value(self):
        """ Test that False is accepted as valid boolean """

        @api_view(['POST'])
        @permission_classes([AllowAny])
        @require_fields(("is_active", bool))
        def test_view(request):
            return Response({"ok": True}, status = status.HTTP_200_OK)

        request = self.factory.post('/test/', {'is_active': False}, format = 'json')
        response = test_view(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_multiple_errors_simultaneously(self):
        """ Test multiple errors at once: missing field AND wrong type """
        
        @api_view(['POST'])
        @permission_classes([AllowAny])
        @require_fields([("age", int), ("email", str), ("is_active", bool)])
        def test_view(request):
            return Response({"ok": True}, status = status.HTTP_200_OK)

        request = self.factory.post('/test/', {
            'age': 'twenty-five',  # Wrong type
            'is_active': True      # email is missing
        }, format = 'json')
        response = test_view(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("age", response.data)
        self.assertIn("email", response.data)
        self.assertIn("Incorrect type", response.data["age"][0])
        self.assertIn("This field is required.", response.data["email"])

    def test_list_as_field_value(self):
        """ Test that list values are accepted as present fields """
        
        @api_view(['POST'])
        @permission_classes([AllowAny])
        @require_fields("tags")
        def test_view(request):
            return Response({"ok": True}, status = status.HTTP_200_OK)

        request = self.factory.post('/test/', {
            'tags': ['python', 'django', 'rest']
        }, format = 'json')
        response = test_view(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_dict_as_field_value(self):
        """ Test that dict values are accepted as present fields """
        
        @api_view(['POST'])
        @permission_classes([AllowAny])
        @require_fields("settings")
        def test_view(request):
            return Response({"ok": True}, status = status.HTTP_200_OK)

        request = self.factory.post('/test/', {
            'settings': {'theme': 'dark', 'language': 'en'}
        }, format = 'json')
        response = test_view(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_empty_list_as_field_value(self):
        """ Test that empty list is accepted as valid field """
        
        @api_view(['POST'])
        @permission_classes([AllowAny])
        @require_fields("items")
        def test_view(request):
            return Response({"ok": True}, status = status.HTTP_200_OK)

        request = self.factory.post('/test/', {'items': []}, format = 'json')
        response = test_view(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_empty_dict_as_field_value(self):
        """ Test that empty dict is accepted as valid field """
        
        @api_view(['POST'])
        @permission_classes([AllowAny])
        @require_fields("metadata")
        def test_view(request):
            return Response({"ok": True}, status = status.HTTP_200_OK)

        request = self.factory.post('/test/', {'metadata': {}}, format = 'json')
        response = test_view(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserSerializerTestCase(TestCase):
    """ Tests for UserSerializer """

    def test_serializer_with_valid_data(self):
        """ Test serializer validation with valid data """
        
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        serializer = UserSerializer(data = data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_with_missing_username(self):
        """ Test serializer validation when username is missing """
        
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        serializer = UserSerializer(data = data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)

    def test_serializer_with_missing_password(self):
        """ Test serializer validation when password is missing """
        
        data = {
            'username': 'testuser',
            'email': 'test@example.com'
        }
        
        serializer = UserSerializer(data = data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_serializer_create_user(self):
        """ Test that create method properly creates a user with hashed password """
        
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        serializer = UserSerializer(data = data)
        self.assertTrue(serializer.is_valid())
        
        user = serializer.save()
        
        # Verify user was created
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
        
        # Verify password was hashed (not stored in plain text)
        self.assertNotEqual(user.password, 'securepass123')
        self.assertTrue(user.check_password('securepass123'))

    def test_serializer_update_user(self):
        """ Test that update method properly updates user data """
        
        # Create an initial user
        user = User.objects.create_user(
            username = 'originaluser',
            email = 'original@example.com',
            password = 'originalpass'
        )
        
        # Update data
        update_data = {
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        serializer = UserSerializer(user, data = update_data, partial = True)
        self.assertTrue(serializer.is_valid())
        
        updated_user = serializer.save()
        
        # Verify updates
        self.assertEqual(updated_user.email, 'updated@example.com')
        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.last_name, 'Name')
        self.assertEqual(updated_user.username, 'originaluser')  # Username unchanged

    def test_serializer_update_password(self):
        """ Test that update method properly hashes new password """
        
        # Create an initial user
        user = User.objects.create_user(
            username = 'testuser',
            email = 'test@example.com',
            password = 'oldpassword'
        )
        
        # Update password
        update_data = {'password': 'newpassword123'}
        
        serializer = UserSerializer(user, data = update_data, partial = True)
        self.assertTrue(serializer.is_valid())
        
        updated_user = serializer.save()
        
        # Verify password was updated and hashed
        self.assertNotEqual(updated_user.password, 'newpassword123')
        self.assertTrue(updated_user.check_password('newpassword123'))
        self.assertFalse(updated_user.check_password('oldpassword'))

    def test_password_write_only(self):
        """ Test that password field is write-only and not included in output """
        
        user = User.objects.create_user(
            username = 'testuser',
            email = 'test@example.com',
            password = 'testpass123'
        )
        
        serializer = UserSerializer(user)
        
        # Verify password is not in serialized data
        self.assertNotIn('password', serializer.data)
        
        # Verify other fields are present
        self.assertIn('username', serializer.data)
        self.assertIn('email', serializer.data)

    def test_serializer_with_duplicate_username(self):
        """ Test serializer validation with duplicate username """
        
        # Create an existing user
        User.objects.create_user(
            username = 'existinguser',
            email = 'existing@example.com',
            password = 'password123'
        )
        
        # Try to create another user with same username
        data = {
            'username': 'existinguser',
            'email': 'different@example.com',
            'password': 'password456'
        }
        
        serializer = UserSerializer(data = data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)


class UserViewSetTestCase(APITestCase):
    """ Tests for UserViewSet endpoints """

    def setUp(self):
        """ Create test users for testing """
        
        self.user1 = User.objects.create_user(
            username = 'user1',
            email = 'user1@example.com',
            password = 'password1',
            first_name = 'First',
            last_name = 'User'
        )
        
        self.user2 = User.objects.create_user(
            username = 'user2',
            email = 'user2@example.com',
            password = 'password2',
            first_name = 'Second',
            last_name = 'User'
        )
        
        # Authenticate client for all requests
        self.client.force_authenticate(user = self.user1)

    def test_list_users(self):
        """ Test GET /users/ - List all users """
        
        response = self.client.get('/users/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Verify user data is present
        usernames = [user['username'] for user in response.data]
        self.assertIn('user1', usernames)
        self.assertIn('user2', usernames)

    def test_retrieve_user(self):
        """ Test GET /users/{id}/ - Retrieve single user """
        
        response = self.client.get(f'/users/{self.user1.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'user1')
        self.assertEqual(response.data['email'], 'user1@example.com')
        self.assertEqual(response.data['first_name'], 'First')
        self.assertNotIn('password', response.data)  # Password should not be exposed

    def test_retrieve_nonexistent_user(self):
        """ Test GET /users/{id}/ with non-existent ID """
        
        response = self.client.get('/users/99999/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_user(self):
        """ Test POST /users/ - Create new user """
        
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'Person'
        }
        
        response = self.client.post('/users/', data, format = 'json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'newuser')
        self.assertEqual(response.data['email'], 'newuser@example.com')
        
        # Verify user was created in database
        user = User.objects.get(username = 'newuser')
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password('newpass123'))

    def test_create_user_with_missing_fields(self):
        """ Test POST /users/ with missing required fields """
        
        data = {
            'username': 'incompleteuser'
            # Missing password and email
        }
        
        response = self.client.post('/users/', data, format = 'json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_create_user_with_duplicate_username(self):
        """ Test POST /users/ with duplicate username """
        
        data = {
            'username': 'user1',  # Already exists
            'email': 'different@example.com',
            'password': 'password123'
        }
        
        response = self.client.post('/users/', data, format = 'json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_update_user(self):
        """ Test PUT /users/{id}/ - Full update """
        
        data = {
            'username': 'user1',  # Required field
            'email': 'updated@example.com',
            'password': 'newpassword',
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        response = self.client.put(f'/users/{self.user1.id}/', data, format = 'json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'updated@example.com')
        self.assertEqual(response.data['first_name'], 'Updated')
        
        # Verify password was updated
        self.user1.refresh_from_db()
        self.assertTrue(self.user1.check_password('newpassword'))

    def test_partial_update_user(self):
        """ Test PATCH /users/{id}/ - Partial update """
        
        data = {
            'first_name': 'PartiallyUpdated'
        }
        
        response = self.client.patch(f'/users/{self.user1.id}/', data, format = 'json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'PartiallyUpdated')
        self.assertEqual(response.data['username'], 'user1')  # Username unchanged
        self.assertEqual(response.data['email'], 'user1@example.com')  # Email unchanged

    def test_delete_user(self):
        """ Test DELETE /users/{id}/ - Delete user """
        
        user_id = self.user1.id
        response = self.client.delete(f'/users/{user_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify user was deleted
        self.assertFalse(User.objects.filter(id = user_id).exists())

    def test_delete_nonexistent_user(self):
        """ Test DELETE /users/{id}/ with non-existent ID """
        
        response = self.client.delete('/users/99999/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
