import face_recognition
import cv2
import os
import csv
from datetime import datetime

# Path to the directory containing known face images and their names
known_faces_dir = 'faces'
csv_file = 'attendance.csv'

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
student_count = 0

# Initialize video capture from the default camera (you can change the index if you have multiple cameras)
video_capture = cv2.VideoCapture(0)

# Create or open the CSV file for attendance
with open(csv_file, 'w', newline='') as csvfile:
    fieldnames = ['Name', 'Timestamp']
    csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # Write the header to the CSV file
    csv_writer.writeheader()

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
                if name != "Unknown" and name not in present_students:
                    present_students.add(name)
                    student_count += 1
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    # Write the attendance to the CSV file
                    csv_writer.writerow({'Name': name, 'Timestamp': timestamp})

        # Draw rectangles around the detected faces
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.putText(frame, f"{name} - Count: {student_count}", (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)

        # Display the resulting frame
        cv2.imshow('Face Recognition Attendance', frame)


       # Exit the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
           break

# Close the video capture and OpenCV windows
video_capture.release()
cv2.destroyAllWindows()

print('Attendance recorded in', csv_file)
