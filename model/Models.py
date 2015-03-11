class Unit():
	unit_name = None
	type = None
	online = None
	end_of_file = "pause"


class Clip():
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