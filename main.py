from flask import Flask, render_template, redirect, session, request
from flask import url_for
from pymongo import MongoClient


app = Flask(__name__)

MONGO_URL_ATLAS = 'mongodb+srv://admin:admin123@denuncias-dkzqn.mongodb.net/test?retryWrites=true&w=majority'

client = MongoClient(MONGO_URL_ATLAS, ssl_cert_reqs=False)
db = client['denuncias']
usuarios = db['usuarios']
denuncias = db['denuncias']

app.secret_key = 'fh879FHSI&/'


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'email' in session:
        return redirect(url_for('aplicacion'))
    if 'email' in session and request.method:
        session.clear()
    else:
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            user = {}
            resultados = usuarios.find(
                {'email': email}, {'_id': 0, 'nombre': 1, 'password': 1, 'email': 1, 'dni': 1})
            resultados = list(resultados)

            for resultado in resultados:
                user.update(
                    {'email': resultado['email'], 'nombre': resultado['nombre'], 'password': resultado['password'], 'dni': resultado['dni']})

            print(user)

            if len(user) > 0:
                if user['email'] == email and user['password'] == password:
                    app.logger.info('%s se conectó con éxito', email)
                    session['email'] = email
                    session['nombre'] = user['nombre']
                    session['dni'] = user['dni']

                    return redirect(url_for('aplicacion'))
                else:
                    return render_template('index.html', error=True)
            else:
                app.logger.info('%s falló en conectarse', email)
                return render_template('index.html', error=True)

    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        direccion = request.form['direccion']
        dni = request.form['dni']
        email = request.form['email']
        password = request.form['password']

        usuarioExistente = usuarios.find_one({'nombre': nombre})

        if usuarioExistente is None:
            usuarios.insert_one({'nombre': nombre, 'direccion': direccion, 'dni': dni, 'email': email, 'password': password})
            session['email'] = email
            return redirect(url_for('crearficha'))

        return render_template('register.html', errorDatos=True)

    return render_template('register.html')


@app.route('/aplicacion', methods=['GET', 'POST'])
def aplicacion():

    return render_template('aplicacion.html')


@app.route('/sign_out', methods=['GET', 'POST'])
def sign_out():
    app.logger.info('%s se desconectó', session['email'])
    session.clear()

    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(error):
    app.logger.info(f"Página no encontrada: {request.url}")

    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(debug=True)
