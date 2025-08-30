import cave
import cave.network


class GameBall(cave.Component):
	def start(self, scene: cave.Scene):
		self.mesh = self.entity.getChild("Mesh")
		self.transf = self.entity.getTransform()
		self.mesh : cave.MeshComponent = self.mesh.get("MeshComponent")
		self.transf = self.entity.getTransform()
		
		self.temptint : cave.Vector4 = cave.Vector4(1,1,1,1)
		pass

	def update(self):
		events = cave.getEvents()
		if events.pressed(cave.event.KEY_G):
			print("Fuck")
			self.mesh.tint.r = .5
			self.transf.setWorldPosition(self.entity.properties.get("targetPos"))

		if events.released(cave.event.KEY_G):
			print("Unfuck")
			self.mesh.tint.r = 1

	def end(self, scene: cave.Scene):
		pass
	