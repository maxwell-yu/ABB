# 调用csv/cv2/numpy/os/time库
import os
import time
from pic_processing import pic_process
import shutil
import cv2 as cv

image_road = r'D:\cv\origin'
picpick_road = r'D:\cv\picpick'
picprocess_road = r'D:\cv\click'

pics_name_list = []
pics_time_list = []
pics_pick_list = []


# 找到击穿时间
def findjichuantime(path):
        if os.path.exists(picpick_road) == False:
                os.makedirs(picpick_road)
        for root,dirs,files in os.walk(path):
                now_time = 0
                ROIlast = 0
                for file in files: 
                        pics_name_list.append(file)
                        pathpic=picprocess_road+'/'+file
                        time_struct = time.strptime(file[:14],"%Y%m%d%H%M%S")
                        pics_time_list.append(time.mktime(time_struct))
                        if not os.path.exists(pathpic):
                                continue
                        tracking_percentage,discharge_percentage,dischargeheigh_percentage,ROInow=pic_process('red',False,pathpic,ROIlast)
                        ROIlast = ROInow
                        if dischargeheigh_percentage > 50:
                                jichuan_time = time.mktime(time_struct)
                                if jichuan_time >= now_time:
                                        now_time = jichuan_time
                                        jichuan_name = file
                                        jichuan_file_path = pathpic                                       
                        else:
                                continue
                jichuan_time=now_time
        return jichuan_time,jichuan_name,jichuan_file_path
"""
函数功能：选取合适的照片
jichuan_time : 击穿的照片的时间
interval ：多少张里面抽取一张，interval = 3时，即6秒一张
minute :当minute = 15分钟 即在击穿前后15分钟内2秒取一张
path : 新生成的照片的文件路径
"""
def pic_pick(jichuan_time,interval,minute,destpath):
        for i in range(len(pics_time_list)):
                if (pics_time_list[i] < jichuan_time - minute*60):
                        zuo = i
                        continue
                if (pics_time_list[i] > jichuan_time + minute*60):
                        you = i
                        break
                else:
                        you = len(pics_time_list)       
        for i in range(len(pics_time_list)):
                if (i < zuo) and (i % interval == 0):
                        pics_pick_list.append(pics_name_list[i])
                        continue
                if (i > zuo) and (i < you):
                        pics_pick_list.append(pics_name_list[i])
                        continue
                if (i > you) and (i % interval == 0):
                        pics_pick_list.append(pics_name_list[i])
                        continue
        pics_pick_list.sort()
        for file in pics_pick_list:
                srcpath=image_road+'/'+file
                shutil.copy(srcpath,destpath)

        
if __name__ == "__main__":
        print ('This is main of module "pic_pick.py"')
        jichuantime,jichuanname,jichuanpath = findjichuantime(image_road)
        print("找到击穿照片：%s" % jichuanname)
        img=cv.imread(jichuanpath)        
        cv.imshow("jichuan_img",img)
        cv.waitKey(0)
        pic_pick(jichuantime,3,2,picpick_road)
        print("已经重新挑选并保存照片")


