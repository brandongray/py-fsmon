#!/usr/bin/env python
"""FilesystemMonitor
Written by : Brandon Gray (bgray@ossenabled.com)
Details : Monitors filesystem size"""

from __future__ import division
import commands
import sys
import time
import xml.sax.handler
import re
import getopt

class Filesystem(object):
	"""This class defines the 'basic' filesystem properties"""
	
	def __init__(self, path, kUsed=1, kFree=1):
		self.path = path
		self.setSpaceUsed(kUsed, kFree)

	def toXML(self):
		"""Returns XML of filesystem information"""
		return "<Filesystem>" + str(self.path) + "</Filesystem>\n\
<kUsed>" + str(self.kUsed) + "</kUsed>\n\
<kFree>" + str(self.kFree) + "</kFree>\n\
<PercentUsed>" + str(self.percentUsed) + "</PercentUsed>\n"

	def setSpaceUsed(self, kUsed, kFree):
		self.kUsed = kUsed
		self.kFree = kFree
		self.kTotal = kUsed + kFree
		self.percentUsed = (self.kUsed / self.kTotal) * 100

class FilesystemManager(object):
	"""This class sets attributes based on filesystem (thresholds, etc.)"""

	def __init__(self,filesystem):
		self.filesystem = filesystem
		self.warn = 90
		self.warn_action = "none"
		self.warn_clear = "none"
		self.aboveWarning = False
		self.critical = 95
		self.critical_action = "none"
		self.critical_clear = "none"
		self.aboveCritical = False
		self.fatal = 100
		self.fatal_action = "none"
		self.fatal_clear = "none"
		self.aboveFatal = False

	def checkWarning(self):
		"""Checks to see if percent is above warning threshold"""
		if self.filesystem.percentUsed >= self.warn:
			if self.aboveWarning != True:
				# Execute warning threshold!
				if self.warn_action != "none":
					commands.getstatusoutput(self.warn_action)
			self.aboveWarning = True
			return True
		if self.aboveWarning != False:
			# Executing warning clearing message!
			if self.warn_clear != "none":
				commands.getstatusoutput(self.warn_clear)
		self.aboveWarning = False
		return False

	def checkCritical(self):
		"""Checks to see if percent is above critical threshold"""
		if self.filesystem.percentUsed >= self.critical:
			if self.aboveCritical != True:
				# Execute critical threshold!
				if self.critical_action != "none":
					commands.getstatusoutput(self.critical_action)
				pass
			self.aboveCritical = True
			return True
		if self.aboveCritical != False:
			# Executing critical clearing message!
			if self.critical_clear != "none":
				commands.getstatusoutput(self.critical_clear)
		self.aboveCritical = False
		return False

	def checkFatal(self):
		"""Checks to see if percent is above fatal threshold"""
		if self.filesystem.percentUsed >= self.fatal:
			if self.aboveFatal != True:
				# Executing fatal threshold!
				if self.fatal_action != "none":
					commands.getstatusoutput(self.fatal_action)
			self.aboveFatal = True
			return True
		if self.aboveFatal != False:
			# Executing fatal clearing message!
			if self.fatal_clear != "none":
				commands.getstatusoutput(self.fatal_clear)
		self.aboveFatal = False
		return False

	def updateSpaceUsed(self):
		"""Updates the used space for the filesystem"""
		(kUsed, kFree) = FilesystemManagerFactory.getFilesystemSpaceUsed(self.filesystem.path)
		self.filesystem.setSpaceUsed(kUsed, kFree)

	def toXML(self):
		return self.filesystem.toXML() + "\
<WarningThreshold>" + str(self.warn) + "</WarningThreshold>\n\
<WarningThresholdAction>" + str(self.warn_action) + "</WarningThresholdAction>\n\
<WarningThresholdClearAction>" + str(self.warn_clear) + "</WarningThresholdClearAction>\n\
<CriticalThreshold>" + str(self.critical) + "</CriticalThreshold>\n\
<CriticalThresholdAction>" + str(self.critical_action) + "</CriticalThresholdAction>\n\
<CriticalThresholdClearAction>" + str(self.critical_clear) + "</CriticalThresholdClearAction>\n\
<FatalThreshold>" + str(self.fatal) + "</FatalThreshold>\n\
<FatalThresholdAction>" + str(self.fatal_action) + "</FatalThresholdAction>\n\
<FatalThresholdClearAction>" + str(self.fatal_clear) + "</FatalThresholdClearAction>\n"

# This class defines actions to be taken on HFS filesystems

class HFSFilesystemManager(FilesystemManager):
	"""This class sets attributes / methods based on HFS filesystem (thresholds, etc.)"""

	def __init__(self,filesystem):
		"""Inherit from FilesystemManager"""
		FilesystemManager.__init__(self,filesystem)

	def increaseFilesystem(self):
		"""Leaving for future development, inheritance testing only"""
		return "future"

