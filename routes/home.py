from python.config import app
from flask_cors import CORS, cross_origin
from flask import request

import simplejson as json 
import pandas as pd
from controllers.forecasting import time_series

@app.route('/')
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def home():
    return {
        'statusCode': 200,
        'body': 'test passed'
    }

@app.route('/forecast', methods=['POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def forecast():
    if request.method == 'POST':
        body = json.loads(request.data)
        columns = body['columns']
        df = pd.DataFrame(body['file'], columns=columns)
        predCol = columns[body['predictionColumn']]
        dateCol = columns[body['dateColumn']]
        results = time_series(df, predCol, dateCol, body['sample'])
        return results
    else:
        return {
            'statusCode': 405,
            'body': 'error'
        }
