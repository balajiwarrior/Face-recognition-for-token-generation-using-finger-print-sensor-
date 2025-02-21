import tkinter as tk
from tkinter import *
import cv2
import csv
import os
import numpy as np
from PIL import Image, ImageTk
import pandas as pd
import datetime
from tkinter import messagebox
from PIL import Image, ImageDraw
import time
from PIL import Image, ImageDraw, ImageFont
import datetime



# Window is our Main frame of system
window = tk.Tk()
window.title("FAMS-Face Recognition Based Attendance Management System")

window.geometry('1280x720')
window.configure(background='grey80')

# GUI for manually fill attendance




# Simulating a database
request_list = []  # Stores token requests as tuples: (student_name, food_type, timestamp)

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"
# Function to recognize face and request token
MODEL_PATH = r'D:\Face-Recognition-Attendance-System-main\TrainingImageLabel\Trainner.yml'



# Admin approval process
from datetime import datetime  # Ensure this is at the top of your script

def generate_token(user_name, food_type):
    try:
        # Create token image
        token_image = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(token_image)

        # Use a specific font or fallback to default
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except IOError:
            font = ImageFont.load_default()

        # Add details to the token
        now = datetime.now()  # Get current date and time
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        draw.text((10, 10), f"Food Token", fill='black', font=font)
        draw.text((10, 50), f"Name: {user_name}", fill='black', font=font)
        draw.text((10, 100), f"Food Type: {food_type}", fill='black', font=font)
        draw.text((10, 150), f"Date & Time: {date_time}", fill='black', font=font)

        # Save token image
        token_path = f"{user_name}_token.png"
        token_image.save(token_path)
        messagebox.showinfo("Token Generated", f"Token saved as {token_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate token: {e}")




def admin_approve_tokens():
    """Admin approval window for pending requests."""
    if not request_list:
        messagebox.showinfo("No Requests", "No pending token requests.")
        return

    approval_window = tk.Toplevel()
    approval_window.title("Approve Token Requests")
    approval_window.geometry("400x400")

    tk.Label(approval_window, text="Pending Requests:", font=('times', 14, 'bold')).pack(pady=10)

    # Listbox to display requests
    listbox = Listbox(approval_window, width=50, height=15)
    listbox.pack(pady=10)

    # Populate listbox with requests
    for i, req in enumerate(request_list):
        if req["status"] == "Pending":
            listbox.insert(i, f"{req['name']} ({req['food_type']}) - {req['status']}")

    # Approve or reject selected request
    def handle_request(approve=True):
        selected = listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "No request selected!")
            return

        index = selected[0]
        request = request_list[index]

        if approve:
            request["status"] = "Approved"
            # Pass both name and food_type to generate_token
            generate_token(request["name"], request["food_type"])
            listbox.delete(index)
            messagebox.showinfo("Approved", f"Token approved for {request['name']} ({request['food_type']}).")
        else:
            request["status"] = "Rejected"
            listbox.delete(index)
            messagebox.showinfo("Rejected", f"Token rejected for {request['name']}.")

    # Buttons for approval and rejection
    tk.Button(approval_window, text="Approve", command=lambda: handle_request(True), bg="green", fg="white").pack(side="left", padx=10, pady=10)
    tk.Button(approval_window, text="Reject", command=lambda: handle_request(False), bg="red", fg="white").pack(side="right", padx=10, pady=10)


# Admin login function
def admin_login():
    login_window = tk.Toplevel()
    login_window.title("Admin Login")
    login_window.geometry("300x200")

    tk.Label(login_window, text="Username:").pack(pady=5)
    username_entry = tk.Entry(login_window)
    username_entry.pack(pady=5)

    tk.Label(login_window, text="Password:").pack(pady=5)
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack(pady=5)

    def validate_login():
        username = username_entry.get()
        password = password_entry.get()

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            messagebox.showinfo("Login Successful", "Welcome Admin!")
            login_window.destroy()
            admin_approve_tokens()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password!")

    tk.Button(login_window, text="Login", command=validate_login).pack(pady=20)

# Mock function to simulate adding a request
def mock_add_request(name, food_type):
    request_list.append({"name": name, "food_type": food_type, "status": "Pending"})
    messagebox.showinfo("Request Added", f"Request added for {name} ({food_type}).")

# Main Tkinter window
root = tk.Tk()
root.title("Food Token System")
root.geometry("500x500")

