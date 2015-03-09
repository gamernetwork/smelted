from lxml import etree
from model import ModelManager

class PlaylistFileController:

	def __init__(self):
		pass

	def import_playlist(self, file):
		tree = etree.parse(file)
		root = tree.getroot()

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
		file.write(xml_string)
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