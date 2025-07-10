#!/usr/bin/env python3
import sys
import signal
import Hobot.GPIO as GPIO
import time
from time import sleep
import os
import threading
import rclpy
from rclpy.node import Node
from my_sensor_msgs.msg import Data,Control
import serial
import serial.tools.list_ports


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

uart_dev= '/dev/ttyS7'
baudrate = '115200'

class Control_Node(Node):
    def __init__(self):
        super().__init__('control')
        self.control_subscriber = self.create_subscription(Control,'/all_to_control_node',self.control_callback,10)
        self.data_subscriber = self.create_subscription(Control,'/my_sensor_data',self.data_callback,10)
        self.publisher_ = self.create_publisher(Control,'/control_data_to_mqtt',10)
        #打开rgb串口
        self.ser = serial.Serial(uart_dev, int(baudrate), timeout=1)

        self.feng_shan = 0
        self.shui_beng = 0
        self.feng_mingqi = 0
        self.kai_guan = 0
        self.rgb_guang = 0

        self.thread_else = threading.Thread(target=self.output_control)
        self.thread_else.start()
        
        self.thread_publisher = threading.Thread(target=self.control_publisher_)
        self.thread_publisher.start()
   
    #回调函数组
    def control_callback(self,msg):  #消息控制 0 保持 1 改变
        self.kai_guan = msg.kai_guan  #0 禁止自动 1 自动
        self.rgb_guang = msg.rgb_guang
        if msg.rgb_guang:
            Rgb_arry = self.rgb_arry(msg.rgb_guang)
            self.ser.write(Rgb_arry) # 0 无效 1 无色 2 红色 3 蓝色 4 白色
        
        if self.kai_guan > 0: #自动开关：赋值为1 则开启
            self.kai_guan -= msg.kai_guan
        else:
            self.kai_guan += msg.kai_guan

        if self.feng_shan > 0:
            self.feng_shan -= msg.feng_shan
        else:
            self.feng_shan += msg.feng_shan

        if self.shui_beng > 0:
            self.shui_beng -= msg.shui_beng
        else:
            self.shui_beng += msg.shui_beng

        if self.feng_mingqi > 0:
            self.feng_mingqi -= msg.feng_mingqi
        else:
            self.feng_mingqi += msg.feng_mingqi


    def data_callback(self,msg): #目前只能控制风扇
        if(kai_guan):
            if msg.temperature > 28.0:
                self.feng_shan = 1
            else:
                self.feng_shan = 0


#RGB补光灯

    def rgb_arry(self,rgb_guang):
        led_arr = bytearray(48)
        # 头部赋值
        led_arr[0] = 0xDD
        led_arr[1] = 0x55
        led_arr[2] = 0xEE
        
        # 组地址 (大端序)
        group_address = 0
        led_arr[3] = (group_address >> 8) & 0xFF
        led_arr[4] = group_address & 0xFF
        
        # 设备地址 (大端序)
        device_address = 1
        led_arr[5] = (device_address >> 8) & 0xFF
        led_arr[6] = device_address & 0xFF
        
        # 端口号
        port=0
        led_arr[7] = port & 0xFF
        
        # 功能码和灯带类型
        led_arr[8] = 0x99
        led_arr[9] = 0x01

        led_arr[10] = 0x00
        led_arr[11] = 0x00

        datalength = 10*3

        led_arr[12] = (datalength >> 8) & 0xFF
        led_arr[13] = datalength & 0xFF

        repeat = 1

        led_arr[14] = (repeat >> 8) & 0xFF
        led_arr[15] = repeat & 0xFF

        led_arr[48 - 2] = 0xAA
        led_arr[48 - 1] = 0xBB
        
        if rgb_guang == 1: # 1 关闭 2 红色 3 蓝色 4 白色
            num0 = 0x00
            num1 = 0x00
            num2 = 0x00
        if rgb_guang == 2:
            num0 = 0xFF
            num1 = 0x00
            num2 = 0x00
        if rgb_guang == 3:
            num0 = 0x00
            num1 = 0x00
            num2 = 0xFF
        if rgb_guang == 4:
            num0 = 0xFF
            num1 = 0xFF
            num2 = 0xFF

        for m in range(0,10):
            for n in range(0,3):
                if n == 0:
                    led_arr[16 + (m * 3) + n] = num0
                if n == 1:
                    led_arr[16 + (m * 3) + n] = num1
                if n == 2:
                    led_arr[16 + (m * 3) + n] = num2
        return led_arr


#其余控制系统

    def output_control(self):    #GPIO输出模式
        channel = [16,18,22]  #11 风扇 13 水泵 15 蜂鸣器
        GPIO.setup(channel, GPIO.OUT)
 
        while True:
            GPIO.output(16 , self.feng_shan)
            GPIO.output(18 , self.shui_beng)
            GPIO.output(22 , self.feng_mingqi)


    def control_publisher_(self):
        while True:
            msg = Control()
            msg.feng_shan = self.feng_shan
            msg.feng_mingqi = self.feng_mingqi
            msg.shui_beng = self.shui_beng
            msg.rgb_guang = self.rgb_guang
            msg.kai_guan = self.kai_guan
            self.publisher_.publish(msg)

            sleep(2)

def main(args=None):
    rclpy.init(args=args)
    control_node = Control_Node()
    rclpy.spin(control_node)
    my_sensor_sub.destroy_node() 
    rclpy.shutdown()

if __name__ == '__main__':
    main()
