class Unit():
	unit_name = None
	type = None
	online = None


class Clip():
	unit = None
	index = None
	path = None
	clip_in = None
	clip_out = None
	end_of_file = "pause"
	length = 0
	calculated_length = 0
	fps = 0
	progress = 0
	looping = False