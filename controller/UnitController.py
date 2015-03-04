from Controller import Controller
from model import ModelManager, Models


class UnitController(Controller):

	melted_telnet_controller = None

	pending_unit_processing = []

	def __init__(self, melted_telnet_controller):
		self.melted_telnet_controller = melted_telnet_controller
		self.find_existing_units()

	def find_existing_units(self):
		self.melted_telnet_controller.get_units(self.add_units)

	def find_all_existing_clips(self, units):
		if len(self.pending_unit_processing) == 0:
			self.pending_unit_processing = units
			self.find_clips_on_unit(units[0])
		else:
			raise Exception("Already looking for clips, soz!")

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
		unit = self.pending_unit_processing.pop()

		for clip_object in clips:
			clip = Models.Clip()
			clip.unit = unit.unit_name
			clip.index = clip_object['index']
			clip.path = clip_object['path']
			clip.clip_in = clip_object['clip_out']
			clip.length = clip_object['length']
			clip.fps = clip_object['fps']

			ModelManager.register_model(clip, ModelManager.MODEL_CLIP)

		if len(self.pending_unit_processing) > 0:
			self.melted_telnet_controller.get_unit_clips(unit.unit_name, self.add_clips)
		else:
			# MainController.on_loaded_from_telnet()
			pass