import cave

class Sentry(cave.Component):
	def start(self, scene: cave.Scene):
		self.scene = scene
		self.target : cave.Entity = None
		self.mesh = self.entity.getChild("Mesh")
		self.anim : cave.AnimationComponent = self.mesh.get("AnimationComponent")
		self.character : cave.CharacterComponent = self.entity.get("CharacterComponent")
		self.transf = self.entity.getTransform()
		self.pos = self.transf.position
		self.pos = self.pos + cave.Vector3(0,2,0)
		self.cooldownTimer = cave.SceneTimer()
	def update(self):
		

		#self.scene.addDebugSphere(self.pos, 1, cave.Vector3(255, 0, 0), 12)
		#self.scene.addDebugLine(self.pos, self.pos + (self.transf.getForwardVector() * 6) - cave.Vector3(0,.3,0), cave.Vector3(255, 0, 0))
		#self.scene.addDebugLine(self.pos, self.targetPos, cave.Vector3(255, 0, 0))
		scan = self.scene.rayCast(self.pos, self.pos + (self.transf.getForwardVector() * 8) - cave.Vector3(0,.3,0), cave.BitMask(15))
		if scan.hit:
			#self.transf.lookAtSmooth(scan.position, .02, cave.Vector3(0, 1, 0))
			if scan.entity.name == "Player":
				print("Player Hit")
				self.target = scan.entity
				self.anim.playByName("BlackOps_Rifle_Idle_Aim", .2)
				self.cooldownTimer.reset()
				#self.transf.lookAtSmooth(self.target.getTransform().position, .02, self.transf.getUpVector())
		else:
			self.anim.playByName("BlackOps_Unarmed_Idle", .2)
			#self.transf.rotateOnYaw(.06, False)
			if self.cooldownTimer.get() > 10:
				self.target = None
		
		if self.target:
			self.transf.lookAtSmooth(self.target.getTransform().getForwardVector(), .04, self.transf.getUpVector())
			#self.character.setWalkDirection(0,0,-2 * cave.getDeltaTime())
			pass
	def end(self, scene: cave.Scene):
		pass
	