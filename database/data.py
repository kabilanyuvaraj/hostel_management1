from flask import Flask,request,render_template,send_file,flash,url_for,redirect,jsonify,session,make_response
import psycopg2
import io
from datetime import datetime
from datetime import date
import time
import cv2 as cv
import face_recognition
import pickle
import psycopg2
import os
import numpy as np
import base64
from collections import defaultdict
import pdfkit
import itertools
from flask_session import Session
from flask_socketio import SocketIO,emit
from fpdf import FPDF
import webbrowser
from io import BytesIO
from tkinter import filedialog
import tkinter as tk
import threading

#from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.secret_key = 'attendance'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)
socketio = SocketIO(app)
#csrf_token = CSRFProtect(app)

conn = psycopg2.connect(host='localhost',database='hostel1',user='postgres',password='root')


# @app.errorhandler(404)
# def page_not_found(error):
#     return render_template('404.html'), 404

@socketio.on("complete_card")
def handle_complete_card(data):
    print(data)
    roll = data["roll"]
    query = data["query"]
    emp = data["employeeName"]
    cursor = conn.cursor()
    cursor.execute("update query set response='Completed',employee=%s where roll=%s and query=%s", (emp,roll, query))
    conn.commit()

    # Emit a Socket.IO event to notify the client about the completion
    # socketio.emit("card_completed", {"roll": roll, "query": query}, broadcast=True)

    cursor = conn.cursor()
    cursor.execute("select roll,query,response from query where response='Not Completed'")
    res = cursor.fetchall()
    print(res)
    if res:
        emit("card_completed", {"res": res,"message":""}, broadcast=True)
    else:
        emit("card_completed", {"res":res,"message":'All queries have been completed'}, broadcast=True)


def login_required(func):
    def decorated_function(*args,**kwargs):
        if 'user_id' not in session:
            return redirect('login')
        return func(*args,**kwargs)
    return decorated_function

@app.route('/upload',methods=['POST'])
def upload_file():
    file = request.files['file']
    file_name = request.form.get('name')
    print(file_name)
    file_data = file.read()
    conn = psycopg2.connect(host='localhost',database='hostel1',user='postgres',password='root')
    try:
        cursor = conn.cursor()
        cursor.execute("insert into photos(roll,data) values(%s,%s)",(file_name,file_data))
        conn.commit()
        # current_date = date.today()
        # current_timestamp = datetime.now()
        # cursor.execute("insert into studinfo(name,attendance,date,time) values(%s,%s,%s,%s)",(file_name,0,current_date,current_timestamp))
        # conn.commit()
        current_date=datetime.today()
        current_time = datetime.now().time()
        current_datetime = datetime.combine(current_date, current_time)
        cursor.execute("insert into student_attendance(roll,total_sessions,time,date) values(%s,%s,%s,%s)",(file_name,0,current_datetime,current_date))
        conn.commit()
        # cursor.execute("insert into bill(roll,bill,paid) values(%s,%s,%s)",(file_name,0,'yes'));
        # conn.commit()
        # cursor.execute("insert into bill_paid values(%s)",(file_name,))
        # conn.commit()
        flash('Upload successfully','info')
        return render_template('upload.html',messages='uploaded')
    except (Exception,psycopg2.Error) as error:
        print('Error storing the file:',error)
        return 'Error storing the file'
    finally:
        if conn:
            conn.close()

@app.route("/questions",methods=["POST"])
def questions():
    name=request.form['name']
    roll=request.form['roll']
    print(name,roll)
    return render_template("questions.html",name=name,roll=roll)

@app.route("/sendtoadmin",methods=['POST'])
def send_to_admin():
    query = request.form['query']
    roll=request.form['roll']
    name=request.form['name']
    if len(query)<=50 and len(query)>=10:
        roll=request.form['roll']
        name=request.form['name']
        cursor=conn.cursor()
        cursor.execute("insert into query(roll,name,query) values(%s,%s,%s)",(roll,name,query))
        conn.commit()
        return render_template("questions.html",roll=roll,name=name)
    return render_template("questions.html",roll=roll,name=name,message="Text size of the query is wrong")

