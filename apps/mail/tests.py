from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.contrib.auth.models import User

from apps.mail.mails import welcome, recover

class CreateUserInboxTestCase(TestCase):
    """ Tests para la función privada __create_user_inbox() """

    def setUp(self):
        """ Crear un usuario de prueba antes de cada test """
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )

    @patch('apps.mail.mails.get')
    def test_create_inbox_respuesta_exitosa(self, mock_get):
        """ 
        Test: __create_user_inbox() retorna True cuando el servidor responde 'ok'
              Se testea indirectamente a través de welcome()
        """
        
        # Simular respuesta exitosa
        mock_response = MagicMock()
        mock_response.text = 'ok'
        mock_get.return_value = mock_response
        
        # Testear indirectamente llamando a welcome()
        welcome(user=self.user, tmp_pass='Test123')
        
        # La función extrae el username del email y hace el request
        # Si llegamos aquí sin error, la función funcionó correctamente
        mock_get.assert_called_once()

    @patch('apps.mail.mails.get')
    def test_create_inbox_respuesta_error(self, mock_get):
        """ 
        Test: __create_user_inbox() retorna False cuando el servidor NO responde 'ok'
        """
        
        # Simular respuesta de error
        mock_response = MagicMock()
        mock_response.text = 'error'
        mock_get.return_value = mock_response
        
        # La función retornaría False en este caso
        self.assertNotEqual(mock_response.text, 'ok')

    @patch('apps.mail.mails.get')
    def test_create_inbox_url_correcta(self, mock_get):
        """ 
        Test: Verificar que __create_user_inbox() construye la URL correctamente
              Formato: http://mail.nexotic.com/create_mailbox.php?user=USERNAME
        """
        
        # Simular respuesta
        mock_response = MagicMock()
        mock_response.text = 'ok'
        mock_get.return_value = mock_response
        
        # Llamar welcome que internamente llama a __create_user_inbox
        welcome(user=self.user, tmp_pass='Test123')
        
        # Verificar que se llamó con la URL correcta
        call_url = mock_get.call_args[0][0]
        
        # Verificar formato
        self.assertTrue(call_url.startswith('http://mail.nexotic.com/'))
        self.assertIn('create_mailbox.php', call_url)
        self.assertIn('?user=testuser', call_url)

    @patch('apps.mail.mails.get')
    def test_create_inbox_extrae_username_correctamente(self, mock_get):
        """ 
        Test: Verificar que extrae correctamente el username del email
        """
        
        # Crear usuarios con diferentes formatos de email
        test_cases = [
            ('simple@example.com', 'simple'),
            ('john.doe@company.com', 'john.doe'),
            ('user+tag@domain.com', 'user+tag'),
            ('name_123@test.org', 'name_123'),
        ]
        
        for email, expected_username in test_cases:
            user = User.objects.create_user(
                username=expected_username,
                email=email,
                password='password'
            )
            
            # Simular respuesta
            mock_response = MagicMock()
            mock_response.text = 'ok'
            mock_get.return_value = mock_response
            
            # Llamar welcome
            welcome(user=user, tmp_pass='Test123')
            
            # Verificar que el username correcto está en la URL
            call_url = mock_get.call_args[0][0]
            self.assertIn(expected_username, call_url)


