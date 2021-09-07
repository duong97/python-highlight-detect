import cv2
import sys
 
# The first argument is the image
image = cv2.imread('../sampleimage.jpg')
 
#convert to grayscale
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
 
#blur it
blurred_image = cv2.GaussianBlur(gray_image, (7,7), 0)
 
cv2.imshow("Orignal Image", image)
canny = cv2.Canny(blurred_image, 80, 100)
cv2.imshow("Canny with low thresholds", canny)
cv2.waitKey(0)