def face_verification_and_token():
    global request_list

    # Initialize the recognizer and check model file existence
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    if not os.path.exists(MODEL_PATH):
        messagebox.showerror("Error", f"Model file not found at: {MODEL_PATH}")
        return
    recognizer.read(MODEL_PATH)

    # Initialize the camera
    camera = cv2.VideoCapture(0)  # 0 for the default camera
    if not camera.isOpened():
        messagebox.showerror("Error", "Unable to access the camera.")
        return

    messagebox.showinfo("Info", "Camera is on. Please position yourself in front of the camera.")
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    face_verified = False
    user_name = ""
    
    while True:
        ret, frame = camera.read()
        if not ret:
            messagebox.showerror("Error", "Camera error occurred!")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            id, confidence = recognizer.predict(gray[y:y+h, x:x+w])

            if confidence < 50:  # Confidence threshold for recognition
                user_name = f"User_{id}"  # Replace with actual name mapping logic
                face_verified = True
                break

        cv2.imshow('Face Verification', frame)

        if face_verified:
            messagebox.showinfo("Success", f"Face verification successful! Welcome {user_name}.")
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Exit on 'q'
            break

    camera.release()
    cv2.destroyAllWindows()

    if face_verified:
        # Use the custom dialog to select food type
        food_type = select_food_type()
        if food_type:
            request_list.append({"name": user_name, "food_type": food_type, "status": "Pending"})
            messagebox.showinfo("Request Added", f"Your request for a {food_type} food token has been added. Waiting for admin approval.")
        else:
            messagebox.showerror("Error", "Food type selection was cancelled.")

def select_food_type():
    """Custom dialog to select food type."""
    food_type_window = tk.Toplevel()
    food_type_window.title("Select Food Type")
    food_type_window.geometry("300x150")

    selected_food_type = tk.StringVar(value="")

    tk.Label(food_type_window, text="Choose your food type:", font=("times", 14)).pack(pady=10)

    def set_food_type(food_type):
        selected_food_type.set(food_type)
        food_type_window.destroy()

    # Buttons for food type selection
    tk.Button(food_type_window, text="Veg", width=10, command=lambda: set_food_type("Veg")).pack(side="left", padx=20, pady=20)
    tk.Button(food_type_window, text="Non-Veg", width=10, command=lambda: set_food_type("Non-Veg")).pack(side="right", padx=20, pady=20)

    # Wait for the window to close
    food_type_window.wait_window()
    return selected_food_type.get()


    def submit_selection():
        if selected_food.get() not in ["Veg", "Non-Veg"]:
            messagebox.showerror("Error", "Please select a valid food type.")
            return
        food_window.destroy()

    tk.Label(food_window, text="Select Food Type:", font=('times', 14, 'bold')).pack(pady=10)
    tk.Radiobutton(food_window, text="Veg", variable=selected_food, value="Veg", font=('times', 12)).pack(pady=5)
    tk.Radiobutton(food_window, text="Non-Veg", variable=selected_food, value="Non-Veg", font=('times', 12)).pack(pady=5)
    tk.Button(food_window, text="Submit", command=submit_selection, bg="green", fg="white", font=('times', 12)).pack(pady=20)

    food_window.wait_window()  # Wait until the window is closed
    return selected_food.get()


# Example of a function to train the model (if needed)
def train_img():
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    # Assuming the images are stored in the 'TrainingImage' folder
    faces, ids = get_images_and_labels('TrainingImage')  # Modify according to your folder structure
    recognizer.train(faces, np.array(ids))

    model_path = r'D:\Face-Recognition-Attendance-System-main\TrainingImageLabel\Trainner.yml'
    recognizer.write(model_path)

    messagebox.showinfo("Success", f"Model trained and saved as {model_path}")

def get_images_and_labels(path):
    faces = []
    ids = []

    # Assuming image filenames are in format ID.jpg
    for image_path in os.listdir(path):
        img = cv2.imread(os.path.join(path, image_path), cv2.IMREAD_GRAYSCALE)
        faces.append(img)
        ids.append(int(image_path.split(".")[0]))  # Assuming the filename starts with the ID

    return faces, ids

# Admin login page
def admin_panel():
    admin_window = tk.Toplevel(window)
    admin_window.title("Admin Panel")
    admin_window.geometry("600x400")

    tk.Label(admin_window, text="Token Requests", font=('times', 20, 'bold')).pack(pady=10)
    
    if request_list:
        for idx, (name, food, time) in enumerate(request_list):
            tk.Label(admin_window, text=f"{idx+1}. {name} | {food} | {time}",
                     font=('times', 14)).pack(anchor="w", padx=20)
        
        # Approve requests
        def approve_requests():
            if not request_list:
                messagebox.showinfo("Approval", "No requests to approve.")
                return
            
            # Process each request and generate tokens
            for name, food, time in request_list:
                print(f"Token Approved for: {name} | Food: {food} | Time: {time}")
            
            # Clear the request list after approval
            request_list.clear()
            messagebox.showinfo("Approval", "All requests approved successfully!")
            admin_window.destroy()
        
        approve_button = tk.Button(admin_window, text="Approve All", command=approve_requests,
                                   font=('times', 14), bg="green", fg="white")
        approve_button.pack(pady=10)
    else:
        tk.Label(admin_window, text="No requests available.", font=('times', 14)).pack(pady=10)

    admin_window.mainloop()
window = tk.Tk()
window.title("Hostel Attendance System")
window.geometry("800x600")


