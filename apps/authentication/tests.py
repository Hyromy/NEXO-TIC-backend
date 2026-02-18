from unittest.mock import patch
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class SignupEndpointTestCase(APITestCase):
    """ Tests para el endpoint POST /auth/signup/ """

    @override_settings(DEBUG=True)
    @patch('apps.authentication.views.welcome')
    @patch('apps.authentication.views.generate_password', return_value='TempPass123')
    def test_signup_exitoso(self, mock_generate_password, mock_welcome):
        """ 
        Test: Signup exitoso crea usuario y envía email de bienvenida
        """
        
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com'
        }
        
        # Llamar al endpoint
        response = self.client.post('/auth/signup/', data, format='json')
        
        # Verificar respuesta
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data.get('ok'))
        
        # Verificar que el usuario fue creado
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        
        # Verificar que se generó password temporal
        mock_generate_password.assert_called_once_with(use_upper=True, use_numbers=True)
        
        # Verificar que se intentó enviar email de bienvenida
        mock_welcome.assert_called_once()
        call_kwargs = mock_welcome.call_args[1]
        self.assertEqual(call_kwargs['user'], user)
        self.assertEqual(call_kwargs['tmp_pass'], 'TempPass123')

    def test_signup_sin_username(self):
        """ 
        Test: Signup sin username debe fallar
        """
        
        data = {
            'email': 'test@example.com'
            # Falta username
        }
        
        response = self.client.post('/auth/signup/', data, format='json')
        
        # Debe fallar por campo faltante
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_signup_sin_email(self):
        """ 
        Test: Signup sin email debe fallar
        """
        
        data = {
            'username': 'testuser'
            # Falta email
        }
        
        response = self.client.post('/auth/signup/', data, format='json')
        
        # Debe fallar por campo faltante
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_signup_email_invalido(self):
        """ 
        Test: Signup con email inválido debe fallar
        """
        
        data = {
            'username': 'testuser',
            'email': 'not-an-email'  # ← Email inválido
        }
        
        response = self.client.post('/auth/signup/', data, format='json')
        
        # Debe fallar por email inválido
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Invalid email', response.data['error'])

    @override_settings(DEBUG=True)
    @patch('apps.authentication.views.welcome')
    @patch('apps.authentication.views.generate_password', return_value='TempPass123')
    def test_signup_usuario_duplicado(self, mock_generate_password, mock_welcome):
        """ 
        Test: Signup con usuario existente debe fallar
        """
        
        # Crear usuario existente
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='password123'
        )
        
        # Intentar crear usuario con mismo username y email
        data = {
            'username': 'existinguser',
            'email': 'existing@example.com'
        }
        
        response = self.client.post('/auth/signup/', data, format='json')
        
        # Debe fallar
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('already exists', response.data['error'])

    @override_settings(DEBUG=True)
    @patch('apps.authentication.views.welcome', side_effect=Exception('Email service down'))
    @patch('apps.authentication.views.generate_password', return_value='TempPass123')
    def test_signup_falla_envio_email(self, mock_generate_password, mock_welcome):
        """ 
        Test: Si falla el envío de email, el signup debe fallar
              (transacción atómica debe hacer rollback)
        """
        
        data = {
            'username': 'testuser',
            'email': 'test@example.com'
        }
        
        response = self.client.post('/auth/signup/', data, format='json')
        
        # Debe fallar
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class LoginEndpointTestCase(APITestCase):
    """ Tests para el endpoint POST /auth/login/ """

    def setUp(self):
        """ Crear un usuario de prueba """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_login_exitoso_con_username(self):
        """ 
        Test: Login exitoso con username y password devuelve tokens
        """
        
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post('/auth/login/', data, format='json')
        
        # Verificar respuesta exitosa
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que devuelve tokens
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
        # Verificar que los tokens no están vacíos
        self.assertTrue(response.data['access'])
        self.assertTrue(response.data['refresh'])

    def test_login_password_incorrecta(self):
        """ 
        Test: Login con password incorrecta debe fallar
        """
        
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post('/auth/login/', data, format='json')
        
        # Debe fallar
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_usuario_inexistente(self):
        """ 
        Test: Login con usuario inexistente debe fallar
        """
        
        data = {
            'username': 'nonexistentuser',
            'password': 'password123'
        }
        
        response = self.client.post('/auth/login/', data, format='json')
        
        # Debe fallar
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_sin_username(self):
        """ 
        Test: Login sin username debe fallar
        """
        
        data = {
            'password': 'testpass123'
        }
        
        response = self.client.post('/auth/login/', data, format='json')
        
        # Debe fallar
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_sin_password(self):
        """ 
        Test: Login sin password debe fallar
        """
        
        data = {
            'username': 'testuser'
        }
        
        response = self.client.post('/auth/login/', data, format='json')
        
        # Debe fallar
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RefreshTokenEndpointTestCase(APITestCase):
    """ Tests para el endpoint POST /auth/refresh/ """

    def setUp(self):
        """ Crear un usuario y obtener tokens """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Obtener tokens
        refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(refresh)
        self.access_token = str(refresh.access_token)

    def test_refresh_token_exitoso(self):
        """ 
        Test: Refresh con token válido devuelve nuevo access token
        """
        
        data = {
            'refresh': self.refresh_token
        }
        
        response = self.client.post('/auth/refresh/', data, format='json')
        
        # Verificar respuesta exitosa
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que devuelve nuevo access token
        self.assertIn('access', response.data)
        self.assertTrue(response.data['access'])
        
        # Verificar que el nuevo token es diferente al anterior
        self.assertNotEqual(response.data['access'], self.access_token)

    def test_refresh_token_invalido(self):
        """ 
        Test: Refresh con token inválido debe fallar
        """
        
        data = {
            'refresh': 'invalid_token_string'
        }
        
        response = self.client.post('/auth/refresh/', data, format='json')
        
        # Debe fallar
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_sin_token(self):
        """ 
        Test: Refresh sin token debe fallar
        """
        
        data = {}
        
        response = self.client.post('/auth/refresh/', data, format='json')
        
        # Debe fallar
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutEndpointTestCase(APITestCase):
    """ Tests para el endpoint POST /auth/logout/ """

    def setUp(self):
        """ Crear un usuario y autenticarlo """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Obtener tokens
        refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(refresh)
        self.access_token = str(refresh.access_token)
        
        # Autenticar cliente
        self.client.force_authenticate(user=self.user)

    def test_logout_exitoso(self):
        """ 
        Test: Logout exitoso blacklistea el refresh token
        """
        
        data = {
            'refresh': self.refresh_token
        }
        
        response = self.client.post('/auth/logout/', data, format='json')
        
        # Verificar respuesta exitosa
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('ok'))

    def test_logout_sin_refresh_token(self):
        """ 
        Test: Logout sin refresh token debe fallar
        """
        
        data = {}
        
        response = self.client.post('/auth/logout/', data, format='json')
        
        # Debe fallar por campo faltante
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('refresh', response.data)

    def test_logout_refresh_token_invalido(self):
        """ 
        Test: Logout con token inválido debe fallar
        """
        
        data = {
            'refresh': 'invalid_token'
        }
        
        response = self.client.post('/auth/logout/', data, format='json')
        
        # Debe fallar
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Invalid token', response.data['error'])

    def test_logout_sin_autenticacion(self):
        """ 
        Test: Logout sin autenticación debe fallar
        """
        
        # Remover autenticación
        self.client.force_authenticate(user=None)
        
        data = {
            'refresh': self.refresh_token
        }
        
        response = self.client.post('/auth/logout/', data, format='json')
        
        # Debe fallar por falta de autenticación
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RecoverPasswordEndpointTestCase(APITestCase):
    """ Tests para el endpoint POST /auth/recover/ """

    def setUp(self):
        """ Crear un usuario de prueba """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='oldpassword123'
        )

    @override_settings(DEBUG=True)
    @patch('apps.authentication.views.recover_mail')
    @patch('apps.authentication.views.generate_password', return_value='NewTempPass456')
    def test_recover_exitoso(self, mock_generate_password, mock_recover_mail):
        """ 
        Test: Recover exitoso cambia password y envía email
        """
        
        data = {
            'username': 'testuser',
            'email': 'test@example.com'
        }
        
        response = self.client.post('/auth/recover/', data, format='json')
        
        # Verificar respuesta exitosa
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('ok'))
        
        # Verificar que se generó nuevo password
        mock_generate_password.assert_called_once_with(use_upper=True, use_numbers=True)
        
        # Verificar que se intentó enviar email
        mock_recover_mail.assert_called_once()
        call_kwargs = mock_recover_mail.call_args[1]
        self.assertEqual(call_kwargs['tmp_pass'], 'NewTempPass456')
        
        # Verificar que el password cambió
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewTempPass456'))
        self.assertFalse(self.user.check_password('oldpassword123'))

    def test_recover_sin_username(self):
        """ 
        Test: Recover sin username debe fallar
        """
        
        data = {
            'email': 'test@example.com'
        }
        
        response = self.client.post('/auth/recover/', data, format='json')
        
        # Debe fallar
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_recover_sin_email(self):
        """ 
        Test: Recover sin email debe fallar
        """
        
        data = {
            'username': 'testuser'
        }
        
        response = self.client.post('/auth/recover/', data, format='json')
        
        # Debe fallar
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_recover_email_invalido(self):
        """ 
        Test: Recover con email inválido debe fallar
        """
        
        data = {
            'username': 'testuser',
            'email': 'not-an-email'
        }
        
        response = self.client.post('/auth/recover/', data, format='json')
        
        # Debe fallar
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Invalid email', response.data['error'])

    @override_settings(DEBUG=True)
    @patch('apps.authentication.views.recover_mail')
    @patch('apps.authentication.views.generate_password', return_value='NewTempPass456')
    def test_recover_usuario_inexistente_no_falla(self, mock_generate_password, mock_recover_mail):
        """ 
        Test: Recover con usuario inexistente devuelve OK
              (por seguridad, no revelar si el usuario existe)
        """
        
        data = {
            'username': 'nonexistent',
            'email': 'nonexistent@example.com'
        }
        
        response = self.client.post('/auth/recover/', data, format='json')
        
        # Debe devolver OK (por seguridad)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('ok'))
        
        # Pero NO debe enviar email ni generar password
        mock_recover_mail.assert_not_called()

    @override_settings(DEBUG=True)
    @patch('apps.authentication.views.recover_mail')
    @patch('apps.authentication.views.generate_password', return_value='NewTempPass456')
    def test_recover_username_correcto_email_incorrecto(self, mock_generate_password, mock_recover_mail):
        """ 
        Test: Recover con username correcto pero email incorrecto no hace nada
        """
        
        data = {
            'username': 'testuser',
            'email': 'wrong@example.com'  # ← Email incorrecto
        }
        
        response = self.client.post('/auth/recover/', data, format='json')
        
        # Debe devolver OK (por seguridad)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Pero NO debe enviar email
        mock_recover_mail.assert_not_called()

    @override_settings(DEBUG=True)
    @patch('apps.authentication.views.recover_mail', side_effect=Exception('Email service down'))
    @patch('apps.authentication.views.generate_password', return_value='NewTempPass456')
    def test_recover_falla_envio_email(self, mock_generate_password, mock_recover_mail):
        """ 
        Test: Si falla el envío de email, recover debe hacer rollback
        """
        
        data = {
            'username': 'testuser',
            'email': 'test@example.com'
        }
        
        # Guardar password actual
        old_password = self.user.password
        
        response = self.client.post('/auth/recover/', data, format='json')
        
        # Debe fallar
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # El password NO debe haber cambiado (rollback)
        self.user.refresh_from_db()
        self.assertEqual(self.user.password, old_password)
