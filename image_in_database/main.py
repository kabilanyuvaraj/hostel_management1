import cv2 as cv
import pickle
import face_recognition
import numpy as np
import cvzone
import os
from datetime import datetime
import psycopg2
from datetime import date,timedelta
import time
import pyttsx3

engine = pyttsx3.init()

connection = psycopg2.connect(
    host="localhost",
    database="hostel1",
    user="postgres",
    password="root"
)

cursor = connection.cursor()



cap = cv.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

imgBackground = cv.imread('back.jpg')


#Resources
folderModePath = "Resources"
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv.imread(os.path.join(folderModePath,path)))


# load the encoding file
print("Loading Encoded File...")
file = open("EncodeFile.p","rb")
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown,studentIds = encodeListKnownWithIds
print(studentIds)
print("Encoded File loaded")

modeType = 0
counter = 0
id = -1
imgStudent=[]
studentInfo = {}

engine_count=0

while True:
    success,img = cap.read()

    if not success:
        print("Error: Unable to read a frame.")
        continue

    imgS = cv.resize(img,(0,0),None,0.25,0.25)
    imgS = cv.cvtColor(imgS,cv.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS,faceCurFrame)

    imgBackground[162:162+480,55:55+640] = img
    imgBackground[44:44+632,808:808+414]=imgModeList[modeType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame,faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
            #print(matches,faceDis)
            matchIndex = np.argmin(faceDis)
            if matches[matchIndex]:
                #print("Known Face detected")
                #print(studentIds[matchIndex])
                y1,x2,y2,x1 = faceLoc
                y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4
                bbox = 55+x1,162+y1,x2-x1,y2-y1
                # imgBackground = cvzone.cornerRect(imgBackground,bbox,rt=0,color=(245,9,169))
                imgBackground = cv.rectangle(imgBackground,bbox,(245,9,169),thickness=6)
                id = studentIds[matchIndex]
                engine_count=0
                if counter==0:
                    counter=1
                    modeType=1

        if counter!=0:
            if counter==1:
                if id==-1:
                    counter=0
                    modeType=0
                    cv.imshow("Face Attendance",imgBackground)
                    cv.waitKey(1)
                    continue
                # Get data
                current_date = date.today()
                print("id=",id)
                # sql="SELECT * FROM student_attendance where roll=%s and date=%s"
                # cursor.execute(sql,(id,current_date))
                # row = cursor.fetchone()
                # if row:
                #     studentInfo["total_sessions"] = row[0]
                #     studentInfo["time"] = row[2]
                #     studentInfo["roll"]=row[1]
                #     studentInfo["date"]=row[3]
                #     print(studentInfo)
                
                # current_date = date.today()
                # current_timestamp = datetime.now()
                # time_dif = current_timestamp - studentInfo["time"]
                # time_diff = time_dif.total_seconds()
                # print("Time difference:",time_diff)


                #secondsElapsed = (datetime.now() - datetime.strptime('2023-07-06 16:29:23.43', '%Y-%m-%d %H:%M:%S.%f')).total_seconds()
                # if studentInfo["date"]!=current_date:
                # if studentInfo["date"]<=current_date and time_diff>60:
                #     # print(type(studentInfo["date"]),type(current_date))
                #     # print("HI")
                #     # print("1232142")
                #     update_sql = "UPDATE studinfo SET attendance=%s,date=%s,time=%s WHERE name=%s"
                #     cursor.execute(update_sql,(studentInfo["total_attendance"]+1,current_date,current_timestamp,studentInfo["name"]))
                #     connection.commit()
                #     # studentInfo["total_attendance"]+=1

                current_time = datetime.now().time()

                # Define the time ranges for morning, afternoon, and night
                morning_start = datetime.strptime("07:00:00", "%H:%M:%S").time()
                morning_end = datetime.strptime("8:59:59", "%H:%M:%S").time()
                afternoon_start = datetime.strptime("12:00:00", "%H:%M:%S").time()
                afternoon_end = datetime.strptime("13:59:59", "%H:%M:%S").time()
                night_start = datetime.strptime("19:00:00", "%H:%M:%S").time()
                night_end = datetime.strptime("21:59:59", "%H:%M:%S").time()

                cursor.execute("select * from student_attendance where roll=%s and date=%s and total_sessions>0",(id,current_date))
                ispresent = cursor.fetchone()
                print("ispresent=",ispresent)
                current_datetime = datetime.combine(current_date, current_time)
                if not ispresent:
                    if morning_start <=current_time<=morning_end:
                        cursor.execute("insert into student_attendance(date,total_Sessions,roll,time,sessions,fees,taken) values(%s,%s,%s,%s,%s,%s,%s)",(current_date,1,id,current_datetime,1,100,'Taken'))
                        connection.commit()
                        cursor.execute("update bill set bill=bill+%s,paid='no' where roll=%s",(100,id))
                        connection.commit()
                        print("Morning")
                    elif afternoon_start <=current_time<=afternoon_end:
                        cursor.execute("insert into student_attendance(date,total_Sessions,roll,time,sessions,fees,taken) values(%s,%s,%s,%s,%s,%s,%s)",(current_date,1,id,current_datetime,2,100,'Taken'))
                        connection.commit()
                        cursor.execute("update bill set bill=bill+%s,paid='no' where roll=%s",(100,id))
                        connection.commit()
                        print("Afternoon")
                    elif night_start<=current_time<=night_end:
                        cursor.execute("insert into student_attendance(date,total_Sessions,roll,time,sessions,fees,taken) values(%s,%s,%s,%s,%s,%s,%s)",(current_date,1,id,current_datetime,3,100,'Taken'))
                        connection.commit()
                        cursor.execute("update bill set bill=bill+%s,paid='no' where roll=%s",(100,id))
                        connection.commit()
                        print("Night")
                    else:
                        if engine_count==0:
                            engine.setProperty('rate',150)
                            engine.setProperty('volume',1.0)
                            engine.say("you cannot eat during this period")
                            engine.runAndWait()
                            engine_count=1
                cursor.execute("select time from student_attendance where roll=%s and date=%s",(id,current_date))
                time_d = cursor.fetchone()
                print("time_d",time_d)
                # time_di = current_time - time_d[0].time()
                # print(time_di)
                dt_current_time = datetime.now().time()
                dt_time_d = time_d[0].time()
                print("val=",dt_current_time,dt_time_d)
                if dt_current_time.hour >=dt_time_d.hour+3:
                    if morning_start <=current_time<=morning_end:
                        cursor.execute("update student_attendance set total_sessions=total_sessions+1 where date=%s and roll=%s",(current_date,id))
                        connection.commit()
                        print("Morning")
                    elif afternoon_start <=current_time<=afternoon_end:
                        cursor.execute("select sessions from student_attendance where date=%s and roll=%s",(current_date,id))
                        res=cursor.fetchone()
                        if res:
                            if res[0]==1:
                                cursor.execute("update student_attendance set total_sessions=total_sessions+1,sessions=4,fees=%s,taken='Taken',time=%s where date=%s and roll=%s",(200,current_datetime,current_date,id,))
                                connection.commit()
                                cursor.execute("update bill set bill=bill+%s,paid='no' where roll=%s",(100,id))
                                connection.commit()
                                print("Afternoon")
                    elif night_start<=current_time<=night_end:
                        cursor.execute("select sessions from student_attendance where date=%s and roll=%s",(current_date,id))
                        res=cursor.fetchone()
                        if res:
                            if res[0]==2:
                                cursor.execute("update student_attendance set total_sessions=total_sessions+1,sessions=5,fees=%s,taken='Taken',time=%s where date=%s and roll=%s",(200,current_datetime,current_date,id))
                                connection.commit()
                                cursor.execute("update bill set bill=bill+%s,paid='no' where roll=%s",(100,id))
                                connection.commit()
                                print("Night")
                            elif res[0]==4:
                                cursor.execute("update student_attendance set total_sessions=total_sessions+1,sessions=6,fees=%s,taken='Taken',time=%s where date=%s and roll=%s",(300,current_datetime,current_date,id))
                                connection.commit()
                                cursor.execute("update bill set bill=bill+%s,paid='no' where roll=%s",(100,id))
                                connection.commit()
                                print("Night")
                    else:
                        modeType=3
                        counter=0
                        imgBackground[44:44+632,808:808+414]=imgModeList[modeType]
                        cursor.execute("select taken from student_attendance where roll=%s and date=%s",(id,current_date))
                        istaken = cursor.fetchone()
                        print("is",istaken)
                # else:
                #     if engine_count==0:
                #             engine.setProperty('rate',150)
                #             engine.setProperty('volume',1.0)
                #             engine.say("you cannot eat during this period")
                #             engine.runAndWait()
                #             engine_count=1
                #Get Image
                #imgStudent=cv.imread("Images/Temp.jpg")
            if modeType!=3:
                if 10<counter<=60:
                    modeType=2

                imgBackground[44:44+632,808:808+414]=imgModeList[modeType]

                if counter<=10:
                    # cv.putText(imgBackground,f'Attendance: {studentInfo["total_sessions"]}',(861,165),cv.FONT_HERSHEY_COMPLEX,1,(255,255,0),3)
                    
                    (w,h),_ = cv.getTextSize(id,cv.FONT_HERSHEY_COMPLEX,1,3)
                    offset = (414-w)//2
                    cv.putText(imgBackground,str(id),(808+offset,405),cv.FONT_HERSHEY_COMPLEX,1,(255,255,0),3)
                    cursor.execute("select taken from student_attendance where roll=%s and date=%s",(id,current_date))
                    istaken = cursor.fetchone()
                    print("istaken",istaken)
                    if istaken[0]:
                        engine.setProperty('rate',150)
                        engine.setProperty('volume',1.0)
                        engine.say(istaken[0])
                        engine.runAndWait()
                        print("Hi")
                        cursor.execute("update student_attendance set taken='Already Taken' where roll=%s and date=%s",(id,current_date))
                        connection.commit()
                    #imgBackground[175:175+216,909:909+216]=imgStudent

                counter+=1

                if counter>=60:
                    counter=0
                    modeType=0
                    #studentInfo=[]
                    imgStudent=[]
                    id=-1
                    imgBackground[44:44+632,808:808+414]=imgModeList[modeType]

    else:
        modeType=0
        counter=0
        id=-1
        



    cv.imshow("Face Attendance",imgBackground)

    cv.waitKey(1)
cursor.close()
connection.close()