def show_token_selection():
    """Display a window to select Veg or Non-Veg token."""
    token_window = tk.Toplevel()  # Use Toplevel to open a new window above the main UI
    token_window.title("Food Token Selection")
    token_window.geometry("300x200")

    tk.Label(token_window, text="Select Food Token").pack(pady=10)

    # Variable to store token type
    token_type = tk.StringVar(value="")  # Initialize with an empty value

    # Create radio buttons and bind them to token_type
    tk.Radiobutton(token_window, text="Veg", variable=token_type, value="Veg").pack()
    tk.Radiobutton(token_window, text="Non-Veg", variable=token_type, value="Non-Veg").pack()

    def submit_token():
        selected_token = token_type.get()  # Retrieve the selected token type
        if selected_token:
            token_window.destroy()
            submit_to_admin(selected_token)  # Proceed to admin verification
        else:
            messagebox.showwarning("Selection Required", "Please select a token type.")

    tk.Button(token_window, text="Submit", command=submit_token).pack(pady=20)
    token_window.mainloop()
def submit_to_admin(token_type):
    """Simulate sending token request to admin and wait for verification."""
    admin_approval = messagebox.askyesno("Admin Approval", f"Approve {token_type} token for user?")
    if admin_approval:
        generate_token_image(token_type)

def generate_token_image(token_type):
    """Generate and display token image after admin approval."""
    img = Image.new('RGB', (200, 100), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    d.text((10, 40), f"{token_type} Token", fill=(255, 255, 0))

    token_path = os.path.join(os.getcwd(), "token_image.png")
    img.save(token_path)
    img.show()

    messagebox.showinfo("Token Generated", f"{token_type} token generated and sent to the user.")
def admin_approve_tokens():
    if not request_list:
        messagebox.showinfo("No Requests", "No pending token requests.")
        return

    approval_window = tk.Toplevel()
    approval_window.title("Approve Token Requests")
    approval_window.geometry("400x400")

    tk.Label(approval_window, text="Pending Requests:", font=('times', 14, 'bold')).pack(pady=10)

    # Listbox to display requests
    listbox = tk.Listbox(approval_window, width=50, height=15)
    listbox.pack(pady=10)

    # Populate listbox with requests
    for i, req in enumerate(request_list):
        if req["status"] == "Pending":
            listbox.insert(i, f"{req['name']} ({req['food_type']}) - {req['status']}")

    # Approve or reject selected request
    def handle_request(approve=True):
        selected = listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "No request selected!")
            return

        index = selected[0]
        request = request_list[index]

        if approve:
            request["status"] = "Approved"
            generate_token(request["name"], request["food_type"])
            listbox.delete(index)
            messagebox.showinfo("Approved", f"Token approved for {request['name']} ({request['food_type']}).")
        else:
            request["status"] = "Rejected"
            listbox.delete(index)
            messagebox.showinfo("Rejected", f"Token rejected for {request['name']} ({request['food_type']}).")

    # Buttons for approval and rejection
    tk.Button(approval_window, text="Approve", command=lambda: handle_request(True), bg="green", fg="white").pack(side="left", padx=10, pady=10)
    tk.Button(approval_window, text="Reject", command=lambda: handle_request(False), bg="red", fg="white").pack(side="right", padx=10, pady=10)

# Function to generate the token




