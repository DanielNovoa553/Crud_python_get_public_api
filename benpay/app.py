from flask import Flask, jsonify, request
from dbConnection import connectdb
from flask_cors import CORS, cross_origin
import requests

app = Flask(__name__)
cors = CORS(app)
app.config['SECRET_KEY'] = 'GHgsfvxhwdcXFty"#&/()=)'

@app.route("/add_user", methods=['POST'])
@cross_origin(supports_credentials=True)
def add_user():
    """
    Function to add a user to the database
    Returns: message if user is added successfully or error message if user is already in the database
    """
    try:
        # Get the parameters from the request json
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data found"}), 400

        name = data.get('name')
        if name:
            name = name.upper()

        lastname = data.get('lastname')
        if lastname:
            lastname = lastname.upper()

        age = data.get('age')
        if not isinstance(age, int) or age <= 0:
            return jsonify({"message": "Age must be a positive integer"}), 400

        gender = data.get('gender')
        if gender:
            gender = gender.upper()

        email = data.get('email')
        if email:
            email = email.lower()

        rol = data.get('rol')
        if rol:
            rol = rol.capitalize()

        if not name:
            return jsonify({"message": "Name is required"}), 400
        if not lastname:
            return jsonify({"message": "Lastname is required"}), 400
        if not age:
            return jsonify({"message": "Age is required"}), 400
        if not gender:
            return jsonify({"message": "Gender is required"}), 400

        # Validate that the gender is 'MALE', 'FEMALE', or 'OTHER'
        if gender not in ['MALE','FEMALE','OTHER']:
            return jsonify({"message" : "The gender must be Male, Female or Other"}), 400

        if not rol:
            return jsonify({"message": "Role is required"}), 400
        # Validate that the role is one of the predefined roles
        if rol not in ['Admin','Films','People','Locations','Species','Vehicles']:
            return jsonify({"message" : "The role must be Admin, Films, People, Locations, Species or Vehicles"}), 400

        if not email:
            return jsonify({"message": "Email is required"}), 400

        conn = connectdb()
        cursor = conn.cursor()
        # Validate if the email is already in the database
        cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user:
            return jsonify({"message": "User already in the database"}), 400

        query = ("INSERT INTO users (name, lastname, age, gender, email) "
                 "VALUES (%s, %s, %s, %s, %s)")
        cursor.execute(query, (name, lastname, age, gender, email))

        # Get the user ID based on the email
        cursor.execute("SELECT id_user FROM users WHERE email = %s", (email,))
        user_id = cursor.fetchone()
        if user_id:
            user_id = user_id[0]
            print(f"User ID: {user_id}")

        # Get the role ID based on the role name
        cursor.execute("SELECT id_rol FROM roles WHERE name_rol = %s", (rol,))
        rol_id = cursor.fetchone()
        if rol_id:
            rol_id = rol_id[0]
            print(f"Rol ID: {rol_id}")

        # Insert the user-role relationship into the user_rol table
        cursor.execute("INSERT INTO user_rol (id_rol, id_user) VALUES (%s, %s)", (rol_id, user_id))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "User added successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route("/get_users", methods=['GET'])
@cross_origin(supports_credentials=True)
def get_users():
    """
    Function to get all users from the database
    Returns: all users from the database or error message if there are no users
    """
    try:
        conn = connectdb()
        cursor = conn.cursor()

        # INNER JOIN entre users, user_rol, y roles
        cursor.execute("""
            SELECT u.id_user, u.name, u.lastname, u.age, u.email, r.name_rol
            FROM users u
            INNER JOIN user_rol ur ON u.id_user = ur.id_user
            INNER JOIN roles r ON ur.id_rol = r.id_rol
        """)

        users = cursor.fetchall()
        cursor.close()
        conn.close()

        if not users:
            return jsonify({"message": "No users found"}), 404

        users_list = []
        for user in users:
            user_dict = {
                "id_user": user[0],
                "name": user[1],
                "lastname": user[2],
                "age": user[3],
                "email": user[4],
                "role": user[5]  # El nombre del rol asociado
            }
            users_list.append(user_dict)

        return jsonify(users_list), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route("/get_user/<int:id_user>", methods=['GET'])
@cross_origin(supports_credentials=True)
def get_user_by_id(id_user):
    """
    Function to get a user by ID from the database
    Returns: user data if found or error message if not found
    """
    try:
        conn = connectdb()
        cursor = conn.cursor()

        # INNER JOIN para obtener el usuario con su rol
        cursor.execute("""
            SELECT u.id_user, u.name, u.lastname, u.age, u.email, r.name_rol
            FROM users u
            INNER JOIN user_rol ur ON u.id_user = ur.id_user
            INNER JOIN roles r ON ur.id_rol = r.id_rol
            WHERE u.id_user = %s
        """, (id_user,))

        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user:
            return jsonify({"message": "User not found"}), 404

        user_dict = {
            "id_user": user[0],
            "name": user[1],
            "lastname": user[2],
            "age": user[3],
            "email": user[4],
            "role": user[5]  # Nombre del rol asociado
        }

        return jsonify(user_dict), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route("/update_user/<int:id_user>", methods=['PUT'])
