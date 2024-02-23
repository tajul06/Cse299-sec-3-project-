from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    # Authenticate with Gmail (pseudo-code)
    if authenticate_with_gmail(email, password):
        # Generate token/session and send it back to frontend
        token = generate_token(email)
        return jsonify({'token': token}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

def authenticate_with_gmail(email, password):
    # Use appropriate library to authenticate with Gmail
    # For example, you might use OAuth2 or SMTP authentication
    # This is a simplified example
    if email == 'example@gmail.com' and password == 'password':
        return True
    else:
        return False

def generate_token(email):
    # Generate a token/session for the user
    # You might use JWT (JSON Web Tokens) or sessions for this
    # This is a simplified example
    return 'some_token_for_' + email

if __name__ == '__main__':
    app.run(debug=True)
