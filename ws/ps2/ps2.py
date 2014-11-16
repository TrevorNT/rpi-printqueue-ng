import logging
logging.basicConfig(level = logging.DEBUG)

from spyne.application import Application

from spyne.decorator import rpc

from spyne.service import ServiceBase

from spyne.model.primitive import Unicode
from spyne.model.complex import Iterable, ComplexModel

from spyne.protocol.http import HttpRpc
from spyne.protocol.json import JsonDocument

from spyne.server.wsgi import WsgiApplication

from spyne.model.fault import Fault

printers = {
	'area': [ 'printer1', 'printer2', 'printer3' ],
}

class PrinterStatus( ComplexModel ):
	# Specification:
	# status: one of "idle" (accepting jobs, queue empty),
	#                "working" (accepting jobs, queue has some jobs),
	#                "loaded" (accepting jobs, queue has many jobs),
	#                "error" (accepting jobs, but printer has encountered error),
	#                "offline" (not accepting jobs)
	# message: if status is "error" or "offline", passes along the message from pstat; otherwise, is an empty string
	# queue: a list of QueueJobs
	pass

class QueueJob( ComplexModel ):
	# Specification:
	# name: name of print job
	# size: size of print job
	# position: position in queue (where 0 is the job which is actively printing)
	pass

class PrinterStatusServer( ServiceBase ):
	@rpc( Unicode, _returns = Unicode )
	def Ping( context, pingMessage ):
		if pingMessage == "Ping":
			return "Pong"
		else
			raise Fault( faultcode = 'Client.MessageFault', faultstring = 'pingMessage was not "Ping"' )
	
	@rpc( Unicode, _returns = PrinterStatus )
	def Status( context, printerName ):
		pass
	
	@rpc( Unicode, _returns = Iterable( Unicode ) )
	def ListPrinters( context, areaName ):
		areaPrinters = printers.get(areaName, False)
		if not areaPrinters:
			raise Fault( faultcode = 'Client.ArgumentFault', faultstring = "The given areaName was not found" )
		for printer in areaPrinters:
			yield printer
	
	@rpc( _returns = Iterable( Unicode ) )
	def ListAreas( context ):
		for area in printers:
			yield area

app = Application( [ HelloWorldService ], tns = 'edu.rpi.PrinterStatusServer', in_protocol = HttpRpc( validator = "soft" ), out_protocol = JsonDocument() )

if __name__ == "__main__":
	from wsgiref.simple_server import make_server
	application = WsgiApplication( app )
	server = make_server( '0.0.0.0', 8000, application )
	server.serve_forever()
