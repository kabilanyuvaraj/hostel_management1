import numpy as np
import cv2 as cv

height = 632
width = 414
img = np.zeros([height,width,3],dtype="uint8")

img[:,:]=(255,255,255)

# cv.rectangle(img,(40,300),(width-40,300+32),(0,0,255),thickness=-1)
# cv.circle(img,(40,316),16,(0,0,255),thickness=-1)
# cv.circle(img,(width-40,316),16,(0,0,255),thickness=-1)
# cv.putText(img,f"{'Already Marked'}",(80,326),cv.FONT_HERSHEY_SIMPLEX,1,(0,255,255),4)
cv.imshow("Image",img)
cv.imwrite("4.jpg",img)
cv.waitKey(0)