import cave
import cave.math
import cave.random



ENEMY_MIN_DISTANCE = 1.0

class EStatePatrol(cave.State):
	
	class Idle(cave.State):
		
		def start(self):
			self.timer = cave.SceneTimer()

		def update(self):
			self.component.character.setWalkDirection(0, 0, 0)

			if self.timer.get() > 1.0:
				if cave.random.random() < 0.5:
					return EStatePatrol.Walk()
				self.timer.reset()

	class Walk(cave.State):
		def start(self):
			angle  = cave.random.uniform(0, 6.3)
			radius = cave.random.uniform(0, self.entity.properties.get("patrolRange", 1.0))

			self.target = cave.Vector3(0)
			for _ in range(16):
				self.target = self.component.spawnPoint.copy()
				self.target += cave.Vector3(cave.math.sin(angle), 0, cave.math.cos(angle)) * radius

				if (self.target - self.component.transf.worldPosition).length() < ENEMY_MIN_DISTANCE * 2:
					break
	
			
		def update(self):
			dt = cave.getDeltaTime()

			dir = (self.component.transf.worldPosition - self.target)
			dir.y = 0
			
			self.component.isRunning = False
			self.component.transf.lookAtSmooth(dir.normalized(), 0.1)
			self.component.character.setWalkDirection(0, 0, self.entity.properties.get("walkSpeed", 1.0) * dt)

			if dir.length() <= ENEMY_MIN_DISTANCE or not self.component.canMoveForward():
				return EStatePatrol.Idle()

	class Chase(cave.State):
		
		def start(self):
			
			self.fsm = cave.StateMachine(self.component)
			self.timer = cave.SceneTimer()
			dt = cave.getDeltaTime()
			self.tempVal = []
			targetTransf : cave.Transform = self.component.targetPlayer.getTransform()
			self.targetPos : cave.Vector3 = targetTransf.position
			print("Start CHASING!!")
			self.component.isRunning = True
			self.component.character.setWalkDirection(0, 0, 8 * dt)
			self.targetDist = self.component.findDistanceFloat(self.component.transf.getWorldPosition(), self.targetPos)

		def update(self):
			dt = cave.getDeltaTime()
			if self.targetDist < 1.5:
				self.timer.reset()
				
				
				return EStateCombat.Melee()
				
			elif self.timer.get() > 1.5:
				self.timer.reset()
				return EStatePatrol.Walk()
			
			

	def start(self):
		self.fsm = cave.StateMachine(self.component)
		options = [EStatePatrol.Idle, EStatePatrol.Walk]
		self.fsm.setState(options[cave.random.randint(0, len(options) - 1)]())
		
	def update(self):
		
		self.fsm.run()
		
		scene = cave.getScene()
		origin = self.component.meshTransf.worldPosition
		origin[1] += 1.7
		target = origin + self.component.transf.getForwardVector(True) * 25
		debugCol = cave.Vector3(255, 0, 0) 
		mask = cave.BitMask(False)
		mask.enable(15)

		result = scene.rayCast(origin, target, mask)
		#scene.addDebugLine(origin, target, debugCol)
		
		
		if result.hit:
			if result.entity.name == "Player":
				#locTransf = result.entity.getTransform()
				#location = locTransf.getPosition()
				#self.component.chasePlayer(result.entity)
				self.component.targetPlayer = result.entity
				self.fsm.setState(EStatePatrol.Chase())
		else:
			pass
			
class EStateCombat(cave.State):
	class Injured(cave.State):
		def start(self):
			self.scene = cave.getScene()
			print("OUCH!")
			self.attacker : cave.Entity = self.component.killer
			pass
		def update(self):
			self.component.character.setWalkDirection(self.attacker.getTransform().getPositionCopy())
			self.component.transf.lookAtPosition(self.attacker.getTransform().getPositionCopy())
			self.scene.addDebugLine(self.component.transf.position, self.attacker.getTransform().getPositionCopy(), cave.Vector3(0,0,255))
			
			return super().update()
		def end(self):
			return super().end()
	class Melee(cave.State):
		
		def start(self):
			print("Start COMBAT!!")
			self.scene = cave.getScene()
			self.timer = cave.SceneTimer()
			self.fsm = cave.StateMachine(self.component)
			self.dt = cave.getDeltaTime()
			self.targetTransf : cave.Transform = self.component.targetPlayer.getTransform()
			self.targetPos : cave.Vector3 = self.targetTransf.position
			self.component.isRunning = False
			self.component.character.setWalkDirection(0, 0, 0 * self.dt)
			#self.targetDist = self.component.findDistanceFloat(self.component.transf.getWorldPosition(), self.targetPos)
			self.attacks = ["p-atk-kick", "p-atk-punch-1", "p-atk-punch-2", "p-atk-punch-3"]
			
			self.origin = self.component.transf.worldPosition
			self.origin[1] = 1.7
		def update(self):
			self.targetPos : cave.Vector3 = self.targetTransf.position
			self.targetDist = self.component.findDistanceFloat(self.component.transf.getWorldPosition(), self.targetPos)
			self.component.character.setWalkDirection(0, 0, 0)
			mask = cave.BitMask(False)
			mask.enable(15)
			if self.targetDist < 1.5:
				#self.component.character.setWalkDirection(enemyResult.position[0], enemyResult.position[2], 0)
				if self.timer.get() > 0.8:
					self.component.animator.playByName(self.attacks[cave.random.randint(0, len(self.attacks) - 1)], 0.2, priority=1)
					#if self.component.animator.getAnimationName() == "p-atk-kick":
					if self.component.animator.isAnyAnimationBeingPlayed():
						self.timer.reset()
						
						enemyResult : cave.rayCastOut = self.scene.rayCast(self.component.origin, self.component.origin + self.component.transf.getForwardVector(True) * 2, cave.BitMask(15))
						
						for hit in self.scene.checkContactSphere(self.origin, 2.0, mask):
								
							if hit.entity.name == "Player":
								
								try:
									self.component.targetPlayer = hit.entity.getPy("FirstPersonController")
									self.hitPlayer = hit.entity
									self.hitPlayer = self.hitPlayer.getPy("FirstPerson")
									self.component.atkMelee()
								except:
									print("Attack Failed")
							
					self.timer.reset()
			
			elif self.targetDist > 1.5 or self.timer.get() > 6.0:
				self.timer.reset()
				return EStatePatrol.Walk()
			else:
				return EStatePatrol.Idle()
			
	def start(self):
		pass

	def update(self):
		pass