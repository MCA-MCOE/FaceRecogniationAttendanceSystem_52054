import face_recognition
import cv2
import os
import csv
from datetime import datetime

# Path to the directory containing known face images and their names
known_faces_dir = 'faces'
attendance_log = 'attendance.csv'

# Initialize lists to store known face encodings and names
known_face_encodings = []
known_face_names = []

# Load known faces and their names
for file_name in os.listdir(known_faces_dir):
    if file_name.endswith('.jpg'):
        face_name = os.path.splitext(file_name)[0]
        image_path = os.path.join(known_faces_dir, file_name)
        image = face_recognition.load_image_file(image_path)
        face_encoding = face_recognition.face_encodings(image)[0]
        known_face_encodings.append(face_encoding)
        known_face_names.append(face_name)

# Initialize variables for attendance tracking
present_students = set()

# Open the webcam for video capture
video_capture = cv2.VideoCapture(0)  # Initialize video_capture here

# Create or open the attendance CSV file
with open(attendance_log, 'a', newline='') as log_file:
    writer = csv.writer(log_file)

    # Create a dictionary to keep track of the last attendance date for each person
    last_attendance_date = {}

    name = "Unknown"  # Initialize name here

    while True:
        # Capture a single frame from the webcam
        ret, frame = video_capture.read()

        # Find all face locations in the current frame
        face_locations = face_recognition.face_locations(frame)

        # Encode the faces in the current frame
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        # Iterate through the faces in the current frame
        for face_encoding in face_encodings:
            # Compare the face with known faces
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]

                # Check if the person has already been marked present today
                today = datetime.now().date().isoformat()
                if last_attendance_date.get(name) != today:
                    present_students.add(name)
                    last_attendance_date[name] = today

        # Draw rectangles around the detected faces
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)

        # Display the resulting frame
        cv2.imshow('Face Recognition Attendance', frame)

        # Log attendance when known faces are detected
        if name != "Unknown" and name in present_students:
            now = datetime.now()
            timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([timestamp, name])
            present_students.remove(name)  # Remove the name from the set to prevent duplicate recording

        # Exit the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Close the video capture and OpenCV windows
video_capture.release()
cv2.destroyAllWindows()

print('Attendance recorded in', attendance_log)
