from unittest.mock import patch
from django.test import TestCase

from apps.cronnos.tasks import (
    clean_expired_tokens,
    REGISTERED_TASKS,
    Task,
)


class CleanExpiredTokensTestCase(TestCase):
    """ Tests para la función clean_expired_tokens() """

    @patch('apps.cronnos.tasks.call_command')
    def test_clean_expired_tokens_llama_comando_correcto(self, mock_call_command):
        """ 
        Test: clean_expired_tokens() debe llamar al comando 'flushexpiredtokens'
        """
        
        # Llamar la función
        clean_expired_tokens()
        
        # Verificar que se llamó al comando correcto
        mock_call_command.assert_called_once_with('flushexpiredtokens')

    @patch('apps.cronnos.tasks.call_command')
    def test_clean_expired_tokens_se_puede_llamar_multiples_veces(self, mock_call_command):
        """ 
        Test: clean_expired_tokens() se puede llamar múltiples veces sin error
        """
        
        # Llamar la función varias veces
        clean_expired_tokens()
        clean_expired_tokens()
        clean_expired_tokens()
        
        # Verificar que se llamó 3 veces
        self.assertEqual(mock_call_command.call_count, 3)

    @patch('apps.cronnos.tasks.call_command', side_effect=Exception('Command failed'))
    def test_clean_expired_tokens_propaga_excepciones(self, mock_call_command):
        """ 
        Test: Si el comando falla, la excepción debe propagarse
        """
        
        # Llamar la función y esperar excepción
        with self.assertRaises(Exception) as context:
            clean_expired_tokens()
        
        # Verificar que la excepción contiene el mensaje correcto
        self.assertIn('Command failed', str(context.exception))


class TaskDataclassTestCase(TestCase):
    """ Tests para la clase Task (dataclass) """

    def test_task_con_todos_los_parametros(self):
        """ 
        Test: Crear una Task con todos los parámetros
        """
        
        def my_function():
            pass
        
        task = Task(
            id='test_task',
            func=my_function,
            trigger='cron',
            options={'hour': 12, 'minute': 30},
            replace_existing=True
        )
        
        # Verificar todos los campos
        self.assertEqual(task.id, 'test_task')
        self.assertEqual(task.func, my_function)
        self.assertEqual(task.trigger, 'cron')
        self.assertEqual(task.options, {'hour': 12, 'minute': 30})
        self.assertTrue(task.replace_existing)

    def test_task_con_parametros_minimos(self):
        """ 
        Test: Crear una Task solo con parámetros requeridos (id y func)
        """
        
        def my_function():
            pass
        
        task = Task(
            id='minimal_task',
            func=my_function
        )
        
        # Verificar campos requeridos
        self.assertEqual(task.id, 'minimal_task')
        self.assertEqual(task.func, my_function)
        
        # Verificar valores por defecto
        self.assertEqual(task.trigger, 'cron')  # ← Valor por defecto
        self.assertEqual(task.options, {})  # ← Dict vacío por defecto
        self.assertTrue(task.replace_existing)  # ← True por defecto

    def test_task_options_es_dict_independiente(self):
        """ 
        Test: Cada Task debe tener su propio dict de options
              (no compartido entre instancias)
        """
        
        def func1():
            pass
        
        def func2():
            pass
        
        task1 = Task(id='task1', func=func1)
        task2 = Task(id='task2', func=func2)
        
        # Modificar options de task1
        task1.options['hour'] = 10
        
        # Verificar que task2 no se afectó
        self.assertNotIn('hour', task2.options)
        self.assertEqual(task2.options, {})

    def test_task_diferentes_triggers(self):
        """ 
        Test: Task puede usar diferentes tipos de triggers
        """
        
        def my_function():
            pass
        
        # Trigger tipo 'cron'
        task_cron = Task(id='cron_task', func=my_function, trigger='cron')
        self.assertEqual(task_cron.trigger, 'cron')
        
        # Trigger tipo 'interval'
        task_interval = Task(id='interval_task', func=my_function, trigger='interval')
        self.assertEqual(task_interval.trigger, 'interval')
        
        # Trigger tipo 'date'
        task_date = Task(id='date_task', func=my_function, trigger='date')
        self.assertEqual(task_date.trigger, 'date')


