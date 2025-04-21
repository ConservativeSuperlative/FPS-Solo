import cave

class StandardMag(cave.Component):

	def start(self, scene: cave.Scene):
		self.scene = cave.getScene()
		self.transf = self.entity.getTransform()
		self.mesh = self.entity.getChild("Mesh")
		self.events = cave.getEvents()
		self.ammo = 30
		self.pickupPlayer = cave.Entity = None
		self.Timer1 = cave.SceneTimer()
		self.pickedUp = False
		#self.light = self.entity.getChild("Light")
		self.icon = self.entity.getChild("Icon")
	def respawn(self):
		
		if self.Timer1.get() > 5:
			self.pickedUp = False
			#self.light.activate(self.scene)
			self.Timer1.reset()
		
	def nearestPlayer(self):
		scene = cave.getScene()
		PlayerList = scene.getEntitiesWithTag(tag="Player")
		player : cave.Entity = PlayerList[0]
		return(player)
	def pickup(self, collision):
		if collision.entity.name == "Player":
					#print(collision.entity.name)
				self.pickupPlayer = collision.entity 
				
				self.pickupPlayer = self.pickupPlayer.getPy("FirstPersonController")
					#print(self.pickupPlayer.getCustomName())
				self.pickupPlayer.ammoPickup(self.ammo)
				sd = cave.playSound("gun-cocking-01.ogg")
				self.pickedUp = True
				#self.light.deactivate(self.scene)
				self.Timer1.reset()
				self.entity.scheduleKill(.05)
	def tryPickup(self):
		
			#collisionList = [cave.RayCastOut]

		collision = self.scene.rayCast(self.transf.position, self.transf.position + self.transf.getUpVector() * 3, cave.BitMask(12))
		if collision.hit:
			self.pickup(collision)
			
	def update(self):
		if self.pickedUp == False:
			
			self.tryPickup()
			self.icon.getTransform().lookAtSmooth(self.transf.getPosition() - self.nearestPlayer().getTransform().getPosition() + cave.Vector3(0,200,0),.2, self.transf.getUpVector())
	
		self.respawn()
		
		'''collision = self.scene.checkContactSphere(self.transf.position, 4, cave.BitMask(12))
		if len(collision) > 0:
			for x in collision:
				if x.entity.name == "Player":
					print(x.entity.uID)
					self.pickupPlayer = x.entity.getChild("FirstPersonController")
					self.entity.scheduleKill(2)
					self.pickupPlayer.ammoPickup(self.ammo)
				elif x.entity.name == "TestCharacter":
					
					print("ENEMY ALERT")'''

	def end(self, scene: cave.Scene):
		pass
	