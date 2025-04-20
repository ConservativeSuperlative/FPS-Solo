import cave
import cave.random
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
		self.MaxHealth = self.entity.properties.get("Health")
		self.Health = self.MaxHealth
		self.isDead = False
		self.anim.playByName("BlackOps_Rifle_Idle", .2)
	def update(self):
		if self.isDead == False:
			
			self.anim.playByName("BlackOps_Rifle_Idle", .2)
			scan = self.scene.rayCast(self.pos, self.pos + (self.transf.getForwardVector() * 20) - cave.Vector3(0,.2,0), cave.BitMask(15))
			if scan.hit:
			
			
				if scan.entity.name == "Player":
					
					print("Player Hit")
					self.target = scan.entity
					self.anim.playByName("BlackOps_Rifle_Idle_Aim", .2, 0, False, 1)
					self.cooldownTimer.reset()
				
				
			else:
				self.anim.playByName("BlackOps_Rifle_Idle", .2)
				if self.cooldownTimer.get() > 3:
					self.target = None
					self.firstShot = True
			if self.target:
				
				self.targetPos = self.pos - self.target.getTransform().getPosition()
				self.targetPos.y = 0
				self.transf.lookAtSmooth(self.targetPos, .04, self.transf.getUpVector())
				
				self.tryAttack()
			else:
				if self.scanTimer.get() < 4.0:
					self.transf.rotate(0,.3 * cave.getDeltaTime(),0)
				
					
				elif self.scanTimer.get() > 4 and self.scanTimer.get() < 8.0:
					self.transf.rotate(0,-.3 * cave.getDeltaTime(),0)
					
				else:
					self.scanTimer.reset()
					self.anim.playByName("BlackOps_Rifle_Idle", .1, 0, True, 0)
					print("reset")
			
			self.checkHealth()
	
	def checkHealth(self):
		scene = cave.getScene()
		if self.Health <= 0:
			if self.isDead == False:	
				self.end(scene)
				self.isDead = True

			
	
	def takeDamage(self, damage, attacker : cave.Entity, position):
		dt = cave.getDeltaTime()
		self.anim.playByName("BlackOps_Rifle_HitReact_2", .2, 0, False, 1)
		self.target = attacker
		#self.character.setWalkDirection(self.pos + self.transf.getForwardVector(), True, 2)
		self.transf.lookAtSmooth(self.pos - attacker.getTransform().getPosition(), .9, self.transf.getUpVector())
		self.Health = self.Health - damage
		Victim()
	
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
		
			if self.shotTimer.get() > 1:

				self.target.getPy("FirstPersonController").takeDamage(15)
				sd = cave.playSound("bang-04.ogg", 1, 0)
				
				self.shotTimer.reset()
		

	def end(self, scene: cave.Scene):
		scene2 = cave.getScene()
		cave.Entity = scene.addFromTemplate("AmmoPickup", self.pos - cave.Vector3(0,1.7,0), cave.Vector3(0,0,0), cave.Vector3(1,1,1))
		self.anim.playByName("BlackOps_Death_Front_Headshot", .1, 0, False, 2)
		
		self.entity.scheduleKill(2.5)
		
		pass
class Victim(cave.Component):
	def start(self, scene: cave.Scene):
		print("VICTIM!")
		pass
	def update(self, scene: cave.Scene):
		pass
	def end(self, scene: cave.Scene):
		pass