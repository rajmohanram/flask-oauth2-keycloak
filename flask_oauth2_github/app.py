import os

from flask import Flask, redirect, url_for, session, jsonify
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_APP_SECRET_KEY')

# Keycloak Configuration
app.config['KEYCLOAK_BASE_URL'] = 'https://keycloak.rlabs.com'
app.config['KEYCLOAK_REALM'] = 'devops'
app.config['KEYCLOAK_CLIENT_ID'] = os.environ.get('KEYCLOAK_CLIENT_ID')
app.config['KEYCLOAK_CLIENT_SECRET'] = os.environ.get('KEYCLOAK_CLIENT_SECRET')
app.config['KEYCLOAK_REDIRECT_URI'] = 'http://127.0.0.1:5000/login/authorized'

# OAuth Configuration
oauth = OAuth(app)
keycloak = oauth.register(
    name='keycloak',
    client_id=app.config['KEYCLOAK_CLIENT_ID'],
    client_secret=app.config['KEYCLOAK_CLIENT_SECRET'],
    server_metadata_url=f"{app.config['KEYCLOAK_BASE_URL']}/realms/{app.config['KEYCLOAK_REALM']}/.well-known/openid-configuration",
    client_kwargs={'scope': 'openid email profile', 'verify': False}
)

@app.route('/')
def index():
    if 'user' in session:
        user_info = session['user']
        return jsonify(user_info)
    return '<a href="/login">Sign in with Keycloak</a>'

@app.route('/login')
def login():
    return keycloak.authorize_redirect(redirect_uri=app.config['KEYCLOAK_REDIRECT_URI'])

@app.route('/login/authorized')
def authorized():
    token = keycloak.authorize_access_token()
    user_info = keycloak.parse_id_token(token, nonce='')
    session['user'] = user_info
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    logout_url = f"{app.config['KEYCLOAK_BASE_URL']}/realms/{app.config['KEYCLOAK_REALM']}/protocol/openid-connect/logout"
    return redirect(logout_url)

if __name__ == "__main__":
    app.run(debug=True)