@app.route("/viewquery",methods=['POST'])
def view_query():
    roll=request.form['roll']
    name=request.form['name']
    cursor=conn.cursor()
    cursor.execute("select query,response,employee from query where roll=%s",(roll,))
    res=cursor.fetchall()
    print(name,roll)
    print(res)
    if res:
        return render_template("viewquery.html",message='',res=res,roll=roll,name=name)
    else:
        return render_template("viewquery.html",message='NO! queries you have made',res=res,roll=roll,name=name)


@app.route("/viewtaken")
def viewtaken():
    cursor = conn.cursor()
    cursor.execute("select roll,query,response,employee from query")
    res=cursor.fetchall()
    if res:
        return render_template("viewtaken.html",res=res)
    else:
        return render_template("viewtaken.html",message='No queries were taken')

@app.route("/ques",methods=["POST"])
def ques():
    return render_template("questions.html",name=request.form['name'],roll=request.form['roll'])

@app.route("/reactquery")
def reactquery():
    cursor=conn.cursor()
    cursor.execute("select roll,query,response from query where response='Not Completed'")
    res=cursor.fetchall()
    if res:
        return render_template("React.html",res=res,message='')
    return render_template("React.html",res=res,message='All queries have been completed')

@app.route("/searchemp",methods=['POST'])
def searchemp():
    name=request.form['name']
    cursor = conn.cursor()
    cursor.execute("select roll,query,response,employee from query where employee=%s",(name,))
    res=cursor.fetchall()
    if res:
        return render_template("viewtaken.html",res=res)
    else:
        return render_template("viewtaken.html",message='No queries were taken')

@app.route("/search")
def search():
    return render_template("search.html")

@app.route('/searchdata', methods=['GET', 'POST'])
def searchdata():
    if request.method == 'POST':
        rollno = request.form['rollno']
        hostel = request.form['hostel']
        # paid = request.form['paid']
        # if paid.lower() == 'paid':
        #     paid='yes'
        # else:
        #     paid='no'
        print(rollno,hostel)
        if rollno!="" and hostel=="":
            # filter_option = request.form['filter_option']
            cursor=conn.cursor()
            messages=""
            query = "SELECT name,year,hostel FROM student_info WHERE rollno = %s"
            cursor.execute(query, (rollno,))
            results = cursor.fetchall()
            if not results:
                messages="No Data to Shown"
            print(results)
            cursor.execute("select bill from bill where roll=%s",(rollno,))
            res=cursor.fetchone()
            print(res)
            return render_template('search.html', results=results, rollno=rollno,res=res,zip=itertools.zip_longest,message=messages)
        elif hostel!="" and rollno=="":
            cursor=conn.cursor()
            cursor.execute("select name,year,rollno from student_info where hostel=%s",(hostel,))
            results=cursor.fetchall()
            messages=""
            if not results:
                messages="No Data to Shown"
            print(results)
            bill=()
            if results:
                for i in results:
                    cursor.execute("select bill from bill where roll=%s",(i[2],))
                    val=cursor.fetchone()
                    if val:
                        bill+=(val[0],)
                    print(val)
            return render_template('search.html', results=results, rollno=rollno,res=bill,zip=itertools.zip_longest,message=messages)
        elif hostel!="" and rollno!="":
            cursor=conn.cursor()
            cursor.execute("select name,year,rollno from student_info where hostel=%s and rollno=%s",(hostel,rollno))
            results=cursor.fetchall()
            messages=""
            if not results:
                messages="No Data to Shown"
            bill=()
            for i in results:
                cursor.execute("select bill from bill where roll=%s",(i[2],))
                val=cursor.fetchone()
                bill+=(val[0],)
            return render_template('search.html', results=results, rollno=rollno,res=bill,zip=itertools.zip_longest,message=messages)
        else:
            return render_template('search.html')
    return render_template('search.html')

@app.route('/complete',methods=['POST'])
def complete():
    roll=request.form['roll']
    query=request.form['query']
    cursor=conn.cursor()
    cursor.execute("update query set response='Completed' where roll=%s and query=%s",(roll,query))
    conn.commit()
    cursor.execute("select roll,query,response from query where response='Not Completed'")
    res=cursor.fetchall()
    if res:
        return render_template("React.html",res=res,message='')
    return render_template("React.html",res=res,message='All queries have been completed')

