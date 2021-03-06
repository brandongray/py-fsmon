import unittest
import sys
import FilesystemMonitor
import re
import xml.sax

class FilesystemTest(unittest.TestCase):
	def test_getPercentUsed(self):
		a = FilesystemMonitor.Filesystem("/tmp", 1, 9)
		self.assertEquals(10, a.percentUsed)
		b = FilesystemMonitor.Filesystem("/tmp", 0, 100)
		self.assertEquals(0, b.percentUsed)
		c = FilesystemMonitor.Filesystem("/tmp", 100, 0)
		self.assertEquals(100, c.percentUsed)

	def test_setSpaceUsed(self):
		a = FilesystemMonitor.Filesystem("/tmp", 5, 5)
		a.setSpaceUsed(1, 9)
		self.assertEquals(10, a.percentUsed)
	
	def test_toXML(self):
		a = FilesystemMonitor.Filesystem("/tmp", 1, 9)
		b = "<Filesystem>/tmp</Filesystem>\n\
<kUsed>1</kUsed>\n\
<kFree>9</kFree>\n\
<PercentUsed>10.0</PercentUsed>\n"
		self.assertEquals(b, a.toXML())

class FilesystemManagerTest(unittest.TestCase):
	def test_checkWarningBelow(self):
		a = FilesystemMonitor.Filesystem("/tmp", 5, 10)
		fm = FilesystemMonitor.FilesystemManager(a)
		self.assertNotEqual(True, fm.checkWarning())

	def test_checkWarningBooleanFalse(self):
		a = FilesystemMonitor.Filesystem("/tmp", 5, 10)
		fm = FilesystemMonitor.FilesystemManager(a)
		fm.checkWarning()
		self.assertNotEqual(True, fm.aboveWarning)

	def test_checkWarningBooleanTrue(self):
		a = FilesystemMonitor.Filesystem("/tmp", 9, 1)
		fm = FilesystemMonitor.FilesystemManager(a)
		fm.checkWarning()
		self.assertEquals(True, fm.aboveWarning)

	def test_checkWarningAbove(self):
		a = FilesystemMonitor.Filesystem("/tmp", 9, 1)
		fm = FilesystemMonitor.FilesystemManager(a)
		self.assertEquals(True, fm.checkWarning())

	def test_checkCriticalBelow(self):
		a = FilesystemMonitor.Filesystem("/tmp", 5, 10)
		fm = FilesystemMonitor.FilesystemManager(a)
		self.assertNotEqual(True, fm.checkCritical())

	def test_checkCriticalAbove(self):
		a = FilesystemMonitor.Filesystem("/tmp", 95, 5)
		fm = FilesystemMonitor.FilesystemManager(a)
		self.assertEquals(True, fm.checkCritical())

	def test_checkFatalBelow(self):
		a = FilesystemMonitor.Filesystem("/tmp", 5, 10)
		fm = FilesystemMonitor.FilesystemManager(a)
		self.assertNotEqual(True, fm.checkFatal())

	def test_checkFatalAbove(self):
		a = FilesystemMonitor.Filesystem("/tmp", 10, 0)
		fm = FilesystemMonitor.FilesystemManager(a)
		self.assertEquals(True, fm.checkFatal())

	def test_toXML(self):
		a = FilesystemMonitor.Filesystem("/tmp", 1, 9)
		fm = FilesystemMonitor.FilesystemManager(a)
		b = "<Filesystem>/tmp</Filesystem>\n\
<kUsed>1</kUsed>\n\
<kFree>9</kFree>\n\
<PercentUsed>10.0</PercentUsed>\n\
<WarningThreshold>90</WarningThreshold>\n\
<WarningThresholdAction>none</WarningThresholdAction>\n\
<WarningThresholdClearAction>none</WarningThresholdClearAction>\n\
<CriticalThreshold>95</CriticalThreshold>\n\
<CriticalThresholdAction>none</CriticalThresholdAction>\n\
<CriticalThresholdClearAction>none</CriticalThresholdClearAction>\n\
<FatalThreshold>100</FatalThreshold>\n\
<FatalThresholdAction>none</FatalThresholdAction>\n\
<FatalThresholdClearAction>none</FatalThresholdClearAction>\n"
		self.assertEquals(b, fm.toXML())

