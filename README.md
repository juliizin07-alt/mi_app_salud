# 🧬 Jarvice Health AI

Sistema de asistencia y monitoreo de salud desarrollado con Django, orientado a la gestión de pacientes, seguimiento clínico, medicación, signos vitales, alertas, emergencias y comunicación entre usuarios y el sistema.

**Jarvice Health AI** fue desarrollado como proyecto académico de programación y desarrollo de software, utilizando una arquitectura modular preparada para futuras ampliaciones.

> **Aviso:** Jarvice es un sistema informático de asistencia y monitoreo. Sus análisis, registros y alertas no sustituyen la evaluación, diagnóstico ni intervención de un profesional de la salud.

---

## 📋 Características principales

* Sistema de autenticación de usuarios.
* Gestión de perfiles, roles y permisos.
* Paneles diferenciados según el tipo de usuario.
* Gestión de pacientes.
* Historia clínica.
* Registro y análisis de signos vitales.
* Motor de análisis clínico.
* Gestión de medicación y recordatorios.
* Evolución médica y de enfermería.
* Estudios médicos y solicitudes.
* Monitoreo mediante dispositivos.
* API para recepción de signos vitales.
* Comunicación en tiempo real mediante Django Channels y WebSockets.
* Sistema de alertas clínicas.
* Escalamiento de emergencias mediante contactos 1, 2 y 3.
* Integración con WhatsApp mediante Twilio.
* Acceso de emergencia mediante QR.
* Ficha clínica de emergencia autorizada.
* Registro de ubicación GPS.
* Integración de coordenadas con Google Maps.
* Centro de Atención Jarvice.
* JARVICE CORE para administración y supervisión centralizada.
* Recuperación de contraseña mediante correo electrónico.
* Registro de auditoría de operaciones.
* Soporte para ejecución mediante Docker.

---

# 👥 Roles y permisos

Jarvice implementa diferentes perfiles de usuario:

| Rol               | Función principal                                                                      |
| ----------------- | -------------------------------------------------------------------------------------- |
| **Administrador** | Administración general del sistema, usuarios, seguridad, configuración y JARVICE CORE. |
| **Médico**        | Acceso a información clínica y seguimiento de pacientes.                               |
| **Enfermería**    | Seguimiento de pacientes y evolución de enfermería.                                    |
| **Paciente**      | Acceso a su información personal, medicación, reportes y Centro de Atención.           |
| **Familiar**      | Acceso limitado a información autorizada.                                              |
| **Emergencia**    | Acceso orientado a situaciones de emergencia.                                          |
| **Institución**   | Acceso institucional según los permisos definidos.                                     |

Los accesos se controlan mediante autenticación, roles y permisos.

---

# 🔐 Autenticación

El sistema utiliza el sistema de autenticación de Django.

Incluye:

* Inicio de sesión.
* Cierre de sesión.
* Protección de vistas mediante autenticación.
* Control de acceso según rol.
* Restricción de módulos según permisos.
* Recuperación de contraseña mediante correo electrónico.

---

# 🔑 Recuperación de contraseña

Jarvice utiliza el sistema de recuperación de contraseña proporcionado por Django mediante correo electrónico.

El flujo contempla:

1. Solicitud de recuperación.
2. Envío de correo.
3. Acceso mediante enlace seguro.
4. Definición de una nueva contraseña.
5. Confirmación del cambio.

La configuración SMTP se realiza mediante variables de entorno.

---

# 🏥 Centro de Atención Jarvice

El sistema cuenta con un Centro de Atención para que los usuarios puedan enviar:

* Sugerencias.
* Opiniones.
* Problemas técnicos.
* Quejas o reclamos.
* Solicitudes de atención.

Las solicitudes quedan almacenadas para su posterior gestión.

---

# 🧬 JARVICE CORE

**JARVICE CORE** funciona como centro de administración y supervisión del sistema.

Permite centralizar información relacionada con:

