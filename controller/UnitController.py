from Controller import Controller
from model import ModelManager, Models


class InitialiseUnitsController(Controller):

	melted_telnet_controller = None

	pending_unit_processing = []

	loaded_callback = None

	def __init__(self, melted_telnet_controller, loaded_callback):
		self.melted_telnet_controller = melted_telnet_controller
		self.loaded_callback = loaded_callback
		self.find_existing_units()

	def find_existing_units(self):
		self.melted_telnet_controller.get_units(self.add_units)

	def find_all_existing_clips(self, units):
		if len(units) > 0:
			self.pending_unit_processing = units
			self.find_clips_on_unit(units[0])
		else:
			print("No units to find clips on")

	def find_clips_on_unit(self, unit):
		self.melted_telnet_controller.get_unit_clips(unit.unit_name, self.add_clips)

	def add_units(self, units):
		unit_list = []
		for unit_object in units:
			unit = Models.Unit()
			unit.unit_name = unit_object['unit_name']
			unit.type = unit_object['type']
			unit.online = unit_object['online']
			unit_list.append(unit)
			ModelManager.register_model(unit, ModelManager.MODEL_UNIT)

		self.find_all_existing_clips(unit_list)

	def add_clips(self, clips):
		if len(self.pending_unit_processing) > 0:
			unit = self.pending_unit_processing.pop()
		else:
			unit = ModelManager.get_models(ModelManager.MODEL_UNIT)[0]['model']

		clip_models = ModelManager.get_models(ModelManager.MODEL_CLIP)
		clip_model_index = 0
		for clip_object in clips:
			if clip_model_index < len(clip_models):
				clip = clip_models[clip_model_index]['model']
			else:
				clip = Models.Clip()

			clip.unit = unit.unit_name
			clip.index = clip_object['index']
			clip.path = clip_object['path']
			clip.clip_in = clip_object['clip_in']
			clip.clip_out = clip_object['clip_out']
			clip.length = clip_object['length']
			clip.calculated_length = clip_object['calculated_length']
			clip.fps = clip_object['fps']

			if clip_model_index >= len(clip_models):
				ModelManager.register_model(clip, ModelManager.MODEL_CLIP)
			clip_model_index += 1

		if len(self.pending_unit_processing) > 0:
			self.melted_telnet_controller.get_unit_clips(unit.unit_name, self.add_clips)
		else:
			self.loaded_callback()