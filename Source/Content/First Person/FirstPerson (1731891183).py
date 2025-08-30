import cave



class FirstPersonController(cave.Component):
	walkSpeed = 5.0
	runSpeed = 8.0
	mouseSens = 0.012
	def start(self, scene: cave.Scene):
		
		self.transf = self.entity.getTransform()
		self.character : cave.CharacterComponent = self.entity.get("Character")
		self.cam = self.entity.getChild("Camera")
		bg = cave.playSound("nowhere-to-run.ogg")
		bg.setVolume(.3)
		self.mouseSens = 0.012
		self.camTransf = self.cam.getTransform()
		self.hm = self.entity.getChild("hitMarker")
		# This will control the fire rate...
		self.shotTimer = cave.SceneTimer()
		self.UI_Kills = self.entity.getChild("UI KillCount")
		self.UI_Ammo = self.entity.getChild("UI Ammo")
		self.UI_Health = self.entity.getChild("UI Health")
		self.UI_Heart_Full = self.entity.getChild("UI Heart_Full")
		self.UI_Ammo_Inv = self.entity.getChild("UI Ammo_Inv")
		self.UI_WeaponImage = self.entity.getChild("UI WeaponImg")
		self.UI_BloodSpatter = self.entity.getChild("UI BloodSpatter")
		self.UI_BloodMesh = self.entity.getChild("UI BloodMesh")
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
		self.KillCount : int = 0
		self.isDead = False
		self.isAiming = False
		self.weaponInv : cave.Entity = []
		self.currentWeapon = cave.Entity()
		self.currentWeaponInt = 0
		self.muzzle = self.entity.getChild("Muzzle")
		self.ADSMesh = self.cam.getChild("ADS Mesh")
		self.ADSMeshB = self.cam.getChild("ADS MeshB")
		self.ADSMuzzle = self.cam.getChild("ADS Muzzle")
		#self.muzzle = self.currentWeapon.getChild("Muzzle")
		#self.mesh.deactivate(scene)
	def movement(self):
		if self.isDead == False:
			
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
			#Weapon Selection
			if events.getMouseScroll():
				cave.playSound("ui-over.ogg")
				#print(events.getMouseScroll())
				self.weaponSelect(events.getMouseScroll())
		
	
	def mouselook(self, sens=-mouseSens):
		if self.isAiming == False:
			print("ADS OFF")
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
		else:
			print("ADS On")
			events = cave.getEvents()
			events.setRelativeMouse(True)

			motion = events.getMouseMotion() * -.0024
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
		
		if self.mesh.isActive():
			print("Shooting - Mesh Active")
			if events.active(cave.event.MOUSE_LEFT) and self.shotTimer.get() > 0.1 and self.ammoCurrent > 0:
				print("Shooting - Ammo Test Passed")
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
					print("Shooting - Enemy Hit")
					#scene.addDebugSphere(result.position, .5, cave.Vector3(0, 255, 0), 10)
					#enemy = scene.checkContactSphere(self, cave.Vector3(enemyResult.position), .5, 12)
					for hit in scene.checkContactSphere(enemyResult.position, .33):
						if hit.entity.name == "TestCharacter":
							
							self.hitEnemy = hit.entity.getPy("Enemy")
						
							try:
								self.hitEnemy.takeDamage(self.AK_Damage, self, self.transf.getPosition())
							
							except:
								print("Player Can't call takeDamage on TestCharacter")
								pass
						if hit.entity.name == "BlackOps":
							self.hitEnemy = hit.entity.getPy("Sentry")
							try:
								self.hitEnemy.takeDamage(self.currentWeapon.properties.get("Damage"), self.entity, self.transf.getPosition())
							except:
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
		if self.isAiming == True:
			if events.active(cave.event.MOUSE_LEFT) and self.shotTimer.get() > 0.1 and self.ammoCurrent > 0:
				self.shotTimer.reset()

				# Shot Sound:
				sd = cave.playSound("bang-04.ogg")
				sd.pitch = cave.random.uniform(0.4, 1.0)

				# Duplicating the Muzzle Effect...
				
				muzzle = self.ADSMuzzle
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
								self.hitEnemy.takeDamage(self.AK_Damage, self, self.transf.getPosition())
							
							except:
								print("Player Can't call takeDamage on TestCharacter")
								pass
						if hit.entity.name == "BlackOps":
							self.hitEnemy = hit.entity.getPy("Sentry")
							try:
								self.hitEnemy.takeDamage(self.currentWeapon.properties.get("Damage"), self.entity, self.transf.getPosition())
							except:
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
					print(f"{self.ammoCurrent} rounds wasted.")
					self.ammoCurrent = self.ammoMax
					self.ammoInv = self.ammoInv - 30
					sd = cave.playSound("gun-cocking-01.ogg")
				else:
					sd = cave.playSound("gun-trigger-click-01.ogg")
					#self.ammoCurrent = self.ammoCurrent + self.ammoInv
					#self.ammoInv = 0
					pass
			
			#sd.pitch = cave.random.uniform(0.4, 1.0)
	#PICKUPS	
	def ammoPickup(self, ammo):
		if self.ammoInv < (self.ammoMax * 4):
			if self.ammoInv + ammo <= self.ammoMax * 4:
				self.ammoInv += ammo
			else:
				self.ammoInv = self.ammoMax * 4
				
			#print("AMMO PICKUP")
	
	def weaponPickup(self, weapon):
	
		if weapon != self.currentWeapon:
			scene = cave.getScene()
			weaponName = weapon.entity.name
			"""for item in self.weaponInv:
				if weaponName == item:
					pass"""
			if not weapon in self.weaponInv:
				if self.mesh.isActive():
					self.mesh.deactivate(scene)
				if not self.mesh.isActive():
					self.mesh.activate(scene)
					for child in self.mesh.getChildren():
						child.deactivate(scene)
				self.weaponInv.append(weapon)
				self.currentWeaponInt = (len(self.weaponInv) - 1)		
				print(f"{weaponName} picked up!")
				sd = cave.playSound("gun-cocking-01.ogg")
				
				if weaponName == "AR4":
					self.currentWeapon = self.AR4
					self.AR4.activate(scene)
					#icon = cave.UIStyleColor.image.setAsset("M4-Thumbnail.png")
					icon : cave.UIElementComponent = self.UI_WeaponImage.get("UI Element")
					self.UI_WeaponImage.getChild("Icon_AR4").activate(scene)
					self.UI_WeaponImage.getChild("Icon_AK74").deactivate(scene)
				if weaponName == "AK74":
					self.currentWeapon = self.AK74
					self.AK74.activate(scene)
					#icon = cave.UIStyleColor.image.setAsset("M4-Thumbnail.png")
					icon : cave.UIElementComponent = self.UI_WeaponImage.get("UI Element")
					self.UI_WeaponImage.getChild("Icon_AK74").activate(scene)
					self.UI_WeaponImage.getChild("Icon_AR4").deactivate(scene)
					#icon.image.setAsset("M4-Thumnail.png")
				
				
			
			self.muzzle = self.currentWeapon.getChild("Muzzle")
			self.muzzle.deactivate(scene)


			
			#pass
		

	
	def weaponSelect(self, value):
		
		scene = cave.getScene()
		if len(self.weaponInv) > 1:
			if self.currentWeapon.name == "AR4":
				self.currentWeapon = self.AK74
				self.AR4.deactivate(scene)
				self.currentWeapon.activate(scene)
				#icon = cave.UIStyleColor.image.setAsset("M4-Thumbnail.png")
				icon : cave.UIElementComponent = self.UI_WeaponImage.get("UI Element")
				self.UI_WeaponImage.getChild("Icon_AK74").activate(scene)
				self.UI_WeaponImage.getChild("Icon_AR4").deactivate(scene)
				
				
			elif self.currentWeapon.name == "AK 74":
				self.currentWeapon = self.AR4
				self.AK74.deactivate(scene)
				self.currentWeapon.activate(scene)
				#icon = cave.UIStyleColor.image.setAsset("M4-Thumbnail.png")
				icon : cave.UIElementComponent = self.UI_WeaponImage.get("UI Element")
				self.UI_WeaponImage.getChild("Icon_AR4").activate(scene)
				self.UI_WeaponImage.getChild("Icon_AK74").deactivate(scene)
				
		self.muzzle = self.currentWeapon.getChild("Muzzle")
		self.muzzle.deactivate(scene)
		print(self.currentWeapon.name)		
	
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
		#killCount = self.UI_Kills.get("UI Element")
		
		#killCount.setText(str(int(self.KillCount)))
		self.UI_Kills.reload()
	#VITALS	
	def causeDamage(self):
		scene = cave.getScene()
		hm = scene.copyEntity(self.hm)
		hm.activate(scene)
		hm.scheduleKill(.02)
		#print(self.hitEnemy.entity.getUID())	
	
	def takeDamage(self, damage):
		
		scene = cave.getScene()
		sd = cave.playSound("grunt.ogg", 3)
		self.healthCurrent = self.healthCurrent - damage
		#print("Hit Landed")
		bs = scene.copyEntity(self.UI_BloodMesh)
		bs.activate(scene)
		bs.scheduleKill(0.05)
		
		
	def checkHealth(self):
		if self.healthCurrent < 100:
			if self.healthCurrent < 1:
				print("YOU DIED")
				self.isDead = True
				
				self.death()

			self.healthCurrent += 0.01

	def death(self):
		scene = cave.getScene()
		self.respawnTimer = cave.SceneTimer()
		
		#self.cam.deactivate(scene)
		self.transf.setWorldPosition(6.3,0,-9.3)
		#self.camTransf.setWorldPosition(0,0,0)
		self.healthCurrent = self.healthMax
		
	
	def respawn(self):
		if self.isDead == True:
			if self.respawnTimer.get() > 4.0:

				
				self.isDead = False
				self.respawnTimer.reset()

		

	def addKill(self, add):
		

		scene = cave.getScene()
		#kills = scene.copyEntity(self.UI_Kills)
		kills = self.UI_Kills
		killsUI = kills.get("UI Element")
		
		
		self.KillCount = self.KillCount + add
		
		if kills.getActive() == False:
			#kills.setActive(True)
			kills.activate(scene)
			killsUI.setText(str(int(self.KillCount)))
			#self.UI_KillCount.reload()
		else:
			killsUI.setText(str(int(self.KillCount)))
	
	def ADS(self):
		if len(self.weaponInv) > 0:
			events = cave.getEvents()
			cam : cave.CameraComponent = self.cam.get("Camera")
			scene = cave.getScene()
			mesh : cave.MeshComponent = self.ADSMeshB.get("MeshComponent")
			meshTransf : cave.TransformComponent = self.ADSMeshB.get("TransformComponent")
			if events.pressed(cave.event.MOUSE_RIGHT):
				if self.currentWeapon == self.AK74:
					mesh.mesh.setAsset("AK74 Mesh")
					meshTransf.rotateOnPitch(1.52)
				elif self.currentWeapon == self.AR4:
					mesh.mesh.setAsset("SK_AR4")	
				self.isAiming = True
				cam.fov = 25
				
				self.mesh.deactivate(scene)
				self.ADSMesh.activate(scene)
				#muz = self.ADSMeshB.getChild("ADS Muzzle")
				#muz.deactivate(scene)
				self.ADSMuzzle.deactivate(scene)
			if events.released(cave.event.MOUSE_RIGHT):
				if self.currentWeapon == self.AK74:
					
					meshTransf.rotateOnPitch(-1.52)
				self.isAiming = False
				self.mesh.activate(scene)
				children = self.mesh.getChildren()
				for child in children:
					if child != self.currentWeapon:
						child.deactivate(scene)
				self.muzzle.deactivate(scene)
				self.ADSMesh.deactivate(scene)
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
		if self.mesh.getActive() == True:

			self.animateAndSounds()
		self.ADS()
		self.reloadWeapon()
		self.updateUI()
		self.checkHealth()
		self.respawn()
	def end(self, scene: cave.Scene):
		pass
	