class HFSFilesystemManagerTest(unittest.TestCase):
	def test_checkWarningBelow(self):
		a = FilesystemMonitor.Filesystem("/tmp", 5, 10)
		fm = FilesystemMonitor.HFSFilesystemManager(a)
		self.assertNotEqual(True, fm.checkWarning())

	# Incomplete test (leaving for future use) : Only for inheritance testing
	def test_increaseFilesystem(self):
		a = FilesystemMonitor.Filesystem("/tmp", 10, 1)
		fm = FilesystemMonitor.HFSFilesystemManager(a)
		self.assertEquals("future", fm.increaseFilesystem())

	def test_updateSpaceUsed(self):
		a = FilesystemMonitor.Filesystem("/tmp", 10, 10)
		initial = 10
		fm = FilesystemMonitor.HFSFilesystemManager(a)
		fm.updateSpaceUsed()
		after = fm.filesystem.kUsed
		self.assertNotEquals(initial, after)

class FilesystemManagerFactoryTest(unittest.TestCase):
	def test_getFilesystemManager(self):
		a = FilesystemMonitor.Filesystem("/tmp")
		fm = FilesystemMonitor.FilesystemManagerFactory.getFilesystemManager(a,"hfs")
		path = fm.filesystem.path
		self.assertEquals("/tmp", path)

	def test_getFilesystemSpaceUsedkUsed(self):
		(kUsed, kFree) = FilesystemMonitor.FilesystemManagerFactory.getFilesystemSpaceUsed("/")
		bool = kUsed > 0
		self.assertTrue(bool)

	def test_getFilesystemSpaceUsedkFree(self):
		(kUsed, kFree) = FilesystemMonitor.FilesystemManagerFactory.getFilesystemSpaceUsed("/")
		bool = kFree > 0
		self.assertTrue(bool)

class FilesystemMonitorTest(unittest.TestCase):
	def test_getFilesystemLayout(self):
		a = FilesystemMonitor.FilesystemMonitor()
		a.getFilesystemLayout()
		# MacOSX specific (change soon)
		self.assertEquals("hfs", a.layout["/"])

	def test_initializeFilesystemManagersContainsRoot(self):
		a = FilesystemMonitor.FilesystemMonitor()
		a.initializeFilesystemManagers()
		self.assertTrue(a.filesystemManagers.has_key("/"))

	def test_initializeFilesystemManagersHasDefaultWarning(self):
		a = FilesystemMonitor.FilesystemMonitor()
		a.initializeFilesystemManagers()
		fm = a.filesystemManagers["/"]
		self.assertEquals(90, fm.warn)

	def test_checkFilesystemThresholds(self):
		a = FilesystemMonitor.FilesystemMonitor()
		a.initializeFilesystemManagers()
		a.checkFilesystemThresholds()
		# I'm not sure the best test case of checking filesystems so I will leave this for later

	def test_toXML(self):
		# Check to see if it fits the following regex one or more times
		a = "(<Filesystem>.*</Filesystem>\n\
<kUsed>\d+</kUsed>\n\
<kFree>\d+</kFree>\n\
<PercentUsed>\d+\.\d+</PercentUsed>\n\
<WarningThreshold>\d\.?\d*</WarningThreshold>\n\
<WarningThresholdAction>.*</WarningThresholdAction>\n\
<WarningThresholdClearAction>.*</WarningThresholdClearAction>\n\
<CriticalThreshold>\d\.?\d*</CriticalThreshold>\n\
<CriticalThresholdAction>.*</CriticalThresholdAction>\n\
<CriticalThresholdClearAction>.*</CriticalThresholdClearAction>\n\
<FatalThreshold>\d\.?\d*</FatalThreshold>\n\
<FatalThresholdAction>.*</FatalThresholdAction>\n\
<FatalThresholdClearAction>.*</FatalThresholdClearAction>\n)+"
		b = FilesystemMonitor.FilesystemMonitor()
		b.initializeFilesystemManagers()
		self.assertTrue(re.search(a, b.toXML()))

	def test_run(self):
		# I'm not sure the best test case for running on a test server so I will leave this for later
		pass

	def test_processConfigurationFile(self):
		a = FilesystemMonitor.FilesystemMonitor()
		a.processConfigurationFile("./xml/simple.xml")
		# Put code here...
		fm = a.filesystemManagers["/"]
		self.assertEquals(85, fm.warn)

	def test_processConfigurationFileMalformedXML(self):
		a = FilesystemMonitor.FilesystemMonitor()
		self.assertRaises(xml.sax.SAXParseException, a.processConfigurationFile, "./xml/simple-mal.xml")

