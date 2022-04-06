import time
import threading
import _thread
import websocket
import argparse
from gui import displayGUI as display
from events import Events
from network_node import networkNode
from data_prep import dataFix
#from proximitySensorArray import sensorArray

# (universal) dict 1-for listing index codes: {module index no., module name, data index no., datatype}
indexCodesDict = {'Central Instance':0, 'Sensor Array':1, 'Scanner':2, 'Orientation Module':3, 'Spillage Module':4, 'Display':5}

# (universal) dict 2-for listing datatype codes: {module index no., module name, data index no., datatype}
indexDatatypesDict = {0:int, 1:str, 2:bytes, 3:float}

class moduleHandler: # class for linking module script with network and data prep layers
	
	# handle module here- using dict which relates 
	# command input from the network node to different action 
	# function from specific module class
	# for the data FROM modules: send all of it regardless to the instance
	
	# (specific) dict 3-for linking command code to action func:{expected command, action func from module}
	#actionFuncDict = {'updateContent': disp.updateContent, 'startDisplay': disp.startDisplay}

	message = ""
	module = display()

	def __init__(self):
		#self.actionFuncDict = actionFuncDict
		print("Module created!")
		d = threading.Thread(target = self.module.startDisplay, args = ())
		d.start()

	def passMessage(self):
		while True:
			message = self.module.displayMessage()
			if self.message is not message:
				self.message = message
				networkNode.ws_send(self.message)

	def onReceived(self, packet):
		print("_______ACTION FUNC________")
		# call action command related functions from module class here
		print(packet)
		data = dataAgent.deserialize_data(packet)
		command = data['command']	
		try:
			#print(command)
			#print(type(command))
			self.module.updateContent(command)
			print(self.module.scanner_state)
		except KeyError:
			print("Wrong Command: Corresponding function not found!")

if __name__ == "__main__": 

	parser = argparse.ArgumentParser(description='Optional app description')
	parser.add_argument('-ip','--ipAddress', help='IP Address of destination node', required=False, default='192.168.68.108')#'35.229.162.143')
	parser.add_argument('-p','--port', help='Port to access at destination node', required=False, default=8080)
	args = parser.parse_args()
	
	moduleAgent = moduleHandler() 

	networkNode = networkNode(args.ipAddress, args.port, moduleAgent.onReceived)
	dataAgent = dataFix( indexCodesDict['Display'], indexCodesDict['Central Instance'], 1) #(source, destination, datatype)

	incoming = threading.Thread(target = networkNode.receiveMsgForever, args = ())
	incoming.start()

	#outgoing = threading.Thread(target = moduleAgent.passMessage, args = ())
	#outgoing.start()