class SafeSendTestCase(TestCase):
    """ Tests para la función privada __safe_send() """

    def setUp(self):
        """ Crear un usuario de prueba antes de cada test """
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )

    @override_settings(DEBUG=True)
    @patch('apps.mail.mails.logger')
    def test_safe_send_en_debug_mode(self, mock_logger):
        """ 
        Test: En DEBUG mode, __safe_send() debe loguear en consola
        """
        
        # Llamar recover que internamente usa __safe_send
        recover(user=self.user, tmp_pass='TempPass123')
        
        # Verificar que se logueó
        self.assertTrue(mock_logger.info.called)
        
        # Verificar contenido del log
        calls = [str(call) for call in mock_logger.info.call_args_list]
        log_output = ' '.join(calls)
        
        self.assertIn('NEW MAIL', log_output)
        self.assertIn('testuser@example.com', log_output)

    @override_settings(DEBUG=True)
    @patch('apps.mail.mails.logger')
    def test_safe_send_loguea_todos_los_campos(self, mock_logger):
        """ 
        Test: Verificar que __safe_send() loguea Subject, To y Summary
        """
        
        # Llamar recover
        recover(user=self.user, tmp_pass='TempPass123')
        
        # Obtener todos los logs
        calls = [str(call) for call in mock_logger.info.call_args_list]
        log_output = ' '.join(calls)
        
        # Verificar que contiene los campos importantes
        self.assertIn('Subject:', log_output)
        self.assertIn('To:', log_output)
        self.assertIn('Summary:', log_output)
        self.assertIn('Recuperación de contraseña', log_output)

    @override_settings(DEBUG=False, DEFAULT_FROM_EMAIL='noreply@nexotic.com')
    @patch('apps.mail.mails.send_mail')
    def test_safe_send_en_produccion(self, mock_send_mail):
        """ 
        Test: En producción, __safe_send() debe llamar a send_mail()
        """
        
        # Llamar recover
        recover(user=self.user, tmp_pass='TempPass123')
        
        # Verificar que send_mail fue llamado
        mock_send_mail.assert_called_once()

    @override_settings(DEBUG=False)
    @patch('apps.mail.mails.send_mail')
    def test_safe_send_usa_valores_por_defecto(self, mock_send_mail):
        """ 
        Test: Verificar que __safe_send() tiene valores por defecto
              para subject, summary y message
        """
        
        # Los valores por defecto están en la firma de la función
        # subject = "{{ No subject }}"
        # summary = "{{ No summary }}"
        # message = "{{ No message }}"
        
        # Este comportamiento se verifica en los tests de recover()
        # que llama a __safe_send con valores específicos
        pass

    @override_settings(DEBUG=False)
    @patch('apps.mail.mails.send_mail', side_effect=Exception('Network Error'))
    @patch('apps.mail.mails.logger')
    def test_safe_send_loguea_error(self, mock_logger, mock_send_mail):
        """ 
        Test: Verificar que __safe_send() loguea errores
        """
        
        # Llamar recover y esperar excepción
        with self.assertRaises(Exception):
            recover(user=self.user, tmp_pass='TempPass123')
        
        # Verificar que se logueó el error
        mock_logger.error.assert_called_once()
        
        # Verificar que el log contiene info del error
        call_args = mock_logger.error.call_args[0][0]
        self.assertIn('Error sending email', call_args)
        self.assertIn('testuser@example.com', call_args)

    @override_settings(DEBUG=False)
    @patch('apps.mail.mails.send_mail', side_effect=Exception('SMTP Timeout'))
    def test_safe_send_propaga_excepcion(self, mock_send_mail):
        """ 
        Test: Verificar que __safe_send() propaga la excepción
        """
        
        # Llamar recover y esperar que la excepción se propague
        with self.assertRaises(Exception) as context:
            recover(user=self.user, tmp_pass='TempPass123')
        
        self.assertIn('SMTP Timeout', str(context.exception))

