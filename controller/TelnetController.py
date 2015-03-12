import telnetlib
import threading
import time
import os
import re
from model import ModelManager
import Smelted_Settings


# General Telnet operations in this class
class TelnetController(object):

	HOST = "localhost"
	PORT = 5250
	polling = False
	tn = None
	telnet_commands = []
	response_codes = [{"code": 200, "meaning": "OK"}]
	poll_rate = 0.1

	line = ''

	def __init__(self, host=HOST, port=PORT):
		self.telnet_commands = []

		print "attempting connection to " + host + ": " + str(port)
		try:
			self.tn = telnetlib.Telnet(host, port)
			self.connection_success()
		except:
			raise Exception("Could not connect, are the details correct?")
	
	def connection_success(self):
		message = self.tn.read_until("100 VTR Ready", 3000)
		if message.find("100 VTR Ready") >= 0:
			print message,
			self.start_polling()
		else:
			raise Exception("Expected '100 VTR Ready', is there something wrong with the server?")

	# Adds a command to a queue
	def push_command(self, command, timeout=5000, match=None, callback=None, process_callback=None, data=None):
		self.telnet_commands.append({"command": command, "time_created": int(round(time.time() * 1000)), "timeout": timeout, "match": match, "callback": callback, "process_callback": process_callback, "data": data})
		if len(self.telnet_commands) == 1:
			self.execute_command(command)

	# Runs telnet commands
	def execute_command(self, command):
		self.line = ''
		print(command)
		self.tn.write(command + "\r\n")

	def start_polling(self):
		self.polling = True
		threading.Timer(self.poll_rate, self.poll_telnet).start()

	def stop_polling(self):
		self.polling = False

	# Runs a timer loop that checks telnet output and runs commands if pending every 100 milliseconds
	def poll_telnet(self):
		if self.polling:
			try:
				self.line += self.tn.read_very_eager()
			except EOFError as e:
				print "EOFError: " + str(e)
				self.disconnect()
				return
			if self.line != '':
				i = 0
				while i < len(self.response_codes):
					if self.line.find(str(self.response_codes[i]['code'])) >= 0:
						if self.response_codes[i]['code'] >= 300:
							print(str(self.response_codes[i]['code']) + "Error! not processing response any further")
							if len(self.telnet_commands) > 0:
								command = self.telnet_commands[0]
								self.remove_command(command)
								if len(self.telnet_commands) > 0:
									self.execute_command(self.telnet_commands[0]['command'])
									threading.Timer(self.poll_rate, self.poll_telnet).start()
									return
						else:
							if len(self.telnet_commands) > 0:
								command = self.telnet_commands[0]
								if command['match'] is None:
									self.remove_command(command)
									if len(self.telnet_commands) > 0:
										self.execute_command(self.telnet_commands[0]['command'])
										threading.Timer(self.poll_rate, self.poll_telnet).start()
										return
							break
					i += 1

			if len(self.telnet_commands) > 0:
				command = self.telnet_commands[0]

				# search for matches to callback to, if it hits timeout remove from telnet_command list
				if command['match']:
					if self.line != '':
						if re.search(command['match'], self.line):
							if command['process_callback']:
								if command['process_callback']:
									command['process_callback'](self.line, command['callback'], command['data'])
								elif command['callback']:
									command['callback']()

								self.remove_command(command)
								if len(self.telnet_commands) > 0:
									self.execute_command(self.telnet_commands[0]['command'])
								command = None
				if command:
					if int(round(time.time() * 1000)) - command['time_created'] > command['timeout']:

						if command['process_callback']:
							command['process_callback'](None, None, command['data'])
						elif command['callback']:
								command['callback']()

						self.remove_command(command)
						if len(self.telnet_commands) > 0:
							self.execute_command(self.telnet_commands[0]['command'])

						self.disconnect()
						raise Exception(command['command'] + ": Timed out, something probably went wrong. Please reconnect")

			threading.Timer(self.poll_rate, self.poll_telnet).start()

	def remove_command(self, command):
		print self.line.encode('utf-8'),
		self.line = ''
		self.telnet_commands.remove(command)

	def disconnect(self):
		self.polling = False
		self.tn.close()
		self.telnet_commands = []
		print("\nDisconnected from telnet")


