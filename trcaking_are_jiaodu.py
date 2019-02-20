# pylint: disable=no-member
import csv
import cv2 as cv
import numpy as np
import os
corner_points = [(145, 250), (126, 425), (336, 413), (367, 255)]
n = 0
tracking_area_90 = 0
"""
函数功能：设置角点
左键设置
右键清除
"""
def set_corner(event,x,y,flags,param):

    if event==cv.EVENT_FLAG_LBUTTON:
        corner_points.append((x,y))
    if event==cv.EVENT_FLAG_RBUTTON:
        corner_points.clear()

"""
函数功能：gamma变换
"""
def gamma_trans(img,gamma):

	#具体做法先归一化到1，然后gamma作为指数值求出新的像素值再还原
	gamma_table = [np.power(x/255.0,gamma)*255.0 for x in range(256)]
	gamma_table = np.round(np.array(gamma_table)).astype(np.uint8)
	#实现映射用的是Opencv的查表函数
	return cv.LUT(img,gamma_table)

"""
函数功能：设置ROI区域  与设置角点函数配合使用
左键设置角点 以逆时针顺序 点击四个角点  可以设置多个roi区域
右键删除设置的角点
"""
def set_ROI(img,origin):

    ROI=[]
    while(True):
        if(len(corner_points)%4==0):
            ROI.clear()
            for i in range(len(corner_points)//4):
                pts=np.float32(corner_points[i*4:i*4+4])
                pts1 = np.float32([ (0,0),(0,200),(200,200),(200,0)])
                M=cv.getPerspectiveTransform(pts,pts1)
                dst = cv.warpPerspective(img,M,(200,200))
                ROI.append(dst)
                # cv.imshow("ROI"+str(i),dst)
            for i in corner_points:
                cv.circle(img,i,2,(255,255,0),1,1)
            cv.imshow('img',img)
        if(len(corner_points)==0):
            img=origin.copy()
            cv.imshow('img',img)
        if(cv.waitKey(10)==13):
            return ROI

cv.namedWindow("img")
cv.setMouseCallback("img",set_corner)

path = r"D:\Python\samples\2\90.jpg"
img=cv.imread(path)
cv.imshow('img',img)
origin=img.copy()
ROIs=set_ROI(img,origin)
for ROI in ROIs:
    ROI_HSV=cv.cvtColor(ROI,cv.COLOR_BGR2HSV)
    ROI_S=cv.split(ROI_HSV)[1]
    ROI_S=gamma_trans(ROI_S,0.5)
    cv.imshow("S",ROI_S)
    ret1,ROI1=cv.threshold(ROI_S,100,255,cv.THRESH_BINARY_INV)
    cv.imshow("roi_S",ROI1)
    image, contours, hierarchy = cv.findContours(ROI1,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
    for i in range(len(contours)):
      tracking_area_90 = tracking_area_90 + cv.contourArea(contours[i])
      cv.drawContours(ROI,contours,i,(0,255,0),1)
    cv.imshow("Region",ROI)


for root,dirs,files in os.walk(r"D:\Python\samples\2\\"):
    for file in files:
        path=root+'/'+file
        img=cv.imread(path)
        cv.imshow('img',img)
        ROI_HSV=cv.cvtColor(ROI,cv.COLOR_BGR2HSV)
        origin=img.copy()
        ROIs=set_ROI(img,origin)
        discharge_area=0
        for ROI in ROIs:
            discharge_area=0
            ROI_S=cv.split(ROI_HSV)[1]
            ROI_S=gamma_trans(ROI_S,0.5)
            cv.imshow("S",ROI_S)
            ret2,ROI2=cv.threshold(ROI_S,100,255,cv.THRESH_BINARY_INV)
            cv.imshow("roi_S",ROI2)
            image, contours, hierarchy = cv.findContours(ROI2,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
            for i in range(len(contours)):
                discharge_area = discharge_area + cv.contourArea(contours[i])
                cv.drawContours(ROI,contours,i,(0,255,0),1)
            discharge_percentage=100.0-discharge_area*100.0/tracking_area_90
            print(file)
            print(discharge_percentage)
            cv.imshow("Region",ROI)

    
        cv.waitKey()



