# load modules
import RPi.GPIO as GPIO
import time
# board numbering system to use
GPIO.setmode(GPIO.BCM)

# variable to hold a short delay time
delayTime = 0.2

# setup trigger and echo pins
trigPin = 23
echoPin = 24
GPIO.setup(trigPin, GPIO.OUT)
GPIO.setup(echoPin, GPIO.IN)

try:
# where the action happens
    while True:
        # start the pulse to get the sensor to send the ping
        # set trigger pin low for 2 micro seconds
        GPIO.output(trigPin, 0)
        time.sleep(2E-6)
        # set trigger pin high for 10 micro seconds
        GPIO.output(trigPin, 1)
        time.sleep(10E-6)
        # go back to zero - communication compete to send ping
        GPIO.output(trigPin, 0)
        # now need to wait till echo pin goes high to start the timer
        # this means the ping has been sent
        while GPIO.input(echoPin) == 0:
            pass
        # start the time - use system time
        echoStartTime = time.time()
        # wait for echo pin to go down to zero
        while GPIO.input(echoPin) == 1:
            pass
        echoStopTime = time.time()
        # calculate ping travel time
        pingTravelTime = echoStopTime - echoStartTime
        # Use the time to calculate the distance to the target.
        # speed of sound at 72 deg F is 344.44 m/s
        # from weather.gov/epz/wxcalc_speedofsound.
        # equations used by calculator at website above.
        # speed of sound = 643.855*((temp_in_kelvin/273.15)^0.5)
        # temp_in_kelvin = ((5/9)*(temp_in_F - 273.15)) + 32
        #
        # divide in half since the time of travel is out and back
        dist_cm = (pingTravelTime*34444)/2
        dist_inch = dist_cm * 0.3937008 # 1 cm = 0.3937008 inches
        print('Distance = ', round(dist_inch, 1),'inches |', round(dist_cm, 1),
              'cm')
        # sleep to slow things down
        time.sleep(delayTime)
        
except KeyboardInterrupt:
    GPIO.cleanup()
