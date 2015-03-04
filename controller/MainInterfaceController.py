from Controller import Controller


class MainInterfaceController(Controller):

	melted_telnet_controller = None

	def __init__(self, melted_telnet_controller):
		self.melted_telnet_controller = melted_telnet_controller

	def change_file_handler(self, paths):
		path = paths[0]
		self.melted_telnet_controller.load_clip(0, path)

	def play_handler(self):
		self.melted_telnet_controller.play_clip(0)

	def pause_handler(self):
		self.melted_telnet_controller.pause_clip(0)

	def stop_handler(self):
		self.melted_telnet_controller.stop_clip(0)

	def rewind_handler(self):
		self.melted_telnet_controller.rewind_clip(0)

	def forward_handler(self):
		self.melted_telnet_controller.forward_clip(0)

	def loop_handler(self, active):
		if active:
			self.melted_telnet_controller.loop_clip(0)
		else:
			self.melted_telnet_controller.stop_looping_clip(0)

	def seek_bar_button_release_handler(self, percent):
		self.melted_telnet_controller.goto_position_clip(0, percent)

	def populate_info(self):
		self.view.builder.get_object("main_interface_window")