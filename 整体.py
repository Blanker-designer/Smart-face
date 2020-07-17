# -*- coding: utf-8 -*-
# Created by: PyQt5 UI code generator 5.13.0
# WARNING! All changes made in this file will be lost!

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtPrintSupport import *
import sys
import cv2
import requests
import json
import urllib
import base64
import pymysql
import os
import datetime

from PyQt5 import QtCore, QtGui, QtWidgets
import sys


class Ui_FirstForm(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1069, 767)

        # 窗口背景设置
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(QPixmap("B.jpg")))
        Form.setPalette(palette)

        self.timer_camera = QtCore.QTimer()         # 定时器timer_camear为每次从摄像头取画面的间隔
        self.timer_camera2 = QtCore.QTimer()        # 定时器timer_camear2从摄像头取画面进行"人脸识别"的时间

        self.cap = cv2.VideoCapture()               #打开摄像头，若参数是0，表示打开笔记本的内置摄像头，参数是视频文件路径则打开视频
        self.CAM_NUM = 0

        # Qt Designer自动生成控件及布局代码

        self.show_camera = QtWidgets.QLabel(Form)
        self.show_camera.setGeometry(QtCore.QRect(194, 160, 681, 481))
        self.show_camera.setAlignment(QtCore.Qt.AlignCenter)
        self.show_camera.setObjectName("show_camera")
        self.show_camera.setPixmap(QPixmap("image.jpg"))
        self.open_camera = QtWidgets.QPushButton(Form)
        self.open_camera.setGeometry(QtCore.QRect(414, 680, 241, 51))
        font = QtGui.QFont()
        font.setFamily("宋体")
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.open_camera.setFont(font)
        self.open_camera.setObjectName("open_camera")
        self.label = QtWidgets.QLabel(Form)
        self.label.setEnabled(True)
        self.label.setGeometry(QtCore.QRect(399, 50, 271, 31))
        font = QtGui.QFont()
        font.setFamily("楷体")
        font.setPointSize(21)
        font.setBold(False)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setEnabled(True)
        self.label_2.setGeometry(QtCore.QRect(286, 95, 500, 51))
        font = QtGui.QFont()
        font.setFamily("黑体")

        font.setPointSize(15)
        font.setBold(False)
        font.setWeight(50)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

        # 信号与槽进行绑定
        self.open_camera.clicked.connect(self.button_open_camera_clicked)     # 若该按键被点击，则调用button_open_camera_clicked()
        self.timer_camera.timeout.connect(self.label_show_camera)             # 若定时器结束，则调用show_camera()
        self.timer_camera2.timeout.connect(self.recognition)
        # self.button_close.clicked.connect(self.close)                       # 若该按键被点击，则关闭程序

    # 一些固定文字控件的标题的设定
    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "相识"))
        self.open_camera.setText(_translate("Form", "打开相机"))

        self.label.setText(_translate("Form", "新生报道系统"))
        # self.label_2.setText(_translate("Form", "人脸识别度低，请寻找工作人员！"))

    # 获取你的access_token
    def get_Token(self):
        AK = 'P6pS6GX1ke3PcfvG4wmU1s2l'                # 填写的你API Key
        SK = 'T8K1m9wpFvgT8xCOVO05WpnaM5ubnF8w'        # 填写你的Secret Key
        host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={}&client_secret={}'.format(AK, SK)
        response = requests.get(host)
        return response.json()['access_token']

    def start_camera(self):
        flag = self.cap.open(self.CAM_NUM)      # 参数是0，表示打开笔记本的内置摄像头，参数是视频文件路径则打开视频
        if flag == False:                       # 如果打开摄像头不成功
            msg = QMessageBox.warning(self, 'warning', "请检查相机于电脑是否连接正确", buttons=QMessageBox.Ok)
        else:
            self.timer_camera.start(30)         # 定时器开始计时30ms，结果是每过30ms从摄像头中取一帧显示
            self.timer_camera2.start(3000)


    def button_open_camera_clicked(self):
        if self.timer_camera.isActive() == False:  # 若定时器未启动
            self.start_camera()
            # 加载人脸数据(人脸特征)，用于绘制人脸框
            self.face_cascase = cv2.CascadeClassifier('./haarshare/haarcascade_frontalface_default.xml')

            # self.open_camera.setText('关闭相机')
            self.open_camera.hide()              # 隐藏这个button

    # 绘制人脸框
    def paint_rectangle(self, image):
        # 得到每一帧->图像计算
        # 灰度转换：转换成灰度的图计算强度得以降低
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 对比 摄像头采集到的数据 -> 人脸特征训练集
        faces = self.face_cascase.detectMultiScale(gray, 1.3, 3)

        for (x, y, w, h) in faces:
            # 在窗口当中标识人脸 画一个矩形
            image = cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 255), 2)

        return image

    def label_show_camera(self):
        flag, self.image = self.cap.read()  # 从视频流中读取一帧图像给self.image

        show = cv2.resize(self.image, (640, 480))  # 把读到的帧的大小重新设置为 640x480

        imag = self.paint_rectangle(show)

        imag = cv2.cvtColor(imag, cv2.COLOR_BGR2RGB)  # 视频色彩转换回RGB，这样才是现实的颜色

        showImage = QImage(imag.data, imag.shape[1], imag.shape[0], QImage.Format_RGB888)  # 把读取到的视频数据变成QImage形式
        self.show_camera.setPixmap(QPixmap.fromImage(showImage))  # 往显示视频的Label里 显示QImag

    # 利用WxPusher公众号发送信息
    def message_send(self, name):
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        url = 'http://wxpusher.zjiecode.com/api/send/message'
        # //内容类型 1表示文字  2表示html(只发送body标签内部的数据即可，不包括body标签) 3表示markdown
        params = {
            "appToken": "AT_qcyg3v1CTknrvJP5OsKowo7styEiUBRL",
            "content": "{}同学已完成报到".format(name) + '\n' + '时间:' + now_time,
            "contentType": 1,
            "uids": ['UID_wMd6nNHG18dLFNkzNDqk2SrBnCgs'],
            "url": ""
        }
        params = json.dumps(params)

        # print(type(params))

        headers = {
            'Content-Type': "application/json",
        }

        html = requests.post(url, data=params, headers=headers)
        # print(html.text)

    # 借助百度智能云api完成人脸识别(搜索)
    def baidu_search(self, codee):
        url = "https://aip.baidubce.com/rest/2.0/face/v3/search"
        request_url = url + "?access_token=" + self.get_Token()

        params = {
            "image": codee,
            "image_type": "BASE64",
            "group_id_list": "1",
            "quality_control": "LOW",
            "liveness_control": "NORMAL"
        }

        headers = {
            'Content-Type': "application/json",
        }

        response = requests.post(url=request_url, data=params, headers=headers)
        return response.json()

    # 关闭摄像头，清空第一个窗口显示的图像
    def close_area(self):
        self.timer_camera.stop()  # 关闭定时器
        self.timer_camera2.stop()
        self.cap.release()  # 释放视频流
        self.show_camera.clear()  # 清空视频显示区域

    def use_mysql(self, number):
        # 使用MySQL数据库
        conn = pymysql.connect(host='localhost', port=3306, user='root', password='150482', db='test')
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM user WHERE 学号 ={}".format(number))
        p = cursor.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        return p

    def recognition(self):
        flag, self.image = self.cap.read()  # 从视频流中读取
        num = 1

        cv2.imwrite("D:/Face_picture/image" + str(num) + ".jpg", self.image)  # 保存一张图像
        strnum = str(num)
        imagenumber = 'image' + strnum
        with open("D:\Face_picture\\" + imagenumber + ".jpg", 'rb') as f:
            base64_data = base64.b64encode(f.read())
            codee = base64_data.decode()
            num += 1

        content = self.baidu_search(codee)

        if content:
            self.label_2.clear()         # 清理上一次的警告信息
            # print(content)             # content为返回信息
            flag = content["error_code"]

            if flag != 0:
                # print("错误！")
                self.label_2.setText("<font color=red>人脸识别度低，请寻找工作人员！</font>")
            else:
                number = content["result"]['user_list'][0]['user_id']
                numm = content["result"]['user_list'][0]['score']
                if numm >= 80:
                    mainWindows.close()

                    self.close_area()

                    Second.label.setPixmap(QPixmap("D:\Face_local\\" + number + ".jpg"))
                    Second.label.setScaledContents(True)  # 让图片自适应label大小

                    Second.label_14.setPixmap(QPixmap("D:\map_local\\" + number + ".png"))
                    Second.label_14.setScaledContents(True)  # 让图片自适应label大小


                    p = self.use_mysql(number)

                    Second.label_3.setText(p['姓名'])
                    Second.label_5.setText(p['学号'])
                    Second.label_7.setText(p['班级'])
                    Second.label_9.setText(p['学院'])
                    Second.label_11.setText(p['宿舍'])
                    Second.label_13.setText(p['辅导员'])

                    self.message_send(p['姓名'])

                    mainWindows2.show()
        else:
            print("未正确调用百度云api,请检查相关代码!")


