

class Controller():

	view = None

	def __init__(self):
		pass

	def set_view(self, view):
		self.view = view
		self.on_view_added(self.view)

	def on_view_added(self, view):
		pass