* Usuarios.
* Pacientes.
* Estados de salud.
* Medicación.
* Recordatorios.
* Estudios.
* Dispositivos.
* Signos vitales.
* Alertas.
* Auditoría.
* Comunicaciones.
* Estado general del sistema.

El acceso se encuentra protegido mediante autenticación y permisos administrativos.

---

# ❤️ Monitoreo y análisis clínico

Jarvice incorpora un motor de análisis clínico destinado a procesar información proveniente de registros manuales y dispositivos.

Los parámetros contemplados incluyen:

* Frecuencia cardíaca.
* Saturación de oxígeno.
* Temperatura.
* Presión arterial.
* Estado emocional.

El motor permite clasificar los registros según diferentes niveles de riesgo y activar mecanismos de alerta cuando se detectan parámetros críticos.

---

# ⌚ API de dispositivos

El sistema incorpora una API para recibir información proveniente de dispositivos autorizados.

El flujo contempla:

* Identificación del dispositivo.
* Validación de credenciales.
* Recepción de signos vitales.
* Validación de datos.
* Registro automático.
* Análisis clínico.
* Comunicación mediante WebSockets.
* Activación del escalamiento de emergencias.
* Recepción de coordenadas GPS cuando están disponibles.

La arquitectura queda preparada para futuras integraciones con dispositivos wearable.

---

# 🚨 Sistema de emergencias

Jarvice incorpora un protocolo de emergencia destinado a facilitar la detección, notificación y gestión de situaciones críticas.

El flujo general contempla:

```text
Signos vitales
      ↓
Detección de situación crítica
      ↓
Generación de alerta
      ↓
Notificación de contactos
      ↓
Escalamiento de emergencia
      ↓
Ubicación GPS disponible
      ↓
Acceso a información clínica autorizada
      ↓
Registro y auditoría
```

El sistema contempla diferentes estados para el seguimiento de una emergencia, desde su detección hasta su cierre.

---

# 📱 Acceso mediante QR

Jarvice incorpora un mecanismo de acceso de emergencia mediante QR y tokens temporales.

### Flujo de acceso

1. Generación de un token temporal.
2. Acceso mediante código QR.
3. Registro del intento de acceso.
4. Validación y autorización.
5. Acceso a información clínica limitada.
6. Registro de auditoría.

La ficha de emergencia puede incluir, según la autorización correspondiente:

* Datos básicos del paciente.
* Antecedentes relevantes.
* Alergias.
* Contactos de emergencia.
* Medicación actual.
* Últimos signos vitales.
* Estado clínico.
* Evolución médica.
* Ubicación GPS disponible.

El objetivo es proporcionar información relevante para una situación de emergencia sin exponer innecesariamente información clínica.

---

# 📞 Escalamiento de emergencias

Ante una situación crítica, Jarvice puede ejecutar un esquema de notificación escalonada:

```text
Situación crítica
       ↓
Contacto 1
       ↓
¿Notificado?
   ┌───┴───┐
  Sí      No
  ↓        ↓
Fin    Contacto 2
           ↓
       ¿Notificado?
        ┌──┴──┐
       Sí    No
       ↓      ↓
      Fin  Contacto 3
               ↓
          SIN_CONTACTO
```

Los intentos de comunicación quedan registrados mediante el sistema de auditoría.

Las alertas pueden incorporar información clínica y, cuando está disponible, ubicación GPS.

---

# 📍 Ubicación GPS

Los registros pueden almacenar:

* Latitud.
* Longitud.
* Fecha y hora de la ubicación.

Cuando existe una ubicación disponible, la ficha de emergencia permite consultar las coordenadas mediante Google Maps.

La precisión de la ubicación depende del dispositivo que proporcione las coordenadas.

---

# 💊 Gestión de medicación

El sistema permite gestionar tratamientos y medicación asociada a pacientes.

Entre las funcionalidades contempladas se encuentran:

* Creación de medicaciones.
* Registro de dosis.
* Horarios.
* Indicaciones.
* Profesional que indicó el tratamiento.
* Recordatorios.
* Registro de administración.
* Confirmación de toma.
* Historial de administraciones.

Los permisos de administración y confirmación se controlan según el rol del usuario.

---

# 🩺 Evolución e historia clínica

Jarvice permite registrar y consultar información relacionada con la evolución clínica del paciente.

El sistema contempla:

* Historia clínica.
* Evolución médica.
* Evolución de enfermería.
* Estudios médicos.
* Solicitudes de estudios.
* Signos vitales.
* Registros clínicos.
* Información relevante para emergencias.

---

# 🔒 Auditoría y seguridad

El proyecto utiliza variables de entorno para evitar almacenar credenciales directamente en el código.

Además:

* `.env` está excluido de Git.
* Las credenciales sensibles no deben publicarse.
* Las bases de datos locales están excluidas del repositorio.
* Las vistas sensibles requieren autenticación.
* Las funciones administrativas requieren los permisos correspondientes.
* Los accesos mediante QR quedan registrados.
* Las operaciones relevantes pueden quedar auditadas.
* Los tokens utilizados para accesos temporales se generan de manera segura.

---

# 🧰 Tecnologías utilizadas

### Backend

* Python 3.14
* Django 6.0.4
* Django Channels 4.3.2
* Daphne 4.2.1

### Comunicación y servicios

* Redis 7.4.0
* WebSockets
* Twilio

### Base de datos

* SQLite para desarrollo local.
* Compatibilidad con PostgreSQL mediante `psycopg2-binary`.

### Frontend

* HTML5
* CSS3
* JavaScript
* Chart.js

### Infraestructura

* Docker
* Dockerfile
* Docker Compose

### Control de versiones

* Git
* GitHub

---

# 📦 Requisitos

Para ejecutar el proyecto localmente se necesita:

* Python 3.14.
* Git.
* Dependencias indicadas en `requirements.txt`.
* Redis para las funciones de comunicación en tiempo real.

También puede utilizarse Docker como alternativa de ejecución.

---

# 🚀 Instalación local

Clonar el repositorio:

```powershell
git clone https://github.com/juliizin07-alt/mi_app_salud.git
cd mi_app_salud
```

Crear el entorno virtual:

```powershell
python -m venv venv
```

Activarlo en Windows:

```powershell
venv\Scripts\activate
```

Instalar las dependencias:

```powershell
pip install -r requirements.txt
```

---

# 🔐 Variables de entorno

Crear un archivo `.env` en la raíz del proyecto.

Utilizar `.env.example` como referencia.

Ejemplo:

```text
DJANGO_SECRET_KEY=
DJANGO_DEBUG=True
JARVICE_ADMIN_CODE=

TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_FROM_NUMBER=
TWILIO_TO_NUMBER=

EMAIL_HOST=
EMAIL_PORT=
EMAIL_USE_TLS=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=
```

### ⚠️ Importante

El archivo `.env` contiene información sensible y **no debe subirse al repositorio**.

El proyecto utiliza `.gitignore` para excluirlo.

Nunca deben publicarse:

* Claves secretas.
* Tokens.
* Contraseñas.
* Credenciales de servicios externos.
* Credenciales SMTP.

---

# 🗄️ Base de datos

Para el entorno local se utiliza SQLite.

Aplicar las migraciones:

```powershell
python manage.py migrate
```

---

# ⚙️ Inicialización de Jarvice

El proyecto incluye un comando de administración para inicializar y verificar determinados componentes de la configuración:

```powershell
python manage.py inicializar_jarvice
```

---

# ▶️ Ejecución del proyecto

Verificar la configuración:

```powershell
python manage.py check
```

Ejecutar las migraciones:

```powershell
python manage.py migrate
```

Iniciar el servidor de desarrollo:

```powershell
python manage.py runserver
```

Acceder desde:

```text
http://127.0.0.1:8000/
```

También puede ejecutarse mediante Daphne:

```powershell
daphne -b 0.0.0.0 -p 8000 core_clean.asgi:application
```

---

# 🐳 Docker

El proyecto incluye configuración para ejecución mediante Docker.

Construir la imagen:

```bash
docker build -t jarvice-health-ai .
```

Ejecutar el contenedor:

```bash
docker run --env-file .env -p 8000:8000 jarvice-health-ai
```

Acceder desde:

```text
http://127.0.0.1:8000/
```

También se incluye configuración de Docker Compose para facilitar la ejecución de los servicios.

La ejecución de Docker depende de que Docker Desktop y los componentes de virtualización correspondientes estén disponibles en el equipo.

---

# 🧪 Pruebas automatizadas

Jarvice cuenta con una suite de pruebas automatizadas para las funcionalidades principales.

Ejecutar:

```powershell
python manage.py test
```

La suite desarrollada para el proyecto contempla pruebas relacionadas con:

* Autenticación de dispositivos.
* Validación de credenciales.
* Validación de signos vitales.
* Estados clínicos.
* Alertas.
* Escalamiento de emergencias.
* WebSockets.
* Roles y permisos.
* Accesos mediante QR.
* Integraciones externas mediante mocks.

Durante el desarrollo se verificó la ejecución de la suite con:

```text
39 tests
OK
```

---

# 👤 Datos de prueba

Para verificar el funcionamiento del sistema pueden utilizarse usuarios, pacientes y dispositivos de prueba creados mediante Django y las herramientas administrativas disponibles.

Se recomienda comprobar diferentes roles para verificar las restricciones de acceso.

Las credenciales sensibles y contraseñas reales no forman parte del repositorio.

---

# 📁 Estructura general

```text
core_clean/
│
├── core_clean/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── ...
│
├── mi_app_salud/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── permissions.py
│   ├── alerts.py
│   ├── consumers.py
│   ├── routing.py
│   ├── clinical_engine.py
│   ├── device_vitals_api.py
│   ├── context_processors.py
│   ├── services/
│   ├── management/
│   ├── migrations/
│   ├── templates/
│   └── static/
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
├── manage.py
└── README.md
```

---

# 🛠️ Comandos principales

```powershell
python manage.py check
python manage.py migrate
python manage.py createsuperuser
python manage.py inicializar_jarvice
python manage.py test
python manage.py runserver
```

---

# 📊 Estado del proyecto

Jarvice Health AI se encuentra preparado para la **entrega académica**.

Las funcionalidades principales desarrolladas incluyen:

* Autenticación.
* Roles y permisos.
* Gestión de pacientes.
* Historia clínica.
* Medicación.
* Evolución médica y de enfermería.
* Análisis clínico.
* Signos vitales.
* Dispositivos.
* Monitoreo en tiempo real.
* Alertas.
* Escalamiento de emergencias.
* Acceso de emergencia mediante QR.
* GPS.
* Auditoría.
* Recuperación de contraseña.
* JARVICE CORE.
* Centro de Atención.
* Integración con WhatsApp.
* Docker.
* Pruebas automatizadas.

La arquitectura queda preparada para futuras ampliaciones, incluyendo una aplicación móvil y una integración más avanzada con dispositivos wearable.

---

# 🎓 Proyecto académico

Proyecto desarrollado como trabajo académico de programación y desarrollo de software.

El objetivo de **Jarvice Health AI** es integrar herramientas de desarrollo web con funcionalidades orientadas al seguimiento, asistencia y monitoreo de salud mediante una arquitectura modular.

El proyecto aborda conceptos de:

* Desarrollo backend.
* Desarrollo frontend.
* Bases de datos.
* Autenticación.
* Autorización.
* APIs.
* Comunicación en tiempo real.
* Seguridad.
* Automatización.
* Integración de servicios externos.
* Contenedores.
* Pruebas de software.
* Control de versiones.

---

# 👩‍💻 Autora

**Julieta Niz**

Proyecto académico — Jarvice Health AI
