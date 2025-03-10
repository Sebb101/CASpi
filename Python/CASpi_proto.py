# Importing python modules
import time
import RPi.GPIO as io
import numpy as np
import os
import socket


# Wheel Motors Pins
MotorALpin = 18 # GPIO18, Left front motor
MotorBLpin = 12 # GPIO12, Left front motor

MotorARpin = 19 # GPIO19, Right front motor
MotorBRpin = 13 # GPIO13, Right front motor

io.setmode(io.BCM)
io.setup(MotorALpin,io.OUT)
io.setup(MotorBLpin,io.OUT)
io.setup(MotorARpin,io.OUT)
io.setup(MotorBRpin,io.OUT)


# Assign PWM channels to motor pins @ 1kHz
pwm_channel0_AL = io.PWM(MotorALpin,1000)
pwm_channel0_BL = io.PWM(MotorBLpin,1000)

pwm_channel1_AR = io.PWM(MotorARpin,1000)
pwm_channel1_BR = io.PWM(MotorBRpin,1000)


# Start at 0% Duty Cycle
pwm_channel0_AL.start(0)
pwm_channel0_BL.start(0)
pwm_channel1_AR.start(0)
pwm_channel1_BR.start(0)


# Server IP or Hostname
HOST = '10.40.6.128' 
# Pick an open Port (1000+ recommended), must match the client sport
PORT = 12345 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')


#managing error exception
try:
	s.bind((HOST, PORT))
except socket.error:
	print('Bind failed ')

s.listen(10)
print('Socket awaiting messages')
(conn, addr) = s.accept()
print('Connected')

def roverStop():
        print("pi: Stop")
        pwm_channel0_AL.ChangeDutyCycle(0)
        pwm_channel0_BL.ChangeDutyCycle(0)
        pwm_channel1_AR.ChangeDutyCycle(0)
        pwm_channel1_BR.ChangeDutyCycle(0)

def roverForward(speed):
        print("pi: Forwards")
        pwm_channel0_AL.ChangeDutyCycle(speed)
        pwm_channel0_BL.ChangeDutyCycle(0)
        pwm_channel1_AR.ChangeDutyCycle(speed)
        pwm_channel1_BR.ChangeDutyCycle(0)

def roverBackward(speed):
        print("pi: Backwards")
        pwm_channel0_AL.ChangeDutyCycle(0)
        pwm_channel0_BL.ChangeDutyCycle(speed)
        pwm_channel1_AR.ChangeDutyCycle(0)
        pwm_channel1_BR.ChangeDutyCycle(speed)

def roverLeft(speed):
        print("pi: Left")
        pwm_channel0_AL.ChangeDutyCycle(speed)
        pwm_channel0_BL.ChangeDutyCycle(0)
        pwm_channel1_AR.ChangeDutyCycle(0)
        pwm_channel1_BR.ChangeDutyCycle(0)

def roverRight(speed):
        print("pi: Right")
        pwm_channel0_AL.ChangeDutyCycle(0)
        pwm_channel0_BL.ChangeDutyCycle(0)
        pwm_channel1_AR.ChangeDutyCycle(speed)
        pwm_channel1_BR.ChangeDutyCycle(0)

def roverDownActuator():
        print("pi: Down Actuator")
        # engage linear actuator down
        pass

def roverUpActuator():
        print("pi: Up Actuator")
        # engage linear actuator up
        pass

def roverDrill():
        print("pi: Drilling")
        # start spinning drill
        pass


# awaiting for message
while True:
        data = (conn.recv(1024)).decode()
        print(data)
        data = np.array(data.split(","))
        speed = int(data[1])
        print(speed)
        print('Replying to: ' + data[0])
        reply = ''

        # process your message
        if data[0] == 'F':
                reply = 'Going Forwards'
                roverForward(speed)

        elif data[0] == 'B':
                reply = 'Going Backwards'
                roverBackward(speed)

        elif data[0] == 'L':
                reply = 'Going Left'
                roverLeft(speed)

        elif data[0] == 'R':
                reply = 'Going Right'
                roverRight(speed)

        elif data[0] == 'DA':
                reply = 'Activating Linear Actuator down'
                roverDownActuator()

        elif data[0] == 'UA':
                reply = 'Activating Linear Actuator up'
                roverUpActuator()

        elif data[0] == 'D':
                reply = 'Activating Drilling'
                roverDrill()

        elif data[0] == 'S':
                reply = 'Stopping Rover'
                roverStop()

        #and so on and on until...
        elif data[0] == 'Q':
                conn.send(str.encode('Terminating'))
                break
        else:
                reply = 'Unknown command'

        # Sending reply
        conn.send(str.encode(reply))

conn.close() # Close connections
io.cleanup()


