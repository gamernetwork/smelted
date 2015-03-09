from lxml import etree
from model import ModelManager

class PlaylistFileController:

	melted_telnet_controller = None
	main_controller = None

	def __init__(self, main_controller, melted_telnet_controller):
		self.melted_telnet_controller = melted_telnet_controller
		self.main_controller = main_controller

	def import_playlist(self, file):
		tree = etree.parse(file)
		playlist_root = tree.getroot()
		if playlist_root.tag == 'playlist':
			for unit in playlist_root:
				self.melted_telnet_controller.clean_unit(unit.attrib.get('name'))
				for clip in unit:
					self.melted_telnet_controller.append_clip_to_queue(unit.attrib.get('name'), clip.find("path").text)
					self.melted_telnet_controller.set_clip_in_point(unit.attrib.get('name'), clip.find("in").text, clip.get('index'))
					self.melted_telnet_controller.set_clip_out_point(unit.attrib.get('name'), clip.find("out").text, clip.get('index'))
					# some sort of memory error without doing this for every clip load :s
					self.main_controller.get_initialise_units_controller().find_clips_on_unit(ModelManager.get_models(ModelManager.MODEL_UNIT)[0]['model'])
		else:
			self.file_error()

	def file_error(self):
		raise Exception("Problem with XML file")

	def export_playlist(self, file):
		root = etree.Element('playlist')

		units = ModelManager.get_models(ModelManager.MODEL_UNIT)

		for unit in units:
			unit = unit['model']
			unit_element = etree.Element('unit', name=unit.unit_name)
			clips = self.get_unit_clips_as_xml(unit)
			for clip in clips:
				unit_element.append(clip)
			root.append(unit_element)

		xml_string = etree.tostring(root, pretty_print=True)
		file = open(file, 'w+')
		file.write('<?xml version="1.0" encoding="utf-8"?>\n' + xml_string)
		file.close()

	def get_unit_clips_as_xml(self, unit):
		clip_elements = []
		clips = ModelManager.get_models(ModelManager.MODEL_CLIP)
		for clip in clips:
			clip = clip['model']
			if clip.unit == unit.unit_name:
				clip_element = etree.Element('clip', index=clip.index, looping=str(clip.looping))

				path_element = etree.Element('path')
				path_element.text = clip.path

				in_element = etree.Element('in')
				in_element.text = clip.clip_in

				out_element = etree.Element('out')
				out_element.text = clip.clip_out

				clip_element.append(path_element)
				clip_element.append(in_element)
				clip_element.append(out_element)

				clip_elements.append(clip_element)

		return clip_elements