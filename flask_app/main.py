### FitnessApp ###
### Sergio Romero ###

#Imports
import json
import os
import pathlib
import time
import requests
from flask import Flask, render_template, session, abort, redirect, request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from pymongo import MongoClient
import socket

# Establecer el tiempo de espera por defecto en 10 segundos
time.sleep(10)
socket.setdefaulttimeout(10)
#Me conecto a la bd
client = MongoClient("mongodb://mongodb:27017/")

#Defino las coleciones
db = client.CaloriasDB
collection = db.CaloriasCollection
collectionUsers = db['Users']


###Inicio de sesión google###
# Se crea una instancia de mi aplicación Flask llamada "FitnessApp"
app = Flask("FitnessApp")

# Se establece una clave secreta para la sesión de la aplicación
app.secret_key = "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"

# Configuramos la variable de entorno para permitir conexiones HTTP inseguras
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# Configuramos el ID del cliente de Google
GOOGLE_CLIENT_ID = "455533765980-7ts30kklc2kb1nf42iovn487mnqa5hai.apps.googleusercontent.com"

# Obtenemos la ruta del archivo JSON con las credenciales del cliente de Google
client_secrets_file = os.path.join(
    pathlib.Path(__file__).parent, "client_secret.json")

# Creamos un objeto Flow para manejar el flujo de autenticación de Google
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://localhost/callback"
)

def get_calories(query):
    '''
    Consulta la base de datos para obtener las calorías de un alimento específico.

    Args:
        query (str): Nombre del alimento a consultar.

    Returns:
        list: Lista de las calorías por cada 100 gramos del alimento consultado.

    '''
    # Consulta a la base de datos y almacena los resultados en 'results'
    results = collection.find({"FoodItem": query.lower()})

    # Crea una lista vacía para almacenar las calorias de la comida recuperada de la consulta
    calories = []

    # Itera sobre los resultados y almacena cada documento en la lista 'calories'
    for result in results:
        calories.append(result.get('Cals_per100grams', None))

    # Devuelve la lista de calories
    return calories

def insertuser(mail):
    '''
    Inserta un nuevo usuario en la base de datos.

    Args:
        mail (str): Correo electrónico del usuario.

    Returns:
        ObjectId: El ID generado para el usuario insertado.

    '''
    #Me conecto a la colleccion
    collectionUsers = db['Users']

    # Crear el diccionario del usuario con los campos correspondientes

    user = {
    'mail': mail,
    'favs_foods' : [],
    'diet' : {}
}

    #Contar numeros de usuarios para saber que id darle a mi nuevo usuario
    num_users = collectionUsers.count_documents({})

    #Añadir un campo id al usuario
    user['id'] = num_users + 1
    #Si el usuario no esta registrado, se le inserta en la bd
    if(not(is_email_registered(mail))):
    #Insertar al usuario en la base de datos
        result = collectionUsers.insert_one(user)

        # Obtener el ID generado para el usuario insertado
        user_id = result.inserted_id

        return user_id
    else:
        print("usuario ya registrado")

def is_email_registered(email):
    '''
    Comprueba si el correo electrónico ya está registrado en la base de datos.

    Args:
        email (str): Correo electrónico a verificar.

    Returns:
        bool: True si el correo electrónico está registrado, False en caso contrario.

    '''
    collectionUsers = db['Users']

    # Buscar un único documento que contenga el correo electrónico en la base de datos
    user = collectionUsers.find_one({'mail': email})

    # Si el usuario existe (el find_one() no retorna None), entonces el correo ya está registrado
    if user:
        return True
    else:
        return False

def add_fav_food(mail, food):
    '''
    Añade una comida buscada por el usuario a favoritos.

    Args:
        mail (str): Correo electrónico del usuario.
        food (str): Nombre de la comida a añadir a favoritos.

    Returns:
        str: Mensaje indicando si la comida se ha añadido correctamente a favoritos o si ya está en la lista.

    '''
    collectionUsers = db["Users"]

    # Verificamos primero si el usuario existe
    if not is_email_registered(mail):
        return "El usuario no existe en la base de datos"

    # Buscamos al usuario por mail en la colección "Users"
    user = collectionUsers.find_one({"mail": mail})

    # Comprobamos si la comida ya está en la lista de comidas favoritas del usuario
    foodExist = food in user['favs_foods']
    #Si la comida no esta en 'favs_foods' la añadimos
    if not foodExist:
        # Agregamos la comida nueva a favs_foods
        user['favs_foods'].append(food)

        # Actualizamos al usuario con los cambios
        collectionUsers.update_one(
            {'_id': user['_id']},
            {'$set': {'favs_foods': user['favs_foods']}}
        )
        #Devolvemos un mensaje para que el usuario pueda saber si se ha agregado correctamente o no
        return "Food added to favorites"
    else:
        return "This food is already in your favorites"

