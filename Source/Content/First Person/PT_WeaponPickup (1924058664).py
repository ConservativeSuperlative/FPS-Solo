import cave

class PT_WeaponPickup(cave.Component):
	def start(self, scene: cave.Scene):
		self.scene = cave.getScene()
		self.transf = self.entity.getTransform()
		self.mesh = self.entity.getChild("Mesh")
		#self.rbc : cave.RigidBodyComponent = self.entity.getParent().get("RigidBodyComponent")
		self.events = cave.getEvents()
		self.pickupPlayer = cave.Entity = None
		self.Timer1 = cave.SceneTimer()
		self.pickedUp = False
		self.thumbnail : cave.ImageTexture = None
		pass

	def respawn(self):
		
		if self.Timer1.get() > 2:
			self.pickedUp = False
			self.Timer1.reset()
			
	def tryPickup(self):
		
		
		
		collision = self.scene.rayCast(self.transf.position, self.transf.position + self.transf.getUpVector() * 3, cave.BitMask(12))
		#collision = self.rbc.collidedWith("Player")
		#self.scene.addDebugLine(self.transf.position, self.transf.position + self.transf.getUpVector() * 3, cave.Vector3(255,255,0))
		if collision.hit:
			
			if collision.entity.name == "Player":
				
				self.pickupPlayer = collision.entity 
				
				self.pickupPlayer = self.pickupPlayer.getPy("FirstPersonController")
				self.pickedUp = True
				self.pickupPlayer.weaponPickup(self)
				#print(self.mesh)
				self.Timer1.reset()
				

	def update(self):
		if self.pickedUp == False:
			pass
			#self.tryPickup()
		elif self.pickedUp == True:
			self.entity.scheduleKill(.01)
		self.respawn()
	def end(self, scene: cave.Scene):
		pass
	