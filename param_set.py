from array import array
from datetime import datetime
import array

class sf_params:
	###roovars in format : [init val, lower lim., upper lim.]
	paramList_default={'dphibins_num':100, 'bal_N':1.,'effcy':[0.9,0.,1.],'mistag':[0.1,0.,1.]}
	def __init__(self,**kwargs):
		##set default value
		for key, value in sf_params.paramList_default:
			self.paramList[key] = value
		
		##set custom value
		for key, value in kwargs.items():
			if key not in self.paramList:
				print("error: wrong key, %s is not in param List" % key)
			else:
				self.paramList[key] = value

		self.setDefaults()
				
			

		for key, value in kwargs.items():
			self.key = value
		

	def get_dphibins(self):
		dphibins = []
		for i in range(self.dphibins_num+1):
			tick = 2.0/self.dphibins_num
			dphibins.append(i*tick)
		return array.array("d",dphibins)