def manually_fill():
    global sb
    sb = tk.Tk()
    # sb.iconbitmap('AMS.ico')
    sb.title("Enter subject name...")
    sb.geometry('580x320')
    sb.configure(background='grey80')

    def err_screen_for_subject():

        def ec_delete():
            ec.destroy()
        global ec
        ec = tk.Tk()
        ec.geometry('300x100')
        # ec.iconbitmap('AMS.ico')
        ec.title('Warning!!')
        ec.configure(background='snow')
        Label(ec, text='Please enter your subject name!!!', fg='red',
              bg='white', font=('times', 16, ' bold ')).pack()
        Button(ec, text='OK', command=ec_delete, fg="black", bg="lawn green", width=9, height=1, activebackground="Red",
               font=('times', 15, ' bold ')).place(x=90, y=50)

    def fill_attendance():
        ts = time.time()
        Date = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d')
        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        Time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        Hour, Minute, Second = timeStamp.split(":")
        # Creatting csv of attendance

        # Create table for Attendance
        date_for_DB = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d')
        global subb
        subb = SUB_ENTRY.get()
        DB_table_name = str(subb + "_" + Date + "_Time_" +
                            Hour + "_" + Minute + "_" + Second)

        import pymysql.connections

        # Connect to the database
        try:
            global cursor
            connection = pymysql.connect(
                host='localhost', user='root', password='', db='manually_fill_attendance')
            cursor = connection.cursor()
        except Exception as e:
            print(e)

        sql = "CREATE TABLE " + DB_table_name + """
                        (ID INT NOT NULL AUTO_INCREMENT,
                         ENROLLMENT varchar(100) NOT NULL,
                         NAME VARCHAR(50) NOT NULL,
                         DATE VARCHAR(20) NOT NULL,
                         TIME VARCHAR(20) NOT NULL,
                             PRIMARY KEY (ID)
                             );
                        """

        try:
            cursor.execute(sql)  # for create a table
        except Exception as ex:
            print(ex)  #

        if subb == '':
            err_screen_for_subject()
        else:
            sb.destroy()
            MFW = tk.Tk()
            # MFW.iconbitmap('AMS.ico')
            MFW.title("Manually attendance of " + str(subb))
            MFW.geometry('880x470')
            MFW.configure(background='grey80')

            def del_errsc2():
                errsc2.destroy()

            def err_screen1():
                global errsc2
                errsc2 = tk.Tk()
                errsc2.geometry('330x100')
                # errsc2.iconbitmap('AMS.ico')
                errsc2.title('Warning!!')
                errsc2.configure(background='grey80')
                Label(errsc2, text='Please enter Student & Enrollment!!!', fg='black', bg='white',
                      font=('times', 16, ' bold ')).pack()
                Button(errsc2, text='OK', command=del_errsc2, fg="black", bg="lawn green", width=9, height=1,
                       activebackground="Red", font=('times', 15, ' bold ')).place(x=90, y=50)

            def testVal(inStr, acttyp):
                if acttyp == '1':  # insert
                    if not inStr.isdigit():
                        return False
                return True

            ENR = tk.Label(MFW, text="Enter Enrollment", width=15, height=2, fg="black", bg="grey",
                           font=('times', 15))
            ENR.place(x=30, y=100)

            STU_NAME = tk.Label(MFW, text="Enter Student name", width=15, height=2, fg="black", bg="grey",
                                font=('times', 15))
            STU_NAME.place(x=30, y=200)

            global ENR_ENTRY
            ENR_ENTRY = tk.Entry(MFW, width=20, validate='key',
                                 bg="white", fg="black", font=('times', 23))
            ENR_ENTRY['validatecommand'] = (
                ENR_ENTRY.register(testVal), '%P', '%d')
            ENR_ENTRY.place(x=290, y=105)

            def remove_enr():
                ENR_ENTRY.delete(first=0, last=22)

            STUDENT_ENTRY = tk.Entry(
                MFW, width=20, bg="white", fg="black", font=('times', 23))
            STUDENT_ENTRY.place(x=290, y=205)

            def remove_student():
                STUDENT_ENTRY.delete(first=0, last=22)

            # get important variable
            def enter_data_DB():
                ENROLLMENT = ENR_ENTRY.get()
                STUDENT = STUDENT_ENTRY.get()
                if ENROLLMENT == '':
                    err_screen1()
                elif STUDENT == '':
                    err_screen1()
                else:
                    time = datetime.datetime.fromtimestamp(
                        ts).strftime('%H:%M:%S')
                    Hour, Minute, Second = time.split(":")
                    Insert_data = "INSERT INTO " + DB_table_name + \
                        " (ID,ENROLLMENT,NAME,DATE,TIME) VALUES (0, %s, %s, %s,%s)"
                    VALUES = (str(ENROLLMENT), str(
                        STUDENT), str(Date), str(time))
                    try:
                        cursor.execute(Insert_data, VALUES)
                    except Exception as e:
                        print(e)
                    ENR_ENTRY.delete(first=0, last=22)
                    STUDENT_ENTRY.delete(first=0, last=22)

            def create_csv():
                import csv
                cursor.execute("select * from " + DB_table_name + ";")
                csv_name = 'C:/Users/Pragya singh/PycharmProjects/Attendace_management_system/Attendance/Manually Attendance/'+DB_table_name+'.csv'
                with open(csv_name, "w") as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow(
                        [i[0] for i in cursor.description])  # write headers
                    csv_writer.writerows(cursor)
                    O = "CSV created Successfully"
                    Notifi.configure(text=O, bg="Green", fg="white",
                                     width=33, font=('times', 19, 'bold'))
                    Notifi.place(x=180, y=380)
                import csv
                import tkinter
                root = tkinter.Tk()
                root.title("Attendance of " + subb)
                root.configure(background='grey80')
                with open(csv_name, newline="") as file:
                    reader = csv.reader(file)
                    r = 0

                    for col in reader:
                        c = 0
                        for row in col:
                            # i've added some styling
                            label = tkinter.Label(root, width=18, height=1, fg="black", font=('times', 13, ' bold '),
                                                  bg="white", text=row, relief=tkinter.RIDGE)
                            label.grid(row=r, column=c)
                            c += 1
                        r += 1
                root.mainloop()

            Notifi = tk.Label(MFW, text="CSV created Successfully", bg="Green", fg="white", width=33,
                              height=2, font=('times', 19, 'bold'))

            c1ear_enroll = tk.Button(MFW, text="Clear", command=remove_enr, fg="white", bg="black", width=10,
                                     height=1,
                                     activebackground="white", font=('times', 15, ' bold '))
            c1ear_enroll.place(x=690, y=100)

            c1ear_student = tk.Button(MFW, text="Clear", command=remove_student, fg="white", bg="black", width=10,
                                      height=1,
                                      activebackground="white", font=('times', 15, ' bold '))
            c1ear_student.place(x=690, y=200)

            DATA_SUB = tk.Button(MFW, text="Enter Data", command=enter_data_DB, fg="black", bg="SkyBlue1", width=20,
                                 height=2,
                                 activebackground="white", font=('times', 15, ' bold '))
            DATA_SUB.place(x=170, y=300)

            MAKE_CSV = tk.Button(MFW, text="Convert to CSV", command=create_csv, fg="black", bg="SkyBlue1", width=20,
                                 height=2,
                                 activebackground="white", font=('times', 15, ' bold '))
            MAKE_CSV.place(x=570, y=300)

            def attf():
                import subprocess
                subprocess.Popen(
                    r'explorer \select,"C:/Face-Recognition-Attendance-System-main/Manually Attendance/-------Check atttendance-------"')

            attf = tk.Button(MFW,  text="Check Sheets", command=attf, fg="white", bg="black",
                             width=12, height=1, activebackground="white", font=('times', 14, ' bold '))
            attf.place(x=730, y=410)

            MFW.mainloop()

    SUB = tk.Label(sb, text="Enter room no : ", width=15, height=2,
                   fg="black", bg="grey80", font=('times', 15, ' bold '))
    SUB.place(x=30, y=100)

    global SUB_ENTRY

    SUB_ENTRY = tk.Entry(sb, width=20, bg="white",
                         fg="black", font=('times', 23))
    SUB_ENTRY.place(x=250, y=105)

    fill_manual_attendance = tk.Button(sb, text="Fill Attendance", command=fill_attendance, fg="black", bg="SkyBlue1", width=20, height=2,
                                       activebackground="white", font=('times', 15, ' bold '))
    fill_manual_attendance.place(x=250, y=160)
    sb.mainloop()