# For executing melted specific commands
class MeltedTelnetController(TelnetController):

	def __init__(self, host, port):
		super(MeltedTelnetController, self).__init__(host, port)
		self.response_codes = [{"code": 200, "meaning": "OK"},
							{"code": 201, "meaning": "OK"},
							{"code": 202, "meaning": "OK"},
							{"code": 400, "meaning": "Unknown Command"},
							{"code": 401, "meaning": "Operation timed out"},
							{"code": 402, "meaning": "Argument Missing"},
							{"code": 403, "meaning": "Unit not found"},
							{"code": 404, "meaning": "Failed to locate or open clip"},
							{"code": 405, "meaning": "Argument value out of range"},
							{"code": 500, "meaning": "Server Error"}]
		# self.load_clip("U0", "/home/luke/Videos/trailer.mp4")
		# self.load_clip("U1", "/home/luke/Videos/video.mp4")
		# self.play_clip("U0")
		# self.clean_unit("U0")

	def create_melted_unit(self, device="sdl"):
		self.push_command("UADD " + device)

	def remove_melted_unit(self, unit_name):
		self.push_command("REMOVE " + unit_name)

	def load_clip(self, unit_name, path):
		self.push_command("LOAD " + unit_name + ' "' + os.path.normpath(path) + '"', 20000)

	def play_clip(self, unit_name):
		self.push_command("PLAY " + unit_name)

	def pause_clip(self, unit_name):
		self.push_command("PAUSE " + unit_name)

	def stop_clip(self, unit_name):
		self.push_command("STOP " + unit_name)
		self.push_command("GOTO " + unit_name + " 0")

	def next_clip(self, unit_name):
		self.push_command("GOTO " + unit_name + " 0 +1")

	def previous_clip(self, unit_name):
		self.push_command("GOTO " + unit_name + " 0 -1")

	def forward_clip(self, unit_name):
		self.push_command("FF " + unit_name)

	def rewind_clip(self, unit_name):
		self.push_command("REW " + unit_name)

	def remove_clip(self, unit_name, clip_index):
		self.push_command("REMOVE " + unit_name + " " + str(clip_index))

	def clip_end_event(self, unit_name, type):
		self.push_command("USET " + unit_name + " eof=" + type)

	def set_clip_in_point(self, unit, point, index):
		self.push_command("SIN " + str(unit) + " " + point + " " + index)

	def set_clip_out_point(self, unit, point, index):
		self.push_command("SOUT " + str(unit) + " " + point + " " + index)

	def append_clip_to_queue(self, unit, path):
		self.push_command("APND " + unit + ' "' + os.path.normpath(path) + '"')

	def goto_position_clip(self, unit, percent):
		self.push_command("GOTO " + unit + " 0")

	def clean_unit(self, unit):
		self.push_command("CLEAN " + unit, 10000)
		self.push_command("REMOVE " + unit, 10000)

	def get_units(self, callback):
		self.push_command("ULS", 10000, r"\r\n\r\n", callback, self.process_units)

	def get_unit_clips(self, unit, callback):
		self.push_command("LIST " + unit, 10000, r"\r\n\r\n", callback, self.process_clips, unit)

	def change_clip_index(self, unit, current_clip_index, target_clip_index):
		self.push_command("MOVE " + unit + " " + str(current_clip_index) + " " + str(target_clip_index))

	def get_eof_from_unit(self, unit, callback):
		self.push_command("UGET " + unit + " eof", 10000, r"202", callback, self.process_eof, unit)

	def process_units(self, result, callback, data):
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

	def process_clips(self, result, callback, data):
		if result:
			result = result.split("\r\n")
			i = 0
			results = []

			while i < len(result):
				if len(result[i]) > 2:
					if result[i][0].isdigit() and result[i][2] == '"':
						clip = result[i].split(" ")
						# used if there are spaces in the file path, there is probably a better method of doing this
						while len(clip) > 7:
							clip[1] = clip[1] + " " + clip[2]
							del clip[2]
						clip[1] = clip[1][1:-1]
						clip = {"index": clip[0], "path": clip[1], "clip_in": clip[2], "clip_out": clip[3], "length": clip[4], "calculated_length": clip[5], "fps": clip[6]}
						results.append(clip)

				i += 1
			if callback:
				callback(results, data)
			else:
				raise Exception("No Callback")
		else:
			print("No clips found on unit")

	def process_eof(self, result, callback, data):
		if result:
			list = ["pause", "loop", "stop", "continue"]
			for item in list:
				if result.find(item) >= 0:
					if callback:
						callback(item, data)
					return
			print("No eof found")
		else:
			print("No eof found")


