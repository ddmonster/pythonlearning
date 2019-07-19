# -*- coding: UTF-8 -*-
from struct import *
from copy import *
import os



class bmp:
    def __init__(self,byteArray_bmp):

        self.byteArray_bmp=bytearray(byteArray_bmp)



        '''
            位图文件头(bitmap-file header)共14字节   小端
             名称             占用空间              内容                                           数据

             bfType            2字节                标识，就是“BM”二字                              BM
             bfSize            4字节                整个BMP文件的大小                               ?
             bfReserved1/2     4字节                保留字                                          0
             bfOffBits         4字节                偏移数，即 位图文件头+位图信息头+调色板 的大小     0x36(54)

        '''
        file_header=unpack("<HIII",byteArray_bmp[0:14])
        self.bitmap_file_header=list(file_header)


        '''
             ----------------------------------------------------------BITMAPINFOHEADER--------------------------------------------------------------
             c++

            Copy
                typedef struct tagBITMAPINFOHEADER {
                    DWORD biSize;
                    LONG  biWidth;
                    LONG  biHeight;
                    WORD  biPlanes;
                    WORD  biBitCount;
                    DWORD biCompression;
                    DWORD biSizeImage;
                    LONG  biXPelsPerMeter;
                    LONG  biYPelsPerMeter;
                    DWORD biClrUsed;
                    DWORD biClrImportant;
                } BITMAPINFOHEADER, *PBITMAPINFOHEADER;


            位图信息头(bitmap-information header) 共40字节 小端
             名称             占用空间              内容                                           数据
             biSize            4字节                位图信息头的大小，为40                          0x28(40)
             biWidth           4字节                位图的宽度，单位是像素                           ?
             biHeight          4字节                位图的高度，单位是像素                           ?
             biPlanes          2字节                固定值1                                         1
             
             biBitCount        2字节                每个像素的位数                                                                  
                                                    1-黑白图，4-16色，8-256色，24-真彩色             0x18(24)          
             
             biCompression     4字节                压缩方式，BI_RGB(0)为不压缩                      0
             
             biSizeImage       4字节                位图全部像素占用的字节数，BI_RGB时可设为0          ?
             biXPelsPerMeter   4字节                水平分辨率(像素/米)                               0
             biYPelsPerMeter   4字节                垂直分辨率(像素/米)                               0
             
             biClrUsed         4字节                位图使用的颜色数                                 
                                                    如果为0，则颜色数为2的biBitCount次方               0
                                                    
             biClrImportant    4字节                重要的颜色数，0代表所有颜色都重要                   0

        '''

        information_header=unpack("<LllHHLLllLL",byteArray_bmp[14:54])
        self.bitmap_information_header=list(information_header)



        '''
            颜色点阵数据(bits data)
            24位真彩色位图没有颜色表，所以只有1、2、4这三部分。
        '''
        tmp=file_header[3]
        self.bits_data=byteArray_bmp[tmp:]
        


        '''
            图片的大小 单位像素
        '''
        self.size=self.bitmap_information_header[1:3]

    def open(filepa):
        '''
            this functoin is used to open a .nmp file
            and return bmp object2
        '''
        with open(filepa,'rb') as bmpByte:
            byte = bmpByte.read()
            byte=bytearray(byte)
        return bmp(byte)


    def crop(self,*position):
        '''
            posiztion=(left,upper,right,lower)
            crop the image then return bmp object
            if the args overflow the size of image return 0
                            upper
                       height-------0
                       |            |
                       |            |
                left   |            |   right
                       |            |
                       0 --------- width
                           lower
        '''
        position=position[0]
        left=position[0]
        upper=position[1]
        right=position[2]
        lower_l=position[3]

        width=self.size[0]
        height=self.size[1]
        errors="the parameter have exceeded the size of this picture "+str(self.size[0])+'x'+str(self.size[1])
        data=b''
        if left >height or right>height:
            print(errors)
            return 0
        if upper >width or lower_l>width:
            print(errors)
            return 0

        lower=(height-right) if left>(height-right) else left
        higher=(height-right) if left<(height-right) else left
        shorter= lower_l if lower_l<(width-upper) else (width-upper)
        longer =  lower_l if lower_l>(width-upper) else (width-upper)
        data=self.bits_data[lower*3*width:higher*3*width]
        new_data=b''
        for h in range(higher-lower):
            start=shorter*3+h*width*3
            end=longer*3+h*width*3
            new_data+=data[start:end]
        after_height=higher-lower
        after_width=longer-shorter
        size=(after_width,after_height)
        after_size=len(new_data)

        self.bitmap_file_header[1]=after_size+54#bfSize
        self.bitmap_information_header[1]=after_width #biWidth
        self.bitmap_information_header[2]=after_height #biHeight
        self.bitmap_information_header[6]=after_size  #biSizeImage
        self.size=size
        self.bits_data=new_data  
        return self
    def save(self,pathName):
        data=b''
        with open(pathName,'wb') as bmpByte:
            data=pack("<HIII",*self.bitmap_file_header)+pack("<LllHHLLllLL",*self.bitmap_information_header)+self.bits_data
            bmpByte.write(data)
            return 0
  
        

#9x9 crop
import sys
filepath=os.path.abspath('.')
print(filepath)
filepath+='\\20140514114029140.bmp'

for row in range(3):
    for col in range(3):
        bmpk=bmp.open(filepath)
        width=bmpk.size[0]
        height=bmpk.size[1]
        peer_col=width//3
        peer_row=height//3
        left=peer_row*row
        upper=(2-col)*peer_col
        right=peer_row*(2-row)
        lower=col*peer_col
        nbmp=bmpk.crop((left,upper,right,lower))
        nbmp.save(os.path.abspath('.')+'\\'+str(row)+"_"+str(col)+".bmp")
 



            

