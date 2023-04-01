import os
import requests
from flask import Flask, request, jsonify, redirect, url_for
from didcomm import DIDComm

app = Flask(__name__)
didcomm = DIDComm()

# ID.me credentials
app.config['IDME_CLIENT_ID'] = os.environ.get('IDME_CLIENT_ID')
app.config['IDME_CLIENT_SECRET'] = os.environ.get('IDME_CLIENT_SECRET')

@app.route('/login')
def login():
    idme_auth_url = f'https://api.id.me/oauth/authorize?client_id={app.config["IDME_CLIENT_ID"]}&redirect_uri={url_for("callback", _external=True)}&response_type=code&scope=openid+email'
    return redirect(idme_auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_data = {
        'client_id': app.config['IDME_CLIENT_ID'],
        'client_secret': app.config['IDME_CLIENT_SECRET'],
        'redirect_uri': url_for('callback', _external=True),
        'code': code,
        'grant_type': 'authorization_code'
    }
    token_response = requests.post('https://api.id.me/oauth/token', data=token_data)
    access_token = token_response.json().get('access_token')

    user_data_response = requests.get('https://api.id.me/api/public/v3/attributes.json', headers={'Authorization': f'Bearer {access_token}'})
    user_data = user_data_response.json()

    # Create a DID for the user with DIDComm
    user_did = didcomm.create_did(user_data)

    return jsonify({'message': 'User identity verified', 'did': user_did})

if __name__ == '__main__':
    app.run(debug=True)
