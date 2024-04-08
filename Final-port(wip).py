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
END = False            #True if red cone detected, ends program
STATE = 0
t_end = 0              #timer variable
t_turn = 0             #timer variable
color = ''
protocal = "none"
wheelpos = "straight"
debounce = 0
# Pin Setup:
GPIO.setmode(GPIO.BCM)                  # Broadcom pin-numbering scheme
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


def SetTime(duration):
    global t_end

    t_end = time.time() + duration

#color detected fn
def CONE_DETECT(color):
    global t_end
    global direction
    global dc
    global END
    global t_turn
    global protocal
    turn_time = .5              #time to turn wheels\
    turn_duration = 5           #time to follow side

    if (color == 'RED'):
        dc = 0                                      #sets duty cycle to 0, stopping the jeep
        protocal = 'red'
    elif (color =='BLUE'):
        print("blue!")

    elif (color == 'GREEN'):
        t_turn = time.time() + turn_time            #turns wheels for .5 
        t_end = time.time() + turn_duration         #sets follow duration for 5 seconds
        direction = "right"                         #sets follow side to right
        dc = 50                                     #sets speed to half
        if(protocal == 'idle'):                     #if its in idle, changes state to green protocal
            protocal = 'green'
    elif (color == 'YELLOW'):
        t_turn = time.time() + turn_time            #turns wheels for .5 
        t_end = time.time() + turn_duration         #sets follow duration for 5 seconds
        direction = "left"                          #sets follow side to left
        dc = 50                                     #sets speed to half
        if(protocal == 'idle'):
            protocal = 'yellow'
    elif (color == 'ORANGE'):
        dc = 50                                     #sets speed to half
        t_end = time.time() + turn_duration
                        #################
                        ###YOLO ENABLE###
                        #################
        if(protocal == 'idle'):
            protocal = 'orange'

try:
    while 1:
        _, frame = cap.read()
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        height, width, _ = frame.shape
        #finds centerpoint: pixel that will detect HSV value
        cx = int(width/2)
        cy = int(height/2)
        ly = int(height/2)
        lx = int(width/4)
        rx =int((width/4)*3)
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
            dc = 100
            protocal = "idle"
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

        # if (t_end > time.time()):             #if grenn left on if yellow right on (simple test) time didnt work
        #     if (t_turn > time.time()):
        #         if (direction == "left"):
        #             GPIO.output(left, GPIO.HIGH)
        #             GPIO.output(right, GPIO.LOW)
        #         elif (direction == 'right'):
        #             GPIO.output(right, GPIO.HIGH)
        #             GPIO.output(left, GPIO.LOW)

        #############################################IDLE SIDEWALK FOLLOWING PROTOCAL############################
        if(protocal=='idle'):
            GPIO.output(red, GPIO.LOW)
            if(left_sense == "off"):
                GPIO.output(left, GPIO.LOW)
                GPIO.output(right, GPIO.HIGH)
            elif(right_sense == "off"):
                GPIO.output(left, GPIO.HIGH)
                GPIO.output(right, GPIO.LOW)
            else:
                GPIO.output(left, GPIO.LOW)
                GPIO.output(right, GPIO.LOW)

        ############################################LATCHING eSTOP PROTOCAL###############################
        if(protocal =='red'):
            pwm.ChangeDutyCycle(0)
            GPIO.output(left, GPIO.LOW)
            GPIO.output(right, GPIO.LOW)
            GPIO.output(red,GPIO.HIGH)
            
            while True:
                if GPIO.input(butPin)==GPIO.LOW:
                    SetTime(.2)
                    debounce = t_end
                    protocal == 'idle'
                    print ("pressed")
                    break

        #Draws circles around sensing pixels
        cv2.circle(frame, (cx, cy),5, (255, 255, 255),3)
        cv2.circle(frame, (lx,ly),5, (255, 255, 255),3)
        cv2.circle(frame, (rx,ry),5, (255, 255, 255),3)
        print(color)
        print(detect)
        print(pixel_center)
        print("left: ",left_sense)
        print("right: ",right_sense)
        print("Protocal:", protocal)


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
