# Import libraries
from flask import Flask, render_template
import time
import RPi.GPIO as GPIO
app = Flask(__name__)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Variable //& pinnumber with pin state
hcLevel = 3        # GPIO input port

# set mode
GPIO.setup(hcLevel, GPIO.IN, GPIO.PUD_UP)

# Create a dictionary called pins to store the pin number, name, and pin state:
pins = {
    4: {'name': 'hcMotor', 'state': GPIO.LOW},
    23: {'name': 'SignalYellow', 'state': GPIO.LOW},
    14: {'name': 'SignalGreen', 'state': GPIO.LOW},
    25: {'name': 'SignalRed', 'state': GPIO.LOW},
    10: {'name': 'Alarm', 'state': GPIO.LOW}
}
manual_modes = {
    1: {'name': 'Mode 1', 'state': 'off'},
    2: {'name': 'Mode 2', 'state': 'off'},
    3: {'name': 'Mode 3', 'state': 'off'},
}
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

hcLimit3 = 150
hcLimit2 = 130
hcLimit1 = 110
hcLimit0 = 100
hc_threshold = 98

# remove trailing one zero
runTime0 = 0
runTime1 = 20
runTime2 = 30                # standard value
runTime3 = 40

# remove trailing double zero
offTime0 = 0
offTime1 = 45
offTime2 = 40          # standard value
offTime3 = 35

# auto hc injection


@app.route("/")
def index():
    templateData = {}
    return render_template('index.html', **templateData)


@app.route("/auto")
def auto():
    currenthcLevel = 140  # GPIO.input(hcLevel)
    level = currenthcLevel
    templateData = {
        'level': level,
    }
    return render_template('auto.html', **templateData)


@app.route("/autorun")
def autohc():
    print(" Starting hc injection in Auto Mode...")
    while True:
        hcMotor, signalYellow, signalGreen, signalRed, alarm = pins
        currenthcLevel = 140  # GPIO.input(hcLevel)
        level = currenthcLevel
        if currenthcLevel > hcLimit0 and currenthcLevel <= hcLimit1:
            runTime = runTime1
            offTime = offTime1
            GPIO.output(signalRed, GPIO.HIGH)

        elif currenthcLevel > hcLimit1 and currenthcLevel <= hcLimit2:
            runTime = runTime2
            offTime = offTime2
            GPIO.output(signalYellow, GPIO.HIGH)
        elif currenthcLevel > hcLimit2 and currenthcLevel <= hcLimit3:
            runTime = runTime3
            offTime = offTime3
            GPIO.output(signalGreen, GPIO.HIGH)
        elif currenthcLevel > hcLimit3:
            GPIO.output(alarm, GPIO.HIGH)
        else:
            runTime = runTime0
            offTime = offTime0
            GPIO.output(signalRed, GPIO.LOW)
            GPIO.output(signalYellow, GPIO.LOW)
            GPIO.output(signalGreen, GPIO.LOW)

        GPIO.output(hcMotor, GPIO.HIGH)
        time.sleep(runTime)
        GPIO.output(hcMotor, GPIO.LOW)
        time.sleep(offTime)
        motor_status = "Motor stopped"
        # For each pin, read the pin state and store it in the pins dictionary:
        for pin in pins:
            pins[pin]['state'] = GPIO.input(pin)
            if pins[pin]['state'] == 1:
                GPIO.output(pin, GPIO.LOW)

        # afterhcLevel = GPIO.input(hcLevel)
        level = 98
        templateData = {
            'pins': pins,
            'motor_status': motor_status,
            'level': level
        }
        # if level == hc_threshold:
        #     return render_template('auto_main.html', **templateData)
        # else:
        #     continue
        return render_template('auto_main.html', **templateData)

# Manual hc injection


@app.route("/manual")
def manual():
    # For each pin, read the pin state and store it in the pins dictionary:
    for pin in pins:
        pins[pin]['state'] = GPIO.input(pin)

    templateData = {
        'pins': pins,
        'manual_modes': manual_modes
    }
    # Pass the template data into the template main.html and return it to the user
    return render_template('main.html', **templateData)

# The function below is executed when someone requests a URL with the pin number and action in it:


@app.route("/manual/<int:mode>")
def manualhc(mode):
    print(" Starting hc injection in manual mode...")
    hcMotor, signalYellow, signalGreen, signalRed, alarm = pins
    mode = int(mode)
    if mode == 1:
        runTime = runTime1
        offTime = offTime1
        GPIO.output(signalRed, GPIO.HIGH)
        message = "Selected " + manual_modes[1]['name'] + " runned."
        manual_modes[1]['state'] = "runned"
    elif mode == 2:
        runTime = runTime2
        offTime = offTime2
        GPIO.output(signalYellow, GPIO.HIGH)
        message = "Selected " + manual_modes[2]['name'] + " runned."
        manual_modes[2]['state'] = "runned"
    elif mode == 3:
        runTime = runTime3
        offTime = offTime2
        GPIO.output(signalGreen, GPIO.HIGH)
        message = "Selected " + manual_modes[3]['name'] + " runned."
        manual_modes[3]['state'] = "runned"
    else:
        runTime = runTime0
        offTime = offTime0
        GPIO.output(signalRed, GPIO.LOW)
        GPIO.output(signalYellow, GPIO.LOW)
        GPIO.output(signalGreen, GPIO.LOW)

    GPIO.output(hcMotor, GPIO.HIGH)
    time.sleep(runTime)
    GPIO.output(hcMotor, GPIO.LOW)
    time.sleep(offTime)
    motor_status = "Motor stopped"
    # For each pin, read the pin state and store it in the pins dictionary:
    for pin in pins:
        pins[pin]['state'] = GPIO.input(pin)
        if pins[pin]['state'] == 1:
            GPIO.output(pin, GPIO.LOW)

    # Along with the pin dictionary, put the message into the template data dictionary:

    templateData = {
        'pins': pins,
        'message': message,
        'manual_modes': manual_modes,
        'motor_status': motor_status,
    }

    return render_template('main.html', **templateData)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