@app.route('/payfees',methods=['POST'])
def payfees():
    roll = request.form['roll']
    name=request.form['name']
    cursor = conn.cursor()
    cursor.execute("select bill,room,water,electricity,permission from bill_needs where roll=%s",(roll,))
    res = cursor.fetchone()
    print(res)
    return render_template("payfees.html",res=res,roll=roll,name=name)

@app.route("/pay",methods=['POST'])
def pay():
    roll = request.form['roll']
    name = request.form['name']
    print("name=",roll,name)
    cursor=conn.cursor()
    cursor.execute("select bill,room,water,electricity from bill_needs where roll=%s",(roll,))
    res=cursor.fetchone()
    val = res[0]+res[1]+res[2]+res[3]
    print('val=',res[0],val)
    cursor.execute("update bill_paid set amount_paid=amount_paid+%s where roll=%s",(val,roll))
    conn.commit()
    cursor.execute("update bill_needs set bill=0,room=0,water=0,electricity=0,permission='no' where roll=%s",(roll,))
    conn.commit()
    cursor.execute("update bill set bill=bill-%s where roll=%s",(res[0],roll))
    conn.commit()
    cursor.execute("select year,hostel from student_info where rollno=%s",(roll,))
    val = cursor.fetchone()
    print(val)
    cursor.execute("select data from photos where roll=%s",(roll,))
    photo = cursor.fetchone()[0]
    photo_encoded = base64.b64encode(photo).decode('utf-8')
    print(val,roll,name)
    return render_template("home.html",roll=roll,val=val,name=name,photo=photo_encoded)

@app.route("/updatebill")
def updatebill():
    return render_template("updatebill.html")

@app.route("/upbill",methods=["POST"])
def upbill():
    room = request.form['room']
    water = request.form['water']
    electricity = request.form['electricity']
    print(room,water,electricity)
    cursor = conn.cursor()
    cursor.execute("select roll,bill from bill")
    res = cursor.fetchall()
    print(res)
    for i in res:
        cursor.execute("update bill_needs set bill=%s,room=room+%s,water=water+%s,electricity=electricity+%s,permission='yes' where roll=%s",(i[1],room,water,electricity,i[0]))
        conn.commit()
    return render_template("updatebill.html")

@app.route("/home",methods=['POST'])
def home():
    roll = request.form['roll']
    name = request.form['name']
    print(roll,name)
    cursor=conn.cursor()
    cursor.execute("select year,hostel from student_info where rollno=%s",(roll,))
    val = cursor.fetchone()
    print(val)
    cursor.execute("select data from photos where roll=%s",(roll,))
    photo = cursor.fetchone()[0]
    photo_encoded = base64.b64encode(photo).decode('utf-8')
    print(val,roll,name)
    return render_template("home.html",roll=roll,val=val,name=name,photo=photo_encoded)


# @app.route('/image/<image_id>')
# def get_image(image_id):
#     # Establish a connection to the PostgreSQL database
#     conn = psycopg2.connect(host='localhost', database='image', user='postgres', password='root')

#     try:
#         # Create a cursor to execute SQL queries
#         cursor = conn.cursor()

#         # Retrieve the image data from the database based on the provided image_id
#         cursor.execute("SELECT data FROM photos WHERE name = %s", (image_id,))
#         result = cursor.fetchone()

#         if result:
#             image_data = result[0]
#             return send_file(io.BytesIO(image_data), mimetype='image/jpeg')  # Adjust mimetype if necessary

#         return 'Image not found.'
#     except (Exception, psycopg2.Error) as error:
#         print('Error retrieving the image:', error)
#         return 'Error retrieving the image.'
#     finally:
#         # Close the database connection
#         if conn:
#             conn.close()

# @app.route("/")
# def home():
#     return render_template('image.html')

@app.route("/contact")
def contact():
    return render_template("contactus.html")


