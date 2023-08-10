import numpy as np
import cv2 as cv

width = 1280
height = 720

img = np.zeros([height,width,3],dtype="uint8")
for i in range(height):
    for j in range(width):
        if(j<width//2+100):
            img[i][j] = (255,255,255)
        else:
            img[i][j] = (245,9,169)


w=width//2+100
cv.rectangle(img,(w+40,40),(w+500,height-40),(255,255,255),thickness=-1)
cv.rectangle(img,(40,147),(710,657),(245,9,169),thickness=-1)
cv.rectangle(img,(0,10),(400,70),(245,9,169),thickness=-1)
cv.circle(img,(400,40),30,(245,9,169),thickness=-1)
cv.putText(img,f"{'ATTENDANCE SYSTEM'}",(30,50),cv.FONT_HERSHEY_SIMPLEX,1,(255,255,255),4)
cv.imshow("White",img)
cv.imwrite("back.jpg",img)
cv.waitKey(0)
