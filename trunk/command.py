
class Command:
	"""
	decorator for text command functions to flag them as commands 
	and specify their access level
	"""
	
	def __init__(self, public=False):
		"""set access level"""
		
		self.public = public
		
	def __call__(self, *args):
		"""bind command on first call"""

		if not hasattr(self, "_command"):
			self._command = args[0]
			return self
		else:
			return self._command(*args)