class FeeReceipt(FPDF):
    def header(self):
        # Add header information
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Hostel Fee Receipt", 0, 1, "C")
        self.cell(0, 10, "University Hostels", 0, 1, "C")
        self.cell(0, 10, "Contact: hostel@example.com", 0, 1, "C")
        self.cell(0, 10, "", ln=True)  # Add an empty line

    def footer(self):
    # Add footer information
        page_width = self.w
        page_height = self.h
        footer_height = 15  # You can adjust this value as needed
        self.set_y(page_height - footer_height)
        self.set_font("Arial", size=8)
        self.cell(page_width, 5, "Thank you for choosing our hostel!", 0, 0, "C")
        self.set_y(page_height - footer_height + 5)
        self.cell(page_width, 5, f"Receipt generated on: {self.get_current_date()}", 0, 0, "C")

    def get_current_date(self):
        # Helper method to get the current date
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def add_receipt_content(self, student_name, roll_number, mess_fees, room_rent, water_charges, electricity_bill):
        # Set font
        self.set_font("Arial", size=12)

        # Add student information
        self.cell(0, 10, f"Student Name: {student_name}", ln=True, align='L')
        self.cell(0, 10, f"Roll Number: {roll_number}", ln=True, align='L')
        # self.cell(0, 10, f"Hostel Name: {hostel_name}", ln=True, align='L')
        self.cell(0, 10, "", ln=True)  # Add an empty line

        # Add fee details
        self.cell(0, 10, "Fee Details", ln=True, align='L')
        self.cell(0, 10, f"Mess Fees: {mess_fees}", ln=True, align='C')
        self.cell(0, 10, f"Room Rent: {room_rent}", ln=True, align='C')
        self.cell(0, 10, f"Water Charges: {water_charges}", ln=True, align='C')
        self.cell(0, 10, f"Electricity Bill: {electricity_bill}", ln=True, align='C')
        self.cell(0, 10, "", ln=True)  # Add an empty line

        # Calculate the total fee
        total_fee = int(mess_fees) + int(room_rent) + int(water_charges) + int(electricity_bill)
        self.cell(0, 10, f"Total Fee: {total_fee}", ln=True, align='L')


def save_receipt(receipt):
    root = tk.Tk()
    root.withdraw()
    receipt_file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
    if not receipt_file:
        print("File save canceled.")
        return
    receipt.output(receipt_file)
    webbrowser.open(receipt_file)
    print(f"Fee receipt generated: {receipt_file}")

@app.route("/generatepdf",methods=["POST"])
def generatepdf():
    mess = request.form['mess']
    room = request.form['room']
    water = request.form['water']
    electricity = request.form['electricity']
    name = request.form['name']
    roll = request.form['roll']
    print(mess,room,water,electricity,name,roll)

    receipt = FeeReceipt()
    receipt.add_page()
    receipt.add_receipt_content(name, roll, mess, room, water, electricity)
    # root = tk.Tk()
    # root.withdraw()
    # receipt_file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
    # if not receipt_file:
    #     print("File save canceled.")
    #     return
    # receipt.output(receipt_file)
    # print(f"Fee receipt generated: {receipt_file}")

    file_dialog_thread = threading.Thread(target=save_receipt,args=(receipt,))
    file_dialog_thread.start()

    cursor = conn.cursor()
    cursor.execute("select bill,room,water,electricity,permission from bill_needs where roll=%s",(roll,))
    res = cursor.fetchone()
    print(res)
    return render_template("payfees.html",res=res,roll=roll,name=name)

    # return redirect(url_for("logout"))


@app.route("/login")
def login():
    message=""
    if request.args.get("message"):
        message = request.args.get("message")
    print(message)
    return render_template("login.html",message=message)

@app.route("/upload")
def upload():
    return render_template("upload.html")

@app.route("/update",methods=['POST'])
def update():
    file = request.files['file']
    file_name = request.form.get('name')
    print(file_name)
    file_data = file.read()
    conn = psycopg2.connect(host='localhost',database='hostel1',user='postgres',password='root')
    try:
        cursor = conn.cursor()
        cursor.execute("select * from student_info where rollno=%s",(file_name,))
        ispresent = cursor.fetchone()
        if ispresent:
            cursor.execute("update photos set data=%s where roll=%s",(file_data,file_name))
            conn.commit()
            flash('Updated successfully','info')
            return render_template('adminupdate.html',messages='uploaded')
        else:
            flash('Not Updated successfully','info')
            return render_template('adminupdate.html',messages='uploaded')
    except (Exception,psycopg2.Error) as error:
        print('Error storing the file:',error)
        return 'Error storing the file'
    finally:
        if conn:
            conn.close()

@app.route("/adminupdate")
def adminupdate():
    return render_template("adminupdate.html")