def shows_favorites(mail):
    '''
    Muestra las comidas favoritas del usuario que está en sesión.

    Args:
        mail (str): Correo electrónico del usuario.

    Returns:
        pymongo.cursor.Cursor: Cursor que contiene los datos de las comidas favoritas del usuario.

    '''
    collectionUsers = db["Users"]
    
    #Busco el usuario específico que ha iniciado sesión
    user = collectionUsers.find_one({"mail": mail})
    #Saco las comidas favoritas de dicho usuario
    favs_foods = user['favs_foods']
    #Sacar datos de dichas comidas
    data_food = collection.find({'FoodItem' : {'$in':favs_foods}})
    #Devuelve una comida con sus datos
    return data_food

def delete_favorite_food(mail, food):
    '''
    Borra la comida favorita especificada por el usuario.

    Args:
        mail (str): Correo electrónico del usuario.
        food (str): Nombre de la comida a eliminar de la lista de alimentos favoritos.

    Returns:
        str: Mensaje indicando que la comida ha sido eliminada correctamente de la lista de alimentos favoritos.

    '''
    collectionUsers=db["Users"]
    #Buscamos al usuario en la bd
    user = collectionUsers.find_one({"mail" : mail})
    # Revisamos si el usuario existe
    if user :
        # Revisamos si "favs_foods" existe en el documento del usuario
        if 'favs_foods' in user:
            # Revisamos si la comida que se quiere borrar ya existe en la lista de alimentos favoritos
            if food in user['favs_foods']:
                # Eliminamos la comida de la lista de alimentos favoritos
                user['favs_foods'].remove(food)

                # Actualizamos al usuario con los cambios
                db.get_collection('Users').update_one(
                    {'_id': user['_id']},
                    {'$set': {'favs_foods': user.get('favs_foods')}}
                )
                #Devolvemos mensaje para que el usuario pueda ver que se ha borrado correctamente su comida
                return "Food remove from favorites"

def get_gym(city):
    '''
    Obtiene una lista de gimnasios en la ciudad o pueblo especificado.

    Args:
        city (str): Nombre de la ciudad o pueblo.

    Returns:
        list: Lista de diccionarios con información de los gimnasios. Cada diccionario contiene las claves 'name', 'lat' y 'lon' para el nombre, latitud y longitud del gimnasio, respectivamente. Si no se encuentran gimnasios o hay un error en la solicitud, se devuelve una lista vacía o None, respectivamente.

    '''
    # Definimos la URL para obtener los datos de OpenStreetMap
    osm_url = 'https://nominatim.openstreetmap.org/search.php?q='+city.lower()+'+gimnasio&format=json&countrycodes=ES'

    # Realizamos una solicitud HTTP GET a la API de OpenStreetMap
    response = requests.get(osm_url)

    # Si la solicitud es exitosa (código de respuesta 200), procesamos los datos
    if response.status_code == 200:
        # Convertimos la respuesta JSON a un objeto Python
        osm_data = json.loads(response.content)
        print(osm_data)
        # Creamos una lista vacía para almacenar la información de los gimnasios
        gyms = []

        # Iteramos sobre los datos para obtener la información de cada gimnasio
        for data in osm_data:
            name = data.get('display_name')
            lat = data.get('lat')
            lon = data.get('lon')
            print(data)
            # Creamos un diccionario con la información del gimnasio
            gym = {'name': name, 'lat': lat, 'lon': lon}

            # Agregamos el diccionario a la lista de gimnasios
            gyms.append(gym)

        # Devolvemos la lista de gimnasios
        return gyms
    else:
        # Si hubo un error al hacer la solicitud, mostramos el código de error
        print(f'Error al hacer la solicitud HTTP: {response.status_code}')
        return None

