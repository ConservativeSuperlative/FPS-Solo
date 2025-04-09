import cave

class MY_FPS_Char(cave.Component):
	walkSpeed = 5.0
	runSpeed = 8.0
	def start(self, scene: cave.Scene):
		self.transf = self.entity.getTransform()
		self.character : cave.CharacterComponent = self.entity.get("Character")
		self.cam = self.entity.getChild("Camera")
		self.camTransf = self.cam.getTransform()
		self.shotTimer = cave.SceneTimer()
		self.mesh = self.entity.getChild("SK_Mannequin_Arms")
		self.animator : cave.AnimationComponent = self.mesh.get("Animation")
		pass
	def movement(self):
		dt = cave.getDeltaTime()
		events = cave.getEvents()
		crouchOffset = cave.Vector3(0, 2, 0)
		defaultOffset = cave.Vector3(0, 1, 0)
		x = events.active(cave.event.KEY_A) - events.active(cave.event.KEY_D)
		z = events.active(cave.event.KEY_W) - events.active(cave.event.KEY_S)
		
		isRunning = events.active(cave.event.KEY_LSHIFT)
		self.movementState = 0

		dir = cave.Vector3(x, 0, z) 
		if dir.length() > 0.0:
			dir.normalize()

			if isRunning:
				dir *= self.runSpeed
				self.movementState = 2
				self.animator.playByName("FP_Rifle_Run", 0, 1, True, 0)
			else:
				dir *= self.walkSpeed
				self.movementState = 1
				self.animator.playByName("FP_Rifle_Idle", 0, 1, True, 0)
		self.character.setWalkDirection(dir * dt)
#JUMP
		if events.pressed(cave.event.KEY_SPACE):
			if self.character.onGround():
				self.character.jump()
				self.animator.playByName("FP_Rifle_Jump", 0, 1, False, 1)
				if not self.character.onGround():
					self.animator.playByName("FP_Rifle_Falling", 0, 1, False, 1)
				self.animator.playByName("FP_Rifle_Land", 0, 1, False, 1)
#Crouch		
		if events.pressed(cave.event.KEY_LCTRL):
			self.character.shape.offset = crouchOffset
			self.walkSpeed = 2
		if events.released(cave.event.KEY_LCTRL):
			self.character.shape.offset = defaultOffset
			self.walkSpeed = 5
			
	def mouselook(self, sens=-0.012):
		events = cave.getEvents()
		events.setRelativeMouse(True)

		motion = events.getMouseMotion() * sens

		self.transf.rotateOnYaw(motion.x)
		self.camTransf.rotateOnPitch(motion.y)
		
		# Limiting the Camera Rotation:
		self.camTransf.setEuler(
			cave.Vector3(
				cave.math.clampEulerAngle(self.camTransf.euler.x, 90, 270), 
				self.camTransf.euler.y, 
				self.camTransf.euler.z
			))
	
	def shoot(self):
		events = cave.getEvents()
		scene = cave.getScene()
		cam = scene.getCamera()
		shotSounds = ["bang-01", "bang-02", "bang-03", "bang-04", "bang-05", "bang-06"]
		# If the Player is holding the Left Mouse Button, it should be able to shoot.
		# But I'm also using a timer to limit how many bullets per second it will be
		# able to shoot. Otherwise, it will become a mess!
		if events.active(cave.event.MOUSE_LEFT) and self.shotTimer.get() > 0.3:
			self.animator.playByName("FP_Rifle_Fire", 0, 1, False, 1)
			
			sd = cave.playSound(f'{shotSounds[cave.random.randint(0, len(shotSounds) -1)]}.ogg')
			#sd = cave.playSound("bang-04.ogg")
			#sd.pitch = cave.random.uniform(0.4, 1.0)
			self.shotTimer.reset()

	def update(self):
		events = cave.getEvents()
		self.movement()
		self.mouselook()
		self.shoot()
	def end(self, scene: cave.Scene):
		pass
	