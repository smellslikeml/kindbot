import os, glob
import serial
from flask import Flask
from flask import render_template, Response, request
from flask_ask import Ask, statement, session

app=Flask(__name__)
ask = Ask(app, '/')

def all_logs():
    log_lst = []
    lst = sorted(glob.glob('/home/pi/kindbot/app/logs/kindbot.*'), reverse=True)
    for fl in lst:
        with open(fl, 'r') as f:
            dict_str = f.read()
            log_lst.append(eval(dict_str))
    return log_lst


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    with open('/home/pi/kindbot/app/logs/kindbot.log', 'rb') as fl:
        last_rd = fl.read()
    read_dict = eval(last_rd)
    all_l = all_logs()
    time_data = [str(x['Time']) for x in all_l]
    temp_data= [int(x['Temperature']) for x in all_l]
    humid_data = [int(x['Humidity']) for x in all_l]
    return render_template('dashboard.html', temp=str(read_dict['Temperature']), hum=str(read_dict['Humidity']),
    lux=str(read_dict['Lumens']), time_data=time_data, temp_data=temp_data, humid_data=humid_data)

@app.route('/camera')
def camera():
    pic_lst = ['../static/images/' + str(x) for x in os.listdir("static/images")]
    pic_lst.sort()
    pic_lst = pic_lst[::-1]
    return render_template('camera.html', pic_lst=pic_lst)

@app.route('/automate', methods=['POST', 'GET'])
def automate():
    if os.path.exist("/home/pi/kindbot/app/logs/schedule_app.logs"):
        with open("/home/pi/kindbot/app/logs/schedule_app.logs", "rb") as fl:
            event_lst = fl.readlines()
        events = [{'id': x['id'], 'start': x['date']+'T'+x['time']}]
    else:
        events = []
    if request.method == 'POST':
        date = request.form['date']
        time = request.form['time']
        monday = request.form.get("monday") != None
        tuesday = request.form.get("tuesday") != None
        wednesday = request.form.get("wednesday") != None
        thursday = request.form.get("thursday") != None
        friday = request.form.get("friday") != None
        saturday = request.form.get("saturday") != None
        sunday = request.form.get("sunday") != None
        with open('/home/pi/kindbot/app/logs/schedule_app.logs', 'a') as fl:
            schedule_dict = {'date': date, 'time': time, 'repeat': {'monday':monday, 'tuesday': tuesday, 'wednesday': wednesday, 'thursday':thursday, 'friday': friday, 'saturday': saturday, 'sunday': sunday}, 'id'=str(random.randint(1,10000))}
            fl.write(str(schedule_dict) + '\n')
    return render_template('automate.html', events=events)

@app.route('/settings')
def settings():
    return render_template('settings.html')


############### Alexa Intents #################

@ask.intent('stats')
def stats():
    """ Returns last reading """
    with open('/home/pi/kindbot/app/logs/kindbot.log', 'rb') as fl:
        last_rd = fl.read()
    read_dict = eval(last_rd)
    speech_text = 'Last reading was taken at %s. The temperature is %s degrees Fahrenheit and humidity is at %s percent. The lux levels are %s.' % (read_dict['Time'], read_dict['Temperature'],read_dict['Humidity'], read_dict['Lumens'])
    return statement(speech_text)


@ask.intent('dripon')
def dripon():
    """ Turn switch on """
    arduinoSerialData = serial.Serial('/dev/ttyACM0',9600)
    arduinoSerialData.write('1')
    speech_text = 'Switch is on now'
    return statement(speech_text)

@ask.intent('dripoff')
def dripoff():
    """ Turn switch off """
    arduinoSerialData = serial.Serial('/dev/ttyACM0',9600)
    arduinoSerialData.write('0')
    speech_text = 'I have turned off the switch'
    return statement(speech_text)


@ask.intent('photo')
def photo():
    """ Show image of grow """
    pic_lst = ['/static/images/' + str(x) for x in os.listdir("static/images")]
    pic_lst.sort()
    last_pic = pic_lst[-1]
    pic_url = <your URL string> + last_pic
    speech_text = 'Here is your grow!'
    return statement(speech_text).display_render(template='BodyTemplate7', title='kindbot', backButton='HIDDEN', token=None, background_image_url=pic_url, text=None, hintText=None)


@ask.intent('schedule')
def schedule(date,time):
    with open('/home/pi/kindbot/app/logs/schedule.logs', 'a') as fl:
        ln = str(date) + ',' + str(time) + '\n'
        fl.write(ln)
    return statement("Ok. I've got it scheduled for {} at {}".format(date, time))


if __name__ == "__main__":
    app.run()
