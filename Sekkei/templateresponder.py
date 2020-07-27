import random
class TemplateResponder():
	def __init__(self):
		return

	#zenbu random
	def response(self,mode,target_name=None,role_name=None):
		self.mode=mode
		self.target_name=target_name
		self.role_name=role_name

		if self.mode=="co":
			return self.co()
		elif self.mode=="seer":
			return self.seer()
		elif self.mode=="medium":
			return self.medium()
		return self.random()


	def co(self):
		r=open("co.txt").read().split("\n")
		t=random.randint(0,len(r)-2)
		sentence=r[t]
		return sentence


	def seer(self):
		r=open("seer.txt").read().split("\n")
		t=random.randint(0,len(r)-2)
		sentence=r[t]
		if sentence.find("%target%")== -1:
			return sentence
		if self.target_name is not None:
			sentence=sentence.replace("%target%",self.target_name)
		return sentence


	def medium(self):
		r=open("medium.txt").read().split("\n")
		t=random.randint(0,len(r)-2)
		sentence=r[t]
		if sentence.find("%target%")== -1:
			return sentence
		if self.target_name is not None:
			sentence=sentence.replace("%target%",self.target_name)
		return sentence


	def random(self):
		r=open("random.txt").read().split("\n")
		t=random.randint(0,len(r)-2)
		sentence=r[t]
		return sentence

		
a=TemplateResponder()
		
		

