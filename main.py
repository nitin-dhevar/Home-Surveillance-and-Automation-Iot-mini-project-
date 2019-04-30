import cv2
import sys
from mail import sendEmail,sendAlertEmail
from flask import Flask, render_template, Response
from camera import VideoCamera
from flask_basicauth import BasicAuth
import time 
import threading
from multiprocessing import Process
import RPi.GPIO as GPIO
from time import sleep


email_update_interval = 600 # sends an email only once in this time interval
video_camera = VideoCamera(flip=True) # creates a camera object, flip vertically
object_classifier = cv2.CascadeClassifier("models/facial_recognition_model.xml") # an opencv classifier

# App Globals (do not edit)
app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = 'nitin'
app.config['BASIC_AUTH_PASSWORD'] = 'password'
app.config['BASIC_AUTH_FORCE'] = True

basic_auth = BasicAuth(app)
last_epoch = 0

def check_for_objects():
	global last_epoch
	while True:
		try:
			frame, found_obj = video_camera.get_object(object_classifier)
			if found_obj and (time.time() - last_epoch) > email_update_interval:
				last_epoch = time.time()
				print ("Sending email...")
				sendEmail(frame)
				print ("done!")
		except:
			print ("Error sending email: ", sys.exc_info()[0])
			
def check_gas_leak():
    channel = 15
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(channel, GPIO.IN)
 
    def callback(channel):
        sendAlertEmail()
 
    GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=300)  # let us know when the pin goes HIGH or LOW
    GPIO.add_event_callback(channel, callback)  # assign function to GPIO PIN, Run function on change
 
# infinite loop
    while True:
        time.sleep(1)

@app.route('/')
@basic_auth.required
def index():
    return render_template('index.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(video_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/home")
def nitin():
	return render_template('new.html')

@app.route("/servoOn/")
def snmain():
    GPIO.setmode(GPIO.BOARD)
    servoPIN = 12
    GPIO.setup(servoPIN, GPIO.OUT)
    p = GPIO.PWM(servoPIN, 50)
    p.start(2.5)
    time.sleep(1.5)
    p.ChangeDutyCycle(2.5)
    time.sleep(1.5)
    GPIO.cleanup()
    return render_template('new.html')
@app.route("/servoOff/")
def sfmain():
    GPIO.setmode(GPIO.BOARD)
    servoPIN = 12
    GPIO.setup(servoPIN, GPIO.OUT)
    p = GPIO.PWM(servoPIN, 50)
    p.start(2.5)
    time.sleep(1.5)
    p.ChangeDutyCycle(12.5)
    time.sleep(1.5)
    GPIO.cleanup()
    return render_template('new.html')
@app.route("/ledOn/")
def lnmain():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(29, GPIO.OUT)
    GPIO.setup(31, GPIO.OUT)
    GPIO.setup(33, GPIO.OUT)
    GPIO.setup(37, GPIO.OUT)
    GPIO.output(29, True)
    GPIO.output(31, True)
    GPIO.output(33, True)
    GPIO.output(37,True)

    return render_template('new.html')
    
	
	
@app.route("/ledOff/")
def lfmain():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(29, GPIO.OUT)
    GPIO.setup(31, GPIO.OUT)
    GPIO.setup(33, GPIO.OUT)
    GPIO.setup(37, GPIO.OUT)
    GPIO.output(29, False)
    GPIO.output(31, False)
    GPIO.output(33, False)
    GPIO.output(37,False)
    return render_template('new.html')

	
@app.route("/fanOff/")
def fanfmain():
    Motor1B = 16
    GPIO.setmode(GPIO.BOARD)		
    GPIO.setup(Motor1B,GPIO.OUT)
    GPIO.output(Motor1B,GPIO.LOW)
    return render_template('new.html')

	
@app.route("/fanOn/")
def fanmain():
    Motor1B = 16
    GPIO.setmode(GPIO.BOARD)		
    GPIO.setup(Motor1B,GPIO.OUT)
    GPIO.output(Motor1B,GPIO.HIGH)
    sleep(5)
    return render_template('new.html')

@app.route("/notify/")
def usmain():
    channel = 15
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(channel, GPIO.IN)
 
    def callback(channel):
        flameStatus='Fire!'
        usStatus='open'
        templateData={'title' : 'Status Check!',
      'ultraSonic'  : usStatus,
      'flameSensor': flameStatus
      
      }
    return render_template('alert.html', **templateData)
    GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=300)  # let us know when the pin goes HIGH or LOW
    GPIO.add_event_callback(channel, callback)  # assign function to GPIO PIN, Run function on change
 
    # infinite loop
    while True:
        time.sleep(1)
    
    
    
    


if __name__ == '__main__':
    t = threading.Thread(target=check_for_objects, args=())
    t.daemon = True
    t.start()
    
    
    app.run(host='0.0.0.0', debug=False)
