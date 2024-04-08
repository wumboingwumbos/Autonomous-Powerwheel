import cv2
import numpy as np

def canny_edge_detector(frame):
    # Convert the image to grayscale (necessary for edge detection)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Applying GaussianBlur to smooth the image. Helps in reducing noise
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Canny Edge Detection
    edges = cv2.Canny(blur, 50, 150)
    
    return edges

def main():
    # Start capturing video
    camera = cv2.VideoCapture("/home/TEAM1PI/Downloads/ExamplePath.mp4")
    # camera.set(cv2.CAP_PROP_FPS, 30.0)
    # camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('m','j','p','g'))
    # camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M','J','P','G'))
    # camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)
    # camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # Adjust the device index as per your setup
    
    while True:
        # Read the frame from the video capture
        ret, frame = camera.read()
        
        # Validate if the frame was successfully captured
        if not ret:
            print("Failed to grab frame")
            break
        
        # Apply Canny Edge Detection
        edges = canny_edge_detector(frame)
        
        # Display the edges in a window
        cv2.imshow('Edges', edges)
        
        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release the VideoCapture object and close display window
    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()