from Controller import Controller
from model import ModelManager
from FileDialogController import FileDialogController
from view.FileDialogView import FileDialogView
import os


class MainInterfaceController(Controller):

	melted_telnet_controller = None
	main_controller = None
	file_dialog_controller = None

	playlist_list_store = None
	unit_list_store = None

	def __init__(self, main_controller, melted_telnet_controller):
		self.main_controller = main_controller
		self.melted_telnet_controller = melted_telnet_controller

	def on_view_added(self, view):
		self.playlist_list_store = self.view.builder.get_object("playlist_list_store")
		self.unit_list_store = self.view.builder.get_object("unit_list_store")
		ModelManager.register_on_model_added_callback(self.refresh_clips, ModelManager.MODEL_CLIP)
		ModelManager.register_on_model_added_callback(self.refresh_units, ModelManager.MODEL_UNIT)

	def add_file_handler(self, paths):
		if len(paths) > 0:
			path = paths[0]
			self.melted_telnet_controller.append_clip_to_queue("U0", path)
			self.main_controller.get_initialise_units_controller().find_clips_on_unit(ModelManager.get_models(ModelManager.MODEL_UNIT)[0]['model'])
		else:
			print("No file selected")

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

	def refresh_clips(self):
		self.playlist_list_store.clear()
		clips = ModelManager.get_models(ModelManager.MODEL_CLIP)
		for clip in clips:
			clip = clip['model']
			self.playlist_list_store.append([os.path.basename(clip.path)])

	def refresh_units(self):
		self.unit_list_store.clear()
		units = ModelManager.get_models(ModelManager.MODEL_UNIT)
		for unit in units:
			unit = unit['model']
			self.unit_list_store.append(["Unit: " + str(unit.unit_name)])