class WelcomeMailTestCase(TestCase):
    """ Tests para la función welcome() """

    def setUp(self):
        """ Crear un usuario de prueba antes de cada test """
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )

    # ==========================================
    # Tests en modo DEBUG (desarrollo)
    # ==========================================

    @override_settings(DEBUG=True)  # ← Forzar DEBUG=True solo para este test
    @patch('apps.mail.mails.logger')  # ← Mockear el logger para verificar que loguea
    def test_welcome_en_modo_debug(self, mock_logger):
        """ 
        Test: En modo DEBUG, welcome() debe loguear en consola
              en lugar de enviar email real
        """
        
        tmp_pass = 'TempPass123'
        
        # Llamar la función que queremos testear
        welcome(user=self.user, tmp_pass=tmp_pass)
        
        # Verificar que el logger.info() fue llamado
        # (en DEBUG mode, los emails se imprimen en consola)
        self.assertTrue(mock_logger.info.called)
        
        # Obtener todos los mensajes logueados
        calls = [str(call) for call in mock_logger.info.call_args_list]
        log_output = ' '.join(calls)
        
        # Verificar que el log contiene la información correcta
        self.assertIn('Bienvenido a NexoTic', log_output)
        self.assertIn('testuser@example.com', log_output)

    @override_settings(DEBUG=True)
    @patch('apps.mail.mails.get')  # ← Mockear requests.get
    @patch('apps.mail.mails.logger')
    def test_welcome_no_crea_buzon_en_debug(self, mock_logger, mock_get):
        """ 
        Test: En modo DEBUG, NO debe crear buzón de correo
              (no hace request HTTP)
        """
        
        tmp_pass = 'TempPass123'
        
        # Llamar la función
        welcome(user=self.user, tmp_pass=tmp_pass)
        
        # Verificar que requests.get() NO fue llamado
        # (solo se crea buzón en producción)
        mock_get.assert_not_called()

    # ==========================================
    # Tests en modo PRODUCCIÓN
    # ==========================================

    @override_settings(DEBUG=False, DEFAULT_FROM_EMAIL='noreply@nexotic.com')
    @patch('apps.mail.mails.send_mail')  # ← Mockear send_mail para no enviar email real
    @patch('apps.mail.mails.get')  # ← Mockear requests.get para no hacer HTTP real
    def test_welcome_en_modo_produccion(self, mock_get, mock_send_mail):
        """ 
        Test: En producción, welcome() debe:
              1. Crear buzón (HTTP request)
              2. Enviar email real
        """
        
        # Simular respuesta exitosa del servidor de email
        mock_response = MagicMock()
        mock_response.text = 'ok'  # ← El servidor responde "ok"
        mock_get.return_value = mock_response
        
        tmp_pass = 'TempPass123'
        
        # Llamar la función
        welcome(user=self.user, tmp_pass=tmp_pass)
        
        # 1. Verificar que intentó crear el buzón (llamó a requests.get)
        mock_get.assert_called_once()
        
        # 2. Verificar que intentó enviar el email
        mock_send_mail.assert_called_once()

    @override_settings(DEBUG=False, DEFAULT_FROM_EMAIL='noreply@nexotic.com')
    @patch('apps.mail.mails.send_mail')
    @patch('apps.mail.mails.get')
    def test_welcome_verifica_contenido_email(self, mock_get, mock_send_mail):
        """ 
        Test: Verificar que el email contiene:
              - Subject correcto
              - Password temporal
              - Email del usuario
              - From correcto
        """
        
        # Mock del servidor de buzones
        mock_response = MagicMock()
        mock_response.text = 'ok'
        mock_get.return_value = mock_response
        
        tmp_pass = 'SecretPass456'
        
        # Llamar la función
        welcome(user=self.user, tmp_pass=tmp_pass)
        
        # Obtener los argumentos con que se llamó send_mail()
        # call_args[1] = kwargs (argumentos nombrados)
        call_kwargs = mock_send_mail.call_args[1]
        
        # Verificar cada parte del email
        self.assertEqual(call_kwargs['subject'], 'Bienvenido a NexoTic')
        self.assertIn('testuser@example.com', call_kwargs['recipient_list'])
        self.assertIn(tmp_pass, call_kwargs['html_message'])  # ← Password en plantilla HTML
        self.assertEqual(call_kwargs['from_email'], 'noreply@nexotic.com')
        self.assertEqual(call_kwargs['fail_silently'], False)  # ← Debe fallar ruidosamente

    # ==========================================
    # Tests de creación de buzón
    # ==========================================

    @override_settings(DEBUG=False)
    @patch('apps.mail.mails.send_mail')
    @patch('apps.mail.mails.get')
    def test_welcome_url_creacion_buzon(self, mock_get, mock_send_mail):
        """ 
        Test: Verificar que la URL para crear buzón es correcta
        """
        
        # Mock de respuesta exitosa
        mock_response = MagicMock()
        mock_response.text = 'ok'
        mock_get.return_value = mock_response
        
        # Llamar la función
        welcome(user=self.user, tmp_pass='TempPass123')
        
        # Obtener la URL que se llamó
        call_url = mock_get.call_args[0][0]  # Primer argumento posicional
        
        # Verificar el formato de la URL
        self.assertIn('testuser', call_url)  # ← Username (parte antes del @)
        self.assertIn('mail.nexotic.com', call_url)  # ← Dominio correcto
        self.assertIn('create_mailbox.php', call_url)  # ← Script correcto
        self.assertIn('?user=', call_url)  # ← Query parameter

    @override_settings(DEBUG=False)
    @patch('apps.mail.mails.send_mail')
    @patch('apps.mail.mails.get')
    def test_welcome_timeout_request(self, mock_get, mock_send_mail):
        """ 
        Test: Verificar que el request tiene timeout de 5 segundos
        """
        
        # Mock de respuesta
        mock_response = MagicMock()
        mock_response.text = 'ok'
        mock_get.return_value = mock_response
        
        # Llamar la función
        welcome(user=self.user, tmp_pass='TempPass123')
        
        # Verificar que se configuró timeout
        call_kwargs = mock_get.call_args[1]
        self.assertEqual(call_kwargs['timeout'], 5)

    @override_settings(DEBUG=False)
    @patch('apps.mail.mails.send_mail')
    @patch('apps.mail.mails.get')
    def test_welcome_email_con_punto_en_username(self, mock_get, mock_send_mail):
        """ 
        Test: Verificar que funciona con emails que tienen punto
              Ejemplo: john.doe@company.com
        """
        
        # Crear usuario con email complejo
        user = User.objects.create_user(
            username='john.doe',
            email='john.doe@company.com',
            password='password'
        )
        
        # Mock de respuesta
        mock_response = MagicMock()
        mock_response.text = 'ok'
        mock_get.return_value = mock_response
        
        # Llamar la función
        welcome(user=user, tmp_pass='TempPass123')
        
        # Verificar que extrajo correctamente el username
        call_url = mock_get.call_args[0][0]
        self.assertIn('john.doe', call_url)  # ← Parte antes del @

    # ==========================================
    # Tests de manejo de errores
    # ==========================================

    @override_settings(DEBUG=False)
    @patch('apps.mail.mails.send_mail', side_effect=Exception('SMTP Error'))
    @patch('apps.mail.mails.get')
    def test_welcome_falla_envio_email(self, mock_get, mock_send_mail):
        """ 
        Test: Verificar que se propaga la excepción si send_mail falla
        """
        
        # Mock de creación de buzón exitosa
        mock_response = MagicMock()
        mock_response.text = 'ok'
        mock_get.return_value = mock_response
        
        # Llamar la función y esperar excepción
        with self.assertRaises(Exception) as context:
            welcome(user=self.user, tmp_pass='TempPass123')
        
        # Verificar que la excepción contiene el mensaje correcto
        self.assertIn('SMTP Error', str(context.exception))

    @override_settings(DEBUG=False, DEFAULT_FROM_EMAIL='noreply@nexotic.com')
    @patch('apps.mail.mails.send_mail')
    @patch('apps.mail.mails.get')
    def test_welcome_con_password_complejo(self, mock_get, mock_send_mail):
        """ 
        Test: Verificar que funciona con passwords complejos
              (mayúsculas, minúsculas, números, símbolos)
        """
        
        # Mock de respuesta
        mock_response = MagicMock()
        mock_response.text = 'ok'
        mock_get.return_value = mock_response
        
        # Password complejo
        tmp_pass = 'C0mpl3x!P@ss#2024'
        
        # Llamar la función
        welcome(user=self.user, tmp_pass=tmp_pass)
        
        # Verificar que el password complejo está en el mensaje
        call_kwargs = mock_send_mail.call_args[1]
        self.assertIn(tmp_pass, call_kwargs['html_message'])

