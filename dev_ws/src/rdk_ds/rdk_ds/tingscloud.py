import paho.mqtt.client as mqtt
import time
import json
import socket  # 用于错误处理
import threading

import rclpy
from rclpy.node import Node
from my_sensor_msgs.msg import Data,Control



# MQTT连接参数 - 替换为您自己的值
BROKER_ADDRESS = "gz-3-mqtt.iot-api.com"  # 确保这个地址正确
BROKER_PORT = 1883
USERNAME = "7xelaugivttjdjb6"  # 替换为您的AccessToken
PASSWORD = "QPX5tjTOpz"     # 替换为您的ProjectKey
CLIENT_ID = "712fb82446b543bf8669bdacbc63bba74"  # 可以保持原样或修改

# 根据平台要求设置主题
ATTRIBUTES_TOPIC = "attributes"
EVENT_TOPIC = "uczw5s66"  # 替换为您的设备ID
DATA_TOPIC = "data/sensor_data"         # 自定义数据标识

class Mqtt_SubNodes(Node):
    def __init__(self):
        super().__init__('mqtt')
        self.temperature = 0
        self.humidity = 0
        self.daqi_ya = 0
        self.blue_light = 0
        self.red_light = 0
        self.air_rating = 0
        self.co2 = 0
        #控制状态回传
        self.feng_shan_c = False
        self.shui_beng_c = False
        self.rgb_guang_c = 1
        self.feng_mingqi_c = False
        self.kai_guan_c = False

        self.mqtt_subscriber = self.create_subscription(Data,'/my_sensor_msg_data',self.mqtt_callback,10)
        self.control_subscriber = self.create_subscription(Control,'/control_data_to_mqtt',self.control_callback,10)
        self.mqtt_publisher = self.create_publisher(Control,'/my_sensor_msg_control',10)
        self.control_publisher_ = self.create_publisher(Control,'/all_to_control_node',10)
        self.thread = threading.Thread(target=self.mqtt_run)
        self.thread.start()


    def control_callback(self,msg):
        if msg.feng_shan > 0:
            self.feng_shan_c = True
        else:
            self.feng_shan_c = False
        if msg.shui_beng > 0:
            self.shui_beng_c = True
        else:
            self.shui_beng_c = False
        if msg.rgb_guang > 0:
            self.rgb_guang_c = msg.rgb_guang

        if msg.feng_mingqi > 0:
            self.feng_mingqi_c = True
        else:
            self.feng_mingqi_c = False
        if msg.kai_guan > 0:
            self.kai_guan_c = True
        else:
            self.kai_guan_c = False

    def mqtt_callback(self,msg):
        self.temperature = round(msg.temperature,1)
        self.humidity = round(msg.humidity,1)
        self.daqi_ya = round(msg.daqi_ya,1)
        self.blue_light = msg.blue_light
        self.red_light = msg.red_light
        self.air_rating = msg.air_rating
        self.co2 = msg.co2 


        print(self.temperature)

    def on_message(self,client, userdata, msg):
        print(f"收到消息: Topic={msg.topic}, Payload={msg.payload.decode()}")
        data = json.loads(msg.payload.decode())
        control_msg = Control()
        if "feng_shan" in data:
           control_msg.feng_shan = 1
        if "rgb_guang" in data:
            control_msg.rgb_guang = int(data["rgb_guang"])
        #control_msg.rgb_guang = data["rgb_guang"]
        if "shui_beng" in data:
            control_msg.shui_beng = 1
        if "switch_x" in data:
            control_msg.kai_guan = int(data["switch_x"])
        self.control_publisher_.publish(control_msg)
        print("解析后的数据:", data)
        # 在这里处理业务逻辑（例如更新设备属性）
       

    def on_connect(self,client, userdata, flags, reason_code, properties):
        client.subscribe("attributes/push", qos=0)  # 订阅主题
        if reason_code == 0:
            print("成功连接到MQTT服务器!")
        else:
            print(f"连接失败，错误代码: {reason_code} - {mqtt.connack_string(reason_code)}")



    def on_disconnect(self,client, userdata, flags, reason_code, properties):
        print(f"断开连接，原因: {reason_code} - {mqtt.error_string(reason_code)}")
    def mqtt_run(self):
        try:
            # 创建MQTT客户端 - 使用V2回调API
            client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
            client.username_pw_set(USERNAME, PASSWORD)
            client.on_connect = self.on_connect
            client.on_message = self.on_message
            client.on_disconnect = self.on_disconnect

            # 连接服务器
            print(f"尝试连接到 {BROKER_ADDRESS}:{BROKER_PORT}...")
            client.connect(BROKER_ADDRESS, BROKER_PORT, keepalive=60)
            
            # 启动网络循环
            client.loop_start()
            
            # 主循环
            while True:
                # 1. 上报属性值
                attributes = {
                    "temperature": self.temperature,
                    "humidity": self.humidity,
                    "pressure": self.daqi_ya,
                    "Blue_Light": self.blue_light,
                    "Red_Light": self.red_light,
                    "tvoc": self.air_rating,
                    "co2": self.co2,
                    "feng_shan_c": self.feng_shan_c,
                    "shui_beng_c": self.shui_beng_c,
                    "rgb_c": self.rgb_guang_c,
                    "switch_c": self.kai_guan_c,
                }
                client.publish(ATTRIBUTES_TOPIC, payload=json.dumps(attributes), qos=0)
                
                print(f"已上报属性: {attributes}")
                time.sleep(20)  # 每10秒上报一次
                
        except socket.gaierror:
            print(f"错误: 无法解析主机名 '{BROKER_ADDRESS}'，请检查服务器地址是否正确")
        except KeyboardInterrupt:
            print("\n正在断开连接...")
            client.loop_stop()
            client.disconnect()
            print("已断开连接")
        except Exception as e:
            print(f"发生错误: {str(e)}")
            client.loop_stop()
            client.disconnect()

def main(args=None):
    rclpy.init(args=args)
    my_sensor_sub = Mqtt_SubNodes()
    rclpy.spin(my_sensor_sub)
    my_sensor_sub.destroy_node() 
    rclpy.shutdown()

if __name__ == '__main__':
    main()
