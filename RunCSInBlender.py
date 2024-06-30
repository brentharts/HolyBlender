import bpy, subprocess, os, mathutils, sys

sys.path.append('/usr/lib/python3/dist-packages')
sys.path.append('/usr/local/lib/python3.12/dist-packages')
sys.path.append(os.path.expanduser('~/.local/lib/python3.12/site-packages'))
from pynput import *

mouseButtonsPressed_ = []
keysPressed_ = []

def OnMouseClick (x, y, button, pressed):
	global mouseButtonsPressed_
	if pressed:
		mouseButtonsPressed_.append(button.name)
	else:
		mouseButtonsPressed_.remove(button.name)

mouseListener = mouse.Listener(on_click=OnMouseClick)
mouseListener.start()

def OnKeyPress (key):
	global keysPressed_
	try:
		keysPressed_.append(key.char)
	except AttributeError:
		keysPressed_.append(key)

def OnKeyRelease (key):
	global keysPressed_
	try:
		keysPressed_.remove(key.char)
	except AttributeError:
		keysPressed_.remove(key)

keyboardListener = keyboard.Listener(on_press=OnKeyPress, on_release=OnKeyRelease)
keyboardListener.start()

def Run (filePath : str, obj):
	global mouseButtonsPressed_
	outputCode = 'self = bpy.data.objects[\'' + obj.name + '\']' + '''
mouseController_ = mouse.Controller()
mousePosition_ = mathutils.Vector((mouseController_.position[0], mouseController_.position[1]))
'''
	outputCode += open(filePath, 'rb').read().decode('utf-8')
	print(outputCode)

	exec(outputCode)