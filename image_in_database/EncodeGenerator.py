import cv2 as cv
import face_recognition
import pickle
import psycopg2
import io
import numpy as np


def fetch_images_from_database():
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

            # Load the image data from bytes
            img_np = cv.imdecode(np.frombuffer(img_data, np.uint8), cv.IMREAD_COLOR)
            cv.imshow("Image",img_np)
            cv.waitKey(0)
            imgList.append(img_np)
            studentIds.append(name)
            print(name)

        return imgList, studentIds

    except (Exception, psycopg2.Error) as error:
        print('Error fetching images from the database:', error)
        return None, None

    finally:
        # Close the database connection
        if conn:
            conn.close()


# Fetch images and names from the database
imgList, studentIds = fetch_images_from_database()

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

else:
    print("Unable to fetch images from the database.")
