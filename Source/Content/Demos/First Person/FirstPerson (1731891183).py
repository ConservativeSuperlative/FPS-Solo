import cave


class FirstPersonController(cave.Component):
	walkSpeed = 5.0
	runSpeed = 8.0

	def start(self, scene: cave.Scene):
		self.transf = self.entity.getTransform()
		self.character : cave.CharacterComponent = self.entity.get("Character")
		self.cam = self.entity.getChild("Camera")
		self.camTransf = self.cam.getTransform()
		self.hm = self.entity.getChild("hitMarker")
		# This will control the fire rate...
		self.shotTimer = cave.SceneTimer()
		self.UI_Kills = self.entity.getChild("UI KillCount")
		self.UI_Ammo = self.entity.getChild("UI Ammo")
		self.UI_Health = self.entity.getChild("UI Health")
		self.UI_Heart_Full = self.entity.getChild("UI Heart_Full")
		self.UI_Ammo_Inv = self.entity.getChild("UI Ammo_Inv")
		self.muzzle = self.entity.getChild("Muzzle")
		self.mesh = self.entity.getChild("FPS Mesh")
		self.AK74 = self.mesh.getChild("AK 74")
		self.AR4 = self.mesh.getChild("AR4")
		self.ammoMax = self.AK74.properties.get("Ammo")
		self.healthMax = self.entity.properties.get("Health")
		self.healthCurrent = self.healthMax
		self.ammoCurrent = self.ammoMax
		self.ammoInv = 0
		self.animator : cave.AnimationComponent = self.mesh.get("Animation")
		self.AK_Damage = self.AK74.properties.get("Damage")
		self.movementState = 0 # [idle, walking, running]
		self.movementTimer = cave.SceneTimer() # To add footsteps...
		self.KillCount = 0
		self.isDead = False
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
			else:
				dir *= self.walkSpeed
				self.movementState = 1

		self.character.setWalkDirection(dir * dt)
#JUMP
		if events.pressed(cave.event.KEY_SPACE):
			if self.character.onGround():
				self.character.jump()
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

		# If the Player is holding the Left Mouse Button, it should be able to shoot.
		# But I'm also using a timer to limit how many bullets per second it will be
		# able to shoot. Otherwise, it will become a mess!
		if events.active(cave.event.MOUSE_LEFT) and self.shotTimer.get() > 0.1 and self.ammoCurrent > 0:
			self.shotTimer.reset()

			# Shot Sound:
			sd = cave.playSound("bang-04.ogg")
			sd.pitch = cave.random.uniform(0.4, 1.0)

			# Duplicating the Muzzle Effect...
			muzzle = scene.copyEntity(self.muzzle)
			muzzle.activate(scene)
			muzzle.scheduleKill(0.05) # Only lasts for a fraction of a Second

			# I'll raycast from the camera position to its backward direction 
			# in order to see if the projectile hits something. 
			origin : cave.Vector3 = cam.getWorldPosition()
			target = origin + cam.getForwardVector(True) * -1000

			# I'll also create a Mask so the raycast only checks for the bodies
			# with the 7th bit enabled. This will prevent it from hitting the
			# player capsule itself.
			mask = cave.BitMask(False)
			mask.enable(7)
			#DA- Create a mask to trace for objects on mask 12 (enemies)
			enemyMask = cave.BitMask(False)
			enemyMask.enable(12)
			
			enemyResult : cave.rayCastOut = scene.rayCast(origin, target, enemyMask)
			# Then I raycast and check to see if it hits...
			result = scene.rayCast(origin, target, mask)
			#DA- Check for an enemy first, if no enemy is hit, check if we need to draw a bullet hole
			self.ammoCurrent -= 1
			if enemyResult.hit:
				#scene.addDebugSphere(result.position, .5, cave.Vector3(0, 255, 0), 10)
				#enemy = scene.checkContactSphere(self, cave.Vector3(enemyResult.position), .5, 12)
				for hit in scene.checkContactSphere(enemyResult.position, .33):
					if hit.entity.name == "TestCharacter":
						
						self.hitEnemy = hit.entity.getPy("Enemy")
						
						try:
							self.hitEnemy.takeDamage(self.AK_Damage, self)
							
						except:
							print("Player Can't call takeDamage on TestCharacter")
							pass
				
				
				self.causeDamage()

			elif result.hit:
				# Adding the Bullet Hole based on its Entity Template:
				obj = scene.addFromTemplate("Bullet Hole", result.position)
				obj.getTransform().lookAt(result.normal)
				# Schedule Bullet Hole to be killed
				obj.scheduleKill(5.0)
