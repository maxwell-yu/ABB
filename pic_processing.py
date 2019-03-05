import cv2 as cv
import numpy as np
import os
from PIL import Image


image_road = r'D:\cv\click'


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
暗通道去雾算法
测试该效果较好
"""
def zmMinFilterGray(src, r=7):
   #最小值滤波
   return cv.erode(src, np.ones((2*r+1, 2*r+1)))

def guidedfilter(I, p, r, eps):
   #引导滤波、
   height, width = I.shape
   m_I = cv.boxFilter(I, -1, (r,r))
   m_p = cv.boxFilter(p, -1, (r,r))
   m_Ip = cv.boxFilter(I*p, -1, (r,r))
   cov_Ip = m_Ip-m_I*m_p
   m_II = cv.boxFilter(I*I, -1, (r,r))
   var_I = m_II-m_I*m_I
   a = cov_Ip/(var_I+eps)
   b = m_p-a*m_I
   m_a = cv.boxFilter(a, -1, (r,r))
   m_b = cv.boxFilter(b, -1, (r,r))
   return m_a*I+m_b

def stretchImage2(data, vv = 10.0):        #非线性拉伸
   m = data-data.mean()
   S = np.sign(m)
   A = np.abs(m)
   A = 1.0 - vv**(-A)
   m = S*A
   vmin, vmax = m.min(), m.max()
   return (m-vmin)/(vmax-vmin)

def getV1(m, r, eps, w, maxV1):  #输入rgb图像，值范围[0,1]
   '''计算大气遮罩图像V1和光照值A, V1 = 1-t/A'''
   V1 = np.min(m,2)
   V1 = guidedfilter(V1, zmMinFilterGray(V1,7), r, eps)     #使用引导滤波优化
   bins = 2000
   ht = np.histogram(V1, bins)                              #计算大气光照A
   d = np.cumsum(ht[0])/float(V1.size)
   for lmax in range(bins-1, 0, -1):
      if d[lmax]<=0.999:
         break
   A  = np.mean(m,2)[V1>=ht[1][lmax]].max()       
   V1 = np.minimum(V1*w, maxV1)                   #对值范围进行限制
   return V1,A

def getV2(m, r, eps, ratio):
   Y = np.zeros(m.shape)
   for k in range(3):                         #对每个通道单独求亮边界
      v2 = 1 - cv2.blur(zmMinFilterGray(1-m[:,:,k],7), (7,7))
      v2 = guidedfilter(m[:,:,k], v2, r, eps)
      v2 = np.maximum(v2, m[:,:,k])
      Y[:,:,k] = np.maximum(1-(1-v2)*ratio, 0.0)
   return Y

def ProcessHdr(m, r, eps, ratio, para1):                                 #单尺度处理
   V1 = getV1(m, r, eps, ratio)                #计算暗边界
   V2 = getV2(m, r, eps, ratio)                #计算亮边界
   Y = np.zeros(m.shape)
   for k in range(3):
      Y[:,:,k] = ((m[:,:,k]-V1)/(V2[:,:,k]-V1))
   Y = stretchImage2(Y,para1)                  #非线性拉伸
   return Y

def ProcessHdrMs(m, r=[161], eps=[0.005,0.001, 0.01], ratio=[0.98, 0.98, 0.92], para1=10.0):    #多尺度处理
   Y = []
   for k in range(len(r)):
      Y.append(ProcessHdr(m, r[k], eps[k], ratio[k], para1))
 
   return sum(Y)/len(r)


#去雾函数
def deHaze(m, r=81, eps=0.001, w=0.95, maxV1=0.80, bGamma=False):
   Y = np.zeros(m.shape)
   V1,A = getV1(m, r, eps, w, maxV1)               #得到遮罩图像和大气光照
   for k in range(3):
      Y[:,:,k] = (m[:,:,k]-V1)/(1-V1/A)           #颜色校正
   Y =  np.clip(Y, 0, 1)
   if bGamma:
      Y = Y**(np.log(0.5)/np.log(Y.mean()))       #gamma校正,默认不进行该操作
   return Y

"""
函数功能：处理板子的程序
color ：white / red
flag : True/False 去烟
path : path of pic
ROIlast:前一个tracking的ROI
"""
def pic_process(color,flag,path,ROIlast):
   img=cv.imread(path)
   img = cv.transpose(img)
   img = cv.flip(img, 0)
   #cv.imshow('img',img)
   if flag == True:
      dehaze_array = deHaze(img/255.0)*255
      print(dehaze_array)
      dehaze_img_pil = Image.fromarray(dehaze_array.astype('uint8')).convert('RGB')
      #dehaze_img_pil.show()
      img = cv.cvtColor(np.asarray(dehaze_img_pil),cv.COLOR_RGB2BGR)  
      cv.imshow("dehaze_img",img)
   if color == 'white':
      discharge_area = 0
      tracking_area = 0
      ROI = img
      ROI_HSV=cv.cvtColor(ROI,cv.COLOR_BGR2HSV)
      ROI_GRAY=cv.cvtColor(ROI,cv.COLOR_BGR2GRAY)
      ROI_GRAY=gamma_trans(ROI_GRAY,0.5)
      ROI_S=cv.split(ROI_HSV)[1]
      ROI_S=gamma_trans(ROI_S,0.5)
      ret,ROI1=cv.threshold(ROI_GRAY,190,255,cv.THRESH_BINARY)
      #cv.imshow('ROI1',ROI1)
      ret2,ROI2=cv.threshold(ROI_S,110,255,cv.THRESH_BINARY_INV)
      #cv.imshow("roi_S",ROI2)
      ROI3=cv.bitwise_and(ROI1,ROI2)
      trackheigh = [0]
      dischargeheigh = [0]
      contours, hierarchy = cv.findContours(ROI3,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
      for i in range(len(contours)):
         discharge_area = discharge_area + cv.contourArea(contours[i])
         cv.drawContours(ROI,contours,i,(0,255,0),1)
         pentagram = contours[i]
         lowmost = tuple(pentagram[:,0][pentagram[:,:,1].argmin()])  #高低方向上
         highmost = tuple(pentagram[:,0][pentagram[:,:,1].argmax()])
         dischargeheigh.append(highmost[1]-lowmost[1])
      dischargeheigh_percent = 100*max(dischargeheigh)/ROI.shape[0]
      discharge_percentage=discharge_area*100/(ROI.shape[0]*ROI.shape[1])
      if discharge_percentage>0.1:
         ret1,ROI4 = cv.threshold(ROI_GRAY,155,255,cv.THRESH_BINARY_INV)
      else:
         ret1,ROI4 = cv.threshold(ROI_GRAY,150,255,cv.THRESH_BINARY_INV)
      ROI3=cv.bitwise_xor(ROI4,ROI1)
      contours, hierarchy = cv.findContours(ROI3,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
      for i in range(len(contours)):
         tracking_area=cv.contourArea(contours[i])+tracking_area
         cv.drawContours(ROI, contours,i , (255,0,128),1,)
         pentagram = contours[i]
         lowmost = tuple(pentagram[:,0][pentagram[:,:,1].argmin()])  #高低方向上
         highmost = tuple(pentagram[:,0][pentagram[:,:,1].argmax()])
         trackheigh.append(highmost[1]-lowmost[1])
      trackheigh_percent = 100*max(trackheigh)/ROI.shape[0]
      tracking_percentage=tracking_area*100/(ROI.shape[0]*ROI.shape[1])
      #print("trackarea %.2f%%" % tracking_percentage)
      #print("trackheigh percent %.2f%%" % trackheigh_percent)
      #print("Dischargearea %.2f%%" % discharge_percentage)
      #print("distrageheigh percent %.2f%%" % dischargeheigh_percent)
      #cv.imshow("Region",ROI)
      #cv.waitKey(0)
      #cv.destroyAllWindows()
   if color == 'red':
      discharge_area = 0
      tracking_area = 0
      ROI = img
      ROI_HSV=cv.cvtColor(ROI,cv.COLOR_BGR2HSV)
      ROI_GRAY=cv.cvtColor(ROI,cv.COLOR_BGR2GRAY)
      ROI_GRAY=gamma_trans(ROI_GRAY,0.5)
      ROI_V=cv.split(ROI_HSV)[2]
      ROI_V=gamma_trans(ROI_V,0.5)
      ROI_V = cv.equalizeHist(ROI_V)
      ret1,ROI1=cv.threshold(ROI_V,30,255,cv.THRESH_BINARY_INV)
      #cv.imshow("roi_v",ROI1)
      ROI1 = cv.bitwise_or(ROI1,ROIlast)
      contours, hierarchy = cv.findContours(ROI1,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
      trackheigh = [0]
      dischargeheigh = [0]
      for i in range(len(contours)):
         tracking_area = tracking_area + cv.contourArea(contours[i])
         cv.drawContours(ROI,contours,i,(0,255,0),1)
         pentagram = contours[i]
         lowmost = tuple(pentagram[:,0][pentagram[:,:,1].argmin()])  
         highmost = tuple(pentagram[:,0][pentagram[:,:,1].argmax()])
         trackheigh.append(highmost[1]-lowmost[1])
      trackheigh_percent = 100*max(trackheigh)/ROI.shape[0]
      tracking_percentage=tracking_area*100/(ROI.shape[0]*ROI.shape[1])
      ret2,ROI2=cv.threshold(ROI_GRAY,180,255,cv.THRESH_BINARY)
      #cv.imshow("roi_gray",ROI2)
      contours, hierarchy = cv.findContours(ROI2,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
      for i in range(len(contours)):
         discharge_area = discharge_area + cv.contourArea(contours[i])
         cv.drawContours(ROI,contours,i,(255,0,128),1)
         pentagram = contours[i]
         lowmost = tuple(pentagram[:,0][pentagram[:,:,1].argmin()])  
         highmost = tuple(pentagram[:,0][pentagram[:,:,1].argmax()])
         #cv.circle(ROI, lowmost, 2, (0,255,255),3)   
         #cv.circle(ROI, highmost, 2, (0,0,255),3)
         dischargeheigh.append(highmost[1]-lowmost[1])
      dischargeheigh_percent = 100*max(dischargeheigh)/ROI.shape[0]
      discharge_percentage=discharge_area*100/(ROI.shape[0]*ROI.shape[1])
      print("trackarea %.2f%%" % tracking_percentage)
      print("trackheigh percent %.2f%%" % trackheigh_percent)
      print("Dischargearea %.2f%%" % discharge_percentage)
      print("distrageheigh percent %.2f%%" % dischargeheigh_percent)
      cv.imshow("Region",ROI)
      cv.waitKey(200)
      cv.destroyAllWindows()
   return tracking_percentage,trackheigh_percent,discharge_percentage,dischargeheigh_percent,ROI1

if __name__ == "__main__":
   print ('This is main of module "pic_processing.py"')
   ROIlast = 0
   for root,dirs,files in os.walk(image_road):
      for file in files:
         path=root+'/'+file
         a,b,c,d,ROInow =pic_process('red',False,path,ROIlast)
         ROIlast = ROInow
         #print("%f %f %f" % (a,b,c))

