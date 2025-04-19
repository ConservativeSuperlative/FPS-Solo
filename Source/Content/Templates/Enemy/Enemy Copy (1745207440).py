import cave


class Enemy(cave.Component):
	def start(self, scene: cave.Scene):
		self.scene = scene
		self.targetPlayer : cave.Entity = None
		self.targetTransf : cave.Transform = None
		self.targetPos : cave.Vector3 = None
		self.mesh = self.entity.getChild("Proto Mesh")
		self.transf = self.entity.getTransform()
		self.meshTransf = self.mesh.getTransform()
		self.animSocket = self.mesh.get("Animation Socket")
		self.origin = self.meshTransf.worldPosition
		self.origin[1] += 1.7
		self.character : cave.CharacterComponent = self.entity.get("Character")
		self.animator  : cave.AnimationComponent = self.mesh.get("Animation")
		self.template : cave.EntityTemplate = cave.getEntityTemplate("TestCharacter")
		self.isRunning = False
		self.spawnPoint = self.transf.worldPosition.copy()
		self.Health = self.entity.properties.get("Health")
		self.isDead = self.entity.properties.get("isDead")
		self.fsm = cave.StateMachine(self)
		self.fsm.setState(EStatePatrol())
		self.respawnTimer = cave.SceneTimer()
		self.attacker : cave.Entity = None
		self.killer : cave.Entity = None
		self.scanTimer : cave.SceneTimer = cave.SceneTimer()
		self.takingDamage : bool = False
	def canMoveForward(self) -> bool:
		fwd = self.meshTransf.getForwardVector() * 0.2
		pos = self.transf.worldPosition + cave.Vector3(0, 1, 0)
		
		mask = cave.BitMask(False)
		mask.enable(0)
		
		if self.scene.rayCast(pos, pos + fwd, mask).hit:
			return False
		return self.scene.rayCast(pos + fwd, pos + fwd - cave.Vector3(0,2,0), mask).hit
	
	

	def enemyScan(self):
		
		timer = cave.SceneTimer()
		yaw = self.meshTransf.getQuaternion()
		origin = self.transf.worldPosition
		origin[1] = 1.7
		
		#self.scene.addDebugArrow(origin, origin + self.transf.getForwardVector(True) * 2, cave.Vector3(0,255,0))
		#print(yaw)
		pass
		
		
	
	def findDistanceVec(self, v1, v2):
		return [a - b for a, b in zip(v1, v2)]
	
	def findDistanceFloat(self, v1, v2):
		distVec = [a - b for a, b in zip(v1, v2)]
		distFloat = (distVec[0] + distVec[1] + distVec[2]) / 3
		return abs(distFloat)
	
	

	
	'''def chasePlayer(self, player : cave.Entity):
	
		playerTransf = player.getTransform()
		playerPos = playerTransf.getWorldPosition()
		#playerDir2 = -playerDir
		try:
			for x in self.findDistance(self.transf.position, playerPos):
				if self.findDistance(self.transf.position, playerPos)[x] < 5:
					print("TOO CLOSE!")
			while self.findDistance(self.transf.position, playerPos)[1] + self.findDistance(self.transf.position, playerPos)[2] < 2:
			
			#self.meshTransf.lookAtSmooth(-location, .2)
			#self.character.setWalkDirection(self.transf.position - location, True)
				self.character.setWalkDirection(self.transf.getForwardVector() * 0.2, True)
				print(self.findDistance(self.transf.position, playerPos))
			#if self.findDistance(self.transf.position, playerPos) < 10:
				#Sself.animator.playByName("p-atk-punch-3", priority = 1)
				return None
		except:
			pass'''
	
	def death(self):
		scene = cave.getScene()
		self.respawnTimer = cave.SceneTimer
		self.character.disable()
		options = ["p-death-1", "p-death-2", "p-death-3", "p-death-4"]
		hndl = self.animator.playByName(options[cave.random.randint(0, len(options) - 1)], 0.2, priority=1)
		hndl.speed *= 1.2
		self.entity.scheduleKill(10)
		
		self.respawn()
		try:
			self.killer.addKill(1)
		except:
			print("fail")
		
			
	def respawn(self):
		

		scene = cave.getScene()
		
		scene.addFromTemplate(templateName = "TestCharacter", position = self.spawnPoint)

		

	def atkMelee(self):
		self.targetPlayer.takeDamage(10)
		
		
	def checkHealth(self):
		if not self.isDead:
			if self.Health < 1:
				
				self.isDead = True
				self.death()
	
	def takeDamage(self, damage, attacker : cave.Entity, position):
		self.takingDamage = True
		scene = cave.getScene()
		try:
			if self.Health >= 1:
				blood : cave.ParticleComponent = self.mesh.getChild("Blood")
				# blood : cave.ParticleComponent = scene.copyEntity(self.mesh.getChild("Blood"))
				self.Health -= damage
				#print(attacker.entity.getUID())
				blood.activate(scene)
				blood.reload()
				#self.meshTransf.lookAtPosition(attacker.getTransform().getWorldPosition())
				#self.entity.getTransform().lookAtPosition(attacker.getTransform().getWorldPosition())
				#self.character.setWalkDirection(position, False)
				self.animator.playByName("p-damage", .2, priority=1)
				self.killer = attacker
				#self.fsm.setState(EStateCombat.Injured())
				print(position)
			else:
				
				print("dead")
		except:
			pass
		#self.takingDamage = False

	def updateAnimation(self):
		dir = self.character.getWalkDirection()

		if dir.length() > 0.0:
			self.meshTransf.lookAtSmooth(-dir, 0.2 if self.character.onGround() else 0.06)

		if self.character.onGround():
			if dir.length() > 0.0:
				if self.isRunning:
					self.animator.playByName("p-run", 0.2, loop=True)
				else:
					self.animator.playByName("p-walk", 0.2, loop=True)
			else:
				self.animator.playByName("p-idle", 0.2, loop=True)
		else:
			if self.character.isFalling():
				self.animator.playByName("p-fall-1", 0.4, loop=True)
			else:
				self.animator.playByName("p-fall-2", 0.3, loop=True)

		# This is necessary to avoid the attack animation to stop immediately:
		layer : cave.AnimationComponentAnimationLayer = self.animator.getAnimation(0)
		if layer:
			if layer.priority > 0:
				if layer.getProgress() > 0.8:
					layer.priority = 0
					self.animator.playByName("p-idle", 0.2, loop=True)

	def update(self):
		if not self.isDead and not self.takingDamage:
			self.checkHealth()
			self.enemyScan()
			self.fsm.run()
			
			self.updateAnimation()
			
			#self.chasePlayer()
	def end(self, scene: cave.Scene):
		pass
	