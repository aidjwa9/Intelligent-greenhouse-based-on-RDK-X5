import rclpy
from rclpy.node import Node
from my_sensor_msgs.msg import Data
from std_msgs.msg import String
from my_sensor_msgs.msg import Data,Control
from audio_msg.msg import SmartAudioData


class Audio_Node(Node):
    def __init__(self):
        super().__init__('my_audio_node')
        self.publisher_ = self.create_publisher(Control,'/all_to_control_node',10)
        self.subscriber = self.create_subscription(SmartAudioData,'/audio_smart',self.audio_callback,10)
        self.tts_publisher_ = self.create_publisher(String,'/tts_text',10)
        self.cmd_word = None 


    def audio_callback(self,msg):
        tts_msg = String()
        self.cmd_word = msg.cmd_word
        control_msg = Control()
        print(self.cmd_word)
        if self.cmd_word == "打开水泵":   
            control_msg.shui_beng = 1
            tts_msg.data = "好的，已打开"
        if self.cmd_word == "关闭水泵":   
            control_msg.shui_beng = 1
            tts_msg.data = "好的，已关闭"
        if self.cmd_word == "开始通风":
            control_msg.feng_shan = 1
            tts_msg.data = "好的，已打开"
        if self.cmd_word == "关闭通风":
            control_msg.feng_shan = 1
            tts_msg.data = "好的，已关闭"
        if self.cmd_word == "蓝色光":
            control_msg.rgb_guang = 3
            tts_msg.data = "好的，已打开"
        if self.cmd_word == "红色光":
            control_msg.rgb_guang = 2
            tts_msg.data = "好的，已打开"
        if self.cmd_word == "白色光":
            control_msg.rgb_guang = 4
            tts_msg.data = "好的，已打开"
        if self.cmd_word == "关闭补光":
            control_msg.rgb_guang = 1
            tts_msg.data = "好的，已关闭"
        if self.cmd_word == "自动模式":
            control_msg.kai_guan = 1
            tts_msg.data = "好的，已为您调成自动模式"
        if self.cmd_word == "手动模式":
            control_msg.kai_guan = 0
            tts_msg.data = "好的，已为您调成手动模式"
        self.tts_publisher_.publish(tts_msg)
        self.publisher_.publish(control_msg)
            
    
def main(args=None):
    rclpy.init(args=args)
    audio_node = Audio_Node()
    rclpy.spin(audio_node)
    audio_node.destroy_node() 
    rclpy.shutdown()

if __name__ == '__main__':
    main()