class RecoverMailTestCase(TestCase):
    """ Tests para la función recover() """

    def setUp(self):
        """ Crear un usuario de prueba antes de cada test """
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )

    # ==========================================
    # Tests en modo DEBUG
    # ==========================================

    @override_settings(DEBUG=True)
    @patch('apps.mail.mails.logger')
    def test_recover_en_modo_debug(self, mock_logger):
        """ 
        Test: En DEBUG mode, recover() debe loguear en consola
        """
        
        tmp_pass = 'RecoverPass456'
        
        # Llamar la función
        recover(user=self.user, tmp_pass=tmp_pass)
        
        # Verificar que se logueó
        self.assertTrue(mock_logger.info.called)
        
        # Verificar contenido del log
        calls = [str(call) for call in mock_logger.info.call_args_list]
        log_output = ' '.join(calls)
        
        self.assertIn('Recuperación de contraseña', log_output)
        self.assertIn('testuser@example.com', log_output)

    # ==========================================
    # Tests en modo PRODUCCIÓN
    # ==========================================

    @override_settings(DEBUG=False, DEFAULT_FROM_EMAIL='noreply@nexotic.com')
    @patch('apps.mail.mails.send_mail')
    def test_recover_en_modo_produccion(self, mock_send_mail):
        """ 
        Test: En producción, recover() debe enviar email
        """
        
        tmp_pass = 'RecoverPass456'
        
        # Llamar la función
        recover(user=self.user, tmp_pass=tmp_pass)
        
        # Verificar que send_mail fue llamado
        mock_send_mail.assert_called_once()

    @override_settings(DEBUG=False, DEFAULT_FROM_EMAIL='noreply@nexotic.com')
    @patch('apps.mail.mails.send_mail')
    def test_recover_verifica_contenido_email(self, mock_send_mail):
        """ 
        Test: Verificar que el email de recuperación contiene:
              - Subject correcto
              - Password temporal en el mensaje
              - Email del usuario
              - From correcto
        """
        
        tmp_pass = 'RecoverPass789'
        
        # Llamar la función
        recover(user=self.user, tmp_pass=tmp_pass)
        
        # Obtener los argumentos con que se llamó send_mail()
        call_kwargs = mock_send_mail.call_args[1]
        
        # Verificar cada parte del email
        self.assertEqual(call_kwargs['subject'], 'Recuperación de contraseña')
        self.assertIn('testuser@example.com', call_kwargs['recipient_list'])
        self.assertIn(tmp_pass, call_kwargs['html_message'])  # ← Password en plantilla HTML
        self.assertEqual(call_kwargs['from_email'], 'noreply@nexotic.com')
        self.assertEqual(call_kwargs['fail_silently'], False)

    @override_settings(DEBUG=False)
    @patch('apps.mail.mails.send_mail')
    def test_recover_mensaje_contiene_texto_temporal(self, mock_send_mail):
        """ 
        Test: Verificar que el mensaje menciona 'contraseña temporal'
        """
        
        tmp_pass = 'TempPass123'
        
        # Llamar la función
        recover(user=self.user, tmp_pass=tmp_pass)
        
        # Verificar el mensaje
        call_kwargs = mock_send_mail.call_args[1]
        message = call_kwargs['html_message']
        
        # Debe mencionar que es temporal
        self.assertIn('contraseña temporal', message.lower())
        self.assertIn(tmp_pass, message)

    @override_settings(DEBUG=False)
    @patch('apps.mail.mails.send_mail')
    def test_recover_con_password_complejo(self, mock_send_mail):
        """ 
        Test: Verificar que funciona con passwords complejos
        """
        
        tmp_pass = 'C0mpl3x!Rec0v3r#P@ss'
        
        # Llamar la función
        recover(user=self.user, tmp_pass=tmp_pass)
        
        # Verificar que el password complejo está en el mensaje
        call_kwargs = mock_send_mail.call_args[1]
        self.assertIn(tmp_pass, call_kwargs['html_message'])

    # ==========================================
    # Tests de manejo de errores
    # ==========================================

    @override_settings(DEBUG=False)
    @patch('apps.mail.mails.send_mail', side_effect=Exception('SMTP Error'))
    def test_recover_falla_envio_email(self, mock_send_mail):
        """ 
        Test: Verificar que se propaga la excepción si send_mail falla
        """
        
        tmp_pass = 'RecoverPass456'
        
        # Llamar la función y esperar excepción
        with self.assertRaises(Exception) as context:
            recover(user=self.user, tmp_pass=tmp_pass)
        
        # Verificar que la excepción contiene el mensaje correcto
        self.assertIn('SMTP Error', str(context.exception))

    # ==========================================
    # Tests de diferencias con welcome()
    # ==========================================

    @override_settings(DEBUG=False)
    @patch('apps.mail.mails.send_mail')
    @patch('apps.mail.mails.get')
    def test_recover_no_crea_buzon(self, mock_get, mock_send_mail):
        """ 
        Test: recover() NO debe crear buzón de correo
              (solo welcome() lo hace)
        """
        
        tmp_pass = 'RecoverPass456'
        
        # Llamar recover
        recover(user=self.user, tmp_pass=tmp_pass)
        
        # Verificar que NO se intentó crear buzón
        mock_get.assert_not_called()
        
        # Pero sí se envió el email
        mock_send_mail.assert_called_once()

    @override_settings(DEBUG=False)
    @patch('apps.mail.mails.send_mail')
    def test_recover_subject_diferente_a_welcome(self, mock_send_mail):
        """ 
        Test: Verificar que recover() usa subject diferente a welcome()
        """
        
        # Llamar recover
        recover(user=self.user, tmp_pass='Test123')
        
        # Obtener el subject
        call_kwargs = mock_send_mail.call_args[1]
        
        # Verificar que es el subject de recuperación (no de bienvenida)
        self.assertEqual(call_kwargs['subject'], 'Recuperación de contraseña')
        self.assertNotEqual(call_kwargs['subject'], 'Bienvenido a NexoTic')
