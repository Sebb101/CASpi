
#import python modules
import time
import RPi.GPIO as io
import os

# Wheel Motors Pins

MotorALpin = 18 # GPIO18, Left front motor
MotorBLpin = 12 # GPIO19, Left front motor

MotorARpin = 19 # GPIO13, Right front motor
MotorBRpin = 13 # GPIO12, Right front motor

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


try:
        cont = input("Cont? [Y] or no?")
        while (cont == 'Y'):
                command = input("Move [F]orwards or [B]ackwards : ")
                if(command == 'F'):
                        pwm_channel0_AL.ChangeDutyCycle(50)
                        pwm_channel0_BL.ChangeDutyCycle(0)
                        pwm_channel1_AR.ChangeDutyCycle(50)
                        pwm_channel1_BR.ChangeDutyCycle(0)
                        time.sleep(4)
                elif(command == 'B'):
                        pwm_channel0_AL.ChangeDutyCycle(0)
                        pwm_channel0_BL.ChangeDutyCycle(50)
                        pwm_channel1_AR.ChangeDutyCycle(0)
                        pwm_channel1_BR.ChangeDutyCycle(50)
                        time.sleep(4)
                else:
                        print("Invalid Command!")
                pwm_channel0_AL.ChangeDutyCycle(0)
                pwm_channel0_BL.ChangeDutyCycle(0)
                pwm_channel1_AR.ChangeDutyCycle(0)
                pwm_channel1_BR.ChangeDutyCycle(0)
                cont = input("Cont? [Y] or no?")

except:
        print("shit boofed")

io.cleanup()