class MeltedTelnetPollingController(TelnetController):

	def __init__(self, host, port):
		self.poll_rate = 0.5
		super(MeltedTelnetPollingController, self).__init__(host, port)
		self.response_codes = [{"code": 200, "meaning": "OK"},
							{"code": 201, "meaning": "OK"},
							{"code": 202, "meaning": "OK"},
							{"code": 400, "meaning": "Unknown Command"},
							{"code": 401, "meaning": "Operation timed out"},
							{"code": 402, "meaning": "Argument Missing"},
							{"code": 403, "meaning": "Unit not found"},
							{"code": 404, "meaning": "Failed to locate or open clip"},
							{"code": 405, "meaning": "Argument value out of range"},
							{"code": 500, "meaning": "Server Error"}]
		self.push_command("USTA " + Smelted_Settings.current_unit, 10000, r'[0-9]\r\n', self.update_gui, self.process_unit_status)

	# Runs telnet commands
	def execute_command(self, command):
		self.line = ''
		# print(command)
		self.tn.write(command + "\r\n")
		self.push_command("USTA " + Smelted_Settings.current_unit, 10000, r'[0-9]\r\n', self.update_gui, self.process_unit_status)

	def remove_command(self, command):
		# print self.line.encode('utf-8'),
		self.line = ''
		self.telnet_commands.remove(command)

	def process_unit_status(self, result, callback, data):
		if result:
			result = result.split("\r\n")
			i = 0
			unit_info = None

			while i < len(result):
				if len(result[i]) > 2:
					if result[i][0].isdigit() and result[i][1] == " ":
						unit_info = result[i].split(" ")
						match = re.search(r"(offline|not_loaded|playing|stopped|paused|disconnected|unknown)", unit_info[1])

						# See if success.
						if match:
							# 2 file paths makes this annoyingly complicated
							test_file = unit_info[2][1:-1]
							while not os.path.exists(test_file) and not os.path.isfile(test_file):
								unit_info[2] = unit_info[2] + " " + unit_info[3]
								del unit_info[3]
								test_file = unit_info[2][1:-1]
								if len(unit_info) < 5:
									print("Malformed unit info")
									return

							test_file_2 = unit_info[9][1:-1]
							while not os.path.exists(test_file_2) and not os.path.isfile(test_file_2):
								unit_info[9] = unit_info[9] + " " + unit_info[10]
								del unit_info[10]
								test_file_2 = unit_info[9][1:-1]
								if len(unit_info) < 5:
									print("Malformed unit info")
									return

							unit_info = {"unit": unit_info[0], "mode": unit_info[1], "path": test_file, "current_position": unit_info[3], "speed": unit_info[4], "fps": unit_info[5], "current_in_point": unit_info[6], "current_out_point": unit_info[7], "length": unit_info[8], "playlist_generation_number": unit_info[15], "clip_index": unit_info[16]}

						else:
							print("Malformed unit info")
							return
				i += 1
			if callback:
				callback(unit_info, data)
			else:
				raise Exception("No Callback")
		else:
			print("No clips found on unit")

	def update_gui(self, result, data):
		clip_list = ModelManager.get_models(ModelManager.MODEL_CLIP)
		for clip in clip_list:
			if result["clip_index"] == clip.index and "U" + result["unit"] == clip.unit:
				clip.set_clip_progress(result["current_position"])
				break