# For clear textbox


def clear():
    txt.delete(first=0, last=22)


def clear1():
    txt2.delete(first=0, last=22)


def del_sc1():
    sc1.destroy()


def err_screen():
    global sc1
    sc1 = tk.Tk()
    sc1.geometry('300x100')
    # sc1.iconbitmap('AMS.ico')
    sc1.title('Warning!!')
    sc1.configure(background='grey80')
    Label(sc1, text='Enrollment & Name required!!!', fg='black',
          bg='white', font=('times', 16)).pack()
    Button(sc1, text='OK', command=del_sc1, fg="black", bg="lawn green", width=9,
           height=1, activebackground="Red", font=('times', 15, ' bold ')).place(x=90, y=50)

# Error screen2


def del_sc2():
    sc2.destroy()


def err_screen1():
    global sc2
    sc2 = tk.Tk()
    sc2.geometry('300x100')
    # sc2.iconbitmap('AMS.ico')
    sc2.title('Warning!!')
    sc2.configure(background='grey80')
    Label(sc2, text='Please enter your subject name!!!', fg='black',
          bg='white', font=('times', 16)).pack()
    Button(sc2, text='OK', command=del_sc2, fg="black", bg="lawn green", width=9,
           height=1, activebackground="Red", font=('times', 15, ' bold ')).place(x=90, y=50)

# For take images for datasets


def take_img():
    l1 = txt.get()
    l2 = txt2.get()
    if l1 == '':
        err_screen()
    elif l2 == '':
        err_screen()
    else:
        try:
            cam = cv2.VideoCapture(0)
            detector = cv2.CascadeClassifier(
                'haarcascade_frontalface_default.xml')
            Enrollment = txt.get()
            Name = txt2.get()
            sampleNum = 0
            while (True):
                ret, img = cam.read()
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = detector.detectMultiScale(gray, 1.3, 5)
                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    # incrementing sample number
                    sampleNum = sampleNum + 1
                    # saving the captured face in the dataset folder
                    cv2.imwrite("TrainingImage/ " + Name + "." + Enrollment + '.' + str(sampleNum) + ".jpg",
                                gray)
                    print("Images Saved for Enrollment :")
                    cv2.imshow('Frame', img)
                # wait for 100 miliseconds
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                #
                # # break if the sample number is morethan 100
                elif sampleNum > 70:
                    break


            cam.release()
            cv2.destroyAllWindows()
            ts = time.time()
            Date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
            Time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
            row = [Enrollment, Name, Date, Time]
            with open(r'StudentDetails\StudentDetails.csv', 'a+') as csvFile:
                writer = csv.writer(csvFile, delimiter=',')
                writer.writerow(row)
                csvFile.close()
            res = "Images Saved for Enrollment : " + Enrollment + " Name : " + Name
            Notification.configure(
                text=res, bg="SpringGreen3", width=50, font=('times', 18, 'bold'))
            Notification.place(x=250, y=400)
        except FileExistsError as F:
            f = 'Student Data already exists'
            Notification.configure(text=f, bg="Red", width=21)
            Notification.place(x=450, y=400)


