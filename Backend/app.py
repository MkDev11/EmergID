import os
import requests
from flask import Flask, request, jsonify, redirect, url_for, render_template, session
from didcomm import DIDComm
from werkzeug.utils import secure_filename

app = Flask(__name__)
didcomm = DIDComm()
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or 'your_super_secret_key_here'
# ID.me credentials
app.config['IDME_CLIENT_ID'] = os.environ.get('IDME_CLIENT_ID')
app.config['IDME_CLIENT_SECRET'] = os.environ.get('IDME_CLIENT_SECRET')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    idme_auth_url = f'https://api.id.me/oauth/authorize?client_id={app.config["IDME_CLIENT_ID"]}&redirect_uri={url_for("callback", _external=True)}&response_type=code&scope=openid+email'
    return redirect(idme_auth_url)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max image size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image provided'})

    image = request.files['image']
    if not allowed_file(image.filename):
        return jsonify({'success': False, 'error': 'Invalid image format'})

    filename = secure_filename(image.filename)
    image_path =  os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(image_path)

    # Save the image path in the user's session
    session['image_path'] = image_path

    return jsonify({'success': True})

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
    user_data['image_path'] = session['image_path']
    del session['image_path']

    # Create a DID for the user with DIDComm
    user_did = didcomm.create_did(user_data)

    return jsonify({'message': 'User identity verified', 'did': user_did})

if __name__ == '__main__':
    app.run(debug=True)
