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

motor_speed_update_id = 0; #incremented for every websocket packet
motor_pin_list = {12,16,21,20,13,25,26,19}
for pin in motor_pin_list:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, False)

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

@socketio.on('my event', namespace='/test')
def handle_my_custom_namespace_event(json):
    print 'received json: ' + str(json)

@socketio.on('json_control', namespace='/active_update')
def handle_json(json_obj):
    global motor_speed_update_id
    print 'recieved json control request id:' + str(motor_speed_update_id + 1)
    send('received json: ' + str(json_obj), json=False)
    if json_obj['mode'] == 'steering':
        #live_motor_update(json_obj, motor_speed_update_id)
        thread = socketio.start_background_task(settings=json_obj, call_id=motor_speed_update_id, target=live_motor_update)
        

def execute_motor_request(settings):
    motor_pins = {}
    motor_pins[12] = True if settings['front_right'] == 'fwd' else False
    motor_pins[16] = True if settings['front_right'] == 'rvs' else False
    motor_pins[21] = True if settings['front_left'] == 'fwd' else False
    motor_pins[20] = True if settings['front_left'] == 'rvs' else False
    motor_pins[13] = True if settings['rear_right'] == 'fwd' else False
    motor_pins[25] = True if settings['rear_right'] == 'rvs' else False
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
    global motor_speed_update_id
    motor_speed_update_id += 1
    time_elapsed = 0
    duration = 0.1
    motor_pins = {}
    motor_pins[12] = True if settings['motor1'] > 0 else False
    motor_pins[16] = True if settings['motor1'] < 0 else False
    motor_pins[21] = True if settings['motor2'] > 0 else False
    motor_pins[20] = True if settings['motor2'] < 0 else False
    motor_pins[25] = True if settings['motor3'] > 0 else False
    motor_pins[13] = True if settings['motor3'] < 0 else False
    motor_pins[26] = True if settings['motor4'] > 0 else False
    motor_pins[19] = True if settings['motor4'] < 0 else False
    print 'Running request id:' + str(motor_speed_update_id + 1)
    speed = abs(settings['motor1'])
    print "speed: " + str(speed)
    while time_elapsed < duration:
        if motor_speed_update_id > call_id + 1:
            for pin, value in motor_pins.items():
                GPIO.output(pin, False)
            print "interupted id:" + str(call_id) + " for id:" + str(motor_speed_update_id)
            return 'New Order!'
        for pin, pin_value in motor_pins.items():
            GPIO.output(pin, pin_value)
            print "Setting pin " + str(pin) + " to " + str(pin_value)
        time.sleep(speed / 10000.0)
        print "sleeping for " + str(speed / 10000.0) + " seconds"
        for pin, pin_value in motor_pins.items():
            GPIO.output(pin, False)
        time.sleep(0.01 - speed / 10000.0)
        print "now sleeping for " + str(0.01 - speed / 10000.0) + " seconds"
        time_elapsed += 0.01

    for pin, value in motor_pins.items():
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
    socketio.run(app, debug=True, host='0.0.0.0', port=80)
