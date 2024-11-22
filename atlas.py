from flask import Flask, render_template, request, redirect, url_for, session, send_file, send_from_directory
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from bson.objectid import ObjectId
import io
from reportlab.pdfgen import canvas
from flask_login import current_user

# Configuración de Flask
app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

# Conexión a MongoDB Atlas
client = MongoClient("mongodb+srv://vargasestebanjv11:12345@juancho.gxblf.mongodb.net/") 
db = client['CRUD_DB']
usuarios = db['usuarios']
datos = db['coleccion_datos']  # Definimos la colección para el CRUD

# Inicialización de Flask-Bcrypt y Flask-Login
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Modelo de usuario para Flask-Login
class Usuario(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(username):
    # Solo cargar el usuario sin necesidad de verificar en la base de datos
    return Usuario(username)

# Ruta para manejar favicon.ico
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Ruta de inicio de sesión
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Este paso ya no verifica la existencia del usuario, solo verifica la contraseña
        username = request.form["username"]
        password = request.form["password"]

        # En vez de buscar un usuario específico, validamos la contraseña con un valor predeterminado
        # Puedes usar cualquier valor que tú desees como contraseña
        if password == "12345":  # Cambia esto a la contraseña que desees
            login_user(Usuario(username))
            return redirect(url_for("index"))
        else:
            return "Usuario o contraseña incorrectos", 401  # Mostrar mensaje de error si la contraseña no coincide
    return render_template("login.html")

# Ruta para cerrar sesión
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# Ruta principal (Index)
@app.route("/")
def index():
    items = list(datos.find())  # Recuperar todos los documentos de la colección
    logged_in = False
    if current_user.is_authenticated:
        logged_in = True
    return render_template("index.html", items=items, logged_in=logged_in)

# Crear un nuevo documento
@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        nuevo_dato = {
            "nombre": request.form["nombre"],
            "apellido": request.form["apellido"],
            "ciudad": request.form["ciudad"],
            "telefono": request.form["telefono"],
            "email": request.form["email"]
        }
        datos.insert_one(nuevo_dato)  # Insertar el nuevo documento en la colección
        return redirect(url_for("index"))
    return render_template("create.html")  # Mostrar formulario para crear datos

# Actualizar un documento
@app.route("/update/<id>", methods=["GET", "POST"])
@login_required
def update(id):
    item = datos.find_one({"_id": ObjectId(id)})
    if request.method == "POST":
        datos.update_one({"_id": ObjectId(id)}, {"$set": {
            "nombre": request.form["nombre"],
            "apellido": request.form["apellido"],
            "ciudad": request.form["ciudad"],
            "telefono": request.form["telefono"],
            "email": request.form["email"]
        }})
        return redirect(url_for("index"))
    return render_template("update.html", item=item)  # Mostrar formulario con los datos actuales

# Eliminar un documento
@app.route("/delete/<id>")
@login_required
def delete(id):
    datos.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("index"))

# Generar PDF de los datos
@app.route("/pdf")
def generar_pdf():
    items = list(datos.find())  # Recuperar los documentos de la colección
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)
    
    # Título del PDF
    pdf.drawString(100, 800, "Datos de la Colección")
    y = 750
    
    # Recorrer los documentos para agregar sus datos al PDF
    for item in items:
        pdf.drawString(10, y, f"Nombre: {item['nombre']}, Apellido: {item['apellido']}, "
                               f"Ciudad: {item['ciudad']}, Teléfono: {item['telefono']}, "
                               f"Email: {item['email']}")
        y -= 20  # Reducir la posición vertical para el siguiente dato

        # Si se agota el espacio vertical, crea una nueva página
        if y < 500:
            pdf.showPage()
            y = 10

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="reporte.pdf", mimetype="application/pdf")

# Ejecutar la aplicación
if __name__ == "__main__":
    app.run(debug=True)