def add_or_update_diet(email, diet_name, start_date, end_date):
    '''
    Añade o actualiza dieta
    
    Args:
        email (str): Correo electrónico del usuario.
        diet_name (str): Nombre de la dieta.
        start_date (str): Fecha de inicio de la dieta (en formato de cadena).
        end_date (str): Fecha de finalización de la dieta (en formato de cadena).

    Returns:
        str: Mensaje indicando el resultado de la operación.

    '''
    #Buscamos al usuario en la bd
    user = collectionUsers.find_one({"mail": email})
     # Comprobamos si la dieta ya existe para el usuario
    if diet_name in user['diet']:
        #Si la dieta eiste actualizamos la fecha de inicio y de finalización de la dieta
        message = "Diet exists. Updating the dates."
        user['diet'][diet_name]['start_date'] = start_date
        user['diet'][diet_name]['end_date'] = end_date
    else:
        #Si no existe creamos la dieta dandole los valores correspondientes
        print("Adding a new diet.")
        num_diet = len(user['diet']) + 1
        diet = {
            'num_diet': num_diet,
            'name': diet_name,
            'start_date': start_date,
            'end_date': end_date,
            'foods': []
        }
        user['diet'][diet_name] = diet
        #Mostramos mensaje de que se ha añadido la dieta
        message = "Diet "+ diet_name+ " added."
    #Actualizamos al usuario con su dieta
    collectionUsers.update_one({"mail": email}, {"$set": user})
    return message

def add_food_diet(email, name_diet, name_food, quantity):
    '''
     Añade comida a una dieta especifica
     
     Args:
        email (str): Correo electrónico del usuario.
        name_diet (str): Nombre de la dieta.
        name_food (str): Nombre de la comida.
        quantity (float): Cantidad de la comida en gramos.

    Returns:
        str: Mensaje indicando que la comida ha sido añadida correctamente a la dieta.

    '''
    
    #Buscamos al usuario en la bd
    user = collectionUsers.find_one({"mail": email})
    #Comprobamos si la dieta no existe
    if name_diet not in user['diet']:
        print("Error: la dieta especificada no existe.")
    #Si la dieta existe se crea la comida y se le añaden los datos correspondientes
    else:
        # Creamos un diccionario para representar la comida
        food = {}
        food['name'] = name_food
        if quantity > 0:
            food['quantity'] = quantity
            food['cals'] = calculate_cals_food(name_food, quantity)
        else:
            food['quantity'] = 0
            #Se llama a la funcion 'calculate_cals_food' para sacar las calorias de la comida  respecto su cantidad en gramos
            food['cals'] = calculate_cals_food(name_food, 0)

        # Verificar si la comida ya existe en la dieta
        for f in user['diet'][name_diet]['foods']:
            #Si la comida existe, se le suma la cantidad ingresada
            if f['name'] == name_food:
                f['quantity'] += quantity
                f['cals'] = calculate_cals_food(name_food, f['quantity'])
                break        
        # Si la comida no existe, agregarla a la dieta
        else:
        
            user['diet'][name_diet]['foods'].append(food)

        # Actualiza el documento del usuario en la base de datos
        collectionUsers.update_one(
            {"mail": user['mail']}, 
            {"$set": user}
        )
        #Se devuelve un mensaje para que el usuario pueda ver que todo ha salido bien
        return "Food added to diet"

def get_foods_in_diet(email, name_diet):
    '''
    Obtiene la lista de comidas en una dieta específica para un usuario dado.
    args:
        email(str) : Correo electronico del usuario
        name_diet(str): Nombre de la dieta
    Returns:
        list: Lista de comidas en la dieta especificada. Si la dieta no existe, se devuelve una lista vacía.
    '''
    user = collectionUsers.find_one({"mail": email})
    if name_diet not in user['diet']:
        print("Error: la dieta especificada no existe.")
        return []  # Devolver una lista vacía si la dieta no existe
    else:
        foods = user['diet'][name_diet].get('foods', [])
        return foods  # Devolver la lista de comidas

def show_option_diets(mail):
    '''
    Muestra las opciones de dietas disponibles para un usuario específico.

    Args:
        mail (str): Correo electrónico del usuario.

    Returns:
        dict: Diccionario que contiene las opciones de dietas disponibles para el usuario.

    '''
    collectionUsers = db["Users"]

    #Busco el usuario específico que ha iniciado sesión
    user = collectionUsers.find_one({"mail": mail})
    #Saco las dietas
    diet = user['diet']
    
    return diet

