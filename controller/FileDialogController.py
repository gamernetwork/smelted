from Controller import Controller
from gi.repository import Gtk


class FileDialogController(Controller):

	callback = None

	def __init__(self):
		pass

	def show_open_dialog(self, callback):
		self.callback = callback
		self.view.open_dialog(Gtk.FileChooserAction.OPEN, "Please choose a playlist XML file")

	def show_save_dialog(self, callback):
		self.callback = callback
		self.view.open_dialog(Gtk.FileChooserAction.SAVE, "Please choose a file to save to")

	def on_close_dialog(self, file):
		if self.callback:
			self.callback(file)