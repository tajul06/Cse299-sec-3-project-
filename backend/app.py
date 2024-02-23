from flask import Flask ,url_for, redirect ,session

from authlib.integrations.flask_client import OAuth


app = Flask(__name__)
app.secret_key='justtry something'

# oauth config
oauth = OAuth(app)
google =oauth.register(
     name='google',
     client_id='948138056692-l0ec5idekoun63t57696tic16qn6pej0.apps.googleusercontent.com',
     client_secret='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',
     access_token_url='https://accounts.google.com/o/oauth2/token',
     access_token_params=None,
     authorize_url='https://accounts.google.com/o/oauth2/auth',
     authorize_params=None,
     api_base_url='https://www.googleapis.com/oauth2/v1/',
     userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
     client_kwargs={'scope': 'email profile'}
     
)

@app.route('/')
def hello_world():
    email= dict(session).get('email', None)
    return f'hello,{email}!'


@app.route('/login')
def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    try:
        token = google.authorize_access_token()
        resp = google.get('userinfo')
        resp.raise_for_status()  # Raise exception for HTTP errors
        user_info = resp.json()
        session['email'] = user_info['email']
    except Exception as e:
        # Log the error and handle it appropriately
        print(f"Error in authorize route: {e}")
        return "An error occurred during authorization", 500  # Return a 500 Internal Server Error status code
    return redirect('/')

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')