def calculate_cals_diet(mail, name_diet):
    '''
    Calcula las calorías totales de una dieta específica para un usuario.

    Args:
        mail (str): Correo electrónico del usuario.
        name_diet (str): Nombre de la dieta.

    Returns:
        str: Calorías totales de la dieta en formato de cadena con dos decimales.

    '''
    collectionUsers = db["Users"]
    
    # Busco el usuario específico que ha iniciado sesión
    user = collectionUsers.find_one({"mail": mail})
    
    # Verificar si la dieta especificada existe en los datos del usuario
    if name_diet not in user['diet']:
        print("Error: la dieta especificada no existe.")
        return 0  # Devolver 0 si la dieta no existe
    
    # Obtener la lista de comidas de la dieta
    foods = user['diet'][name_diet].get('foods', [])
    
    # Calcular las calorías totales de la dieta
    total_calories = 0
    for food in foods:
        cals_str = food.get('cals', '0')
        # Las calorías en la base de datos están en formato de cadena como '21 cal'
        # Así que eliminamos la palabra 'cal' y convertimos la cadena a entero
        cals_str = cals_str.replace("cal", "").strip()
        total_calories += float(cals_str)
    
    # Devolver las calorías totales de la dieta
    
    return "{:.2f}".format(round(total_calories, 2))

def delete_food_diet(email, diet_name,food_name):
    '''
    Elimina una comida específica de una dieta seleccionada del usuario.

    Args:
        email (str): Correo electrónico del usuario.
        diet_name (str): Nombre de la dieta.
        food_name (str): Nombre de la comida a eliminar.

    Returns:
        str: Mensaje indicando que la comida se ha eliminado de la dieta.

    '''
    user = collectionUsers.find_one({"mail": email})
    if diet_name not in user['diet']:
        return "Error: la dieta especificada no existe."
    else:
        foods = user['diet'][diet_name].get('foods', [])
        for f in foods:
            if f['name'] == food_name:
                foods.remove(f)
                break   # salir del for loop después de que se ha eliminado la comida

        user['diet'][diet_name]['foods'] = foods
        collectionUsers.update_one({"mail": user['mail']}, {"$set": user})

        return "Food removed from diet"

def delete_diet_user(mail, diet_names):
    '''
    Elimina una o varias dietas de un usuario.

    Args:
        mail (str): Correo electrónico del usuario.
        diet_names (list): Lista de nombres de las dietas a eliminar.

    Returns:
        str: Mensaje indicando que las dietas se han eliminado correctamente.

    '''

    user = collectionUsers.find_one({"mail": mail})
    if not user:
        return "Email not found in database"

    for diet_name in diet_names:
        if diet_name in user['diet']:
            del user['diet'][diet_name]

    collectionUsers.update_one({"mail": user['mail']}, {"$set": user})
    return "Diets deleted successfully"

# Creamos un decorador para verificar si el usuario ha iniciado sesión
def login_is_required(function):
    def wrapper(*args, **kwargs):
        # Si el usuario no ha iniciado sesión, retornamos un error de autorización
        if "google_id" not in session:
            return abort(401)  # Authorization required
        # Si el usuario ha iniciado sesión, llamamos a la función correspondiente
        else:
            return function()

    return wrapper

def calculate_cals_food(food, quantity):
    '''
    Calcula el total de calorías para un alimento y una cantidad específica.

    Args:
        food (str): Nombre del alimento.
        quantity (int): Cantidad del alimento en gramos.

    Returns:
        str: Número de calorías totales para el alimento y cantidad especificada, formateado como string.

    '''
    # Obtiene las calorías del alimento
    cals_str = get_calories(food)

    # Si las calorías no se pueden obtener, devuelve 'No se encontraron calorías para este alimento'
    if not cals_str:
        return 'No se encontraron calorías para este alimento'

    # Calcula las calorías totales para la cantidad especificada del alimento
    cals = int(cals_str[0].replace("cal", "").strip())
    cals_per_gramo = cals / 100
    total_calories = cals_per_gramo * quantity
    total_calories = "{:.2f}".format(round(total_calories, 2))


    # Devuelve un mensaje con el número de calorías totales como un string
    return str(total_calories)
#Capta una excepción que se da a veces 
@app.errorhandler(requests.exceptions.ConnectionError)
def handle_connection_error(error):
    # Realizar acciones personalizadas, como recargar automáticamente la página
    return render_template('index.html')
# Definimos la ruta de inicio de sesión
@app.route("/login", methods=["GET", "POST"])
def login():
    # Obtenemos la URL de autorización y el estado del objeto Flow
    authorization_url, state = flow.authorization_url()
    # Guardamos el estado en la sesión
    session["state"] = state
    # Redirigimos al usuario a la URL de autorización de Google
    return redirect(authorization_url)

