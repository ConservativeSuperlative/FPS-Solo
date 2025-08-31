import cave

class PY_Inv_Cell(cave.Component):
	def start(self, scene: cave.Scene):
		self.scene = scene
		self.ent = self.getEntity()
		self.transf = self.ent.getTransform()
		
		self.ui = self.ent.get("UI Element")
		self.uiComp : cave.UIElementComponent = self.ent.get("UIElementComponent")
		
		self.x = 0
		
		pass

	def update(self):
		events = cave.getEvents()
		#print(self.style)
		#self.x += 1
		#print(self.ent.name)
		#print(self.pos)
		#print(self.ent.getComponents())
		
	def end(self, scene: cave.Scene):
		pass
	