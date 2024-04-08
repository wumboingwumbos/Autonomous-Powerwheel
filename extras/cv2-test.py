#import libraries
import cv2
from gpiozero import LED, Button
from signal import pause
import numpy as np
import time

#initialize variables
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
red = LED(17)           #STOP
green = LED(23)         #RIGHT 
blue = LED(27)          #LEFT
yellow = LED(23)        #FORWARD

button = Button(2)
left_sense = ""
right_sense = ""
INGNORE=False
t_end = 0
edge_enable= False
direction="none"
                                                #Cone commands fn
def CONE_DETECTED(color):
    global t_end
    global direction
    if (IGNORE==True):
        print("COLOR INTERRUPT")
        yellow.off()
    elif (color == 'RED'):
        red.on()
        blue.off()
        green.off()
        yellow.off()

    elif (color =='BLUE'):
        # red.off()
        # blue.on()
        # green.off()
        # yellow.off()
        print("blue")
    elif (color == 'GREEN'):
        
        if(t_end<time.time()):            
            t_end = time.time() + .2
        direction = "left"
    elif (color == 'YELLOW'):
        if(t_end<time.time()):            
            t_end = time.time() + .2                  #right function
        direction="right"
    elif (color == 'ORANGE'):
        red.on()
        blue.off()
        green.off()
        yellow.on()
    else:
        red.off()
        blue.off()
        green.off()
        yellow.on()
############################################################ generate camera stream ######################################################
while True:
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
    # rx = rxt*3

    #HSV setup
    pixel_center = hsv_frame[cy,cx]
    detector_left = hsv_frame[ly,lx]
    detector_right = hsv_frame[ry,rx]

    hue_value = pixel_center[0]
    saturation_mid = pixel_center[1]
    # print(saturation_mid)
    saturation_left = detector_left[1]
    saturation_right = detector_right[1]

    

    #if saturation is low, no color(cone) is detected: turn LED on
    if saturation_mid < 50:
        detect = "no cones"
        #sidewalk detection
        if saturation_left <50:
            left_sense = "on"
        else:
            left_sense = "off"
            t_end  = time.time() +1
            direction = 'right'
        if saturation_right <50:
            right_sense = "on"
        else:
            right_sense = "off"
            t_end  = time.time() +1
            direction = 'left'
        color = 'no color'
    
    #else the saturation is high enough to detect color: turn LED off
    else:
        detect = "cones"
        if hue_value < 5:
            color = "RED"
        elif hue_value <22:
            color = "ORANGE"
        elif hue_value <33:
            color = "YELLOW"
        elif hue_value <80:
            color = "GREEN"
        elif hue_value < 170:
            color = "BLUE"
        else:
            color = "RED"
    
    ########################################################### # Turns # ###############################################
    if (t_end < time.time()):
        direction="none"
        IGNORE=False
    elif (time.time() < t_end):
        IGNORE=True
        yellow.off()
        if (direction=="left"):
            yellow.off
            print("WAITING-LEFT")
            if(edge_enable==True):
                if (left_sense == "off"):
                                                    #immitate h-bridge right                               ################################################
                    green.off()                                                                         #### Edge enable is so that i can use the turn #######                                         
                    blue.on()                                                                           #### functions for the blue following protocal #######                          
                # elif (left_sense == "on"):                                                            ############# and ignore terrain  ####################
                #                                   #immitate h-bridge left                                ################################################
                #     yellow.off()                     ####Redundant?####
                #     red.on()
            else:
                #TURNLEFT
                green.on()   
                blue.off()
        elif (direction =="right"):
            yellow.off
            print("WAITING-RIGHT")
            if(edge_enable==True):
                if (right_sense == "off"):
                                                    #immitate h-bridge left                               ################################################
                    blue.off()                                                                         #### Edge enable is so that i can use the turn #######                                         
                    green.on()                                                                           #### functions for the blue following protocal #######                          
                # elif (left_sense == "on"):                                                            ############# and ignore terrain  ####################
                #                                   #immitate h-bridge right                                ################################################
                #     yellow.off()                     ####Redundant?####
                #     red.on()
            else:
                #TURNRIGHT
                blue.on()   
                green.off()


    CONE_DETECTED(color)
    print(color)
    print(detect)
    print(pixel_center)
    print("left: ",left_sense)
    print("right: ",right_sense)
    
    # if button.is_pressed:
    #     print('button')
    # else:
    #     print('no button :(')
    # print()

    

    #detects color of the cone based on hue value

    #print color, cone detection, and hsv value of center point. 
    
    

#####ATTEMPT AT PORTION DETECTION######
    # left_poly = np.array([[cx-50,cy-50], [cx-50,cy+50], [cx+50, cy+50], [cx+50, cy-50]], np.int32)
    # left_poly = left_poly.reshape((-1, 1 , 2))
    # # print(left_poly)
    # # for i in left_poly.reshape((-1,2)):         ## ONLY READS IN THE 4 CORNERS NOT ALL THE PIXELS
    # #     pixel_value = hsv_frame[i[1], i[0]]
    # #     saturation = pixel_value[1]

    # #     print(saturation, end='\n', flush=True) ## Flush = True turn off the output print buffer
    # #                                             ## so the values print in real time
    # #                                             ## end = '\n' prints next values on a new line.

    # # print("End")
######################################
    
    #Draws the square
    #cv2.polylines(frame, [left_poly],isClosed=True, color=(255,0,0), thickness=2 )

    #Draws the white circle pixel outlines

    cv2.circle(frame, (cx, cy),5, (255, 255, 255),3)
    cv2.circle(frame, (lx,ly),5, (255, 255, 255),3)
    cv2.circle(frame, (rx,ry),5, (255, 255, 255),3)
    #show video
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1)
    if key == 27:
        break
cap.release()
cv2.destroyAllWindows()  
