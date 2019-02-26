# 调用csv/cv2/numpy/os/time库。。。。
import os
import cv2 as cv
import numpy as np

g_filepath = r"D:\cv\\"


click_points = []
perspective_points = []
x_list = []
y_list = []

"""
函数功能：初始图片过大，因此本函数通过手工选定位置，裁剪出含board部分图片
"""
def cut_picture():
    path_origin = g_filepath + '/' + 'origin' + '/'
    path_dest = g_filepath + '/' + 'cut' + '/'
    for root,dirs,files in os.walk(path_origin):
        count = 0
        for file in files:
            originfile_path = root + '/' + file
            destfile_path = g_filepath + '/' + 'cut' + '/'+ file
            img=cv.imread(originfile_path)
            sp = img.shape  
            print(sp)  #heght/width/channel
            #cv.imshow('origin_img',img)
            a=int(300) # row start
            b=int(800) # row end
            c=int(700) # col start
            d=int(1050) # col end
            copy_img = img[a:b, c:d]   #裁剪图像 height/width //300-800; 700-1050 test on 0128-OK!
            cv.imwrite(destfile_path, copy_img)   #写入图像路径
            cv.imshow('cut_img', copy_img)
            key = cv.waitKey(30) & 0xff  
            count += 1
        print("The total files of cut is: ", count)


"""
函数功能:通过鼠标回调函数来选取角点：点击裁剪的四个点，右键删除设置的角点
"""
def perspective_click(event,x,y,flags,param):
    if event == cv.EVENT_FLAG_LBUTTON:
        perspective_points.append((x,y))
        #cv.circle(img,(x,y),100,(255,255,0),3)
        print(perspective_points)
    if event == cv.EVENT_FLAG_RBUTTON:
        perspective_points.clear()
        print(perspective_points)

"""
函数功能:对先期手工cut得到的图片进行透视变换操作
         透视变换手工选取点时应该由左上点开始，逆时针选取board的四个角点
"""
def perspective_transform():
    cv.namedWindow("pre_perspective")
    cv.setMouseCallback("pre_perspective",perspective_click)

    path_origin = g_filepath + '/' + 'cut' + '/'
    for root, dirs, files in os.walk(path_origin):
        count = 0
        flag = True
        for file in files:
            originfile_path = root + '/' + file
            destfile_path = g_filepath + '/' + 'perspective' + '/'+ file
            img=cv.imread(originfile_path)
            #img = cv.transpose(img)
            #img = cv.flip(img, 0) //realize the retation at 90
            #cv.imshow("pre_perspective", img)
            while (flag):
                image = img.copy()
                print("time to start perspective!")
                while(1):
                    cv.imshow('pre_perspective',image)
                    if cv.waitKey(100) & 0xFF == 13:
                        #ctrl 退出
                        flag = False
                        break
            pts = np.float32(perspective_points[0:4])
            pts1 = np.float32([(0,0),(0,720),(300,720),(300,0)])
            M = cv.getPerspectiveTransform(pts,pts1)
            perspctive_img = cv.warpPerspective(img, M, (300,720))
            cv.imshow("perspctive_image", perspctive_img)
            cv.imwrite(destfile_path, perspctive_img)   #写入图像路径
            cv.waitKey(30)
            #key = cv.waitKey(300) & 0xff  
            count += 1
        print("The total files of perspctive is: ", count)

"""
函数功能：设置角点
左键设置
右键清除
"""
def set_click(event,x,y,flags,param):
    if event==cv.EVENT_FLAG_LBUTTON:
        click_points.append((x,y))
        #cv.circle(img,(x,y),100,(255,255,0),3)
        print(click_points)
    if event==cv.EVENT_FLAG_RBUTTON:
        click_points.clear()
        print(click_points)

"""
函数功能：设置感兴趣区域，该区域主要是集中tracking周围
"""
def click_picture():
    cv.namedWindow("preclick_img")
    cv.setMouseCallback("preclick_img",set_click)
    path_origin = g_filepath + '/' + 'perspective' + '/'
    path_dest = g_filepath + '/' + 'click' + '/'
    #print (path_dest, "------------1")

    for root, dirs, files in os.walk(path_origin):
        flag = True
        count = 0
        print("time to start click!")
        for file in files:
            originfile_path = root + '/' + file
            destfile_path = g_filepath + '/' + 'click' + '/'+ file
            img = cv.imread(originfile_path)
            #cv.imshow("cut_preclick_img", img)
            while (flag):
                image = img.copy()
                while(1):
                    cv.imshow('preclick_img',img)
                    if cv.waitKey(100) & 0xFF == 13:
                        break
                for i in click_points:
                    x_list.append(i[0])
                    y_list.append(i[1])
                    cv.circle(image,i,3,(255,0,0),3)
                    print(x_list)
                cv.imshow("point_click_img", image)
                #key = cv.waitKey(300) & 0xff == 13 
                cv.waitKey(30)       
                
                #本部分注释函数主要是用于做重新click的部分操作
                """ 
                input_ok = input("press ok in the keyboard if you think OK:")
                print("your input is: ", input_ok)
                if input_ok == "ok":
                    flag = False
                    break
                print("reclick the points in the preclick_img")
                x_list.clear()
                y_list.clear()
                click_points.clear()
                print(x_list)
                """
                flag = False

            click_img = img[min(y_list):max(y_list), min(x_list):max(x_list)]
            sp = click_img.shape  
            print(sp)  #heght/width/channel
            #img=cv.resize(img,(360,600))
            cv.imshow("click_img", click_img)
            cv.imwrite(destfile_path, click_img)   #写入图像路径
            #cv.waitKey(0)
            key = cv.waitKey(30) & 0xff  
            count += 1
        print("The total files of click is: ", count)

if __name__ == "__main__":
    print ('This is main of module "set_ROI.py"')
    cut_picture()
    perspective_transform()
    click_picture()