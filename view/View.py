

class View(object):

	controller = None

	def __init__(self, controller):
		controller.set_view(self)
		self.controller = controller