@app.route("/login",methods=["POST"])
def log():
    user = request.form.get('user')
    password = request.form.get('password')
    if ((user=='raja') and (password=='123456')):
        return render_template('adminoptions.html')
    conn = psycopg2.connect(host='localhost',database='hostel1',user='postgres',password='root')
    try:
        cursor = conn.cursor()
        print(user,password)
        cursor.execute("select name,roll from admin where password=%s",(password,))
        results = cursor.fetchone()
        print(results)
        res={}
        if "user_id" in session:
            return redirect(url_for('logout',message="you have been logged out"))
        if results:
            session['user_id'] = results[1]
            print(session['user_id'])
            res['name']=results[0]
            res['roll']=results[1]
            if user!=res['name']:
                return render_template("login.html",message="The username or password should be incorrect")
            print(res['name'])
        elif not results:
            return render_template("login.html",message="The username or password should be incorrect")
        cursor.execute("select year,hostel from student_info where rollno=%s",(res['roll'],))
        val = cursor.fetchone()
        cursor.execute("select data from photos where roll=%s",(res['roll'],))
        photo = cursor.fetchone()[0]
        photo_encoded = base64.b64encode(photo).decode('utf-8')
        return render_template('home.html',name=res['name'],roll=res['roll'],val=val,photo=photo_encoded)
    except Exception as error:
        print('Cannot login',error)
        return render_template('login.html')

@app.route("/register",methods=["GET"])
def reg():
    print("HI")
    return render_template("register.html")

@app.route('/loader')
def loader():
    return render_template('loader.html')

@app.route('/logout')
def logout():
    message=""
    if request.args.get("message"):
        message = request.args.get("message")
    session.pop("user_id",None)
    session.clear()
    return redirect(url_for('login',message=message))

