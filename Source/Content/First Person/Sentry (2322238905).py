import cave
import cave.random

class Sentry(cave.Component):
	def start(self, scene: cave.Scene):
		self.scene = scene
		self.target : cave.Entity = None
		self.mesh = self.entity.getChild("Mesh")
		self.anim : cave.AnimationComponent = self.mesh.get("AnimationComponent")
		self.character : cave.CharacterComponent = self.entity.get("CharacterComponent")
		self.transf = self.entity.getTransform()
		self.pos = self.transf.position
		self.pos = self.pos + cave.Vector3(0,1.7,0)
		self.cooldownTimer = cave.SceneTimer()
		self.scanTimer = cave.SceneTimer()
		self.hitTimer = cave.SceneTimer()
		self.shotTimer = cave.SceneTimer()
		self.firstShot = True
	def update(self):
		"""dt = cave.getDeltaTime()
		self.scene.addDebugLine(self.pos, self.pos + (self.transf.getForwardVector() * 8) - cave.Vector3(self.transf.getRightVector()[0]*2,.2,0), cave.Vector3(255,255,255))
		self.scene.addDebugLine(self.pos, self.pos + (self.transf.getForwardVector() * 8) - cave.Vector3(self.transf.getRightVector()[1]*2,.2,0), cave.Vector3(255,0,0))
		self.scene.addDebugLine(self.pos, self.pos + (self.transf.getForwardVector() * 8) - cave.Vector3(self.transf.getRightVector()[2]*2,.2,0), cave.Vector3(255,0,0))
		self.scene.addDebugLine(self.pos, self.pos + (self.transf.getForwardVector() * 8) + cave.Vector3(self.transf.getRightVector()[0]*2,-.2,0), cave.Vector3(255,255,255))
		self.scene.addDebugLine(self.pos, self.pos + (self.transf.getForwardVector() * 8) + cave.Vector3(self.transf.getRightVector()[1]*2,-.2,0), cave.Vector3(255,0,0))
		self.scene.addDebugLine(self.pos, self.pos + (self.transf.getForwardVector() * 8) - cave.Vector3(0,.2,1.2), cave.Vector3(255,0,0))
		self.scene.addDebugLine(self.pos, self.pos + (self.transf.getForwardVector() * 8) - cave.Vector3(0,.2,.9), cave.Vector3(255,0,0))
		self.scene.addDebugLine(self.pos, self.pos + (self.transf.getForwardVector() * 8) - cave.Vector3(0,.2,.6), cave.Vector3(255,0,0))
		self.scene.addDebugLine(self.pos, self.pos + (self.transf.getForwardVector() * 8) - cave.Vector3(0,.2,.3), cave.Vector3(255,0,0))
		self.scene.addDebugLine(self.pos, self.pos + (self.transf.getForwardVector() * 8) - cave.Vector3(0,.2,0), cave.Vector3(0,255,0))
		self.scene.addDebugLine(self.pos, self.pos + (self.transf.getForwardVector() * 8) + cave.Vector3(0,-.2,.3), cave.Vector3(0,0,255))
		self.scene.addDebugLine(self.pos, self.pos + (self.transf.getForwardVector() * 8) + cave.Vector3(0,-.2,.6), cave.Vector3(0,0,255))
		self.scene.addDebugLine(self.pos, self.pos + (self.transf.getForwardVector() * 8) + cave.Vector3(0,-.2,.9), cave.Vector3(0,0,255))
		self.scene.addDebugLine(self.pos, self.pos + (self.transf.getForwardVector() * 8) + cave.Vector3(0,-.2,1.2), cave.Vector3(0,0,255))
		self.scene.addDebugLine(self.pos, self.pos + (self.transf.getForwardVector() * 8) + cave.Vector3(0,-.2,1.5), cave.Vector3(0,0,255))
		self.scene.addDebugLine(self.pos, self.pos + (self.transf.getForwardVector() * 8) + cave.Vector3(0,-.2,1.8), cave.Vector3(0,0,255))"""
		self.scene.addDebugLine(self.pos, self.pos + (self.transf.getForwardVector() * 8) + cave.Vector3(0,-.2,0), cave.Vector3(0,0,255))
		scan = self.scene.rayCast(self.pos, self.pos + (self.transf.getForwardVector() * 20) - cave.Vector3(0,.2,0), cave.BitMask(15))
		if scan.hit:
			
			
			if scan.entity.name == "Player":
				print("Player Hit")
				
				self.target = scan.entity
				
				#self.anim.playByName("BlackOps_Unarmed_Walk_Fwd", .2)
				self.anim.playByName("BlackOps_Rifle_Idle_Aim", .2)
				#self.character.setWalkDirection(0,0,.5 * cave.getDeltaTime())
				self.cooldownTimer.reset()
				
				
		else:
			self.anim.playByName("BlackOps_Rifle_Idle", .2)
			if self.cooldownTimer.get() > 3:
				self.target = None
				self.firstShot = True
		if self.target:
			#self.transf.lookAtSmooth(self.target.getTransform().getForwardVector(), .04, self.transf.getUpVector())
			self.targetPos = self.pos - self.target.getTransform().getPosition()
			self.targetPos.y = 0
			self.transf.lookAtSmooth(self.targetPos, .04, self.transf.getUpVector())
			#self.character.setWalkDirection(0,0,-2 * cave.getDeltaTime())
			self.tryAttack()
		else:
			if self.scanTimer.get() < 4.0:
				self.transf.rotate(0,.3 * cave.getDeltaTime(),0)
				
				#self.anim.playByName("BlackOps_Rifle_TurnL_Idle", .3, 1, True, 0)
				#print(self.transf.getRightVector())
			elif self.scanTimer.get() > 4 and self.scanTimer.get() < 8.0:
				self.transf.rotate(0,-.3 * cave.getDeltaTime(),0)
				#self.anim.playByName("BlackOps_Rifle_TurnR_Idle", .3, 1, True, 0)
			else:
				self.scanTimer.reset()
				self.anim.playByName("BlackOps_Rifle_Idle", .1, 0, True, 0)
				print("reset")
		#self.tryAttack()
		
	def takeDamage(self, damage, attacker : cave.Entity, position):
		self.anim.playByName("BlackOps_Rifle_HitReact_2", .2, 0, False, 1)
		self.target = attacker
		self.transf.lookAtSmooth(self.pos - attacker.getTransform().getPosition(), .9, self.transf.getUpVector())

		#print(attacker.getUID())
		print("OUCH!")

	def tryAttack(self):
		if self.firstShot == True:
			self.hitTimer.reset()
			self.firstShot = False
			if self.hitTimer.get() > 4:

				self.target.getPy("FirstPersonController").takeDamage(15)
				sd = cave.playSound("bang-04.ogg", 1, 0)
				
				self.hitTimer.reset()
			else:
				pass
		if self.anim.getAnimationName() == "BlackOps_Rifle_Idle_Aim":
		#if self.target:
			if self.shotTimer.get() > 1:

				self.target.getPy("FirstPersonController").takeDamage(15)
				sd = cave.playSound("bang-04.ogg", 1, 0)
				
				self.shotTimer.reset()
		

	def end(self, scene: cave.Scene):
		pass
	