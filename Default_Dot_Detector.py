import cv2
import numpy as np
import os

# current image data - mat
currentImg = None
imgHeightWidth = 540

# default color values - HSV
color_dict_HSV = {
    'red1': [[123, 30, 110], [180, 255, 250]],
    'red2': [[9, 255, 255], [0, 50, 70]],
    'background': [[45, 20, 0], [85, 255, 255]]
}

# image processing parameters
binaryThreshold = 178
kernel1 = np.ones((2, 2), np.uint8)
kernel2 = np.ones((5, 5), np.uint8)
kernel3 = np.ones((3, 3), np.uint8)
kernel4 = np.ones((1, 1), np.uint8)
kernel5 = np.ones((7, 7), np.uint8)

objectAreaMin = 17
objectAreaMax = 250
WhiteRed_Distance = 10


# function 1 : black pixel to white pixel
def convertBlackToWhite(_img):
    for y in range(imgHeightWidth):
        for x in range(imgHeightWidth):
            if _img[y, x] == 0:
                _img[y, x] = 255
    return _img


# function 2 : detect white object
def WhiteCalculateDefault():
    original_img = currentImg.copy()
    original_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2HSV)

    # 1. convert to image : BGR to HSV
    hsv = cv2.cvtColor(original_img, cv2.COLOR_BGR2HSV)

    # 2. remove background
    mask = cv2.inRange(hsv, np.array(color_dict_HSV['background'][0]), np.array(color_dict_HSV['background'][1]))
    masking_result = cv2.bitwise_and(original_img, original_img, mask=~mask)

    # 3. convert to image : BGR to Gray
    img_gray = cv2.cvtColor(masking_result, cv2.COLOR_BGR2GRAY)

    # 4. convert pixel
    img_gray = convertBlackToWhite(img_gray.copy())

    # 5. image processing
    img_gray = cv2.GaussianBlur(img_gray, (3, 3), 0)
    (ret, img_binary) = cv2.threshold(img_gray, binaryThreshold, 255, cv2.THRESH_BINARY_INV)
    img_binary = cv2.erode(img_binary, kernel1, iterations=1)
    img_binary = cv2.dilate(img_binary, kernel2, iterations=1)
    img_binary = cv2.erode(img_binary, kernel3, iterations=1)

    return img_binary


# function 3 : detect red object
def RedCalculateDefault():
    original_img = currentImg.copy()

    # 1. convert to image : BGR to HSV
    hsv = cv2.cvtColor(original_img, cv2.COLOR_BGR2HSV)

    # 2. extract object
    mask1 = cv2.inRange(hsv, np.array(color_dict_HSV['red1'][0]), np.array(color_dict_HSV['red1'][1]))
    mask2 = cv2.inRange(hsv, np.array(color_dict_HSV['red2'][0]), np.array(color_dict_HSV['red2'][1]))

    # 3. image processing
    img_binary1 = cv2.erode(mask1, kernel1, iterations=1)
    img_binary1 = cv2.dilate(img_binary1, kernel2, iterations=1)
    img_binary1 = cv2.erode(img_binary1, kernel3, iterations=1)

    img_binary2 = cv2.erode(mask2, kernel1, iterations=1)
    img_binary2 = cv2.dilate(img_binary2, kernel2, iterations=1)
    img_binary2 = cv2.erode(img_binary2, kernel3, iterations=1)

    return img_binary1 + img_binary2


# function 4 : find group area in the input image
def findObjectArea(_img):
    cnt, labels, stats, centroids = cv2.connectedComponentsWithStats(_img)

    detectedObject = []
    for i in range(1, cnt):
        (x, y, w, h, area) = stats[i]

        if area > objectAreaMin and area < objectAreaMax:
            centerX, centerY = int(x + (w / 2)), int(y + (h / 2))
            radius = int((w + h) / 2)
            data = [centerX, centerY, radius, area]
            detectedObject.append(data)

    return detectedObject


# function 5 : draw result of white object detection
def drawDetectedWhiteObjectPositions(_whitePos):
    original_image = currentImg.copy()

    # draw white pos
    areaData_white = []
    for white in _whitePos :
        cv2.circle(original_image, (white[0], white[1]), white[2], (0, 0, 255), 1)
        areaData_white.append(white[3])

    return original_image, areaData_white


# function 6 : draw result of red object detection
def drawDetectedRedObjectPositions(_redPos):
    original_image = currentImg.copy()

    # draw red pos
    areaData_red = []
    for red in _redPos:
        cv2.circle(original_image, (red[0], red[1]), red[2], (0, 255, 255), 1)
        areaData_red.append(red[3])

    return original_image, areaData_red


# function 7 : filtering
def FinalObjectDetection(_whiteImg, _redImg):
    # detected Data = [centerX, centerY, radius, area]
    whiteData = findObjectArea(_whiteImg)
    redData = findObjectArea(_redImg)

    # calculate distance between white and red
    deleteIndex = []
    indexW = 0
    for white in whiteData:
        for red in redData:
            distance = ((white[0] - red[0]) ** 2 + (white[1] - red[1]) ** 2) ** 0.5
            if distance < WhiteRed_Distance:
                deleteIndex.append(indexW)
        indexW += 1

    # delete duplicated data
    delCount = 0
    for i in deleteIndex:
        whiteData.pop(i - delCount)
        delCount += 1

    # draw detected data
    # white
    finalImageWhite, areaW = drawDetectedWhiteObjectPositions(whiteData)

    # red
    finalImageRed, areaR = drawDetectedRedObjectPositions(redData)

    return finalImageWhite, finalImageRed, areaW, areaR


# server function - ** 변형 필요 **
def excute(input_image) :

    # white Object Detection
    detectionWhiteResult = WhiteCalculateDefault()

    # red Object Detection
    detectionRedResult = RedCalculateDefault()

    # draw result into image
    finalImageWhite, finalImageRed, areaW, areaR = FinalObjectDetection(detectionWhiteResult, detectionRedResult)

    if len(areaW) != 0:
        whiteInfo = "MIN : " + str(min(areaW)) + " | MAX : " + str(max(areaW)) + " | AVG = " + str(sum(areaW, 0.0) / len(areaW))
        print("WHITE INFO = " + whiteInfo)
    if len(areaR) != 0:
        redInfo = "MIN : " + str(min(areaR)) + " | MAX : " + str(max(areaR)) + " | AVG = " + str(sum(areaR, 0.0) / len(areaR))
        print("RED INFO = " + redInfo)

    # out images - ** 변형 필요 **
    finalImageWhite = cv2.resize(finalImageWhite, (imgHeightWidth * 2, imgHeightWidth * 2))
    finalImageRed = cv2.resize(finalImageRed, (imgHeightWidth * 2, imgHeightWidth * 2))
    cv2.imwrite("outputWhite.jpg", finalImageWhite)
    cv2.imwrite("outputRed.jpg", finalImageRed)


if __name__ == '__main__':

    # image path that want to detect
    input_imagePath = os.getcwd() + "/HairImages/0881a9e0-ff1a-4a35-93e0-2c946d28cd03.jpg"
    currentImg = cv2.imread(input_imagePath)
    currentImg = cv2.resize(currentImg, (imgHeightWidth, imgHeightWidth))

    # server function
    excute(currentImg)




