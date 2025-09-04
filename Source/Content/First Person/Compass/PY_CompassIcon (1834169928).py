import cave

class CompassIcon(cave.Component):
	newID = 0
	def start(self, scene: cave.Scene):
		
		self.scene = scene
		self.icon = self.entity.get("CompassIcon")
		
		pass
	
	def update(self):
		events = cave.getEvents()
		
		playerloc = self.scene.getEntitiesWithTag("Player")[0].getTransform().getWorldPosition()
		
		

			#self.ent.position.relativeX = int(self.uID / 1000)
	def bang(self):
		print("bang")
	def end(self, scene: cave.Scene):
		pass
	