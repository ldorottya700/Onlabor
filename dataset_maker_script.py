#!/usr/bin/env python
from picamera import PiCamera
from time import sleep
import RPi.GPIO as GPIO
import sys
import os
import argparse
from datetime import date, datetime

#camera = PiCamera()
#camera.resolution = (1920, 1080)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

parser = argparse.ArgumentParser()
parser.add_argument("value", type = str)
parser.add_argument("format", type = str)
args = parser.parse_args()



while True:
	if len(input("kep")) >= 0:
#	if GPIO.input(15) == GPIO.HIGH:
		now_def = datetime.now()
		now = now_def.strftime("%d-%m-%Y_%H-%M-%S")
		name = args.value + "_" + now + "." + args.format
		#camera.start_preview()
		#print("started to take picture")
		#camera.capture("/home/dodo/onlabor/money_dataset/" + args.value + "/" + name)
		#print("took picture")
		#camera.stop_preview()
		#print("close camera")
		cmd0 = ["cd", "/home/dodo/onlabor/money_dataset/" + args.value]
		cmd = "raspistill -t 50 -o " + name + " -w 1920 -h 1080"

		os.chdir("/home/dodo/onlabor/money_dataset/" + args.value)
		os.system(cmd)
		print("took a picture")
