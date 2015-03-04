from MainInterfaceController import MainInterfaceController
from TelnetController import MeltedTelnetController
from UnitController import UnitController
from view import MainInterfaceView
from gi.repository import Gtk
from model import ModelManager

def on_loaded_from_telnet():
	main_interface_controller.populate_info()

# sets up telnet interface
telnetController = None
telnetController = MeltedTelnetController()

# manages melted units, existing units and their clips
unit_controller = UnitController(telnetController)

# Sets up GUI with pygtk and their event listeners
main_interface_controller = MainInterfaceController(telnetController)
MainInterfaceView.MainInterfaceView(main_interface_controller)

try:
	Gtk.main()
	telnetController.disconnect()
except KeyboardInterrupt:
	if telnetController is not None:
		telnetController.disconnect()