# for choose subject and fill attendance
def subjectchoose():
    def Fillattendances():
        sub = tx.get()
        now = time.time()  # For calculate seconds of video
        future = now + 20
        if time.time() < future:
            if sub == '':
                err_screen1()
            else:
                recognizer = cv2.face.LBPHFaceRecognizer_create()  # cv2.createLBPHFaceRecognizer()
                try:
                    recognizer.read(r"D:\Face-Recognition-Attendance-System-main\TrainingImageLabel\Trainner.yml")
                except:
                    e = 'Model not found,Please train model'
                    Notifica.configure(
                        text=e, bg="red", fg="black", width=33, font=('times', 15, 'bold'))
                    Notifica.place(x=20, y=250)

                harcascadePath = "haarcascade_frontalface_default.xml"
                faceCascade = cv2.CascadeClassifier(harcascadePath)
                df = pd.read_csv(r"StudentDetails\StudentDetails.csv")
                cam = cv2.VideoCapture(0)
                font = cv2.FONT_HERSHEY_SIMPLEX
                col_names = ['Enrollment', 'Name', 'Date', 'Time']
                attendance = pd.DataFrame(columns=col_names)
                while True:
                    ret, im = cam.read()
                    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
                    faces = faceCascade.detectMultiScale(gray, 1.2, 5)
                    for (x, y, w, h) in faces:
                        global Id

                        Id, conf = recognizer.predict(gray[y:y + h, x:x + w])
                        if (conf < 70):
                            print(conf)
                            global Subject
                            global aa
                            global date
                            global timeStamp
                            Subject = tx.get()
                            ts = time.time()
                            date = datetime.datetime.fromtimestamp(
                                ts).strftime('%Y-%m-%d')
                            timeStamp = datetime.datetime.fromtimestamp(
                                ts).strftime('%H:%M:%S')
                            aa = df.loc[df['Enrollment'] == Id]['Name'].values
                            global tt
                            tt = str(Id) + "-" + aa
                            En = '15624031' + str(Id)
                            attendance.loc[len(attendance)] = [
                                Id, aa, date, timeStamp]
                            cv2.rectangle(
                                im, (x, y), (x + w, y + h), (0, 260, 0), 7)
                            cv2.putText(im, str(tt), (x + h, y),
                                        font, 1, (255, 255, 0,), 4)

                        else:
                            Id = 'Unknown'
                            tt = str(Id)
                            cv2.rectangle(
                                im, (x, y), (x + w, y + h), (0, 25, 255), 7)
                            cv2.putText(im, str(tt), (x + h, y),
                                        font, 1, (0, 25, 255), 4)
                    if time.time() > future:
                        break

                    attendance = attendance.drop_duplicates(
                        ['Enrollment'], keep='first')
                    cv2.imshow('Filling attedance..', im)
                    key = cv2.waitKey(30) & 0xff
                    if key == 27:
                        break

                ts = time.time()
                date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                timeStamp = datetime.datetime.fromtimestamp(
                    ts).strftime('%H:%M:%S')
                Hour, Minute, Second = timeStamp.split(":")
                fileName = "Attendance/" + Subject + "_" + date + \
                    "_" + Hour + "-" + Minute + "-" + Second + ".csv"
                attendance = attendance.drop_duplicates(
                    ['Enrollment'], keep='first')
                print(attendance)
                attendance.to_csv(fileName, index=False)

                # Create table for Attendance
                date_for_DB = datetime.datetime.fromtimestamp(
                    ts).strftime('%Y_%m_%d')
                DB_Table_name = str(
                    Subject + "_" + date_for_DB + "_Time_" + Hour + "_" + Minute + "_" + Second)
                import pymysql.connections

                # Connect to the database
                try:
                    global cursor
                    connection = pymysql.connect(
                        host='localhost', user='root', password='', db='Face_reco_fill')
                    cursor = connection.cursor()
                except Exception as e:
                    print(e)

                sql = "CREATE TABLE " + DB_Table_name + """
                (ID INT NOT NULL AUTO_INCREMENT,
                 ENROLLMENT varchar(100) NOT NULL,
                 NAME VARCHAR(50) NOT NULL,
                 DATE VARCHAR(20) NOT NULL,
                 TIME VARCHAR(20) NOT NULL,
                     PRIMARY KEY (ID)
                     );
                """
                # Now enter attendance in Database
                insert_data = "INSERT INTO " + DB_Table_name + \
                    " (ID,ENROLLMENT,NAME,DATE,TIME) VALUES (0, %s, %s, %s,%s)"
                VALUES = (str(Id), str(aa), str(date), str(timeStamp))
                try:
                    cursor.execute(sql)  # for create a table
                    # For insert data into table
                    cursor.execute(insert_data, VALUES)
                except Exception as ex:
                    print(ex)  #

                M = 'Attendance filled Successfully'
                Notifica.configure(text=M, bg="Green", fg="white",
                                   width=33, font=('times', 15, 'bold'))
                Notifica.place(x=20, y=250)

                cam.release()
                cv2.destroyAllWindows()

                import csv
                import tkinter
                root = tkinter.Tk()
                root.title("Attendance of " + Subject)
                root.configure(background='grey80')
                cs = r'C:/Face-Recognition-Attendance-System-main/' + fileName
                with open(cs, newline="") as file:
                    reader = csv.reader(file)
                    r = 0

                    for col in reader:
                        c = 0
                        for row in col:
                            # i've added some styling
                            label = tkinter.Label(root, width=10, height=1, fg="black", font=('times', 15, ' bold '),
                                                  bg="white", text=row, relief=tkinter.RIDGE)
                            label.grid(row=r, column=c)
                            c += 1
                        r += 1
                root.mainloop()
                print(attendance)

    # windo is frame for subject chooser
    windo = tk.Tk()
    # windo.iconbitmap('AMS.ico')
    windo.title("Enter subject name...")
    windo.geometry('580x320')
    windo.configure(background='grey80')
    Notifica = tk.Label(windo, text="Attendance filled Successfully", bg="Green", fg="white", width=33,
                        height=2, font=('times', 15, 'bold'))

    def Attf():
        import subprocess
        subprocess.Popen(
            r'explorer /select,"C:\Users\Pragya Singh\PycharmProjects\Attendace_management_system\Attendance\-------Check atttendance-------"')

    attf = tk.Button(windo,  text="Check Sheets", command=Attf, fg="white", bg="black",
                     width=12, height=1, activebackground="white", font=('times', 14, ' bold '))
    attf.place(x=430, y=255)

    sub = tk.Label(windo, text="Enter room no : ", width=15, height=2,
                   fg="black", bg="grey", font=('times', 15, ' bold '))
    sub.place(x=30, y=100)

    tx = tk.Entry(windo, width=20, bg="white",
                  fg="black", font=('times', 23))
    tx.place(x=250, y=105)

    fill_a = tk.Button(windo, text="Fill Attendance", fg="white", command=Fillattendances, bg="SkyBlue1", width=20, height=2,
                       activebackground="white", font=('times', 15, ' bold '))
    fill_a.place(x=250, y=160)
    windo.mainloop()


