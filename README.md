Ghibli User API
Esta es una API REST desarrollada con Flask que permite gestionar usuarios y sus roles, conectados a una base de datos, y consultar datos públicos de la API de Studio Ghibli en función del rol de cada usuario.

Características
Añadir, consultar, actualizar y eliminar usuarios.

Validación de datos y relaciones con roles definidos.

Consulta de datos públicos desde la API de Studio Ghibli según el rol del usuario.

Conexión a base de datos mediante un módulo externo connectdb().

Soporte para CORS (Cross-Origin Resource Sharing).

Endpoints disponibles
1. POST /add_user
Crea un nuevo usuario con los siguientes campos:

json

{
  "name": "John",
  "lastname": "Doe",
  "age": 30,
  "gender": "MALE",
  "email": "john.doe@example.com",
  "rol": "Films"
}
2. GET /get_users
Retorna una lista de todos los usuarios registrados con su respectivo rol.

3. GET /get_user/<id_user>
Consulta la información de un usuario por su ID.

4. PUT /update_user/<id_user>
Actualiza la información de un usuario. Requiere todos los campos:

json

{
  "name": "Jane",
  "lastname": "Smith",
  "age": 28,
  "gender": "FEMALE",
  "email": "jane.smith@example.com",
  "rol": "People"
}
5. DELETE /delete_user/<id_user>
Elimina a un usuario de la base de datos, incluyendo su asociación con roles.

6. GET /get_ghibli_data/<id_user>
Retorna los datos de la API de Ghibli a los que el usuario tiene acceso según su rol:

Admin: Acceso total a todas las categorías.

Films, People, Locations, Species, Vehicles: Acceso según su rol.

Roles válidos
Admin

Films

People

Locations

Species

Vehicles

Géneros válidos
MALE

FEMALE

OTHER

Requisitos
Python 3.7 o superior

Flask

Flask-CORS

requests

Una base de datos (ej. PostgreSQL o MariaDB) con las tablas users, roles, y user_rol

Estructura esperada de la base de datos
Tabla users:

id_user: INT, PRIMARY KEY

name: VARCHAR

lastname: VARCHAR

age: INT

gender: VARCHAR

email: VARCHAR

Tabla roles:

id_rol: INT, PRIMARY KEY

name_rol: VARCHAR

Tabla user_rol:

id_user: INT, FOREIGN KEY a users.id_user

id_rol: INT, FOREIGN KEY a roles.id_rol

Cómo ejecutar
Clona el repositorio.

Asegúrate de tener un archivo dbConnection.py que exponga la función connectdb() para conectarte a tu base de datos.

Instala las dependencias necesarias:

pip install flask flask-cors requests
Ejecuta el servidor:

python app.py
Notas
El código convierte automáticamente nombres y apellidos a mayúsculas, roles a capitalizados y emails a minúsculas.

Las validaciones están integradas para asegurar integridad de datos antes de insertar en la base de datos.

La API de Ghibli se consume externamente usando el paquete requests.