@app.route("/redirect_to_login")
def redirect_to_login():
    return render_template("iniciosesion.html")

# Definimos la ruta de callback después de la autenticación de Google
@app.route("/callback")
def callback():
    time.sleep(5)
    # Verificamos el token de acceso recibido de Google
    flow.fetch_token(authorization_response=request.url)
    # Comparamos el estado guardado en la sesión con el estado recibido de Google
    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    # Se utiliza la librería google-auth para verificar el token de identificación del usuario.
    # Si se verifica con éxito, se almacena el "google_id" y el nombre del usuario en la sesión.
    # Obtenemos las credenciales de acceso
    credentials = flow.credentials
    # Creamos una sesión HTTP y la cachemos para mejorar el rendimiento
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    # Creamos una sesión HTTP y la cachemos para mejorar el rendimiento
    token_request = google.auth.transport.requests.Request(
        session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )
    print(id_info) 
    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["google_email"] = id_info.get("email")
    session["google_picture"] = id_info.get("picture").replace("http://", "https://")
    # Se redirige al usuario a la ruta "/protected_area".
    return redirect("/protected_area")

@app.route("/logout")
def logout():
    # La ruta "/logout" maneja la solicitud GET del usuario para cerrar la sesión.
    # Se llama a la función "session.clear()" para eliminar todas las variables de sesión.
    # Se redirige al usuario a la página de inicio.
    session.clear()
    return redirect("/")

@app.route("/")
def index():
    collectionFood =collection.find()
    return render_template("index.html",collectionFood=collectionFood)

@app.route("/protected_area", methods=["GET", "POST"])
# La ruta "/protected_area" solo está disp0onible para usuarios autenticados.
# La función "login_is_required" se utiliza como decorador para asegurarse de que el usuario esté autenticado.
# Si el usuario está autenticado, se muestra un mensaje de bienvenida con el nombre del usuario y un botón para cerrar la sesión.
@login_is_required
def protected_area():
    email = session.get("google_email")
    insertuser(email)
    collectionFood =collection.find()
    return render_template("index.html",collectionFood=collectionFood)

#Añade una comida buscada del usuario a favoritos
@app.route('/add_favorite', methods=['POST'])
def add_favorite():
    email = session.get("google_email")
    collectionFood =collection.find()
    if email:
        #Comprueba que el usuario haya hecho click en el boton de favoritos del usuario
        if request.method == 'POST':
            food = request.form['my-button']
            message = add_fav_food(email,food)
    #Sino esta sin iniciar sesion no deja y muestra un mensaje
    else:
        message = "For this action you must be registered"
    return render_template('index.html', message=message,collectionFood=collectionFood)

#Muestra las comidas favoritas
@app.route("/favorite_foods")
def favorite_foods():
    email = session.get("google_email")
    if email: 
        # Convertir cursor a lista
        favs_foods = list(shows_favorites(email))
        return render_template("favoritefoods.html",favs_foods=favs_foods)
    else:
        return render_template("favoritefoods.html")

#Permite borrar una comida de favoritos
@app.route('/delete_fav_food', methods=['GET','POST'])
def delete_fav_food():
    email = session.get("google_email")
    #Si hay email en sesion
    if email:
        if request.method == 'POST':
            food_delete = request.form['food_delete']
            message = delete_favorite_food(email,food_delete)
            # Obtener las comidas favoritas actualizadas y pasarlas a la plantilla
            favs_foods_cursor = shows_favorites(email)
            favs_foods = list(favs_foods_cursor)
            return render_template('favoritefoods.html', message=message, favs_foods=favs_foods)
        else:
            # Devolver una respuesta en caso de una solicitud GET
            return render_template('favoritefoods.html',favs_foods=favs_foods)

#Funcion para crear una dieta a través de las comidas favoritas de cada usuario
@app.route('/create_diet', methods=['GET','POST'])
def create_diet():
    email = session.get("google_email")
    #Si hay email en sesion
    if email:
        favs_foods=shows_favorites(email)
        #Comprueba que el usuario haya dado click en el boton de añadir a dieta
        return render_template("creatediet.html", favs_foods=favs_foods)
    else:
        return render_template("creatediet.html")

@app.route("/show_options_diet", methods=["GET","POST"])
def shows_options_diet():
    email = session.get("google_email")
    #Si hay email en sesion
    if email:
        diets = list(show_option_diets(email))
        return render_template("show_option_diet.html",diets=diets)
    else:
         return render_template("show_option_diet.html")