def admin_panel():
    win = tk.Tk()
    # win.iconbitmap('AMS.ico')
    win.title("LogIn")
    win.geometry('880x420')
    win.configure(background='grey80')

    def log_in():
        username = un_entr.get()
        password = pw_entr.get()

        if username == '1234':
            if password == '5678':
                win.destroy()
                import csv
                import tkinter
                root = tkinter.Tk()
                root.title("Student Details")
                root.configure(background='grey80')

                cs = 'D:/Face-Recognition-Attendance-System-main/StudentDetails/StudentDetails.csv'
                with open(cs, newline="") as file:
                    reader = csv.reader(file)
                    r = 0

                    for col in reader:
                        c = 0
                        for row in col:
                            # i've added some styling
                            label = tkinter.Label(root, width=10, height=1, fg="black", font=('times', 15, ' bold '),
                                                  bg="white", text=row, relief=tkinter.RIDGE)
                            label.grid(row=r, column=c)
                            c += 1
                        r += 1
                root.mainloop()
            else:
                valid = 'Incorrect ID or Password'
                Nt.configure(text=valid, bg="red", fg="white",
                             width=38, font=('times', 19, 'bold'))
                Nt.place(x=120, y=350)

        else:
            valid = 'Incorrect ID or Password'
            Nt.configure(text=valid, bg="red", fg="white",
                         width=38, font=('times', 19, 'bold'))
            Nt.place(x=120, y=350)

    Nt = tk.Label(win, text="Attendance filled Successfully", bg="Green", fg="white", width=40,
                  height=2, font=('times', 19, 'bold'))
    # Nt.place(x=120, y=350)

    un = tk.Label(win, text="Enter username : ", width=15, height=2, fg="black", bg="grey",
                  font=('times', 15, ' bold '))
    un.place(x=30, y=50)

    pw = tk.Label(win, text="Enter password : ", width=15, height=2, fg="black", bg="grey",
                  font=('times', 15, ' bold '))
    pw.place(x=30, y=150)

    def c00():
        un_entr.delete(first=0, last=22)

    un_entr = tk.Entry(win, width=20, bg="white", fg="black",
                       font=('times', 23))
    un_entr.place(x=290, y=55)

    def c11():
        pw_entr.delete(first=0, last=22)

    pw_entr = tk.Entry(win, width=20, show="*", bg="white",
                       fg="black", font=('times', 23))
    pw_entr.place(x=290, y=155)

    c0 = tk.Button(win, text="Clear", command=c00, fg="white", bg="black", width=10, height=1,
                   activebackground="white", font=('times', 15, ' bold '))
    c0.place(x=690, y=55)

    c1 = tk.Button(win, text="Clear", command=c11, fg="white", bg="black", width=10, height=1,
                   activebackground="white", font=('times', 15, ' bold '))
    c1.place(x=690, y=155)

    Login = tk.Button(win, text="LogIn", fg="black", bg="SkyBlue1", width=20,
                      height=2,
                      activebackground="Red", command=log_in, font=('times', 15, ' bold '))
    Login.place(x=290, y=250)
    win.mainloop()