@cross_origin(supports_credentials=True)
def update_user(id_user):
    """
    Function to update a user's information in the database.
    Returns: message indicating success or failure.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400

        name = data.get('name', '').upper()
        lastname = data.get('lastname', '').upper()
        age = data.get('age')
        gender = data.get('gender', '').upper()
        email = data.get('email', '').lower()
        rol = data.get('rol', '').capitalize()

        if not name or not lastname or not age or not gender or not email or not rol:
            return jsonify({"message": "All fields are required"}), 400

        if not isinstance(age, int) or age <= 0:
            return jsonify({"message": "Age must be a positive integer"}), 400

        if gender not in ['MALE', 'FEMALE', 'OTHER']:
            return jsonify({"message": "The gender must be Male, Female or Other"}), 400

        if rol not in ['Admin', 'Films', 'People', 'Locations', 'Species', 'Vehicles']:
            return jsonify({"message": "The role must be Admin, Films, People, Locations, Species or Vehicles"}), 400

        conn = connectdb()
        cursor = conn.cursor()

        # Verificar si el usuario existe
        cursor.execute("SELECT * FROM users WHERE id_user = %s", (id_user,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"message": "User not found"}), 404

        # Actualizar datos del usuario
        cursor.execute("""
            UPDATE users 
            SET name = %s, lastname = %s, age = %s, gender = %s, email = %s
            WHERE id_user = %s
        """, (name, lastname, age, gender, email, id_user))

        # Obtener el id_rol del nuevo rol
        cursor.execute("SELECT id_rol FROM roles WHERE name_rol = %s", (rol,))
        rol_id = cursor.fetchone()
        if not rol_id:
            return jsonify({"message": "Role not found"}), 400
        rol_id = rol_id[0]

        # Actualizar el rol en user_rol
        cursor.execute("""
            UPDATE user_rol 
            SET id_rol = %s
            WHERE id_user = %s
        """, (rol_id, id_user))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "User updated successfully"}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route("/delete_user/<int:id_user>", methods=['DELETE'])
@cross_origin(supports_credentials=True)
def delete_user(id_user):
    """
    Function to delete a user from the database
    Returns: message indicating success or failure
    """
    try:
        conn = connectdb()
        cursor = conn.cursor()

        # Verificar si el usuario existe
        cursor.execute("SELECT * FROM users WHERE id_user = %s", (id_user,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"message": "User not found"}), 404

        # Borrar primero de user_rol (porque tiene una clave foránea de users)
        cursor.execute("DELETE FROM user_rol WHERE id_user = %s", (id_user,))

        # Borrar de users
        cursor.execute("DELETE FROM users WHERE id_user = %s", (id_user,))

        # Confirmar cambios
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "User deleted successfully"}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500



@app.route("/get_ghibli_data/<int:id_user>", methods=['GET'])
@cross_origin(supports_credentials=True)
def get_ghibli_data(id_user):
    """
    Function to return Studio Ghibli data based on the user's role.
    """
    try:
        conn = connectdb()
        cursor = conn.cursor()

        # Obtener el rol del usuario
        cursor.execute("""
            SELECT r.name_rol FROM roles r
            INNER JOIN user_rol ur ON r.id_rol = ur.id_rol
            WHERE ur.id_user = %s
        """, (id_user,))
        user_role = cursor.fetchone()

        cursor.close()
        conn.close()

        if not user_role:
            return jsonify({"message": "User not found or has no role"}), 404

        user_role = user_role[0].lower()  # Convertir a minúsculas para comparación

        # Definir los endpoints de Studio Ghibli según el rol
        ghibli_api_url = "https://ghibliapi.vercel.app"
        endpoints = {
            "admin": "",  # Admin puede acceder a todos los datos
            "films": "/films",
            "people": "/people",
            "locations": "/locations",
            "species": "/species",
            "vehicles": "/vehicles"
        }

        if user_role not in endpoints:
            return jsonify({"message": "Role not recognized"}), 400

        # Si es admin, traer todos los datos
        if user_role == "admin":
            data = {}
            for role, endpoint in endpoints.items():
                if endpoint:
                    response = requests.get(ghibli_api_url + endpoint)
                    if response.status_code == 200:
                        data[role] = response.json()
            return jsonify(data), 200
        else:
            # Consultar solo el endpoint del usuario
            response = requests.get(ghibli_api_url + endpoints[user_role])
            if response.status_code != 200:
                return jsonify({"message": "Error retrieving data from Ghibli API"}), 500

            return jsonify(response.json()), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500


if __name__ == '__main__':
    app.run()