#DRY FIRE#######		
		elif events.active(cave.event.MOUSE_LEFT) and self.shotTimer.get() > 0.1 and self.ammoCurrent <= 0:
			
			emptySd = cave.playSound("gun-trigger-click-01.ogg")
			emptySd.setProgress(.5)
			emptySd.setVolume(3)
			self.shotTimer.reset()
			
	def reloadWeapon(self):
		
		scene = cave.getScene()
		events = cave.getEvents()
		if events.pressed(cave.event.KEY_R):
			if self.ammoCurrent < self.ammoMax and self.ammoInv > 0:
				x = self.ammoMax - self.ammoCurrent
					
				if self.ammoInv >= 30:

					self.ammoCurrent = self.ammoMax
					self.ammoInv = self.ammoInv - 30
					sd = cave.playSound("gun-cocking-01.ogg")
				else:
					sd = cave.playSound("gun-trigger-click-01.ogg")
					#self.ammoCurrent = self.ammoCurrent + self.ammoInv
					#self.ammoInv = 0
					pass
			
			#sd.pitch = cave.random.uniform(0.4, 1.0)
	
	def ammoPickup(self, ammo):
		if self.ammoInv < (self.ammoMax * 4):
			if self.ammoInv + ammo <= self.ammoMax * 4:
				self.ammoInv += ammo
			else:
				self.ammoInv = self.ammoMax * 4
				
			print("AMMP PICKUP")
	
	def weaponPickup(self, weapon):
		print(f"{weapon} picked up!")
		x = cave.newMeshEntity("SK_AR4")
		x.setParent(self.entity)
		pass		
		
	def updateUI(self):
		ammoUI = self.UI_Ammo.get("UI Element")
		ammoUI.setText(f'{str(int(self.ammoCurrent))} / {str(int(self.ammoMax))}')
		healthUI = self.UI_Health.get("UI Element")
		healthUI.setText(str(int(self.healthCurrent)))
		
		heartFullUI : cave.UIElementComponent = self.UI_Heart_Full.get("UI Element")
		heartFullUI.setDefaultQuadAlpha(float(self.healthCurrent * 0.01))
		heartFullUI.reload()
		
		ammoInvUI = self.UI_Ammo_Inv.get("UI Element")
		ammoInvUI.setText(str(int(self.ammoInv)))
	def causeDamage(self):
		scene = cave.getScene()
		hm = scene.copyEntity(self.hm)
		hm.activate(scene)
		hm.scheduleKill(.02)
		#print(self.hitEnemy.entity.getUID())	
	
	def takeDamage(self, damage):
		self.healthCurrent = self.healthCurrent - damage
		print("Hit Landed")
		#self.entity.
	
	def checkHealth(self):
		if self.healthCurrent < 100:
			if self.healthCurrent < 1:
				print("YOU DIED")
				self.isDead = True
				#self.death()
			
			self.healthCurrent += 0.01

	def addKill(self, add):
		

		scene = cave.getScene()
		kills = scene.copyEntity(self.UI_Kills)
		killsUI = kills.get("UI Element")
		self.KillCount = self.KillCount + add
		
		if kills.getActive() == False:
			#kills.setActive(True)
			kills.activate(scene)
			killsUI.setText(str(self.KillCount))
			#self.UI_KillCount.reload()
		
	def ADS(self):
		events = cave.getEvents()
		cam : cave.CameraComponent = self.cam.get("Camera")
		
		if events.pressed(cave.event.MOUSE_RIGHT):
			cam.fov = 60
			

		if events.released(cave.event.MOUSE_RIGHT):
			cam.fov = 85

	def animateAndSounds(self):
		layer : cave.AnimationComponentAnimationLayer = self.animator.getAnimation(0)
		layer.speed = 100

		addFootstep = False
		timer = self.movementTimer.get()

		if self.movementState == 1:
			if timer > 0.3:
				addFootstep = True
			layer.speed = 300
		elif self.movementState == 2:
			if timer > 0.22:
				addFootstep = True
			layer.speed = 500

		if addFootstep and self.character.onGround():
			self.movementTimer.reset()

			sd = cave.playSound("footstep-1.ogg")
			sd.pitch = cave.random.uniform(0.5, 1.5)
			sd.volume = 0.2

	def update(self):
		self.movement()
		self.mouselook()
		self.shoot()
		self.animateAndSounds()
		self.ADS()
		self.reloadWeapon()
		self.updateUI()
		self.checkHealth()
	def end(self, scene: cave.Scene):
		pass
	
