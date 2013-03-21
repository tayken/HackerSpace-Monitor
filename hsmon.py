import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.ioloop
import tornado.options

import RPi.GPIO as GPIO
import subprocess
import re
from uuid import uuid4

class Sensor(object):
	callbacks = []
	switch = "static/images/open.jpg"
	tempHum = 'Initiatizing sensor'
	
	def register(self, callback):
		self.callbacks.append(callback)

	def unregister(self, callback):
		self.callbacks.remove(callback)
	
	def notifyCallbacks(self):
		sw = self.getSwitch()
		tempHum = self.getTempHum()
		for callback in self.callbacks:
			callback(sw, tempHum)

	def getSwitch(self):
		if GPIO.input(23) == 1:
			self.switch = "static/images/open.jpg"
		else:
			self.switch = "static/images/closed.jpg"

		print self.switch
		return self.switch
	
	def getTempHum(self):
		temp, hum = 0,0
		output = subprocess.check_output(["./Adafruit_DHT", "11", "8"]);
		matches = re.search("Temp =\s+([0-9.]+)", output)
		if (matches):
			temp = float(matches.group(1))
		matches = re.search("Hum =\s+([0-9.]+)", output)
		if (matches):
			hum = float(matches.group(1))

		self.tempHum = "Current Temperature: %.1f C, Current Humidity: %.1f %%" % (temp,hum)
		print self.tempHum
		return self.tempHum

class DetailHandler(tornado.web.RequestHandler):
	def get(self):
		session = uuid4()
		swData = self.application.sensor.switch
		tempData = self.application.sensor.tempHum
		self.render("index.html", session=session, switch=swData, temphum=tempData)

class StatusHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		self.application.sensor.register(self.callback)
	
	def on_close(self):
		self.application.sensor.unregister(self.callback)
	
	def on_message(self, message):
		pass
	
	def callback(self, swData, tempData):
		self.write_message('{"swData":"%s","tempData":"%s"}' % (swData,tempData))
		
class Application(tornado.web.Application):
	def __init__(self):
		self.sensor = Sensor()
		
		handlers = [
			(r'/', DetailHandler),
			(r'/status', StatusHandler)
		]
		
		settings = {
			'template_path': 'templates',
			'static_path': 'static'
		}
		
		tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == '__main__':
	tornado.options.parse_command_line()

	GPIO.setmode(GPIO.BCM)
	GPIO.setup(23,GPIO.IN)
	
	app = Application()
	server = tornado.httpserver.HTTPServer(app)
	server.listen(80)
	main_loop = tornado.ioloop.IOLoop.instance()
	scheduler = tornado.ioloop.PeriodicCallback(app.sensor.notifyCallbacks,5000,io_loop = main_loop)
	scheduler.start()
	main_loop.start()