@app.route("/register",methods=["POST"])
def register():
    pas = request.form['password']
    if len(pas)<=7:
        return render_template("register.html",message="Password should be atleast 8 characters")
    rollno = request.form['rollno']
    print(pas,rollno)
    conn = psycopg2.connect(host='localhost',database='hostel1',user='postgres',password='root')
    cursor = conn.cursor()
    cursor.execute("select * from admin where password=%s or roll=%s",(pas,rollno))
    pick = cursor.fetchone()
    if pick:
        return render_template("register.html",message="Password or rollno was taken")
    cap = cv.VideoCapture(0)
    cap.set(3,640)
    cap.set(4,480) 

    print("Loading Encoded File...")
    file = open("EncodeFile.p","rb")
    encodeListKnownWithIds = pickle.load(file)
    file.close()
    encodeListKnown,studentIds = encodeListKnownWithIds
    print(studentIds)
    print("Encoded File loaded")

    while True:
        success,img = cap.read()

        imgS = cv.resize(img,(0,0),None,0.25,0.25)
        imgS = cv.cvtColor(imgS,cv.COLOR_BGR2RGB)

        faceCurFrame = face_recognition.face_locations(imgS)
        encodeCurFrame = face_recognition.face_encodings(imgS,faceCurFrame)
        counter=0

        if faceCurFrame:
            for encodeFace, faceLoc in zip(encodeCurFrame,faceCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
                #print(matches,faceDis)
                matchIndex = np.argmin(faceDis)
                counter+=1
                if matches[matchIndex]:
                    #print("Known Face detected")
                    #print(studentIds[matchIndex])
                    y1,x2,y2,x1 = faceLoc
                    y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4
                    bbox = 55+x1,162+y1,x2-x1,y2-y1
                    # imgBackground = cvzone.cornerRect(imgBackground,bbox,rt=0,color=(245,9,169))
                    img = cv.rectangle(img,bbox,(245,9,169),thickness=6)
                    id = studentIds[matchIndex]
                    cap.release()
                    name = request.form['name']
                    password = request.form['password']
                    year = request.form['year']
                    roll = request.form['rollno']
                    hostel = request.form['hostelname']
                    # conn = conn = psycopg2.connect(host='localhost',database='hostel1',user='postgres',password='root')
                    cursor = conn.cursor()
                    cursor.execute("select * from student_attendance where roll=%s",(roll,))
                    result = cursor.fetchone()
                    cursor.execute("select * from student_info where rollno=%s",(roll,))
                    res = cursor.fetchone()

                    if result and not res:
                        cursor.execute("insert into student_info values(%s,%s,%s,%s)",(name,year,roll,hostel))
                        conn.commit()
                        cursor.execute("insert into admin values(%s,%s,%s)",(name,password,roll))
                        conn.commit()
                        cursor.execute("insert into bill(roll,bill,paid) values(%s,%s,%s)",(roll,0,'yes'))
                        conn.commit()
                        cursor.execute("insert into bill_paid(roll) values(%s)",(roll,))
                        conn.commit()
                        cursor.execute("insert into bill_needs(roll) values(%s)",(roll,))
                        conn.commit()
                    if not result:
                        return render_template("register.html",message="Your Face is not present")
                    conn.close()
                    cursor.close()
                    # return render_template('register.html')
                    return redirect(url_for('login'))
                if counter==300:
                    return render_template("register.html",message="Not registered")
                    
            # cv.imshow("Face Attendance",imgBackground)
            # cv.waitKey(1)
        

# @app.route("/home")
# def start():
#     return render_template('upload.html')


@app.route("/encode",methods=["POST"])
def encode():
    print("encode")
    # Configure PostgreSQL connection parameters
    db_host = 'localhost'
    db_name = 'hostel1'
    db_user = 'postgres'
    db_password = 'root'

    # Establish a connection to the PostgreSQL database
    conn = psycopg2.connect(host=db_host, database=db_name, user=db_user, password=db_password)

    try:
        # Create a cursor to execute SQL queries
        cursor = conn.cursor()

        # Fetch images and names from the database
        cursor.execute("SELECT data, roll FROM photos")
        results = cursor.fetchall()

        imgList = []
        studentIds = []

        for result in results:
            img_data = result[0]
            name = result[1]
            print(name)
            # Load the image data from bytes
            img_np = cv.imdecode(np.frombuffer(img_data, np.uint8), cv.IMREAD_COLOR)
            cv.imshow("Image",img_np)
            cv.waitKey(0)
            imgList.append(img_np)
            studentIds.append(name)
        print(studentIds)
        if imgList is not None and studentIds is not None:
            def findEncodings(imagesList):
                encodeList = []
                for img in imagesList:
                    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
                    encode = face_recognition.face_encodings(img)[0]
                    encodeList.append(encode)

                return encodeList

            print("Encoding started")
            encodeListKnown = findEncodings(imgList)
            encodeListKnownWithIds = [encodeListKnown, studentIds]
            print("Encoding Completed")

            file = open("EncodeFile.p", "wb")
            pickle.dump(encodeListKnownWithIds, file)
            file.close()
            print("File Saved")
            conn.close()
            cursor.close()
            return render_template("login.html")
        else:
            print("Images cannot be loaded from database")
            return render_template("upload.html")
        

    except (Exception, psycopg2.Error) as error:
        print('Error fetching images from the database:', error)
        return render_template("upload.html")

@app.route("/hom",methods=["POST"])
def hom():
    name=request.form['name']
    roll=request.form['roll']
    print(name,roll)
    cursor = conn.cursor()
    cursor.execute("select year,hostel from student_info where rollno=%s",(roll,))
    val = cursor.fetchone()
    cursor.execute("select data from photos where roll=%s",(roll,))
    photo = cursor.fetchone()[0]
    photo_encoded = base64.b64encode(photo).decode('utf-8')
    return render_template('home.html',name=name,roll=roll,val=val,photo=photo_encoded)

@app.route("/mess")
@login_required
def messfees():
    return render_template("login.html")

@app.route('/mess',methods=['POST'])
def mess():
    name=request.form['name']
    roll=request.form['roll']
    conn = psycopg2.connect(host="localhost", database="hostel1", user="postgres", password="root")
    cursor = conn.cursor()
    cursor.execute("select date,total_sessions,fees,sessions from student_attendance where roll=%s",(roll,))
    results = cursor.fetchall()
    total_fees = defaultdict(int)
    for i in results:
        date=i[0]
        month = date.strftime('%B %Y')
        fees = i[2]
        total_fees[month]+=fees
    return render_template("messfees.html",results=results,roll=roll,name=name,total_fees=total_fees)

if __name__=='__main__':
    # app.run(debug=True)
    socketio.run(app,debug=True)