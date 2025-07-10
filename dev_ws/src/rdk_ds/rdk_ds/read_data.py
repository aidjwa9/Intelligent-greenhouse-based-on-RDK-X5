import time 
from time import sleep
import sys
import os
import logging
import bme680
import Hobot.GPIO as GPIO 
import signal 
sys.path.append("/root/TVOC_Sensor_Demo/Raspberrypi/python")
from lib import TVOC_Sense

import rclpy
from rclpy.node import Node
from my_sensor_msgs.msg import Data

output_pin = 29 #风扇
tvoc = TVOC_Sense.TVOC_Sense('/dev/ttyS1', 115200)
# Configure logging
logging.basicConfig(level=logging.INFO)
GPIO.setwarnings(False)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(output_pin, GPIO.OUT)


class My_SensorPublisher(Node):
    def __init__(self):
        super().__init__('sensor_node')
        self.publisher_ = self.create_publisher(Data,'/my_sensor_msg_data',10)
        self.result = [0,0]
        self.sensor()


    def tvoc_active_print(self):
        tvoc.TVOC_Set_Device_Active_Mode()  
        while True:
            self.result = tvoc.TVOC_Get_Active_Device_Data()  #二氧化碳数据
            if self.result:
                return                
            sleep(0.02)

    def init_as7341(self):
        try:
            libdir = os.path.join("/root/AS7341_Spectral_Color_Sensor_code/RaspberryPi/python", 'lib')
            if os.path.exists(libdir):
                sys.path.append(libdir)
                from waveshare_AS7341 import AS7341
                obj = AS7341.AS7341()
                obj.measureMode = 0
                obj.AS7341_ATIME_config(100)   #光谱数据
                obj.AS7341_ASTEP_config(999)
                obj.AS7341_AGAIN_config(6)
                obj.AS7341_EnableLED(False)
                return obj
        except Exception as e:
            logging.error(f"AS7341 initialization failed: {e}")
            return None

    def init_bme680(self):
        try:
            sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
        except (RuntimeError, IOError):
            sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)
        
        sensor.set_humidity_oversample(bme680.OS_2X)
        sensor.set_pressure_oversample(bme680.OS_4X)
        sensor.set_temperature_oversample(bme680.OS_8X)
        sensor.set_filter(bme680.FILTER_SIZE_3)
        sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)  #温湿度数据
        sensor.set_gas_heater_temperature(320)
        sensor.set_gas_heater_duration(150)
        sensor.select_gas_heater_profile(0)
        return sensor

    def sensor(self):
        as7341 = self.init_as7341()
        bme = self.init_bme680()
        try:
            while True:
                msg = Data()
                if as7341:
                    try:
                        as7341.AS7341_ControlLed(True, 10)
                        as7341.AS7341_startMeasure(0)
                        as7341.AS7341_ReadSpectralDataOne()
                        msg.blue_light = as7341.channel3
                        msg.red_light = as7341.channel8
                        #print('\n--- Spectral Data ---')
                        #print(f'405-425nm: {as7341.channel1}')
                        #print(f'435-455nm: {as7341.channel2}')
                        #print(f'470-490nm: {as7341.channel3}')
                        #print(f'505-525nm: {as7341.channel4}')
                        
                        as7341.AS7341_startMeasure(1)
                        as7341.AS7341_ReadSpectralDataTwo()
                        #print(f'545-565nm: {as7341.channel5}')
                        #print(f'580-600nm: {as7341.channel6}')
                        #print(f'620-640nm: {as7341.channel7}')
                        #print(f'670-690nm: {as7341.channel8}')
                    except Exception as e:
                        logging.error(f"AS7341 read error: {e}")
                
                if bme and bme.get_sensor_data():
                    msg.temperature = bme.data.temperature
                    msg.humidity = bme.data.humidity
                    msg.daqi_ya = bme.data.pressure

                self.tvoc_active_print()
                msg.air_rating,msg.co2 = self.result
                self.publisher_.publish(msg)
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            logging.info("Exiting...")

def main(args=None):
    rclpy.init(args=args)
    my_sensor_node = My_SensorPublisher()
    rclpy.spin(my_sensor_node)
    my_sensor_node.destroy_node() 
    rclpy.shutdown()


if __name__ == '__main__':
    main()