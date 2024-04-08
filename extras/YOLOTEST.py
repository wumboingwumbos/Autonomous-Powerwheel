



#### RUNS MODEL ON CAMERA INPUT ####

#from ultralytics import YOLO

#model = YOLO('best.onnx')      ##'yolov8n-seg.pt' should switch to segmented mode##

#results = model(source='0', show=True, stream = True, device = 'cpu', verbose = False, imgsz = 800)

        #model function reads in a bunch of values: source= (image inupt: can be image from file or cameral interface denoted by its position**CHANGES DAILY**)
        #show = (t/f: true shows images on screen)
        #stream = (t/f: true deletes images immediately after use **SLOWER**)
        #device = (*multiple choices*)
        #verbose = (t/f) shows terminal comments on image read in, states which classes are detected

#for result in results:
   # boxes = result.boxes
    #print(boxes)
    #result.show()



############################################################################
####################### RUNS MODEL ON SINGLE IMAGE ##########################
################## ctrl + / to uncomment/comment section of code #############
###############################################################################

# from ultralytics import YOLO

# # Load a pretrained YOLOv8n model
# model = YOLO('yolov8n-seg.pt')

# # Run inference on an image
# results = model('bus.jpg', show=True)  # results list
# # # View results
# # for r in results:
# #     print(r.masks)  # print the Boxes object containing the detection bounding boxes



