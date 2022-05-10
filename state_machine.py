#!/usr/bin/env  python

import RPi.GPIO as GPIO
from picamera import PiCamera
import time
from signal import signal, SIGTERM, SIGHUP, pause
from rpi_lcd import LCD
from mfrc522 import SimpleMFRC522
from datetime import date, datetime
import tensorflow as tf
from tensorflow import keras
import numpy as np
import traceback

lcd = LCD()
reader = SimpleMFRC522()
camera = PiCamera()
model = keras.models.load_model("final_model_big_dataset.h5")

id = ""         # id of the rfid card in use
state = "default"    # state
pics_num = 0
tray_button_pin = 0
tray_button = False
X_button_pin = 15
X_button = False
O_button_pin = 13
O_button = False
end_button_pin = 11
end_button = False
photo_path = "/home/dodo/onlabor/pics"
file_name = "/home/dodo/onlabor/transactions.txt"
money = ""


def button_pushed(pin, btn):
	global state, end_button_pin, X_button_pin, end_button, X_button, O_button_pin, O_button, tray_button_pin, tray_button
	cnt = 0.0
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	b = GPIO.input(pin) == GPIO.HIGH
	r = (b and not btn)
	if pin == end_button_pin:
		end_button = b
	if pin == X_button_pin:
		X_button = b
	if pin == O_button_pin:
		O_button = b
	if pin == tray_button_pin:
		tray_button = b
	#print(f"pushed {b}")
	return r

def predict(imgpath):
	img = keras.preprocessing.image.load_img(imgpath, target_size = model.image_size)
	img_array = keras.preprocessing.image.img_to_array(img)
	img_array = tf.expand_dims(img_array, 0)
	predictions = model.predict(img_array)
	score = predictions[0]
	idx = np.where(score == np.amax(score))
	return(model.class_names[int(idx[0])])


def tray_in():
	return()

def tray_out():
	return()

def money_to_box():
	return()

def auth():
	global id, state
	try:
		id, text = reader.read()
		print(id, "      ", text)
		lcd.clear()
		lcd.text(str(id), 1)
		state = "waiting_for_money"
	except Exception as err:
		print(err)
		print("Failed to read card")
		lcd.clear()
		lcd.text("Failed",1)
		time.sleep(3)
		lcd.clear()


def money_waiting():
	global state, end_button_pin, X_button_pin, end_button, X_button, O_button_pin, O_button, tray_button_pin, tray_button
	cnt = 0.0
	tray_out()
	while(not button_pushed(end_button_pin, end_button)):
		time.sleep(0.05)
		cnt += 0.05
		if cnt > 30 or button_pushed(X_button_pin, X_button):
			tray_in()
			state = "waiting_for_auth"
			break
		if button_pushed(O_button_pin, O_button):
			tray_in()
		state = "photo"


def photoshoot(format = "png"):
	global pics_num, lcd
	name = "pic" + str(pics_num) + "." + format
	camera.start_preview()
	#time.sleep(2)
	camera.resolution = (1920,1080)
	#camera.resolution = (3280, 2464)
	camera.preview_fullscreen = False
	camera.preview.window = (400,0,1080,1080)
	camera.capture('/home/dodo/onlabor/pics/' + name)
	camera.stop_preview()
	pics_num = pics_num + 1
	print("photo is taken")
	lcd.clear()
	lcd.text("photo is taken", 2)
	time.sleep(3)
	lcd.clear()
	return('/home/dodo/onlabor/pics/' + name)

def picture_taken():
	global state
	state = "ai"

def ai():
	global state, lcd, money, photo_path
	money = predict(photo_path)
	lcd.clear()
	lcd.text(str(money), 1)
	state = "waiting_for_approval"

def approve():
	global X_button, O_button, X_button_pin, O_button_pin, state
	lcd.text("press X or O",2)
	while(not button_pushed(O_button_pin, O_button) or not  button_pushed(X_button_pin, X_button)):
		if button_pushed(O_button_pin, O_button):
			state = "commit_transaction"
			break
		elif button_pushed(X_button_pin, X_button):
			tray_out()
			lcd.clear()
			state = "money_back"
			break

def write_to_file(file_name):
	global state, lcd
	now_def = datetime.now()
	now = now_def.strftime("%d/%m/%Y %H:%M:%S")
	try:
		f = open(file_name, "a")
		f.write(id + "\t" + str(money) + "\t" + now)
		lcd.clear()
		lcd.text("success",1)
		money_to_box()
		state = "waiting_for_money"
	except Exception as err:
		print("error while writing")
		state = "money_back"
	finally:
		f.close

def money_back():
	global lcd, state
	lcd.clear()
	lcd.text("giving money back",1)
	tray_out()
	time.sleep(3)
	lcd.clear()
	state = "waiting_for_money"

def error_func(arg):
	global state
	print("invalid sate: " + arg)
	lcd.clear()
	lcd.text("error", 1)
	time.sleep(5)
	lcd.clear()
	state = "default"
	return()


def states(arg):
	global lcd, state, file_name
	if (arg == "waiting_for_auth"):
		lcd.clear()
		lcd.text("place your card",1)
		auth()
		return()
	elif (arg == "waiting_for_money"):
		lcd.text("put the money into the tray", 2)
		money_waiting()
		return()
	elif (arg == "photo"):
		photoshoot()
		picture_taken()
		return()
	elif (arg == "ai"):
		ai()
		return()
	elif (arg == "waiting_for_approval"):
		approve()
		return()
	elif (arg == "commit_transaction"):
		write_to_file(file_name)
		return()
	elif (arg == "money_back"):
		money_back()
		return()
	elif (arg == "default"):
		state = "waiting_for_auth"
		return()
	else:
		error_func(arg)
		return()


def main():
	global state
	try:
		states(state)
		print(state)
	except KeyboardInterrupt:
		state = "default"
		lcd.clear()
		exit(0)


if __name__ == "__main__":
	while True:
		main()

