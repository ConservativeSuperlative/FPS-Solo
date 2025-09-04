import cave

class CompassComponent(cave.Component):
	def start(self, scene: cave.Scene):
		self.scene = scene
		self.icons = []
		self.pyList = ["Sentry", "Enemy"]
		self.Ents = self.scene.getEntitiesWithTag("IconEnt")
		pass

	def update(self):
		events = cave.getEvents()
		#self.Ents = self.scene.getEntitiesWithTag("IconEnt")
		if len(self.Ents) > 0:
			#print(len(self.Ents))
			for ent in self.Ents:
				asset = self.Ents.pop(self.Ents.index(ent))
				
				if not asset.name in self.icons:
					print(f'Popped {ent.name}')
					print(f'{asset.name} - New')
					assetPY = asset.getPy(self.findPY(asset))
					#assetPY = asset.getPy("PythonComponent")
					
					print("check1")
					
					
					#print(asset.name)
					#img = asset.getPy("Sentry")
					img = assetPY.iconRef
					icon : cave.Entity = self.scene.addFromTemplate("CompassIcon")
					#icon.setParent(self.entity)
					icon.name = f'{asset.name}_Icon'
					self.icons.append(asset.name)
					iconUI : cave.UIElementComponent = icon.getChild("IconImage").get("UIElementComponent")
					iconUI.position.setRelativeX(-.25)
					pycon = iconUI.entity.getPy("PythonComponent")
					print(pycon.getCustomName())
					
				else:
					print(f'{asset.name} - Old')
					print("Check2")
				#self.entity.add
	def findPY(self, ent : cave.Entity):
		python = "None"
		for py in self.pyList:
			if ent.getPy(py) != None:
				
				return(py)
			
			

	def end(self, scene: cave.Scene):
		pass
	