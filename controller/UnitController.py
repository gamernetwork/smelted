from Controller import Controller
from model import ModelManager, Models

class UnitsController():

	melted_telnet_controller = None
	main_controller = None

	def __init__(self, main_controller, melted_telnet_controller):
		self.melted_telnet_controller = melted_telnet_controller
		self.main_controller = main_controller

	def find_existing_units(self):
		self.melted_telnet_controller.get_units(self.add_units)

	def add_units(self, units):
		ModelManager.empty_model_list(ModelManager.MODEL_UNIT)

		for unit_object in units:
			unit = Models.Clip()
			unit.unit_name = unit_object['unit_name']
			unit.type = unit_object['type']
			unit.online = unit_object['online']
			ModelManager.register_model(unit, ModelManager.MODEL_UNIT)

	def find_clips_on_unit(self, unit_name):
		self.melted_telnet_controller.get_unit_clips(unit_name, self.add_clips)

	def get_eof_from_unit(self, unit_name):
		self.melted_telnet_controller.get_eof_from_unit(unit_name, self.set_eof_on_unit)

	def set_eof_on_unit(self, eof, unit_name):
		self.get_unit_by_name(unit_name).end_of_file = eof
		self.main_controller.get_main_interface_controller().update_eof_combo(int(unit_name[1]), eof, 1)

	def check_unit_exists(self, unit_name):
		units = ModelManager.get_models(ModelManager.MODEL_UNIT)
		for unit in units:
			if unit.unit_name == unit_name:
				return True
				break
		return False

	def get_unit_by_name(self, unit_name):
		units = ModelManager.get_models(ModelManager.MODEL_UNIT)
		for unit in units:
			if unit.unit_name == unit_name:
				return unit
		return None

	def clean_units(self):
		old_units = ModelManager.get_models(ModelManager.MODEL_UNIT)
		for unit in old_units:
			self.melted_telnet_controller.clean_unit(unit.unit_name)
			self.find_clips_on_unit(unit.unit_name)

	def add_clips(self, clips, unit_name):

		clip_models = ModelManager.get_models(ModelManager.MODEL_CLIP)
		for clip in clip_models:
			if clip.unit == unit_name:
				ModelManager.remove_model(clip, ModelManager.MODEL_CLIP)

		for clip_object in clips:
			clip = Models.Clip()
			clip.unit = unit_name
			clip.index = clip_object['index']
			clip.path = clip_object['path']
			clip.clip_in = clip_object['clip_in']
			clip.clip_out = clip_object['clip_out']
			clip.length = clip_object['length']
			clip.calculated_length = clip_object['calculated_length']
			clip.fps = clip_object['fps']

			ModelManager.register_model(clip, ModelManager.MODEL_CLIP)

		if len(clips) == 0:
			self.main_controller.get_main_interface_controller().refresh_clips()


# used for getting the initial state of the server, should not be used for general playlist operations
class InitialiseUnitsController(Controller):

	melted_telnet_controller = None
	main_controller = None

	pending_unit_processing = []

	loaded_callback = None

	def __init__(self, main_controller, melted_telnet_controller, loaded_callback):
		self.main_controller = main_controller
		self.melted_telnet_controller = melted_telnet_controller
		self.loaded_callback = loaded_callback
		self.find_existing_units()

	def find_existing_units(self):
		self.melted_telnet_controller.get_units(self.add_units)

	def find_all_existing_clips(self, units):
		if len(units) > 0:
			self.pending_unit_processing = units
			self.find_clips_on_unit(units[0].unit_name)
		else:
			print("No units to find clips on")

	def find_clips_on_unit(self, unit_name):
		self.melted_telnet_controller.get_unit_clips(unit_name, self.add_clips)

	def add_units(self, units):
		unit_list = []
		for unit_object in units:
			unit = Models.Unit()
			unit.unit_name = unit_object['unit_name']
			unit.type = unit_object['type']
			unit.online = unit_object['online']
			unit_list.append(unit)
			ModelManager.register_model(unit, ModelManager.MODEL_UNIT)
			self.get_eof_from_unit(unit.unit_name)

		self.find_all_existing_clips(unit_list)

	def get_eof_from_unit(self, unit_name):
		self.melted_telnet_controller.get_eof_from_unit(unit_name, self.set_eof_on_unit)

	def set_eof_on_unit(self, eof, unit_name):
		self.get_unit_by_name(unit_name).end_of_file = eof
		self.main_controller.get_main_interface_controller().update_eof_combo(int(unit_name[1]), eof, 1)

	def get_unit_by_name(self, unit_name):
		units = ModelManager.get_models(ModelManager.MODEL_UNIT)
		for unit in units:
			if unit.unit_name == unit_name:
				return unit
		return None

	def add_clips(self, clips, unit_name):
		unit = self.pending_unit_processing.pop(0)

		for clip_object in clips:
			clip = Models.Clip()
			clip.unit = unit.unit_name
			clip.index = clip_object['index']
			clip.path = clip_object['path']
			clip.clip_in = clip_object['clip_in']
			clip.clip_out = clip_object['clip_out']
			clip.length = clip_object['length']
			clip.calculated_length = clip_object['calculated_length']
			clip.fps = clip_object['fps']

			ModelManager.register_model(clip, ModelManager.MODEL_CLIP)

		if len(self.pending_unit_processing) > 0:
			self.melted_telnet_controller.get_unit_clips(self.pending_unit_processing[0].unit_name, self.add_clips)
		else:
			self.loaded_callback()