import ModelManager

class Unit():
	unit_name = None
	type = None
	online = None
	end_of_file = "pause"


class Clip():
	CLIP_PROGRESS = "clip_progress"

	unit = None
	index = None
	path = None
	clip_in = None
	clip_out = None
	length = 0
	calculated_length = 0
	fps = 0
	progress = 0
	looping = False

	def set_clip_progress(self, clip_progress):
		if self.progress == clip_progress:
			return
		self.progress = clip_progress
		ModelManager.on_model_attribute_changed(self, self.CLIP_PROGRESS)

	def set_clip_in(self, clip_in):
		if self.clip_in == clip_in:
			return
		self.clip_in = clip_in