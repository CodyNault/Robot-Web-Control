from flask import Flask, render_template, request
from flask_socketio import SocketIO, send
import RPi.GPIO as GPIO
import json
import time
import math
import Adafruit_PCA9685

app = Flask(__name__)
GPIO.setmode(GPIO.BCM)
pwm = Adafruit_PCA9685.PCA9685()
socketio = SocketIO(app)

motor1_speed = 0
motor2_speed = 0
motor3_speed = 0
motor4_speed = 0
motor_speed_update_id = 0;

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        request_string = str(request.form)
        display_request_string = "Recieved request: "+ request_string
        if request.form['request_type'] == 'servo_positions':
            display_request_string += " \n result: " + execute_servo_position_request(request.form)
        else:
            display_request_string += " \n result: " + execute_motor_request(request.form)
    else:
        display_request_string = "Waiting for request..."
    return render_template('index.html', recieved_request=display_request_string)

@socketio.on('json', namespace='/active_update')
def handle_json(json_obj):
    send('received json: ' + str(json_obj), json=False)
    if json_obj['mode'] == 'steering':
        live_motor_update(json_obj, motor_speed_update_id)
        motor1_speed = settings['motor1']
        motor2_speed = settings['motor2']
        motor3_speed = settings['motor3']
        motor4_speed = settings['motor4']
        motor_speed_update_id += 1
        

def execute_motor_request(settings):
    motor_pins = {}
    motor_pins[12] = True if settings['front_right'] == 'fwd' else False
    motor_pins[16] = True if settings['front_right'] == 'rvs' else False
    motor_pins[21] = True if settings['front_left'] == 'fwd' else False
    motor_pins[20] = True if settings['front_left'] == 'rvs' else False
    motor_pins[13] = True if settings['rear_right'] == 'fwd' else False
    motor_pins[6] = True if settings['rear_right'] == 'rvs' else False
    motor_pins[26] = True if settings['rear_left'] == 'fwd' else False
    motor_pins[19] = True if settings['rear_left'] == 'rvs' else False
    for pin, value in motor_pins.items():
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, False)
    duration = float(settings['duration'])
    speed = float(settings['speed'])
    time_elapsed = 0
    while time_elapsed < duration:
        for pin, pin_value in motor_pins.items():
            GPIO.output(pin, pin_value)
        time.sleep(speed / 10000)
        for pin, pin_value in motor_pins.items():
            GPIO.output(pin, False)
        time.sleep(0.01 - speed / 10000)
        time_elapsed += 0.01
    return 'Success!'
    
def execute_servo_position_request(settings):
    pwm.set_pwm(0, 0, int((360 / settings['debug_servo_1']) * 4095) )
    pwm.set_pwm(1, 0, int((360 / settings['debug_servo_2']) * 4095) )
    pwm.set_pwm(2, 0, int((360 / settings['debug_servo_3']) * 4095) )
    pwm.set_pwm(3, 0, int((360 / settings['debug_servo_4']) * 4095) )
    pwm.set_pwm(4, 0, int((360 / settings['debug_servo_5']) * 4095) )
    pwm.set_pwm(5, 0, int((360 / settings['debug_servo_6']) * 4095) )
    pwm.set_pwm(6, 0, int((360 / settings['debug_servo_7']) * 4095) )
    pwm.set_pwm(7, 0, int((360 / settings['debug_servo_8']) * 4095) )
    return 'Success!'

def live_motor_update(settings, call_id):
    duration = 0.1
    motor_pins = {}
    motor_pins[12] = settings['motor1'] if settings['motor1'] > 0 else False
    motor_pins[16] = math.abs(settings['motor1']) if settings['motor1'] < 0 else False
    motor_pins[21] = settings['motor2'] if settings['motor2'] > 0 else False
    motor_pins[20] = math.abs(settings['motor2']) if settings['motor2'] < 0 else False
    motor_pins[13] = settings['motor3'] if settings['motor3'] > 0 else False
    motor_pins[6] = math.abs(settings['motor3']) if settings['motor3'] < 0 else False
    motor_pins[26] = settings['motor4'] if settings['motor4'] > 0 else False
    motor_pins[19] = math.abs(settings['motor4']) if settings['motor4'] < 0 else False
    for pin, value in motor_pins.items():
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, False)
    time_elapsed = 0
    while time_elapsed < duration:
        if motor_speed_update_id call_id > call_id:
            return 'New Order!'
        for pin, pin_value in motor_pins.items():
            GPIO.output(pin, pin_value)
        for i in range(100)
            time.sleep(0.001)
            time_elapsed += 0.001
            for pin, pin_value in motor_pins.items():
                if pin_value != False and pin_value / 1000 < time_elapsed
                    GPIO.output(pin, False)
    return 'Success!'
    

def inOutCirc(t, b, c, d): #(time,beginning,change,duration)
    t = t / d * 2
    if t < 1:
        return -c / 2 * (math.sqrt(1 - t * t) - 1) + b
    else:
        t = t - 2
        return c / 2 * (math.sqrt(1 - t * t) + 1) + b
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
    socketio.run(app)
