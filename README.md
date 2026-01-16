# Student Participation Counting System using Real-time Face Recognition with Multiple Cameras
A Python computer vision–based system (including desktop &amp; web) designed to automatically measure student participation in a learning environment. The system utilizes real-time face recognition to identify students and track their presence and activity across multiple camera sources simultaneously.

## HOW TO USE (Windows)
--------------------------------------------------
### 1. REQUIREMENTS
- Microsoft Visual Studio 2015 (or newer) with C/C++ Compiler installed. (Visual C++ 2015 Build Tools didn't work for me, and I got into problems in compiling dlib)
- Of course Python3 (I used Python3.11 but the other versions may work too)
- <a href="https://cmake.org/download/">Cmake<>for windows and add it to your system environment variables.

--------------------------------------------------
### 2. PROJECT STRUCTURE
Web/ <br>
├── models/ <br>
├── static/ <br>
├── templates/ <br>
├── app.py <br>
├── forms.py <br>
└── main.py <br>
└── queries.py <br>
└── requirements.txt <br>
└── utils.py <br>
└── utils_face.py <br>
Desktop/ <br>
├── data/ <br>
├── models/ <br>
├── static/ <br>
├── faceID.py <br>
├── facerecognition.ico <br>
└── loading.png <br>
└── requirements.txt <br>

--------------------------------------------------
### 3. CREATE A VIRTUAL ENVIRONMENT (OPTIONAL)
Run the following commands in the terminal/command prompt inside the "Web/" and "Desktop/" directories:

- "python -m venv virtualenvironmentname"
- Then activate it using: "source virtualenvironmentname/Scripts/activate"

--------------------------------------------------
### 4. INSTALL DEPENDENCIES
Run the following command in the terminal/command prompt:

- "pip install -r requirements.txt"

--------------------------------------------------
### 6. LAUNCH THE PROGRAM
Run the following commands in the terminal/command prompt inside the "Web/" and "Desktop/" directories:

- In the "Web/" directory, run:  
  "python main.py"
- Then open "localhost:4000" in your browser
- To stop the program: press "Ctrl + C" in the terminal/command prompt
- Username / Password:
  1. Student (Mahasiswa): rian123 / 123
  2. Parent (Orang tua): ortu123 / 123
  3. Lecturer (Dosen): dosen123 / 123

- In the "Desktop/" directory, run:  
  "python faceID.py"
- The application window will then open