class ConfigHandlerTest(unittest.TestCase):
	"""The tests below are all related to XML parsing"""

	def test_DefaultThresholds(self):
		parser = xml.sax.make_parser()
		handler = FilesystemMonitor.ConfigHandler()
		parser.setContentHandler(handler)
		parser.parse("./xml/simple.xml")
		self.assertEquals(80, handler.mapping["default"]["warn"])
		self.assertEquals(85, handler.mapping["default"]["critical"])
		self.assertEquals(90, handler.mapping["default"]["fatal"])
		self.assertEquals("echo \"warn default!\"", handler.mapping["default"]["warn_action"])
		self.assertEquals("echo \"critical default!\"", handler.mapping["default"]["critical_action"])
		self.assertEquals("echo \"fatal default!\"", handler.mapping["default"]["fatal_action"])
		self.assertEquals("echo \"warn default clear!\"", handler.mapping["default"]["warn_clear"])
		self.assertEquals("echo \"critical default clear!\"", handler.mapping["default"]["critical_clear"])
		self.assertEquals("echo \"fatal default clear!\"", handler.mapping["default"]["fatal_clear"])

	def test_DefinedThresholds(self):
		parser = xml.sax.make_parser()
		handler = FilesystemMonitor.ConfigHandler()
		parser.setContentHandler(handler)
		parser.parse("./xml/simple.xml")
		self.assertEquals(85, handler.mapping["/"]["warn"])
		self.assertEquals(90, handler.mapping["/"]["critical"])
		self.assertEquals(95, handler.mapping["/"]["fatal"])
		self.assertEquals("echo \"warn defined!\"", handler.mapping["/"]["warn_action"])
		self.assertEquals("echo \"critical defined!\"", handler.mapping["/"]["critical_action"])
		self.assertEquals("echo \"fatal defined!\"", handler.mapping["/"]["fatal_action"])
		self.assertEquals("echo \"warn defined clear!\"", handler.mapping["/"]["warn_clear"])
		self.assertEquals("echo \"critical defined clear!\"", handler.mapping["/"]["critical_clear"])
		self.assertEquals("echo \"fatal defined clear!\"", handler.mapping["/"]["fatal_clear"])

	def test_malformedXML(self):
		parser = xml.sax.make_parser()
		handler = FilesystemMonitor.ConfigHandler()
		parser.setContentHandler(handler)
		self.assertRaises(xml.sax.SAXParseException, parser.parse, "./xml/simple-mal.xml")

	def test_DefinedFatalActionClearThresholdMinDefault(self):
		fsmon = FilesystemMonitor.FilesystemMonitor()
		fsmon.processConfigurationFile("./xml/simple-min.xml")
		fm = fsmon.filesystemManagers["/"]
		self.assertEquals("echo \"critical default!\"", fm.critical_action)

	def test_DefinedFatalActionClearThresholdMinDefined(self):
		fsmon = FilesystemMonitor.FilesystemMonitor()
		fsmon.processConfigurationFile("./xml/simple-min.xml")
		fm = fsmon.filesystemManagers["/"]
		self.assertEquals(91, fm.fatal)


if __name__ == '__main__':
	if sys.platform != "darwin":
		print "The platform " + sys.platform + " is not yet implemented!"
		sys.exit(1)
	else:
		unittest.main()
