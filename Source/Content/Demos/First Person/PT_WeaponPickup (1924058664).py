import cave

class PT_WeaponPickup(cave.Component):
	def start(self, scene: cave.Scene):
		self.scene = cave.getScene()
		self.transf = self.entity.getTransform()
		self.mesh = self.entity.getChild("Mesh")
		self.events = cave.getEvents()
		self.pickupPlayer = cave.Entity = None
		self.Timer1 = cave.SceneTimer()
		self.pickedUp = False
		pass

	def respawn(self):
		
		if self.Timer1.get() > 2:
			self.pickedUp = False
			self.Timer1.reset()

	def tryPickup(self):
		
		

		collision = self.scene.rayCast(self.transf.position, self.transf.position + self.transf.getUpVector() * 3, cave.BitMask(12))
		#self.scene.addDebugLine(self.transf.position, self.transf.position + self.transf.getUpVector() * 3, cave.Vector3(255,255,0))
		if collision.hit:
			
			if collision.entity.name == "Player":
				
				self.pickupPlayer = collision.entity 
				print("Trying WeaponPickup")
				self.pickupPlayer = self.pickupPlayer.getPy("FirstPersonController")
				sd = cave.playSound("gun-cocking-01.ogg")
				self.pickedUp = True
				self.pickupPlayer.weaponPickup(self)
				#print(self.mesh)
				self.Timer1.reset()
				

	def update(self):
		if self.pickedUp == False:
			self.tryPickup()
		self.respawn()
	def end(self, scene: cave.Scene):
		pass
	