class Ui_SecondForm(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1324, 873)


        # 设置窗口背景
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(QPixmap("B2.jpg")))
        Form.setPalette(palette)


        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(240, 120, 171, 201))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(270, 760, 212, 51))
        font = QtGui.QFont()
        font.setFamily("宋体")
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.layoutWidget = QtWidgets.QWidget(Form)
        self.layoutWidget.setGeometry(QtCore.QRect(160, 380, 351, 311))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setVerticalSpacing(12)
        self.gridLayout.setObjectName("gridLayout")
        self.label_9 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(15)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 3, 1, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(15)
        self.label_11.setFont(font)
        self.label_11.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_11.setObjectName("label_11")
        self.gridLayout.addWidget(self.label_11, 4, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(15)
        self.label_8.setFont(font)
        self.label_8.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 3, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(15)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 1, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(15)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(15)
        self.label_6.setFont(font)
        self.label_6.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 2, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(15)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 1, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(15)
        self.label_10.setFont(font)
        self.label_10.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 4, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(15)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 1, 0, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(15)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 2, 1, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(15)
        self.label_12.setFont(font)
        self.label_12.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_12.setObjectName("label_12")
        self.gridLayout.addWidget(self.label_12, 5, 0, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(15)
        self.label_13.setFont(font)
        self.label_13.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_13.setObjectName("label_13")
        self.gridLayout.addWidget(self.label_13, 5, 1, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setGeometry(QtCore.QRect(840, 760, 212, 51))
        font = QtGui.QFont()
        font.setFamily("宋体")
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.label_14 = QtWidgets.QLabel(Form)
        self.label_14.setGeometry(QtCore.QRect(620, 150, 631, 511))
        self.label_14.setAlignment(QtCore.Qt.AlignCenter)
        self.label_14.setObjectName("label_14")
        self.label_15 = QtWidgets.QLabel(Form)
        self.label_15.setGeometry(QtCore.QRect(510, 30, 361, 51))
        font = QtGui.QFont()
        font.setFamily("楷体")
        font.setPointSize(21)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(75)
        self.label_15.setFont(font)
        self.label_15.setAlignment(QtCore.Qt.AlignCenter)
        self.label_15.setObjectName("label_15")

        # 将信号与槽绑定
        self.pushButton.clicked.connect(self.shut)
        self.pushButton_2.clicked.connect(self.Print)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    # 一些固定文字控件的标题的设定
    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        # self.label.setText(_translate("Form", "TextLabel"))
        self.pushButton.setText(_translate("Form", "重新扫描"))
        # self.label_9.setText(_translate("Form", "电气与电子工程学院"))
        # self.label_11.setText(_translate("Form", "7#502"))
        self.label_8.setText(_translate("Form", "学    院："))
        # self.label_5.setText(_translate("Form", "20183372"))
        self.label_2.setText(_translate("Form", "姓    名："))
        self.label_6.setText(_translate("Form", "班    级："))
        # self.label_3.setText(_translate("Form", "解佳坤"))
        self.label_10.setText(_translate("Form", "宿    舍："))
        self.label_4.setText(_translate("Form", "学    号："))
        # self.label_7.setText(_translate("Form", "试1804"))
        self.label_12.setText(_translate("Form", "辅导员："))
        # self.label_13.setText(_translate("Form", "庞玉印"))
        self.pushButton_2.setText(_translate("Form", "打印信息"))
        # self.label_14.setText(_translate("Form", "1"))
        self.label_15.setText(_translate("Form", "您的信息如下"))

    # 关闭窗口，返回原窗口
    def shut(self):
        mainWindows2.close()
        ui.start_camera()
        mainWindows.show()

    # 打印整个窗口
    def Print(self):
        self.printer = QPrinter()
        # 将打印页面设置为横向
        self.printer.setOrientation(QPrinter.Landscape)

        printdialog = QPrintDialog(self.printer, mainWindows2)
        if QDialog.Accepted == printdialog.exec():
            painter = QtGui.QPainter()
            # 将绘制目标重定向到打印机
            painter.begin(self.printer)
            # screen = mainWindows2.grab(QRect(100, 80, 760, 330))
            screen = mainWindows2.grab()
            painter.drawPixmap(40, 60, screen)
            painter.end()


if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QIcon("人脸识别.png"))

    mainWindows = QMainWindow()
    mainWindows2 = QMainWindow()

    ui = Ui_FirstForm()
    Second = Ui_SecondForm()

    #向主窗口添加控件
    ui.setupUi(mainWindows)
    Second.setupUi(mainWindows2)

    mainWindows.show()

    sys.exit(app.exec_())