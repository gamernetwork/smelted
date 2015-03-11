from Controller import Controller
from model import ModelManager
from FileDialogController import FileDialogController
from view.FileDialogView import FileDialogView
import Smelted_Settings
from gi.repository import GObject, Gtk
import os


class MainInterfaceController(Controller):

	melted_telnet_controller = None
	main_controller = None
	file_dialog_controller = None

	playlist_list_store = None
	unit_list_store = None
	end_event_list_store = None

	end_event_list_items = None

	unit_tree_view = None
	playlist_tree_view = None

	refreshing_clips = False

	def __init__(self, main_controller, melted_telnet_controller):
		self.main_controller = main_controller
		self.melted_telnet_controller = melted_telnet_controller

	def on_view_added(self, view):
		self.playlist_list_store = self.view.builder.get_object("playlist_list_store")
		self.unit_list_store = self.view.builder.get_object("unit_list_store")
		self.unit_tree_view = self.view.builder.get_object("unit_tree_view")
		self.playlist_tree_view = self.view.builder.get_object("playlist_tree_view")

		# create combo box column on playlist tree view, should be moved to view if time allows
		end_event_list_store = Gtk.ListStore(str)
		self.end_event_list_items = ["Stop", "Loop", "Continue", "Pause"]
		for item in self.end_event_list_items:
			end_event_list_store.append([item])

		renderer_combo = Gtk.CellRendererCombo()
		renderer_combo.set_property("editable", True)
		renderer_combo.set_property("model", end_event_list_store)
		renderer_combo.set_property("text-column", 0)
		renderer_combo.set_property("has-entry", False)
		renderer_combo.connect("edited", self.on_combo_changed)

		column_combo = Gtk.TreeViewColumn("Unit Ended Event", renderer_combo, text=1)
		self.unit_tree_view.append_column(column_combo)

		ModelManager.register_on_model_added_callback(self.refresh_clips, ModelManager.MODEL_CLIP)
		ModelManager.register_on_model_added_callback(self.add_unit, ModelManager.MODEL_UNIT)
		ModelManager.register_on_model_list_emptied_callback(self.remove_units, ModelManager.MODEL_UNIT)

	def add_file_handler(self, paths):
		if len(paths) > 0:
			path = paths[0]
			self.melted_telnet_controller.append_clip_to_queue(Smelted_Settings.current_unit, path)
			self.main_controller.get_units_controller().find_clips_on_unit(Smelted_Settings.current_unit)
		else:
			print("No file selected")

	def play_handler(self):
		self.melted_telnet_controller.play_clip(Smelted_Settings.current_unit)

	def pause_handler(self):
		self.melted_telnet_controller.pause_clip(Smelted_Settings.current_unit)

	def stop_handler(self):
		self.melted_telnet_controller.stop_clip(Smelted_Settings.current_unit)

	def next_clip_handler(self):
		self.melted_telnet_controller.next_clip(Smelted_Settings.current_unit)

	def previous_clip_handler(self):
		self.melted_telnet_controller.previous_clip(Smelted_Settings.current_unit)

	def remove_clip(self):
		model, list_iter = self.playlist_tree_view.get_selection().get_selected()
		if list_iter is None:
			return
		for item in model.get_path(list_iter):
			self.melted_telnet_controller.remove_clip(Smelted_Settings.current_unit, item)
			self.main_controller.get_units_controller().find_clips_on_unit(Smelted_Settings.current_unit)

	def loop_handler(self, active):
		if active:
			self.melted_telnet_controller.loop_clip(Smelted_Settings.current_unit)
		else:
			self.melted_telnet_controller.stop_looping_clip(Smelted_Settings.current_unit)

	def seek_bar_button_release_handler(self, percent):
		self.melted_telnet_controller.goto_position_clip(Smelted_Settings.current_unit, percent)

	def import_playlist_button_clicked(self):
		file_dialog_controller = FileDialogController()
		FileDialogView(file_dialog_controller)
		file_dialog_controller.show_open_dialog(self.main_controller.get_playlist_file_controller().import_playlist)

	def export_playlist_button_clicked(self):
		file_dialog_controller = FileDialogController()
		FileDialogView(file_dialog_controller)
		file_dialog_controller.show_save_dialog(self.main_controller.get_playlist_file_controller().export_playlist)

	def add_unit_button_clicked(self):
		self.melted_telnet_controller.create_melted_unit()
		self.main_controller.get_units_controller().find_existing_units()

	def unit_tree_view_cursor_changed(self, index):
		Smelted_Settings.current_unit = "U" + str(index)
		self.refresh_clips(None)

	def check_playlist_order_changed(self):
		if self.view.dragged_playlist():
			index = 0
			for item in self.playlist_list_store:
				if index != item[1]:
					self.melted_telnet_controller.change_clip_index(Smelted_Settings.current_unit, item[1], index)
					self.main_controller.get_units_controller().find_clips_on_unit(Smelted_Settings.current_unit)
					break
				index += 1

	def on_combo_changed(self, widget, path, text):
		self.unit_list_store[path][1] = text
		if text == self.end_event_list_items[0]:
			self.melted_telnet_controller.clip_end_event(Smelted_Settings.current_unit, "stop")
		elif text == self.end_event_list_items[1]:
			self.melted_telnet_controller.clip_end_event(Smelted_Settings.current_unit, "loop")
		elif text == self.end_event_list_items[2]:
			self.melted_telnet_controller.clip_end_event(Smelted_Settings.current_unit, "continue")
		elif text == self.end_event_list_items[3]:
			self.melted_telnet_controller.clip_end_event(Smelted_Settings.current_unit, "pause")


	def clear_list_model(self, store):
		store.clear()

	def update_list_model(self, store, data):
		store.append(data)

	# could optimise this, clears list on every new clip added
	def refresh_clips(self, clip=None):
		GObject.idle_add(self.clear_list_model, self.playlist_list_store)
		clips = ModelManager.get_models(ModelManager.MODEL_CLIP)
		clip_index = 0
		for clip in clips:
			if clip.unit == Smelted_Settings.current_unit:
				GObject.idle_add(self.update_list_model, self.playlist_list_store, [os.path.basename(clip.path), int(clip.index)])
				clip_index += 1

	def remove_units(self):
		GObject.idle_add(self.clear_list_model, self.unit_list_store)

	def add_unit(self, unit):
		GObject.idle_add(self.update_list_model, self.unit_list_store, ["Unit " + str(unit.unit_name)[1], "Pause"])