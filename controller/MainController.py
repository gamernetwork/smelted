from MainInterfaceController import MainInterfaceController
from TelnetController import MeltedTelnetController
from UnitController import InitialiseUnitsController
from view import MainInterfaceView
from gi.repository import Gtk
from model import ModelManager


class MainController():

	main_interface_controller = None
	telnet_controller = None
	unit_controller = None

	def __init__(self):
		# sets up telnet interface
		self.telnet_controller = MeltedTelnetController()

		# manages melted units, existing units and their clips
		self.unit_controller = InitialiseUnitsController(self.telnet_controller, self.on_loaded_from_telnet)

		# Sets up GUI with pygtk and their event listeners
		self.main_interface_controller = MainInterfaceController(self.telnet_controller)
		main_interface_controller = MainInterfaceView.MainInterfaceView(self.main_interface_controller)

		try:
			Gtk.main()
			self.telnet_controller.disconnect()
		except KeyboardInterrupt:
			if self.telnet_controller is not None:
				self.telnet_controller.disconnect()

	def on_loaded_from_telnet(self):
		self.main_interface_controller.populate_info()