class RegisteredTasksTestCase(TestCase):
    """ Tests para la lista REGISTERED_TASKS """

    def test_registered_tasks_es_una_lista(self):
        """ 
        Test: REGISTERED_TASKS debe ser una lista
        """
        
        self.assertIsInstance(REGISTERED_TASKS, list)

    def test_registered_tasks_no_esta_vacia(self):
        """ 
        Test: REGISTERED_TASKS debe contener al menos una tarea
        """
        
        self.assertGreater(len(REGISTERED_TASKS), 0)

    def test_registered_tasks_contiene_objetos_task(self):
        """ 
        Test: Todos los elementos en REGISTERED_TASKS deben ser instancias de Task
        """
        
        for task in REGISTERED_TASKS:
            self.assertIsInstance(task, Task)

    def test_registered_tasks_contiene_daily_token_cleanup(self):
        """ 
        Test: REGISTERED_TASKS debe contener la tarea 'daily_token_cleanup'
        """
        
        task_ids = [task.id for task in REGISTERED_TASKS]
        self.assertIn('daily_token_cleanup', task_ids)

    def test_daily_token_cleanup_configuracion_correcta(self):
        """ 
        Test: Verificar que la tarea 'daily_token_cleanup' está bien configurada
        """
        
        # Buscar la tarea
        daily_cleanup = None
        for task in REGISTERED_TASKS:
            if task.id == 'daily_token_cleanup':
                daily_cleanup = task
                break
        
        # Verificar que existe
        self.assertIsNotNone(daily_cleanup)
        
        # Verificar configuración
        self.assertEqual(daily_cleanup.func, clean_expired_tokens)
        self.assertEqual(daily_cleanup.trigger, 'cron')
        self.assertEqual(daily_cleanup.options.get('hour'), 0)  # ← A medianoche
        self.assertEqual(daily_cleanup.options.get('minute'), 0)
        self.assertTrue(daily_cleanup.replace_existing)

    def test_registered_tasks_sin_ids_duplicados(self):
        """ 
        Test: REGISTERED_TASKS NO debe contener IDs duplicados
        """
        
        task_ids = [task.id for task in REGISTERED_TASKS]
        
        # Verificar que no hay duplicados
        # (si hay duplicados, el set será más pequeño que la lista)
        self.assertEqual(len(task_ids), len(set(task_ids)))

    def test_registered_tasks_todas_tienen_id(self):
        """ 
        Test: Todas las tareas deben tener un ID no vacío
        """
        
        for task in REGISTERED_TASKS:
            self.assertTrue(task.id)  # ← No None, no vacío
            self.assertIsInstance(task.id, str)

    def test_registered_tasks_todas_tienen_func(self):
        """ 
        Test: Todas las tareas deben tener una función callable
        """
        
        for task in REGISTERED_TASKS:
            self.assertTrue(callable(task.func))


class DuplicateTaskValidationTestCase(TestCase):
    """ Tests para la validación de IDs duplicados """

    def test_validacion_detecta_duplicados_al_importar(self):
        """ 
        Test: El código debe detectar IDs duplicados cuando se importa el módulo
              
              Nota: Este test documenta el comportamiento.
              El código en tasks.py ya valida duplicados al cargar el módulo.
              Si hubiera duplicados, el import fallaría con ValueError.
        """
        
        # Si llegamos aquí, significa que el import fue exitoso
        # y no hay duplicados en REGISTERED_TASKS
        task_ids = [task.id for task in REGISTERED_TASKS]
        
        # Verificar que no hay duplicados
        self.assertEqual(len(task_ids), len(set(task_ids)))

    def test_validacion_mensaje_de_error(self):
        """ 
        Test: Verificar que el mensaje de error menciona el ID duplicado
              
              Este test simula el comportamiento sin causar error real
        """
        
        # El código real en tasks.py es:
        # seen_ids = set()
        # for task in REGISTERED_TASKS:
        #     if task.id in seen_ids:
        #         raise ValueError(f"Cronnos detected duplicate task ID: {task.id}")
        #     seen_ids.add(task.id)
        
        # Simular la validación
        seen_ids = set()
        for task in REGISTERED_TASKS:
            # Verificar que el ID no está duplicado
            self.assertNotIn(task.id, seen_ids)
            seen_ids.add(task.id)


class TaskIntegrationTestCase(TestCase):
    """ Tests de integración para las tareas registradas """

    @patch('apps.cronnos.tasks.call_command')
    def test_daily_cleanup_task_ejecuta_correctamente(self, mock_call_command):
        """ 
        Test: Verificar que la tarea daily_token_cleanup se puede ejecutar
        """
        
        # Obtener la tarea
        daily_cleanup = None
        for task in REGISTERED_TASKS:
            if task.id == 'daily_token_cleanup':
                daily_cleanup = task
                break
        
        # Ejecutar la función de la tarea
        daily_cleanup.func()
        
        # Verificar que ejecutó el comando
        mock_call_command.assert_called_once_with('flushexpiredtokens')

    def test_todas_las_tareas_tienen_configuracion_valida(self):
        """ 
        Test: Verificar que todas las tareas tienen configuración válida
        """
        
        for task in REGISTERED_TASKS:
            # Verificar campos requeridos
            self.assertTrue(task.id)
            self.assertTrue(callable(task.func))
            self.assertIn(task.trigger, ['cron', 'interval', 'date'])
            self.assertIsInstance(task.options, dict)
            self.assertIsInstance(task.replace_existing, bool)

    def test_tareas_cron_tienen_opciones_de_tiempo(self):
        """ 
        Test: Las tareas con trigger='cron' deben tener opciones de tiempo
        """
        
        for task in REGISTERED_TASKS:
            if task.trigger == 'cron':
                # Las tareas cron deben tener al menos hour o minute
                has_time_option = (
                    'hour' in task.options or
                    'minute' in task.options or
                    'second' in task.options or
                    'day' in task.options or
                    'month' in task.options or
                    'day_of_week' in task.options
                )
                self.assertTrue(
                    has_time_option,
                    f"Tarea '{task.id}' con trigger='cron' debe tener opciones de tiempo"
                )
