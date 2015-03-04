from gi.repository import Gtk
from View import View


class GtkView(View, Gtk.Window):

	def __init__(self, controller):
		super(GtkView, self).__init__(controller)