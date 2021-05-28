from flask import Flask, request, make_response
from flask_cors import CORS, cross_origin

# init app.
application = app = Flask(__name__, template_folder='../templates')
app.secret_key = 'BAD_SECRET_KEY'
CORS(app, support_credentials=True)
