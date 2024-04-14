import cv2
import RPi.GPIO as GPIO
import numpy as np
import time

                        #cv setup
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

            #variables
red = 14               #STOP indicator
right = 27             #(green) right hbridge high
left = 22              #(blue)  left hbridge high
pwmPin = 18            #forward using PWM
butPin = 17            # Broadcom pin 17 (P1 pin 11) (BUTTON)
dc = 0                 # duty cycle (0-100) for PWM pin
last_dc = 0            # for determining a dc change
STATE = 0
t_end = 0              #timer variable
t_turn = 0             #timer variable
color = ''
protocol = "idle"
debounce = 0
trigPin = 23            # setup trigger and echo pins
echoPin = 24



                        # Pin Setup:
GPIO.setmode(GPIO.BCM)                  # Broadcom pin-numbering scheme
GPIO.setup(trigPin, GPIO.OUT)           # setup trigger and echo pins
GPIO.setup(echoPin, GPIO.IN)
GPIO.setup(red, GPIO.OUT)               # LED pin set as output
GPIO.setup(left, GPIO.OUT)              # LED pin set as output
GPIO.setup(right, GPIO.OUT)             # LED pin set as output
GPIO.setup(pwmPin, GPIO.OUT)            # PWM pin set as output
pwm = GPIO.PWM(pwmPin, 50)              # Initialize PWM on pwmPin 100Hz frequency
GPIO.setup(butPin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Button pin set as input w/ pull-up
                        # Output pin setup
GPIO.output(red, GPIO.LOW)
GPIO.output(left, GPIO.LOW)
GPIO.output(right, GPIO.LOW)
pwm.start(dc)
#####################################ULTRASONIC################################
def Ultrasonic():
    
    global dist_cm
    delayTime = 0
    GPIO.output(trigPin, 0)
    time.sleep(2E-6)
    # set trigger pin high for 10 micro seconds
    GPIO.output(trigPin, 1)
    time.sleep(10E-6)
    # go back to zero - communication compete to send ping
    GPIO.output(trigPin, 0)
    # now need to wait till echo pin goes high to start the timer
    # this means the ping has been sent
    delayTime = time.time() + .1
    while GPIO.input(echoPin) == 0:
        if (time.time() > delayTime):
            break
        pass
    # start the time - use system time
    echoStartTime = time.time()
    # wait for echo pin to go down to zero
    delayTime = time.time() + .1
    while GPIO.input(echoPin) == 1:
        if (time.time() > delayTime):
            break
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
    # sleep to slow things down
    # time.sleep(delayTime)
                    #Timer Function
def SetTime(duration):
    global t_end

    t_end = time.time() + duration

                        #color detected fn
def CONE_DETECT(color):
    global t_end
    global dc
    global t_turn
    global protocol

    if (color == 'RED'):
        dc = 0                                      #sets duty cycle to 0, stopping the jeep
        protocol = 'red'
    elif (color =='BLUE'):
        print("blue!")
    elif (color == 'GREEN'):
        if(protocol == 'idle'):                     #if its in idle, changes state to green protocol
            SetTime(5)
            protocol = 'green'
    elif (color == 'YELLOW'):
        if(protocol == 'idle'):
            SetTime(5)
            protocol = 'yellow'
    elif (color == 'ORANGE'):
        if(protocol == 'idle'):
            SetTime(5)
            protocol = 'orange'

try:
    while 1:
        Ultrasonic()
        if (dist_cm <50):
            protocol ="red"

        print(round(dist_cm, 1),'cm')
        _, frame = cap.read()
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        height, width, _ = frame.shape
        #finds centerpoint: pixel that will detect HSV value
        cx = int(width/2)
        cy = int(height/2)
        ly = int(height/2)
        lx = int(width/8)
        rx =int((width/8)*7)
        ry = int(height/2)

        #HSV pixel setup
        pixel_center = hsv_frame[cy,cx]
        detector_left = hsv_frame[ly,lx]
        detector_right = hsv_frame[ry,rx]
        hue_value = pixel_center[0]
        saturation_mid = pixel_center[1]
        saturation_left = detector_left[1]
        saturation_right = detector_right[1]

        if (last_dc != dc):
            pwm.ChangeDutyCycle(dc)
            last_dc = dc

        #Saturation Detection (Left,right)
        if saturation_left <50:
            left_sense = "on"
        else:
            left_sense = "off"
        if saturation_right <50:
            right_sense = "on"
        else:
            right_sense = "off"

        #saturation detection (mid)
        if saturation_mid < 50:
            detect = "no cones"
        else:                       #Bright enough to be a color
            detect = "cones"
            if hue_value < 5:
                color = "RED"
            elif hue_value < 25:
                color = "ORANGE"
            elif hue_value <35:
                color = "YELLOW"
            elif hue_value <80:
                color = "GREEN"
            elif hue_value < 150:
                color = "BLUE"
            else:
                color = "RED"
            CONE_DETECT(color)

        #############################################GREEN RIGHT YELLOW LEFT TURN protocol##################################
        if(protocol == "green"):   
            dc = 100
            if(t_end > time.time()):
                GPIO.output(red, GPIO.LOW)
                if(left_sense == "off"):
                    GPIO.output(left, GPIO.LOW)
                    GPIO.output(right, GPIO.HIGH)
                elif(right_sense == "off"):
                    GPIO.output(left, GPIO.HIGH)
                    GPIO.output(right, GPIO.LOW)
                else:
                    GPIO.output(left, GPIO.LOW)
                    GPIO.output(right, GPIO.HIGH)
            else:
                protocol = "idle"

        elif(protocol == "yellow"):
            dc = 100    
            if(t_end > time.time()):
                GPIO.output(red, GPIO.LOW)
                if(left_sense == "off"):
                    GPIO.output(left, GPIO.LOW)
                    GPIO.output(right, GPIO.HIGH)
                elif(right_sense == "off"):
                    GPIO.output(left, GPIO.HIGH)
                    GPIO.output(right, GPIO.LOW)
                else:
                    GPIO.output(left, GPIO.HIGH)
                    GPIO.output(right, GPIO.LOW)
            else:
                protocol = "idle"

        #############################################IDLE SIDEWALK FOLLOWING protocol############################
        elif(protocol=='idle'):
            GPIO.output(red, GPIO.LOW)
            dc = 100
            if(left_sense == "off"):
                GPIO.output(left, GPIO.LOW)
                GPIO.output(right, GPIO.HIGH)
            elif(right_sense == "off"):
                GPIO.output(left, GPIO.HIGH)
                GPIO.output(right, GPIO.LOW)
            else:
                GPIO.output(left, GPIO.LOW)
                GPIO.output(right, GPIO.LOW)

        ############################################ORANGE PROTOCOL######################################
        elif(protocol == "orange"):
            dc = 100
            protocol = 'idle'
        ############################################LATCHING eSTOP protocol###############################
        elif(protocol =='red'):
            pwm.ChangeDutyCycle(0)
            GPIO.output(left, GPIO.LOW)
            GPIO.output(right, GPIO.LOW)
            GPIO.output(red,GPIO.HIGH)
            
            while True:
                if GPIO.input(butPin)==GPIO.LOW:
                    SetTime(.2)
                    debounce = t_end
                    protocol = 'idle'
                    print ("pressed")
                    break
        else:
            protocal ="idle"
        #Draws circles around sensing pixels
        cv2.circle(frame, (cx, cy),5, (255, 255, 255),3)
        cv2.circle(frame, (lx,ly),5, (255, 255, 255),3)
        cv2.circle(frame, (rx,ry),5, (255, 255, 255),3)
        # print(color)
        # print(detect)
        # print(pixel_center)
        # print("left: ",left_sense)
        # print("right: ",right_sense)
        # print("protocol:", protocol)
        # print(t_end-time.time())

        #break on button press/terminate program
        if(debounce < time.time()):
            if GPIO.input(butPin)==GPIO.LOW:

                GPIO.output(red, GPIO.LOW)
                GPIO.output(left, GPIO.LOW)
                GPIO.output(right, GPIO.LOW)
                dc=0
                break
        #show the frame!
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1)
        if key == 27:
            break



except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
    pwm.stop() # stop PWM
    GPIO.cleanup() # cleanup all GPIO
    cap.release()
    cv2.destroyAllWindows()