# For train the model
def trainimg():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    global detector
    detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    try:
        global faces, Id
        faces, Id = getImagesAndLabels("TrainingImage")
    except Exception as e:
        l = 'please make "TrainingImage" folder & put Images'
        Notification.configure(text=l, bg="SpringGreen3",
                               width=50, font=('times', 18, 'bold'))
        Notification.place(x=350, y=400)

    recognizer.train(faces, np.array(Id))
    try:
        recognizer.save(r"TrainingImageLabel\Trainner.yml")
    except Exception as e:
        q = 'Please make "TrainingImageLabel" folder'
        Notification.configure(text=q, bg="SpringGreen3",
                               width=50, font=('times', 18, 'bold'))
        Notification.place(x=350, y=400)

    res = "Model Trained"  # +",".join(str(f) for f in Id)
    Notification.configure(text=res, bg="olive drab",
                           width=50, font=('times', 18, 'bold'))
    Notification.place(x=250, y=400)


def getImagesAndLabels(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    # create empth face list
    faceSamples = []
    # create empty ID list
    Ids = []
    # now looping through all the image paths and loading the Ids and the images
    for imagePath in imagePaths:
        # loading the image and converting it to gray scale
        pilImage = Image.open(imagePath).convert('L')
        # Now we are converting the PIL image into numpy array
        imageNp = np.array(pilImage, 'uint8')
        # getting the Id from the image

        Id = int(os.path.split(imagePath)[-1].split(".")[1])
        # extract the face from the training image sample
        faces = detector.detectMultiScale(imageNp)
        # If a face is there then append that in the list as well as Id of it
        for (x, y, w, h) in faces:
            faceSamples.append(imageNp[y:y + h, x:x + w])
            Ids.append(Id)
    return faceSamples, Ids


window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)
# window.iconbitmap('AMS.ico')


def on_closing():
    from tkinter import messagebox
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        window.destroy()


window.protocol("WM_DELETE_WINDOW", on_closing)

message = tk.Label(window, text="Face-Recognition-Based-Hostel-Attendance-Management-System", bg="black", fg="white", width=50,
                   height=3, font=('times', 30, ' bold '))

message.place(x=80, y=20)

Notification = tk.Label(window, text="All things good", bg="Green", fg="white", width=15,
                        height=3, font=('times', 17))

lbl = tk.Label(window, text="Enter Enrollment : ", width=20, height=2,
               fg="black", bg="grey", font=('times', 15, 'bold'))
lbl.place(x=200, y=200)


def testVal(inStr, acttyp):
    if acttyp == '1':  # insert
        if not inStr.isdigit():
            return False
    return True


txt = tk.Entry(window, validate="key", width=20, bg="white",
               fg="black", font=('times', 25))
txt['validatecommand'] = (txt.register(testVal), '%P', '%d')
txt.place(x=550, y=210)

lbl2 = tk.Label(window, text="Enter Name : ", width=20, fg="black",
                bg="grey", height=2, font=('times', 15, ' bold '))
lbl2.place(x=200, y=300)

txt2 = tk.Entry(window, width=20, bg="white",
                fg="black", font=('times', 25))
txt2.place(x=550, y=310)

clearButton = tk.Button(window, text="Clear", command=clear, fg="white", bg="black",
                        width=10, height=1, activebackground="white", font=('times', 15, ' bold '))
clearButton.place(x=950, y=210)

clearButton1 = tk.Button(window, text="Clear", command=clear1, fg="white", bg="black",
                         width=10, height=1, activebackground="white", font=('times', 15, ' bold '))
clearButton1.place(x=950, y=310)

AP = tk.Button(window, text="Check Registered students", command=admin_panel, fg="black",
               bg="SkyBlue1", width=19, height=1, activebackground="white", font=('times', 15, ' bold '))
AP.place(x=990, y=410)

takeImg = tk.Button(window, text="Take Images", command=take_img, fg="black", bg="SkyBlue1",
                    width=20, height=3, activebackground="white", font=('times', 15, ' bold '))
takeImg.place(x=90, y=500)

trainImg = tk.Button(window, text="Train Images", fg="black", command=trainimg, bg="SkyBlue1",
                     width=20, height=3, activebackground="white", font=('times', 15, ' bold '))
trainImg.place(x=390, y=500)

FA = tk.Button(window, text="Automatic Attendance", fg="black", command=subjectchoose,
               bg="SkyBlue1", width=20, height=3, activebackground="white", font=('times', 15, ' bold '))
FA.place(x=690, y=500)

quitWindow = tk.Button(window, text="Manually Fill Attendance", command=manually_fill, fg="black",
                       bg="SkyBlue1", width=20, height=3, activebackground="white", font=('times', 15, ' bold '))
quitWindow.place(x=990, y=500)



start_token_button = tk.Button(
    window, text="Food Token",
    command=face_verification_and_token,
    fg="black", bg="SkyBlue1", width=20, height=2,
    font=('times', 15, 'bold')
)
start_token_button.place(x=50, y=370)



approve_button = tk.Button(
    root, text="Approve Tokens", command=admin_login,
    fg="black", bg="green", width=20, height=2,
    font=('times', 15, 'bold')
)
approve_button.pack(pady=30)

window.mainloop()
