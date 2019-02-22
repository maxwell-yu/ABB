# 调用csv/cv2/numpy/os/time库
import csv
import os
import time
from pic_processing import pic_process

image_road = r'D:\cv\click'
ultrasound_road = r'D:\cv\ultrasonic'
link_road = r'D:\cv\merge.csv'

audio_name_list = []
pics_name_list = []
audio_time_list = []
pics_time_list = []
dic = {}

# csv文件写入，写入标题栏
csv_file = open(link_road,"a",newline='')
csv_write = csv.writer(csv_file,dialect='excel')
stu1 = ['audio_name','pic_name','discharge','tracking']
csv_write.writerow(stu1)
csv_file.close()

# 将pic按照名字转换为距1970年的时间x秒
for root,dirs,files in os.walk(image_road):
    pics_name_list = files
    for file in files:
        time_struct = time.strptime(file[:14],"%Y%m%d%H%M%S")
        pics_time_list.append(time.mktime(time_struct))

# 将超声按照名字转换为距1970年的时间x秒
for root,dirs,files in os.walk(ultrasound_road):
    audio_name_list = files
    for file in files:
        time_struct = time.strptime(file[-19:-4],"%Y%m%d_%H%M%S")
        audio_time_list.append(time.mktime(time_struct))
        
# 利用两类文件的时间秒数来对齐时间轴
for i in range(len(audio_time_list)):
    dic[audio_name_list[i]]=[]
    for j in range(len(pics_time_list)):
        if(pics_time_list[j]<audio_time_list[i]):
            continue
        elif(pics_time_list[j]<audio_time_list[i]+15):
            dic[audio_name_list[i]].append(pics_name_list[j])
        else:
            continue
            
# 对图片进行处理,写入相关信息
for item,key in dic.items():
    for j in range(len(key)):
        path = image_road+'/' + key[j]
        # 调用图片处理函数对图片信息进行采集
        tracking_percentage,discharge_percentage=pic_process('white',False,path)
        # 将pic的信息按顺序写入csv文件中
        stu1 = [item,key[j],str(round(discharge_percentage,2))+'%',str(round(tracking_percentage,2))+'%']
        csv_file = open(link_road,"a",newline = "")
        csv_write = csv.writer(csv_file,dialect='excel')
        csv_write.writerow(stu1)
        csv_file.close()