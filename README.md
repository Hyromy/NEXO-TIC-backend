# NEXO_TIC (Backend)

![Django](https://img.shields.io/badge/Django-6.0.1-green?logo=django)
![DRF](https://img.shields.io/badge/DRF-3.16.1-red?logo=django)
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Docker](https://img.shields.io/badge/Docker-Container-blue?logo=docker)

## ÍNDICE
- [NEXO\_TIC (Backend)](#nexo_tic-backend)
  - [ÍNDICE](#índice)
  - [VARIABLES DE ENTORNO](#variables-de-entorno)
  - [INSTALACIÓN](#instalación)
  - [DESPLIEGUE](#despliegue)
    - [Local](#local)
    - [Docker](#docker)
    - [Docker Compose](#docker-compose)
  - [USO](#uso)
  - [SERVICIOS ADICIONALES](#servicios-adicionales)
    - [Especificaciones de la VM](#especificaciones-de-la-vm)
    - [Configuración de Red](#configuración-de-red)
    - [Credenciales de la VM](#credenciales-de-la-vm)

## VARIABLES DE ENTORNO

En la raíz del proyecto crea un archivo `.env` y define las variables de entorno necesarias.

Sin embargo el proyecto puede funcionar sin establecer ninguna variable.

| Clave | Valor por defecto | Descripción |
| - | - | - |
| `PRODUCTION` | `False` | Modo de despliegue |
| `DJANGO_SECRET_KEY` | `"secret"` | Secret de seguridad |
| `PG_DB` | `"postgres"` | Base de datos de PostgreSQL |
| `PG_USER` | `"postgres"` | Usuario de PostgreSQL |
| `PG_PASS` | `"postgres"` | Contraseña de PostgreSQL |
| `PG_HOST` | `"localhost"` | Host de PostgreSQL |
| `PG_PORT` | `5432` | Puerto de PostgreSQL |
| `MAILER_IP` | `"192.168.1.100"` | Dirección de servidor de correos SMTP |
| `MAILER_PORT` | `25` | Puerto de servidor de correos SMTP |

> [!NOTE]
> En caso de que `PRODUCTION=False` la base de datos será una instancia de __SQLite__

## INSTALACIÓN

1. Creación de entorno virtual
   ```bash
   python -m venv env
   ```

2. Activar entorno virtual
   ```bash
   .\env\Scripts\activate    # Windows
   ```

3. Instalación de dependencias
   ```bash
   pip install -r requirements.txt
   ```

## DESPLIEGUE

### Local
Para el caso de `PRODUCTION=True` y si es que aún no hay un archivo `db.sqlite3` o esta vacío, aplica las migraciones.
```bash
python manage.py migrate
```

Posterior a ello, ejecuta el proyecto, este se encuentra en el puerto __8000__ pero se puede especificar otro al final de comando
```bash
python manage.py runserver         # Puerto 8000

python manage.py runserver 7001    # Puerto 7001
```

### Docker

Crea la imagen del proyecto
```bash
docker build -t app_image .
```

Crea un contenedor de la imagen previamente construida.
```bash
docker run -d --name app_container -p 8000:8000 app_image
```

### Docker Compose
[Este archivo](./docker-compose.yml) está pensado para un despliegue rápido pre-producción. Solo tiene configurado `PRODUCTION=True` y una conexion a un contenedor de PostgreSQL-18 con su respectivo volumen.
```bash
docker compose up
```

## USO
El proyecto incluye interfaces de usuario y una API REST ubicado en `/api/`. Cada subruta perteneciente posee 5 metodos (GET, POST, PUT, PATCH y DELETE). A continuacion se muestra el uso de los endpoints usando `users/` como ejemplo.

```
[GET]       /api/users/             ->    Búsqueda general
[POST]      /api/users/             ->    Registro

[GET]       /api/users/<int:id>/    ->    Búsqueda especifica
[PUT]       /api/users/<int:id>/    ->    Actualización completa
[PATCH]     /api/users/<int:id>/    ->    Actualización parcial
[DELETE]    /api/users/<int:id>/    ->    Eliminación
```

> [!WARNING]
> Todos los enpoints deben de tener el prefijo `api/` y terminar en `/`.

## SERVICIOS ADICIONALES

Para fines demostrativos, se provee una [máquina virtual (.ova)](https://drive.google.com/drive/folders/14Xemi1hzUwIlnEw8voOBDg7O-mPNd43a?usp=sharing) pre-configurada. Esto es necesario cuando `PRODUCTION=True`, ya que el módulo [mail](./apps/mail/) requiere un servidor SMTP activo y una infraestructura de red específica.

### Especificaciones de la VM
La máquina virtual **Debian** incluye:
- **DNS (bind9):** Resuelve los dominios locales del proyecto.
- **Proxy Inverso (Nginx):** Redirige el tráfico.
- **MTA (Postfix):** Gestión de envío y recepción de correos.
- **Webmail/Scripting (PHP):** Lógica para creación de buzones y visualización.

> [!WARNING]
> La configuración de la VM puede no ser apta para entornos productivos.

### Configuración de Red
La VM debe importarse usando virtualización (ej. VirtualBox) con la red en modo **Adaptador Puente (Bridged Adapter)**.

**Configuración por defecto:**
La VM tiene una IP estática, pero espera que la máquina anfitriona (tu PC) tenga una IP específica para que el DNS funcione correctamente.

| Dispositivo | IP Configurada | Dominio |
| - | - | - |
| **VM (Guest)** | `192.168.1.100` | `mail.nexotic.com` |
| **PC (Host)** | `192.168.1.128` | `nexotic.com` |

> [!IMPORTANT]
> Si tu red local asigna IPs diferentes, deberás entrar a la VM y modificar las zonas DNS o ajustar la asignación de IPs del router.

### Credenciales de la VM
- **Usuario:** `root`
- **Contraseña:** `hyro`
