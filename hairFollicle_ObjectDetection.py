import cv2
import numpy as np

class imgProcessing :
    def __init__(self):

        # current image data - mat
        self.currentImg = None
        self.imgHeightWidth = 540

        # default color values - HSV
        self.color_dict_HSV = {
            'red1': [[123, 30, 110], [180, 255, 250]],
            'red2': [[9, 255, 255], [0, 50, 70]],
            'background': [[45, 20, 0], [85, 255, 255]]
        }

        # default color values - BGR
        self.color_dict_BGR = {
            'Red_Union': [[110, 0, 60], [180, 140, 150]],
            'White_Union': [[110, 70, 30], [200, 160, 95]]
        }

        self.binaryThreshold = 178
        self.kernel1 = np.ones((2, 2), np.uint8)
        self.kernel2 = np.ones((5, 5), np.uint8)
        self.kernel3 = np.ones((3, 3), np.uint8)
        self.kernel4 = np.ones((1, 1), np.uint8)
        self.kernel5 = np.ones((7, 7), np.uint8)

        self.objectAreaMin = 17
        self.objectAreaMax = 250
        self.WhiteRed_Distance = 10


    def setCurrentImg(self, _img):
        self.currentImg = _img


    def RGBcodeParser(self, _rgb):
        colorValue = []
        for i in range(0, 6, 2) :
            colorValue.append(int('0x' + _rgb[i : i + 2], base=16))
        return list(reversed(colorValue))


    def extractColorData(self, xPos, yPos):
        # colorData = [blue, green, red]
        colorData = self.currentImg[yPos, xPos]
        return colorData


    def extractHSV(self, _bgr):
        pixel = np.uint8([[_bgr]])
        hsv = cv2.cvtColor(pixel, cv2.COLOR_BGR2HSV)
        return hsv[0][0]


    def convertBlackToWhite(self, _img):
        for y in range(self.imgHeightWidth):
            for x in range(self.imgHeightWidth):
                if _img[y, x] == 0:
                    _img[y, x] = 255
        return _img


    def findObjectArea(self, _img):
        cnt, labels, stats, centroids = cv2.connectedComponentsWithStats(_img)

        detectedObject = []
        for i in range(1, cnt):
            (x, y, w, h, area) = stats[i]

            if area > self.objectAreaMin and area < self.objectAreaMax:
                centerX, centerY = int(x + (w / 2)), int(y + (h / 2))
                radius = int((w + h) / 2)
                data = [centerX, centerY, radius, area]
                detectedObject.append(data)

        return detectedObject


    def drawDetectedObjectPositions(self, _whitePos, _redPos):
        original_image = self.currentImg.copy()

        # draw white pos
        areaData_white = []
        for white in _whitePos :
            cv2.circle(original_image, (white[0], white[1]), white[2], (0, 0, 255), 1)
            areaData_white.append(white[3])

        # draw red pos
        areaData_red = []
        for red in _redPos:
            cv2.circle(original_image, (red[0], red[1]), red[2], (0, 255, 255), 1)
            areaData_red.append(red[3])

        return original_image, areaData_white, areaData_red


    def FinalObjectDetection(self, _whiteImg, _redImg):
        # detected Data = [centerX, centerY, radius, area]
        whiteData = self.findObjectArea(_whiteImg)
        redData = self.findObjectArea(_redImg)

        # calculate distance between white and red
        deleteIndex = []
        indexW = 0
        for white in whiteData :
            for red in redData :
                distance = ((white[0] - red[0]) ** 2 + (white[1] - red[1]) ** 2) ** 0.5
                if distance < self.WhiteRed_Distance :
                    deleteIndex.append(indexW)
            indexW += 1

        # delete duplicated data
        delCount = 0
        for i in deleteIndex :
            whiteData.pop(i - delCount)
            delCount += 1

        # draw detected data
        finalImage, areaW, areaR = self.drawDetectedObjectPositions(whiteData, redData)

        return finalImage, areaW, areaR


    def WhiteObjectDetection(self, _whiteMode, _whiteList):

        detectionResult = None
        if _whiteMode == "D":
            detectionResult = self.WhiteCalculateDefault()
        elif _whiteMode == "I":
            detectionResult = self.calculateIntersection("W", _whiteList)
        elif _whiteMode == "U":
            detectionResult = self.calculateUnion("W", _whiteList)
        else :
            detectionResult = self.calculateCutomColor("W", _whiteMode)

        return detectionResult


    def RedObjectDetection(self, _redMode, _redList):

        detectionResult = None
        if _redMode == "D":
            detectionResult = self.RedCalculateDefault()
        elif _redMode == "I":
            detectionResult = self.calculateIntersection("R", _redList)
        elif _redMode == "U":
            detectionResult = self.calculateUnion("R", _redList)
        else :
            detectionResult = self.calculateCutomColor("R", _redMode)

        return detectionResult


    def WhiteCalculateDefault(self):
        original_img = self.currentImg.copy()
        original_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2HSV)

        # 1. convert to image : BGR to HSV
        hsv = cv2.cvtColor(original_img, cv2.COLOR_BGR2HSV)

        # 2. remove background
        mask = cv2.inRange(hsv, np.array(self.color_dict_HSV['background'][0]), np.array(self.color_dict_HSV['background'][1]))
        masking_result = cv2.bitwise_and(original_img, original_img, mask=~mask)

        # 3. convert to image : BGR to Gray
        img_gray = cv2.cvtColor(masking_result, cv2.COLOR_BGR2GRAY)

        # 4. convert pixel
        img_gray = self.convertBlackToWhite(img_gray.copy())

        # 5. image processing
        img_gray = cv2.GaussianBlur(img_gray, (3, 3), 0)
        (ret, img_binary) = cv2.threshold(img_gray, self.binaryThreshold, 255, cv2.THRESH_BINARY_INV)
        img_binary = cv2.erode(img_binary, self.kernel1, iterations=1)
        img_binary = cv2.dilate(img_binary, self.kernel2, iterations=1)
        img_binary = cv2.erode(img_binary, self.kernel3, iterations=1)

        return img_binary


    def RedCalculateDefault(self):
        original_img = self.currentImg.copy()

        # 1. convert to image : BGR to HSV
        hsv = cv2.cvtColor(original_img, cv2.COLOR_BGR2HSV)

        # 2. extract object
        mask1 = cv2.inRange(hsv, np.array(self.color_dict_HSV['red1'][0]), np.array(self.color_dict_HSV['red1'][1]))
        mask2 = cv2.inRange(hsv, np.array(self.color_dict_HSV['red2'][0]), np.array(self.color_dict_HSV['red2'][1]))

        # 3. image processing
        img_binary1 = cv2.erode(mask1, self.kernel1, iterations=1)
        img_binary1 = cv2.dilate(img_binary1, self.kernel2, iterations=1)
        img_binary1 = cv2.erode(img_binary1, self.kernel3, iterations=1)

        img_binary2 = cv2.erode(mask2, self.kernel1, iterations=1)
        img_binary2 = cv2.dilate(img_binary2, self.kernel2, iterations=1)
        img_binary2 = cv2.erode(img_binary2, self.kernel3, iterations=1)

        return img_binary1 + img_binary2


    def calculateUnion(self, _mode, _colorList):
        dicName = ""
        if _mode == "W" :
            dicName = "White_Union"
        elif _mode == "R" :
            dicName = "Red_Union"

        # 1. extract object
        original_img = self.currentImg.copy()
        mask = cv2.inRange(original_img, np.array(self.color_dict_BGR[dicName][0]), np.array(self.color_dict_BGR[dicName][1]))

        # 2. image processing
        img_binary = cv2.erode(mask, self.kernel4, iterations=1)
        img_binary = cv2.dilate(img_binary, self.kernel5, iterations=1)
        img_binary = cv2.erode(img_binary, self.kernel2, iterations=1)

        return img_binary


    def calculateIntersection(self, _mode, _colorList):

        result = np.zeros((self.imgHeightWidth, self.imgHeightWidth), np.uint8)
        for color in _colorList:
            result += self.calculateCutomColor(_mode, color)

        return result


    def calculateCutomColor(self, _mode, _color):
        rgbValue = self.RGBcodeParser(_color)

        R = rgbValue[0]
        G = rgbValue[1]
        B = rgbValue[2]

        addValue = 0

        if _mode == "W" :
            addValue = 5
        elif _mode == "R":
            addValue = 10

        # 1. extract object
        original_img = self.currentImg.copy()
        mask = cv2.inRange(original_img, np.array([B, G, R]), np.array([B + addValue, G + addValue, R + addValue]))

        # 2. image processing
        img_binary = cv2.erode(mask, self.kernel4, iterations=1)
        img_binary = cv2.dilate(img_binary, self.kernel5, iterations=1)
        img_binary = cv2.erode(img_binary, self.kernel2, iterations=1)

        return img_binary