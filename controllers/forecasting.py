from prophet import Prophet
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import simplejson as json 

def time_series(df, predCol, dateCol, sample):
    deleteColumns = [col for col in df.columns if (col!=dateCol and col!=predCol)]
    df = df.drop(deleteColumns, axis=1)
    df = df.rename(columns={predCol:'y', dateCol: 'ds'})
    df['ds'] = pd.to_datetime(df['ds'])
    df['y'] = pd.to_numeric(df['y'])
    df = df.sort_values(by='ds')
    df = df.groupby(['ds'])['y'].sum()
    df = df.asfreq('D')
    df = df.reset_index()
    df['y'] = df['y'].fillna(0)

    m = Prophet()
    if sample == 'Daily':
        predLength = 30
        m.fit(df)
        future = m.make_future_dataframe(periods=predLength, freq='D')
    elif sample == 'Weekly':
        predLength = 4
        df = df.set_index('ds')
        df = df.resample('W').sum()
        df = df.reset_index()
        m.fit(df)
        future = m.make_future_dataframe(periods=predLength, freq='W')
    else:
        predLength = 4
        df = df.set_index('ds')
        df = df.resample('M').sum()
        df = df.reset_index()
        m.fit(df)
        future = m.make_future_dataframe(periods=predLength, freq='M')

    df = df[-365:]

    calendar = []
    for value, day in zip(df['y'].values.tolist(), df['ds'].dt.strftime('%Y-%m-%d').values.tolist()):
        calendar.append({
            'day': day,
            'value': value
        })

    hist = np.histogram(df['y'], bins=10)
    hist_x = []
    for range_ in range(len(hist[1])-1):
        hist_x.append(nicefy(hist[1][range_]) + '-' + nicefy(hist[1][range_]+1))

    histogram = []
    for ind, frequency in enumerate(hist[0]):
        histogram.append({
            "interval": hist_x[ind],
            hist_x[ind]: int(frequency) 
        })


    X = [[x] for x in range(len(df))]
    lr_model = LinearRegression().fit(X, df['y'].values)
    lr_model.predict(X).tolist()
    lrX = df['ds'].dt.strftime('%d/%m/%Y').values.tolist()
    lrY = lr_model.predict(X).tolist()

    parsedLr = {'id': 'trend', "color": "hsl(148, 70%, 50%)", 'data': []}
    for xPoint, yPoint in zip(lrX, lrY):
        parsedLr['data'].append({'x': xPoint, 'y': round(yPoint)})
    del lrY

    fft_list = np.fft.fft(df['y'])
    fft_list[3:-3]=0
    fftY = np.abs(np.fft.ifft(fft_list)).tolist()
    del fft_list
    

    parsedFFT = {'id': 'fft', "color": "hsl(148, 70%, 50%)", 'data': []}
    for xPoint, yPoint in zip(lrX, fftY):
        parsedFFT['data'].append({'x': xPoint, 'y': round(yPoint)})
    del lrX, fftY

    forecast = m.predict(future)
    forecastX = forecast['ds'].iloc[-predLength:].dt.strftime('%d/%m/%Y').values.tolist()
    forecastY = forecast['yhat'].iloc[-predLength:].values.tolist()

    parsedForecast = {'id': 'forecast', "color": "hsl(149, 70%, 50%)", 'data': []}
    for xPoint, yPoint in zip(forecastX, forecastY):
        parsedForecast['data'].append({'x': xPoint, 'y': round(yPoint)})
    
    del forecast, forecastX, forecastY, future

    dataX = df['ds'].dt.strftime('%d/%m/%Y').values.tolist()
    dataY = df['y'].values.tolist()

    parsedData = {'id': 'your data', "color": "hsl(150, 70%, 50%)", 'data': []}
    for xPoint, yPoint in zip(dataX, dataY):
        parsedData['data'].append({'x': xPoint, 'y': round(yPoint)})
    
    results = {
        'data': parsedData,
        'forecast': parsedForecast,
        'fft': parsedFFT,
        'lr': parsedLr,
        'histogram': histogram,
        'calendar': calendar
    }

    return results


def nicefy(n):
	n = round(n,2)
	if ((n >= 1000) & (n < 1000000)):
		return str(round(n/1000, 3))+'K'
	elif ((n >= 1000000) & (n < 1000000000)):
		return str(round(n/1000000, 3))+'M'
	elif n >= 1000000000:
		return str(round(n/1000000000, 3))+'B'
	return str(n)