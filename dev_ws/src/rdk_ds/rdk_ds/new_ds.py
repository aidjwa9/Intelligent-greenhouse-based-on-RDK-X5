from openai import OpenAI

import rclpy
from rclpy.node import Node
from my_sensor_msgs.msg import Data,Control
from std_msgs.msg import String

api_key = "sk-ZXN6AuHAcmiAXX3a2f26E9B40dB94f5a89D6D1F741820526"  # 请替换为您的 API Key  
api_base = "http://maas-api.cn-huabei-1.xf-yun.com/v1"  

client = OpenAI(api_key=api_key,base_url=api_base)  


class Deepseek_Node(Node):
    def __init__(self):
        super().__init__('deepseek_node')
        self.publisher_ = self.create_publisher(String,'/tts_text',10)
        self.subscriber = self.create_subscription(String,'/audio_asr',self.ds_callback,10)
        self. subscriber = self.create_subscription(Data,'/my_sensor_msg_data',self.sensor_callback,10)
        self.question = None
        self.temperature = 0
        self.humidity = 0
        self.daqi_ya = 0
        self.blue_light = 0
        self.red_light = 0
        self.air_rating = 0
        self.co2 = 0
        self.fanqiebing = "青枯病"

    def sensor_callback(self,msg):
        self.temperature = round(msg.temperature,1)
        self.humidity = round(msg.humidity,1)
        self.daqi_ya = round(msg.daqi_ya,1)
        self.blue_light = msg.blue_light
        self.red_light = msg.red_light
        self.air_rating = msg.air_rating
        self.co2 = msg.co2 

    def ds_callback(self,msg):
        recive_msg = String()
        self.question = msg.data
        recive_msg.data = "好的"

        self.publisher_.publish(recive_msg)
        self.deepseek(self.question)

    def prompt(self,question):
        prompt = f'''
# 角色与能力定义 (Role & Capabilities - System Prompt)
你是一个专业的智慧大棚农艺助手，名字叫地瓜。你的核心任务是帮助管理者理解大棚状况、诊断潜在问题并提供基于数据和农业知识的专业建议。你拥有以下能力：
1.  **实时数据感知：** 可以获取当前大棚内各种传感器的实时读数（下方[当前棚内状态]会提供）。
2.  **专业知识库：** 可以访问一个包含作物栽培技术、病虫害防治、环境调控策略等内容的农业知识库（下方[相关知识片段]会提供检索到的相关内容）。
3.  **数据分析与解释：** 能够分析传感器数据，解释其含义，并结合作物生长阶段和知识库判断是否正常或存在风险。
4.  **建议提供：** 能够基于分析和知识库，给出具体、可操作的环境调整或管理建议。
5.  **历史参考 (可选)：** 在需要时，可以对比历史数据（下方[相关历史数据]会提供）。
**重要约束：**
*   你的回答必须基于提供的【当前棚内状态】和【相关知识片段】。
*   如果数据不足以得出结论，请明确说明需要哪些额外信息。
*   对于涉及设备操作（如开灯、关窗、浇水）的建议，**务必明确指出这是建议**，并提醒用户手动操作或通过控制系统执行。**你本身不直接控制任何设备。**
*   保持回答专业、简洁、清晰，优先使用分点说明。避免过度推测。

# 当前上下文 (Context - Dynamically Inserted by Your System)
## [当前棚内状态] (实时数据 - 格式清晰)
*   **时间戳：** 2025-07-06 14:30:00
*   **温度：** {self.temperature} °C (传感器位置：棚中部)
*   **大气压：** {self.daqi_ya}
*   **湿度：** {self.humidity}% (传感器位置：棚中部)
*   **红色光谱：** {self.red_light} Lux (传感器位置：作物冠层)
*   **蓝色光谱：** {self.blue_light} Lux (传感器位置：作物冠层)
*   **土壤湿度：** 35% (传感器位置：A区番茄根部)
*   **CO2浓度：** {self.co2} ppm
*   **当前主要作物：** 番茄 (品种：丰收一号， 生长阶段：盛花期)
*   **设备状态：** 顶窗开50%， 遮阳网未开启， 环流风扇开启， 灌溉系统关闭
*(根据实际传感器增减项目)*

## [相关知识片段] (Retrieved by RAG from your KB - 关键！)
*   **片段1 (来源：番茄栽培手册-环境篇):** 番茄盛花期最适日间温度为 22-28°C。温度持续高于 30°C 会导致花粉活力下降，影响授粉坐果。湿度宜保持在 60-70%，湿度过低 (<50%) 易导致柱头干燥，同样不利授粉。
*   **片段2 (来源：本地农技站建议-夏季管理):** 当光照强度持续 > 70000 Lux 且温度 > 28°C 时，建议打开通风装置，避免棚内温度过高。
*   **片段3 (来源：土壤水分管理指南):** 番茄盛花期土壤湿度(体积含水量)宜保持在 40%-50%。低于 35% 应考虑灌溉，但需避免花期大水漫灌，建议采用滴灌或小水勤浇。
*(系统根据用户问题自动检索最相关的3-5个知识片段插入此处)*

## [相关历史数据] (Optional - If Relevant)
*   过去3小时温度持续上升 (从 28°C -> 32.5°C)。
*   过去24小时未灌溉。
*(系统根据问题判断是否需要插入特定历史数据)*

# 用户问题 (User Query)
{question}

# 任务指令 (Task Instruction)
请基于以上【当前棚内状态】、【相关知识片段】和【相关历史数据】(如有)，以专业农艺助手的身份回答用户问题：
1.  **分析解释：** 清晰解读当前数据状态及其对作物（番茄盛花期）的潜在影响。
2.  **诊断建议 (如适用)：** 指出是否存在问题或风险。如果存在问题，给出具体、可操作的建议（包括建议采取的措施、原因依据、注意事项）。
3.  **回答格式：** 先直接简要回答用户问题，以自述的口吻进行。语言专业且易懂，且你输出的应该为文本格式，不要出现除标点符号以外的其他标点且使用自述格式，我需要将你的输出转换为语音,目前仅支持中文和英文文本内容，切记勿发布其他语言文本消息。
'''
        return prompt

    def deepseek(self,question):
        Prompt = self.prompt(question)
        response = client.chat.completions.create(
            model="xdeepseekv3",
            messages=[{
            "role": "user", 
            "content": Prompt
        }],
            stream=True,
            temperature=0.5,
            max_tokens=500,
            extra_headers={"lora_id": "0"},  # 调用微调大模型时,对应替换为模型服务卡片上的resourceId
            stream_options={"include_usage": True},
            extra_body={"search_disable": False, "show_ref_label": False} 
        )

        full_response = ""
        for chunk in response:
            if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                msg = String()
                msg.data = content
                self.publisher_.publish(msg)
                #print(content, end="", flush=True)  # 实时打印每个片段
                full_response += content
        

def main(args=None):
    rclpy.init(args=args)
    deepseek_node = Deepseek_Node()
    rclpy.spin(deepseek_node)
    deepseek_node.destroy_node() 
    rclpy.shutdown()


if __name__ == '__main__':
    main()
