from flask import Flask, render_template, request, flash, url_for, redirect,session
from pymongo import MongoClient
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.secret_key="claveSegura"

client=MongoClient("mongodb+srv://bddeivin:sBPkNdVHPh3mWjLK@cluster0.b4idi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db=client['bdprueba1']
coleccion=db['usuarios']

@app.route('/')
def home():
    return redirect(url_for('pagina_principal'))
    # if 'usuario' not in session:
    #     return redirect(url_for('login'))
    # return redirect(url_for('pagina_principal'))

@app.route('/pagina_principal')
def pagina_principal():       
    usuario = session.get('usuario',"Iniciar sesión")
    return render_template('index.html', usuario=usuario)
    # if 'usuario' not in session:
    #     return redirect(url_for('login'))
    # return render_template('index.html', usuario=session['usuario'])

@app.route('/registro',methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        usuario = request.form['usuario']
        email = request.form['email']
        contraseña=request.form['contraseña']

        if coleccion.find_one({'email': email}):
            flash("El correo electronico ya esta registrado.")
            return redirect(url_for('registro'))
        
        claveEncriptada = bcrypt.generate_password_hash(contraseña).decode('utf-8')

        coleccion.insert_one({
            'usuario':usuario,
            'email':email,
            'contraseña':claveEncriptada
        })

        session['usuario']=usuario
        return redirect(url_for('pagina_principal'))
    
    return render_template('registro.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario=request.form['usuario']
        contraseña=request.form['contraseña']

        user = coleccion.find_one({'usuario': usuario})

        if user and bcrypt.check_password_hash(user['contraseña'], contraseña):
            session['usuario'] = usuario
            return redirect(url_for('pagina_principal'))
        else:
            flash("Usuario o contraseña incorrecta")
            return render_template('login.html')    
        
    return render_template('login.html')

@app.route('/perfil')
def perfil():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    usuario = session['usuario']
    datos_usuario = coleccion.find_one({'usuario': usuario})
    return render_template('perfil.html', usuario=datos_usuario['usuario'], email=datos_usuario['email'])

@app.route('/carrito')
def carrito():

    carrito = session.get('carrito', [])  # Obtener el carrito desde la sesión
    return render_template('carrito.html', carrito=carrito, usuario=session['usuario'])


@app.route('/agregarAlCarrito', methods=['POST'])
def agregarAlCarrito():
    nombre = request.form.get('nombre')
    precio = request.form.get('precio')
    imagen = request.form.get('imagen')  # Obtener la URL de la imagen

    if 'carrito' not in session:
        session['carrito'] = []

    session['carrito'].append({'nombre': nombre, 'precio': precio, 'imagen': imagen})
    session.modified = True  # Guardar cambios en la sesión

    return redirect(url_for('carrito'))  # Redirigir al carrito

@app.route('/vaciar_carrito')
def vaciar_carrito():
    session.pop('carrito',None)
    return redirect(url_for('carrito'))


@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/recuperar_contraseña')
def recuperar_contraseña():
    return render_template('recuperar_contraseña.html')

@app.route('/cerrar_sesion')
def cerrar_sesion():
    session.pop('usuario', None)
    return redirect(url_for('pagina_principal'))

if __name__ == '__main__':
    app.run(debug=True)
