from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal, QEvent, QObject, QPoint
import xml.etree.ElementTree as ET
import os
import cv2
import numpy as np

# file read and write utils
class fileUtils:
    def __init__(self):
        None

    # judge that color list file exist or not
    def judgeColorDataFile(self):
        currentPath = os.getcwd()
        if os.path.exists(currentPath + "/colorDataList.xml"):
            return True
        else:
            return False

    # load color data list file
    def loadColorDataFile(self):
        whiteColorData = []
        redColorData = []

        xmlData = ET.parse("./colorDataList.xml")
        root = xmlData.getroot()

        for white in root.findall("WHITE") :
            for i in range(0, int(white.attrib["num"])) :
                whiteValue = white.find("N" + str(i)).text
                whiteColorData.append(whiteValue)
        for red in root.findall("RED") :
            for i in range(0, int(red.attrib["num"])):
                redValue = red.find("N" + str(i)).text
                redColorData.append(redValue)

        return whiteColorData, redColorData


    # store color data list
    def storeColorDataFile(self, _white, _red):
        whiteColorData = _white
        redColorData = _red

        root = ET.Element("COLOR")
        element1 = ET.SubElement(root, "WHITE", num=str(len(whiteColorData)))
        element2 = ET.SubElement(root, "RED", num=str(len(redColorData)))

        for i in range(0, len(whiteColorData)):
            sub_element1 = ET.SubElement(element1, "N" + str(i))
            #sub_element1.text = (str(format(whiteColorData[i][2], 'x')) + str(format(whiteColorData[i][1], 'x')) + str(format(whiteColorData[i][0], 'x'))).upper()
            sub_element1.text = str(whiteColorData[i])
        for i in range(0, len(redColorData)):
            sub_element2 = ET.SubElement(element2, "N" + str(i))
            #sub_element2.text = (str(format(redColorData[i][2], 'x')) + str(format(redColorData[i][1], 'x')) + str(format(redColorData[i][0], 'x'))).upper()
            sub_element2.text = str(redColorData[i])

        self.indent(root)
        tree = ET.ElementTree(root)

        with open('./colorDataList.xml', "wb") as file:
            tree.write(file, encoding='utf-8', xml_declaration=True)


    # arrange xml data
    def indent(self, elem, level = 0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i


# image read and show utils
class imgUtils :

    # read images from directory
    def readImages(self, _directory):
        files = []
        for (dirpath, dirnames, filenames) in os.walk(_directory):
            files.extend(filenames)
        return files


    # load image data
    def showImage(self, _imageFrame, currentImage):
        returnImageData = []
        try :
            #currentImageData = cv2.imread(currentImage)
            img_array = np.fromfile(currentImage, np.uint8)
            currentImageData = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            currentImageData = cv2.resize(currentImageData, (540, 540))
            returnImageData = currentImageData

            currentImageData = QtGui.QImage(currentImageData.data, currentImageData.shape[0], currentImageData.shape[1], QtGui.QImage.Format_RGB888).rgbSwapped()
            _imageFrame.setPixmap(QtGui.QPixmap.fromImage(currentImageData))
        except cv2.error as e :
            return returnImageData
        else :
            return returnImageData


    # draw object detection result image
    def showImage_DetectionResult(self, _imageFrame, _img):
        _img = QtGui.QImage(_img.data, _img.shape[0], _img.shape[1], QtGui.QImage.Format_RGB888).rgbSwapped()
        _imageFrame.setPixmap(QtGui.QPixmap.fromImage(_img))


# image hover event
class hoverTracker(QObject):
    positionChanged = pyqtSignal(QPoint)

    def __init__(self, widget):
        super().__init__(widget)
        self._widget = widget
        self.widget.setMouseTracking(True)
        self.widget.installEventFilter(self)


    @property
    def widget(self):
        return self._widget


    def eventFilter(self, obj, event):
        if obj is self.widget and event.type() == QEvent.MouseMove:
            self.positionChanged.emit(event.pos())
        return super().eventFilter(obj, event)