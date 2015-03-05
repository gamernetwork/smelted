import telnetlib
import threading
import re
import time


# General Telnet operations in this class
class TelnetController(object):

	HOST = "localhost"
	PORT = 5250
	polling = False
	tn = None
	input_blocked = True
	telnet_callbacks = None

	def __init__(self, host=HOST, port=PORT):
		self.telnet_callbacks = []

		print "attempting connection to " + host + ": " + str(port)
		try:
			self.tn = telnetlib.Telnet(host, port)
		except:
			raise Exception("Could not connect, are the details correct?")
		message = self.tn.read_until("100 VTR Ready", 3000)
		if re.match(message, "100 VTR Ready"):
			print message,
		else:
			# possible error here
			print message,
		self.start_polling()

	def write_commands(self):
		while 1:
			if not self.input_blocked:
				command = raw_input("> ")
				self.input_blocked = True
				self.tn.write(command + "\r\n")
				if command == "exit":
					self.disconnect()
					break

	def push_command(self, command, match=None, timeout=1000, process_callback=None, callback=None):
		print(command)
		self.tn.write(command + "\r\n")

		if match:
			self.telnet_callbacks.append({"match": match, "time_created": int(round(time.time() * 1000)), "timeout": timeout, "process_callback": process_callback, "callback": callback})

	def start_polling(self):
		self.polling = True
		threading.Timer(0.5, self.poll_for_output).start()

	def stop_polling(self):
		self.polling = False

	def poll_for_output(self):
		if self.polling:
			try:
				line = self.tn.read_very_eager()
			except EOFError as e:
				print "EOFError: " + str(e)
				self.disconnect()
				return
			if line != '':
				print line.encode('utf-8'),
			else:
				self.input_blocked = False

			# search for matches to callback to, if it hits timeout remove from checks
			for callback in self.telnet_callbacks:
				if line != '':
					if line.find(callback['match']) >= 0:
						if callback['process_callback']:
							self.telnet_callbacks.remove(callback)
							callback['process_callback'](line, callback['callback'])
							continue

				if int(round(time.time() * 1000)) - callback['time_created'] > callback['timeout']:
					callback['process_callback'](None, None)
					self.telnet_callbacks.remove(callback)

			threading.Timer(0.1, self.poll_for_output).start()

	def disconnect(self):
		self.polling = False
		self.tn.close()
		print("Disconnected from telnet")


# For melted specific commands
class MeltedTelnetController(TelnetController):

	def __init__(self):
		super(MeltedTelnetController, self).__init__()
		# self.load_clip(0, "/home/luke/Videos/trailer.mp4")
		# self.load_clip(1, "/home/luke/Videos/video.mp4")
		# self.play_clip(0)

	def create_melted_unit(self, device="sdl"):
		self.push_command("UADD " + device)

	def remove_melted_unit(self, unit):
		self.push_command("REMOVE U" + str(unit))

	def load_clip(self, unit, path):
		self.push_command("LOAD U" + str(unit) + " " + path)

	def play_clip(self, unit):
		self.push_command("PLAY U" + str(unit))

	def pause_clip(self, unit):
		self.push_command("PAUSE U" + str(unit))

	def stop_clip(self, unit):
		self.push_command("STOP U" + str(unit))
		self.push_command("GOTO U" + str(unit) + " 0")

	def forward_clip(self, unit):
		self.push_command("FF U" + str(unit))

	def rewind_clip(self, unit):
		self.push_command("REW U" + str(unit))

	def loop_clip(self, unit):
		self.push_command("USET U" + str(unit) + " eof=loop")

	def stop_looping_clip(self, unit):
		# TODO stop looping, currently not working
		self.push_command("USET U" + str(unit))

	def append_clip_to_queue(self, unit, clip):
		self.push_command("APND U" + str(unit) + " " + clip)

	def goto_position_clip(self, unit, percent):
		self.push_command("GOTO U" + str(unit) + " 0")

	def get_units(self, callback):
		self.push_command("ULS", "U0", 1000, self.process_units, callback)

	def get_unit_clips(self, unit, callback):
		self.push_command("LIST " + unit, ' "', 1000, self.process_clips, callback)

	def process_units(self, result, callback):
		if result:
			result = result.split("\r\n")
			i = 0
			results = []
			while i < len(result):
				if len(result[i]) > 0:
					if result[i][0] == "U" and result[i][1].isdigit():
						unit = result[i].split(" ")
						unit = {"unit_name": unit[0], "??": unit[1], "type": unit[2], "online": unit[3]}
						results.append(unit)

				i += 1
			if callback:
				callback(results)
			else:
				raise Exception("No Callback")
		else:
			print("No units found")

	def process_clips(self, result, callback):
		if result:
			result = result.split("\r\n")
			i = 0
			results = []

			while i < len(result):
				if len(result[i]) > 2:
					if result[i][0].isdigit() and result[i][2] == '"':
						clip = result[i].split(" ")
						clip = {"index": clip[0], "path": clip[1], "clip_in": clip[2], "clip_out": clip[3], "length": clip[4], "fps": clip[5]}
						results.append(clip)

				i += 1
			if callback:
				callback(results)
			else:
				raise Exception("No Callback")
		else:
			print("No clips found on unit")