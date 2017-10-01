from flask import Flask, render_template, request
import RPi.GPIO as GPIO
import time
import math
import Adafruit_PCA9685

app = Flask(__name__)
GPIO.setmode(GPIO.BCM)
pwm = Adafruit_PCA9685.PCA9685()

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

def inOutCirc(t, b, c, d): #(time,beginning,change,duration)
    t = t / d * 2
    if t < 1:
        return -c / 2 * (math.sqrt(1 - t * t) - 1) + b
    else:
        t = t - 2
        return c / 2 * (math.sqrt(1 - t * t) + 1) + b
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
