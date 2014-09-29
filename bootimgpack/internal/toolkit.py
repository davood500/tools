#!/usr/bin/env python
# Filename tools.py

__author__ = 'duanqizhi01@baidu.com (duanqz)'


### Import blocks

import os
import shutil
import commands
import tempfile

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET



### Class blocks

class Toolkit:
    """
    Toolkit including all tools
    """

    TOOLS_ROOT = os.path.dirname(os.path.abspath(__file__))
    TOOLKIT_XML = os.path.join(TOOLS_ROOT, "toolkit.xml")
    TYPE_CONFIG = "type.config"

    allTools = {}

    def __init__(self):
        """
        Initialize tools factory from config.xml
        """

        tree = ET.parse(Toolkit.TOOLKIT_XML)
        for tool in tree.findall("tool"):
            bootType = tool.attrib["type"]
            unpackTool = tool.find("unpack").text
            packTool = tool.find("pack").text
            self.allTools[bootType] =  { "UNPACK" : os.path.join(Toolkit.TOOLS_ROOT, unpackTool),
                                         "PACK"   : os.path.join(Toolkit.TOOLS_ROOT, packTool) }

    def parseType(self, bootfile):
        """
        Match appropriate tools for the boot image file.
        """

        tryType = None

        # Try to unpack boot image for each type,
        # choose the appropriate one.
        sortedTypes = sorted(self.allTools.keys(), reverse=True)
        for bootType in sortedTypes:
            # Try to unpack the boot image by unpack tool
            unpackTool = self.getTools(bootType, "UNPACK")
            if BootimgParser.tryUnpack(unpackTool, bootfile) == True:
                tryType = bootType
                break

        BootimgParser.clearTempDir()

        return tryType

    def getTools(self, bootType, attrib=None):
        """
        Get tools by type.
        """

        tools = self.allTools.get(bootType)
        if attrib == None :
            return tools
        else:
            return tools[attrib]

    @staticmethod
    def storeType(bootType, bootout):
        # Serialize
        fileHandle = open(os.path.join(bootout, Toolkit.TYPE_CONFIG), "w")
        fileHandle.write(bootType)
        fileHandle.close()

    @staticmethod
    def retrieveType(bootout):
        # De-serialize
        try:
            fileHandle = open(os.path.join(bootout, Toolkit.TYPE_CONFIG), "r")
            bootType = fileHandle.read().rstrip()
            fileHandle.close()
        except:
            print ">>> Can not find type.config, use COMMON as image type by default"
            bootType = "COMMON"
        return bootType

### End of class Toolkit


class BootimgParser:
    """
    Match out appropriate tools
    """

    # Directory for temporary data storage.
    TEMP_DIR = tempfile.mkdtemp()

    @staticmethod
    def tryUnpack(unpackTool, bootimg):
        """
        Try to unpack the boot image into TEMP_DIR.
        Return whether unpack successfully or not.
        """

        BootimgParser.clearTempDir()

        cmd = unpackTool + " " + bootimg + " " + BootimgParser.TEMP_DIR
        result = commands.getstatusoutput(cmd)

        # Debug code. Useless for release version
        BootimgParser.__debug("Try " + cmd)
        BootimgParser.__debug(result)

        return BootimgParser.isUnpackSuccess(result)

    @staticmethod
    def isUnpackSuccess(result):
        """
        Check whether unpack the boot image successfully or not.
        """

        kernelExists = os.path.exists(os.path.join(BootimgParser.TEMP_DIR, "kernel")) or \
                       os.path.exists(os.path.join(BootimgParser.TEMP_DIR, "zImage"))

        initrcExists = os.path.exists(os.path.join(BootimgParser.TEMP_DIR, "ramdisk/init.rc")) or \
                       os.path.exists(os.path.join(BootimgParser.TEMP_DIR, "RAMDISK/init.rc"))

        # True : Result is correct and one the file exists
        return BootimgParser.isCorretResult(result) and \
               (kernelExists and initrcExists)

    @staticmethod
    def isCorretResult(result):
        """
        Check whether the result contains error or not
        """

        errKey1 = "Could not find any embedded ramdisk images"
        errKey2 = "Aborted"
        strResult = str(result)

        # True : all the error keys are not found in result
        return strResult.find(errKey1) < 0 and \
               strResult.find(errKey2) < 0

    @staticmethod
    def clearTempDir():
        """
        Clear the temporary directory
        """

        if os.path.exists(BootimgParser.TEMP_DIR) == True:
            shutil.rmtree(BootimgParser.TEMP_DIR)

    @staticmethod
    def __debug(msg):
        if False: print msg
### End of class ToolsMatcher

