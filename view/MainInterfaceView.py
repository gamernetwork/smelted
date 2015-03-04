#!/usr/bin/python
from gi.repository import Gtk
from GtkView import GtkView


class MainInterfaceView(GtkView):

	def __init__(self, main_interface_controller):
		super(MainInterfaceView, self).__init__(main_interface_controller)

		self.gladefile = "view/designs/test.glade"
		self.builder = Gtk.Builder()
		self.builder.add_from_file(self.gladefile)
		self.builder.connect_signals(self)
		self.window = self.builder.get_object("main_interface_window")
		self.slider = self.builder.get_object("seek_bar")
		self.playlist_list_view = self.builder.get_object("playlist_list_view")
		self.slider.set_range(0, 100)
		self.window.show()

	def on_window1_destroy(self, object, data=None):
		Gtk.main_quit()

	def on_gtk_quit_activate(self, menuitem, data=None):
		Gtk.main_quit()

	def on_filechooserbutton_file_set(self, file_chooser_button, data=None):
		self.controller.change_file_handler(file_chooser_button.get_filenames())

	def on_play_button_clicked(self, button, data=None):
		self.controller.play_handler()

	def on_pause_button_clicked(self, button, data=None):
		self.controller.pause_handler()

	def on_stop_button_clicked(self, button, data=None):
		self.controller.stop_handler()

	def on_forward_button_clicked(self, button, data=None):
		self.controller.forward_handler()

	def on_rewind_button_clicked(self, button, data=None):
		self.controller.rewind_handler()

	def on_loop_toggle_button_toggled(self, button, data=None):
		self.controller.loop_handler(button.get_active())

	def on_seek_bar_button_release_event(self, seek_bar, data=None):
		self.controller.seek_bar_button_release_handler(seek_bar.get_value())