class FilesystemManagerFactory(object):
	"""This class determines the filesystem type and returns the correct manager"""

	@staticmethod
	def getFilesystemManager(filesystem, type):
		"""This method determines the platform type and returns the correct filesystem manager"""
		if type == "hfs":
			return HFSFilesystemManager(filesystem)

	@staticmethod
	def getFilesystemSpaceUsed(filesystem):
		"""This method determines the platform type and returns (kUsed, kFree)"""
		if sys.platform == "darwin":
			(rc, output) = commands.getstatusoutput("df -k " + filesystem + " | egrep -v '^Filesystem'")
			line = output.split()
			return (int(line[2]), int(line[3]))

class FilesystemMonitor(object):
	"""This is the 'main' class which monitors, initializing, etc."""

	def __init__(self):
		self.layout = {}
		self.filesystemManagers = {}

	def getFilesystemLayout(self):
		"""Outputs a layout of {<filesystem name> : <filesystem type>}"""
		layout = {}
		if sys.platform == "darwin":
			(rc, output) = commands.getstatusoutput("mount -t hfs")
			lines = output.split("\n")
			for line in lines:
				items = line.split()
				layout[items[2]]= "hfs"
			self.layout = layout
	
	def initializeFilesystemManagers(self):
		"""Initializes the filesystem on the system, this is where fs configuration occurs"""
		self.getFilesystemLayout()
		for fs in self.layout:
			filesystem = Filesystem(fs)
			filesystemManager = FilesystemManagerFactory.getFilesystemManager(filesystem, self.layout[fs])
			filesystemManager.updateSpaceUsed()
			self.filesystemManagers[fs] = filesystemManager

	def checkFilesystemThresholds(self):
		"""Checks the filesystem thresholds for all initialized filesystems"""
		for key in self.filesystemManagers:
			fm = self.filesystemManagers[key]
			fm.updateSpaceUsed()
			if fm.checkWarning:
				if fm.checkCritical:
					if fm.checkFatal:
						pass
					pass
				pass

	def toXML(self):
		"""Returns XML of filesystem monitoring filesystems"""
		xmlOutput = ""
		for key in self.filesystemManagers:
			fm = self.filesystemManagers[key]
			xmlOutput += fm.toXML()
		return xmlOutput

	def run(self, timeout=60, file="none"):
		"""Main method for monitoring execution"""
		self.processConfigurationFile(file)
		self.checkFilesystemThresholds()
		while True:
			time.sleep(timeout)
			self.checkFilesystemThresholds()

	def processConfigurationFile(self, filename):
		"""Parses and processes the configuration file"""
		self.initializeFilesystemManagers()
		parser = xml.sax.make_parser()
		handler = ConfigHandler()
		parser.setContentHandler(handler)
		# Throws xml.sax.SAXParseException
		parser.parse(filename)

		for mount in self.filesystemManagers:
			fm = self.filesystemManagers[mount]
			if handler.mapping.has_key("default"):
				for key in handler.mapping["default"]:
					setattr(fm, key, handler.mapping["default"][key])
			if handler.mapping.has_key(mount):
				for key in handler.mapping[mount]:
					setattr(fm, key, handler.mapping[mount][key])

class ConfigHandler(xml.sax.handler.ContentHandler):
		"""Content handler for XML parsing"""
		def __init__(self):
			self.mapping = {}
			self.title = ""
			self.buffer = ""

		def startElement(self, name, attributes):
			self.buffer = ""
			if name == "default":
				self.title = name
				self.mapping[self.title] = {}
			elif name == "filesystem":
				self.title = attributes["mount"]
				self.mapping[self.title] = {}
		
		def characters(self, data):
			self.buffer += data

		def endElement(self, name):
			if re.search("^((warn)|(critical)|(fatal))(_action)?(_clear)?$", name):
				if re.match("^\d+$", self.buffer):
					self.mapping[self.title][name] = int(self.buffer)
				else:
					self.mapping[self.title][name] = self.buffer

def main(argv):
	if sys.platform != "darwin":
		print "The platform " + sys.platform + " is not yet implemented!"
		sys.exit(1)
	else:
		try:
			opts, args = getopt.getopt(argv, "hc:", ["help", "config="])
		except getopt.GetoptError, err:
			usage()
			sys.exit(2)

		config = "none"

		for o, a in opts:
			if o in ("-h", "--help"):
				usage()
				sys.exit(1)
			elif o in ("-c", "--config"):
				config = a

		if config == "none":
			usage()
			sys.exit(1)
		else:
			mon = FilesystemMonitor()
			try:
				mon.run(file=config)
			except xml.sax.SAXParseException:
				print "Problem parsing XML configuration file"
				sys.exit(1)

def usage():
	print "Usage : FilesystemMonitor.py --config=<path_to_config>"

if __name__ == '__main__':
		main(sys.argv[1:])