@app.route('/show_diet', methods=['GET','POST'])
def show_diet():
    email = session.get("google_email")
    #Si hay email en sesion
    if email:
        selected_diet = request.form['selected_diet']
        print("Dieta seleccionada: " + selected_diet)
        diet_data = get_foods_in_diet(email,selected_diet)
        total_cals = calculate_cals_diet(email,selected_diet)
        # message_delete = delete_food_diet()
        print(diet_data)
        # Aquí puedes obtener los datos de la dieta seleccionada y enviarlos a la plantilla
        return render_template('show_diet.html', diet_data=diet_data, selected_diet=selected_diet, total_cals=total_cals)
    else:
        return render_template('show_diet.html')

@app.route('/delete_food_diet_web', methods=['GET','POST'])
def delete_food_diet_web():
    email = session.get("google_email")
    #Si hay email en sesion
    if email:
        #Si hay un post es porque le han dado al boton de eliminar dicha comida de la dieta entonces llama a la funcion delete_food_diet
        if request.method == 'POST':
            selected_diet = request.form['diet_id']
            food_delete = request.form['food_delete']
            print("Dieta : " + selected_diet)
            print("Food: " + food_delete)
            message = delete_food_diet(email,selected_diet,food_delete)
            # Obtener las comidas favoritas actualizadas y pasarlas a la plantilla
            total_cals = calculate_cals_diet(email,selected_diet)
            diet_data = list(get_foods_in_diet(email,selected_diet))
            return render_template('show_diet.html', message=message, diet_data=diet_data,selected_diet=selected_diet,total_cals=total_cals,)
    else:
        return render_template('show_diet.html')

@app.route('/add_to_diet', methods=['GET','POST'])
def add_to_diet():
    email = session.get("google_email")
    #Si hay email en sesion
    if email:
        favs_foods = shows_favorites(email)
        food_item = request.form['food']
        diet_name = request.form['diet_name']
        start_date=request.form["start_date"]
        end_date=request.form["end_date"]
        quantity = int(request.form['quantity'])
        print(start_date)
        message_diet = add_or_update_diet(email,diet_name,start_date=start_date,end_date=end_date)
        message_food = add_food_diet(email,diet_name,food_item,quantity)
        return render_template("creatediet.html",favs_foods=favs_foods,message_diet=message_diet, message_food=message_food)
    else:
         return render_template("creatediet.html")

@app.route('/delete_diet', methods=['GET','POST'])
def delete_diet():
    email = session.get("google_email")
    #Si hay email en sesion
    if email:
        diet_names = request.form.getlist('diet_names')
        message = delete_diet_user(email, diet_names)
        if not diet_names:
            message = "You must select at least one diet to eliminate"
        diets = list(show_option_diets(email))
        return render_template("show_option_diet.html",diets=diets, message=message)
    else:
        return render_template("show_option_diet.html")

@app.route("/show_calendar",methods=['GET','POST'])
def show_calendar():
    email = session.get("google_email")
    #Si hay email en sesion
    if email:
        diets = show_option_diets(email)
        print(diets)
        return render_template("calendar.html", diets=diets)
    else:
         diets = []
         return render_template("calendar.html",diets=diets)

@app.route("/add_food_menu", methods=['GET','POST'])
def add_food_menu():
    email = session.get("google_email")
    #Si hay email en sesion
    if email:
        favs_foods=shows_favorites(email)
        return render_template("add_food_menu.html", favs_foods=favs_foods)

@app.route("/add_food_to_diet", methods=['GET','POST'])
def add_food_to_diet():
    email = session.get("google_email")
    #Si hay email en sesion
    if email:
        favs_foods = shows_favorites(email)
        diets = list(show_option_diets(email))
        food_item = request.form['food']
        diet_name = request.form['diet_name']
        quantity = int(request.form['quantity'])
        message_food = add_food_diet(email,diet_name,food_item,quantity)
        return render_template("show_option_diet.html",favs_foods=favs_foods, message_food=message_food, diets=diets)
    else:
         return render_template("show_option_diet.html")

@app.route('/search_gyms', methods=['GET', 'POST'])
def search_gyms():
    if request.method == 'POST':
        city = request.form['city']
        print(city)
        gyms = get_gym(city)
        print(gyms)
        return render_template('gyms.html', gyms=gyms)
    return render_template('search_gym.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)

