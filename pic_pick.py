# 调用csv/cv2/numpy/os/time库
import os
import time
from pic_processing import pic_process
import shutil

image_road = r'D:\cv\origin'
picpick_road = r'D:\cv\picpick'
picprocess_road = r'D:\cv\click'

pics_name_list = []
pics_time_list = []
pics_pick_list = []


# 将pic按照名字转换为距1970年的时间x秒
def findjichuantime(path):
        if os.path.exists(picpick_road) == False:
                os.makedirs(picpick_road)
        for root,dirs,files in os.walk(path):
                now_time = 0
                for file in files: 
                        pics_name_list.append(file)
                        pathpic=picprocess_road+'/'+file
                        tracking_percentage,discharge_percentage,dischargeheigh_percentage=pic_process('red',False,pathpic)
                        time_struct = time.strptime(file[:14],"%Y%m%d%H%M%S")
                        pics_time_list.append(time.mktime(time_struct))
                        if dischargeheigh_percentage > 50:
                                jichuan_time = time.mktime(time_struct)
                                if jichuan_time >= now_time:
                                        now_time = jichuan_time
                                        jichuan_name = file
                        else:
                                continue
                jichuan_time=now_time
        return jichuan_time,jichuan_name
"""
函数功能：选取合适的照片
jichuan_time : 击穿的照片的时间
interval ：多少张里面抽取一张，默认3取1的间隔，即6秒一张
minute : 默认值15分钟 即在击穿前后15分钟内2秒取一张
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
        print ('This is main of module "pic_processing.py"')
        jichuantime,jichuanname  = findjichuantime(image_road)
        print(jichuanname)
        pic_pick(jichuantime,3,2,picpick_road)


