from python.config import app
import simplejson as json 

@app.route('/')
def home():
    return "hey"
