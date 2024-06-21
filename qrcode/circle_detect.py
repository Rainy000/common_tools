import cv2

def circle_detect(image):
    h, w, c = image.shape
    if c == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(image,
                        cv2.HOUGH_GRADIENT, 2, 20, param1 = 80,
                        param2 = 200, minRadius = 10, maxRadius = 200)
    return circles