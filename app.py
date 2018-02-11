import os
import serial
from flask import Flask
from flask import render_template, Response, request
from flask_ask import Ask, statement
from reverse_read import reverse_readline

app=Flask(__name__)
ask = Ask(app, '/')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    gen = reverse_readline('/var/www/FlaskApps/kindbot/dht_log.txt')
    last_line = next(gen)
    _, temp, hum, lux = last_line.split(',')
    return render_template('dashboard.html', temp=temp, hum=hum, lux=lux)

@app.route('/camera')
def camera():
    pic_lst = ['../static/images/' + str(x) for x in os.listdir("/var/www/FlaskApps/kindbot/static/images")]
    pic_lst.sort()
    pic_lst = pic_lst[::-1]
    return render_template('camera.html', pic_lst=pic_lst)

@app.route('/automate', methods=['POST', 'GET'])
def automate():
#    if request.form['button'] == "on":
#        print 'yass'
#    elif request.form['button'] == "off":
#        print 'poo'
    return render_template('automate.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')


@app.route('/data_stream')
def data_stream():
    def gen():
        for c in 'Hello world!':
            yield c
            time.sleep(0.5)
    return Response(gen())

### Alexa Stuff
@ask.intent('stats')
def stats():
    """ Returns last reading """
    gen = reverse_readline('dht_log.txt')   #our sensor reading logs
    last_line = next(gen)
    tm, temp, hum, lux = last_line.split(',')
    tm = tm.split(' ')[1]
    speech_text = 'Last reading was taken at %s. The temperature is %s degrees Fahrenheit and humidity is at %s percent. The lux levels are %s.' % (tm, temp, hum, lux)
    return statement(speech_text)


@ask.intent('dripon')
def dripon():
    """ Turn switch on """
    arduinoSerialData = serial.Serial('/dev/ttyACM0',9600)
    arduinoSerialData.write('1')
    speech_text = 'I have turned on the switch'
    return statement(speech_text)

@ask.intent('dripoff')
def dripoff():
    """ Turn switch off """
    arduinoSerialData = serial.Serial('/dev/ttyACM0',9600)
    arduinoSerialData.write('0')
    speech_text = 'I have turned it off!'
    return statement(speech_text)


if __name__ == "__main__":
    app.run()
