from PyQt5.QtCore import Qt, pyqtSlot, QPoint
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QDesktopWidget, QGroupBox, QLabel, QComboBox, QPushButton, QMessageBox, QFileDialog, QAction, qApp

from programUtils import imgUtils, fileUtils, hoverTracker
from hairFollicle_ObjectDetection import imgProcessing


class HairFollicle_mainpage(QMainWindow) :
    def __init__(self):
        super().__init__()

        # data directory info
        self.imageDirectoryPath = QLabel("NONE")
        self.imageDirectoryPath.setAlignment(Qt.AlignCenter)
        self.imageDirectoryPath.setStyleSheet('QLabel {color:red}')

        # image Data list
        self.currentImgNum = QLabel()
        self.totalImgNum = QLabel()
        self.imageDataList = []
        self.currentImgIndex = -1

        # mode info - 1: setting mode, 2: detection mode
        self.modeNum = 2

        # color list
        self.whiteColorData = []
        self.redColorData = []
        self.White_list = QComboBox()
        self.Red_list = QComboBox()

        # color values
        self.redColorValue = "D"
        self.whiteColorValue = "D"

        # store or detection start button
        self.calculationButton = QPushButton('Store Color Data / Start To Detection')

        # show image
        self.imageFrame = QLabel(self)
        self.imageFrame.setFixedWidth(540)
        self.imageFrame.setFixedHeight(540)

        # image data
        self.colorINFO_Label = QLabel()
        self.hovered_Xpos = 0
        self.hovered_Ypos = 0

        # show image button
        self.beforeButton = QPushButton('<')
        self.nextButton = QPushButton('>')

        # result
        self.whiteNum_Label = QLabel()
        self.whiteArea_Label = QLabel()
        self.redNum_Label = QLabel()
        self.redArea_Label = QLabel()

        # class variables
        self.imgUtils_class = imgUtils()
        self.fileUtils_class = fileUtils()
        self.hoverTracker_class = hoverTracker(self.imageFrame)
        self.imageProcessing_class = imgProcessing()

        # init UI
        self.initUI()


    def initUI(self):

        # Draw
        self.createMenuBar()
        self.drawLayoutAndWidget()

        # Window
        # self.setWindowIcon(QIcon('ICON.ico'))
        self.setWindowTitle('Hair Follicle Processing Application')
        self.resize(900, 1000)
        self.moveCenter()


    def moveCenter(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def createMenuBar(self):
        menubar = self.menuBar()
        infoMenu = menubar.addMenu('INFO')

        info = QAction('About', self)
        info.triggered.connect(self.infoWindows)
        exit = QAction('Exit', self)
        exit.triggered.connect(qApp.quit)

        infoMenu.addAction(info)
        infoMenu.addAction(exit)


    def drawLayoutAndWidget(self):

        firstFloor = self.directoryPathLayout()
        secondFloor = self.modeSelectLayout()
        thirdFloor = self.setColorLayout()
        fourthFloor = self.ImageLayout()
        fifthFloor = self.resultLayout()

        vLayout = QVBoxLayout()
        vLayout.addStretch(1)
        vLayout.addWidget(firstFloor)
        vLayout.addStretch(1)
        vLayout.addWidget(secondFloor)
        vLayout.addStretch(1)
        vLayout.addWidget(thirdFloor)
        vLayout.addStretch(1)
        vLayout.addWidget(fourthFloor)
        vLayout.addStretch(1)
        vLayout.addWidget(fifthFloor)
        vLayout.addStretch(1)

        centralWidget = QWidget()
        centralWidget.setLayout(vLayout)
        self.setCentralWidget(centralWidget)


    def infoWindows(self):
        QMessageBox.information(self, 'INFO', 'Program Version : 1.02 ver \nFinal Update : 2022-07-08', QMessageBox.Yes)


    def directoryPathLayout(self):

        groupbox = QGroupBox('Set Data')

        directory_Label = QLabel('Select Image Directory : ', self)
        setDirectoryPushButton = QPushButton("Select Directory That Stored Images")
        setDirectoryPushButton.clicked.connect(self.setDirectory)

        hcontent_Layout = QHBoxLayout()
        hcontent_Layout.addStretch(1)
        hcontent_Layout.addWidget(directory_Label)
        hcontent_Layout.addWidget(setDirectoryPushButton)
        hcontent_Layout.addStretch(1)

        vcontent_Layout = QVBoxLayout()
        vcontent_Layout.addStretch(1)
        vcontent_Layout.addLayout(hcontent_Layout)
        vcontent_Layout.addWidget(self.imageDirectoryPath)
        vcontent_Layout.addStretch(1)

        groupbox.setLayout(vcontent_Layout)

        return groupbox


    def modeSelectLayout(self):

        groupbox = QGroupBox('Set Mode')

        mode_Label = QLabel('Select Mode : ', self)

        mode_list = QComboBox(self)
        mode_list.addItem('Setting Mode')
        mode_list.addItem('Detection Mode')
        mode_list.activated[str].connect(self.onMODE_ComboBoxActivated)
        mode_list.setCurrentIndex(1)

        hcontent_Layout = QHBoxLayout()
        hcontent_Layout.addStretch(1)
        hcontent_Layout.addWidget(mode_Label)
        hcontent_Layout.addWidget(mode_list)
        hcontent_Layout.addStretch(1)

        vcontent_Layout = QVBoxLayout()
        vcontent_Layout.addStretch(1)
        vcontent_Layout.addLayout(hcontent_Layout)
        vcontent_Layout.addStretch(1)

        groupbox.setLayout(vcontent_Layout)

        return groupbox


    def setColorLayout(self):

        groupbox = QGroupBox('Select Color Values')

        White_Label = QLabel('Select White Color Value : ', self)
        self.White_list.addItem('Default Result')
        self.White_list.addItem('Intersection Result')
        self.White_list.addItem('Union Result')
        self.White_list.activated[str].connect(self.onWHITEcolor_ComboBoxActivated)
        self.White_list.setCurrentIndex(0)

        hcontent_Layout1 = QHBoxLayout()
        hcontent_Layout1.addStretch(1)
        hcontent_Layout1.addWidget(White_Label)
        hcontent_Layout1.addWidget(self.White_list)
        hcontent_Layout1.addStretch(1)

        Red_Label = QLabel('Select Red Color Value :   ', self)
        self.Red_list.addItem('Default Result')
        self.Red_list.addItem('Intersection Result')
        self.Red_list.addItem('Union Result')
        self.Red_list.activated[str].connect(self.onREDcolor_ComboBoxActivated)
        self.Red_list.setCurrentIndex(0)

        hcontent_Layout2 = QHBoxLayout()
        hcontent_Layout2.addStretch(1)
        hcontent_Layout2.addWidget(Red_Label)
        hcontent_Layout2.addWidget(self.Red_list)
        hcontent_Layout2.addStretch(1)

        self.calculationButton.setDisabled(True)
        self.calculationButton.clicked.connect(self.calulationButton_Clicked)

        vcontent_Layout = QVBoxLayout()
        vcontent_Layout.addStretch(1)
        vcontent_Layout.addLayout(hcontent_Layout1)
        vcontent_Layout.addStretch(1)
        vcontent_Layout.addLayout(hcontent_Layout2)
        vcontent_Layout.addStretch(1)
        vcontent_Layout.addWidget(self.calculationButton)
        vcontent_Layout.addStretch(1)

        groupbox.setLayout(vcontent_Layout)

        return groupbox


    def ImageLayout(self):

        groupbox = QGroupBox('Image Field')

        self.currentImgNum.setText("N")
        slash_Label = QLabel(' / ', self)
        self.totalImgNum.setText("N")

        hcontent_Layout1 = QHBoxLayout()
        hcontent_Layout1.addStretch(1)
        hcontent_Layout1.addWidget(self.currentImgNum)
        hcontent_Layout1.addWidget(slash_Label)
        hcontent_Layout1.addWidget(self.totalImgNum)
        hcontent_Layout1.addStretch(1)

        self.colorINFO_Label.setStyleSheet('QLabel {color:blue}')
        self.colorINFO_Label.setAlignment(Qt.AlignCenter)

        self.beforeButton.setDisabled(True)
        self.beforeButton.clicked.connect(self.beforeButton_Clicked)

        self.imageFrame.mousePressEvent = self.imageClicked
        self.hoverTracker_class.positionChanged.connect(self.imageHovered)

        self.nextButton.setDisabled(True)
        self.nextButton.clicked.connect(self.nextButton_Clicked)

        hcontent_Layout2 = QHBoxLayout()
        hcontent_Layout2.addStretch(1)
        hcontent_Layout2.addWidget(self.beforeButton)
        hcontent_Layout2.addWidget(self.imageFrame)
        hcontent_Layout2.addWidget(self.nextButton)
        hcontent_Layout2.addStretch(1)

        vcontent_Layout = QVBoxLayout()
        vcontent_Layout.addStretch(1)
        vcontent_Layout.addLayout(hcontent_Layout1)
        vcontent_Layout.addStretch(1)
        vcontent_Layout.addWidget(self.colorINFO_Label)
        vcontent_Layout.addStretch(1)
        vcontent_Layout.addLayout(hcontent_Layout2)
        vcontent_Layout.addStretch(1)

        groupbox.setLayout(vcontent_Layout)

        return groupbox


    def resultLayout(self):

        groupbox = QGroupBox('Detection Result')

        Twhite_Label = QLabel('White INFO : ', self)
        Twhite_Label.setStyleSheet('QLabel {color:red}')

        TwhiteNum_Label = QLabel('White Total Num : ', self)
        self.whiteNum_Label.setText("N")

        TwhiteArea_Label = QLabel('White Area : ', self)
        self.whiteArea_Label.setText("N")

        hcontent_Layout1 = QHBoxLayout()
        hcontent_Layout1.addStretch(1)
        hcontent_Layout1.addWidget(TwhiteNum_Label)
        hcontent_Layout1.addWidget(self.whiteNum_Label)
        hcontent_Layout1.addStretch(1)
        hcontent_Layout1.addStretch(1)
        hcontent_Layout1.addWidget(TwhiteArea_Label)
        hcontent_Layout1.addWidget(self.whiteArea_Label)
        hcontent_Layout1.addStretch(1)

        Tred_Label = QLabel('Red INFO : ', self)
        Tred_Label.setStyleSheet('QLabel {color:red}')

        TredNum_Label = QLabel('Red Total Num : ', self)
        self.redNum_Label.setText("N")

        TredArea_Label = QLabel('Red Area : ', self)
        self.redArea_Label.setText("N")

        hcontent_Layout2 = QHBoxLayout()
        hcontent_Layout2.addStretch(1)
        hcontent_Layout2.addWidget(TredNum_Label)
        hcontent_Layout2.addWidget(self.redNum_Label)
        hcontent_Layout2.addStretch(1)
        hcontent_Layout2.addStretch(1)
        hcontent_Layout2.addWidget(TredArea_Label)
        hcontent_Layout2.addWidget(self.redArea_Label)
        hcontent_Layout2.addStretch(1)

        vcontent_Layout = QVBoxLayout()
        vcontent_Layout.addStretch(1)
        vcontent_Layout.addWidget(Twhite_Label)
        vcontent_Layout.addStretch(1)
        vcontent_Layout.addLayout(hcontent_Layout1)
        vcontent_Layout.addStretch(1)
        vcontent_Layout.addWidget(Tred_Label)
        vcontent_Layout.addStretch(1)
        vcontent_Layout.addLayout(hcontent_Layout2)
        vcontent_Layout.addStretch(1)

        groupbox.setLayout(vcontent_Layout)

        return groupbox


    # load color data file
    def loadColorDataFile(self):
        if not self.fileUtils_class.judgeColorDataFile() :
            return False
        else :
            # load data
            self.whiteColorData, self.redColorData = self.fileUtils_class.loadColorDataFile()

            # set comboBox
            for i in range(0, len(self.whiteColorData)) :
                self.White_list.addItem(str(self.whiteColorData[i]))
            for i in range(0, len(self.redColorData)) :
                self.Red_list.addItem(str(self.redColorData[i]))

            return True


    # load images from directory and then show image
    def showImage(self):
        self.imageDataList = self.imgUtils_class.readImages(self.imageDirectoryPath.text())
        self.currentImgNum.setText(str(self.currentImgIndex + 1))
        self.totalImgNum.setText(str(len(self.imageDataList)))
        currentImg_mat = self.imgUtils_class.showImage(self.imageFrame, self.imageDirectoryPath.text() + "/" + self.imageDataList[self.currentImgIndex])

        if currentImg_mat == [] :
            QMessageBox.warning(self, 'Attention', 'Color image files is not exist in this directory. \nSelect right directory.', QMessageBox.Yes)
        else :
            # set currnet image
            self.imageProcessing_class.setCurrentImg(currentImg_mat)


    # button event - select image directory
    def setDirectory(self):
        directoryPath = QFileDialog.getExistingDirectory(self)
        self.imageDirectoryPath.setText(directoryPath)
        self.imageDirectoryPath.setStyleSheet('QLabel {color:red}')

        # load image and then draw
        self.currentImgIndex = 0
        self.showImage()

        # activate button
        self.beforeButton.setDisabled(False)
        self.nextButton.setDisabled(False)
        self.onMODE_ComboBoxActivated("Detection Mode")


    # combobox event - select mode
    def onMODE_ComboBoxActivated(self, text):
        if text == "Setting Mode" :
            self.modeNum = 1
            self.calculationButton.setText("STORE Color Data")
            self.calculationButton.setDisabled(False)

        elif text == "Detection Mode" :
            if not self.loadColorDataFile() :
                QMessageBox.warning(self, 'Attention', 'Color data list file is not exist. \nDo setting first.', QMessageBox.Yes)
            else :
                self.modeNum = 2
                self.calculationButton.setText("START To Detection")
                self.calculationButton.setDisabled(False)


    # message box in combo box : select use or delete
    def messageBox_in_comboBox(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Attention")
        msg.setText('Select One. \nDo you want to use this color or delete this color?')

        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        button1 = msg.button(QMessageBox.Yes)
        button1.setText('USE')
        button2 = msg.button(QMessageBox.No)
        button2.setText('DELETE')
        msg.exec_()

        if msg.clickedButton() == button1:
            return 1
        elif msg.clickedButton() == button2:
            return 2


    # combobox event - select white color
    def onWHITEcolor_ComboBoxActivated(self, text):
        # message box
        retVal = self.messageBox_in_comboBox()

        if retVal == 1 :
            if text == "Default Result":
                self.whiteColorValue = "D"
            elif text == "Intersection Result":
                self.whiteColorValue = "I"
            elif text == "Union Result":
                self.whiteColorValue = "U"
            else :
                self.whiteColorValue = text

        elif retVal == 2 :
            itemIndex = self.White_list.currentIndex()
            if itemIndex > 106:
                self.White_list.removeItem(itemIndex)


    # combobox event - select red color
    def onREDcolor_ComboBoxActivated(self, text):
        # message box
        retVal = self.messageBox_in_comboBox()

        if retVal == 1:
            if text == "Default Result":
                self.redColorValue = "D"
            elif text == "Intersection Result":
                self.redColorValue = "I"
            elif text == "Union Result":
                self.redColorValue = "U"
            else:
                self.redColorValue = text

        elif retVal == 2:
            itemIndex = self.Red_list.currentIndex()
            if itemIndex > 160 :
                self.Red_list.removeItem(itemIndex)


    # button event - calculate
    def calulationButton_Clicked(self):
        if self.modeNum == 1 :
            self.fileUtils_class.storeColorDataFile(self.whiteColorData, self.redColorData)
        elif self.modeNum == 2 :
            whiteResultImg = self.imageProcessing_class.WhiteObjectDetection(self.whiteColorValue, self.whiteColorData)
            redResultImg = self.imageProcessing_class.RedObjectDetection(self.redColorValue, self.redColorData)
            finalImage, areaW, areaR = self.imageProcessing_class.FinalObjectDetection(whiteResultImg, redResultImg)

            # draw result image
            self.imgUtils_class.showImage_DetectionResult(self.imageFrame, finalImage)

            # draw result data
            self.whiteNum_Label.setText(str(len(areaW)))
            self.redNum_Label.setText(str(len(areaR)))

            whiteInfo = "NO DATA"
            redInfo = "NO DATA"
            if len(areaW) != 0:
                whiteInfo = "MIN : " + str(min(areaW)) + " | MAX : " + str(max(areaW)) + " | AVG = " + str(sum(areaW, 0.0) / len(areaW))
            if len(areaR) != 0:
                redInfo = "MIN : " + str(min(areaR)) + " | MAX : " + str(max(areaR)) + " | AVG = " + str(sum(areaR, 0.0) / len(areaR))

            self.whiteArea_Label.setText(whiteInfo)
            self.redArea_Label.setText(redInfo)


    # button event - select before image
    def beforeButton_Clicked(self):

        # init text
        self.whiteNum_Label.setText("N")
        self.whiteArea_Label.setText("N")
        self.redNum_Label.setText("N")
        self.redArea_Label.setText("N")

        if self.currentImgIndex < 1 :
            QMessageBox.warning(self, 'Attention', 'This is the first image.', QMessageBox.Yes)

        else :
            self.currentImgIndex -= 1

            # load image and then draw
            self.showImage()


    # button event - select next image
    def nextButton_Clicked(self):

        # init text
        self.whiteNum_Label.setText("N")
        self.whiteArea_Label.setText("N")
        self.redNum_Label.setText("N")
        self.redArea_Label.setText("N")

        if self.currentImgIndex == (int(self.totalImgNum.text()) - 1):
            QMessageBox.warning(self, 'Attention', 'This is the last image.', QMessageBox.Yes)

        else :
            self.currentImgIndex += 1

            # load image and then draw
            self.showImage()


    # message box in combo box : select use or delete
    def messageBox_in_colorData(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Attention")
        msg.setText('Select One. \nIs this color red or white?')

        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        button1 = msg.button(QMessageBox.Yes)
        button1.setText('WHITE')
        button2 = msg.button(QMessageBox.No)
        button2.setText('RED')
        msg.exec_()

        if msg.clickedButton() == button1:
            return 1
        elif msg.clickedButton() == button2:
            return 2


    # click - image store or delete
    def imageClicked(self, event) :
        # extract color data
        colorData = self.imageProcessing_class.extractColorData(self.hovered_Xpos, self.hovered_Ypos)
        colorData_text = (str(format(colorData[2], 'x')) + str(format(colorData[1], 'x')) + str(format(colorData[0], 'x'))).upper()
        self.colorINFO_Label.setText(colorData_text)

        # add color
        color = self.messageBox_in_colorData()
        if color == 1 :
            self.whiteColorData.append(colorData_text)
            self.White_list.addItem(colorData_text)
        elif color == 2 :
            self.redColorData.append(colorData_text)
            self.Red_list.addItem(colorData_text)


    # hover - show color data
    @pyqtSlot(QPoint)
    def imageHovered(self, _pos):
        if self.modeNum == 1 :
            self.hovered_Xpos = _pos.x()
            self.hovered_Ypos = _pos.y()