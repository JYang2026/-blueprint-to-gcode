"""
豆包AI视觉识别模块
使用多模态大模型分析零件加工图纸
"""

import os
import json
import base64
import requests
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# 豆包API配置
DOUBAO_API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
DOUBAO_MODEL = "doubao-vision-pro"

# 环境变量获取API Key
DOUBAO_API_KEY = os.environ.get("DOUBAO_API_KEY", "")


class DoubaoBlueprintRecognizer:
    """豆包AI图纸识别器"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or DOUBAO_API_KEY
        self.model = DOUBAO_MODEL
        self.api_url = DOUBAO_API_URL
        
    def encode_image(self, image_path: str) -> str:
        """将图片编码为base64"""
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    def call_api(self, image_path: str, prompt: str) -> Dict:
        """调用豆包API"""
        if not self.api_key:
            raise ValueError("需要配置豆包API Key")
        
        # 编码图片
        base64_image = self.encode_image(image_path)
        
        # 构建请求
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "temperature": 0.1
        }
        
        # 发送请求
        response = requests.post(
            self.api_url,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"API调用失败: {response.text}")
        
        result = response.json()
        return result
    
    def parse_response(self, response_text: str) -> Dict:
        """解析API响应，提取JSON"""
        # 尝试提取JSON部分
        try:
            # 查找JSON块
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        return {}
    
    def recognize_from_image(self, image_path: str) -> Dict:
        """从图片识别图纸"""
        prompt = """你是一个专业的机械制图AI助手。请仔细分析这张零件加工图纸，提取所有技术信息。

## 必须提取的信息（严格JSON格式）：

1. **零件基本信息**
   - part_number: 图纸上的型号（如GZ-305、GZ-308等）
   - part_name: 零件名称

2. **尺寸参数** - 逐个标注尺寸
   - 总长(_total_length)
   - 最大外径(_max_diameter) 
   - 其他台阶直径
   - 孔径

3. **技术要求**
   - surface_finish: 表面粗糙度（如Ra3.2、Ra1.6）
   - tolerance: 形位公差
   - material: 材料

4. **加工特征（关键！）** - 所有孔、槽、螺纹等
   - type: "hole"(光孔) 或 "thread_hole"(螺纹孔)
   - diameter: 直径mm
   - depth: 深度mm
   - position: {x, y} 相对坐标
   - is_threaded: true/false

## 返回格式（必须是合法JSON）：
```json
{
  "part_number": "GZ-305",
  "part_name": "锁头轴端5-G50-700A",
  "dimensions": {
    "总长": "700mm",
    "最大外径": "50mm",
    "孔径": "10mm"
  },
  "technical": {
    "表面粗糙度": "Ra3.2",
    "材料": "45#钢"
  },
  "features": [
    {"type": "hole", "diameter": 10, "position": {"x": 0, "y": 0}, "depth": 30, "is_threaded": false},
    {"type": "thread_hole", "diameter": 8, "position": {"x": 20, "y": 0}, "depth": 20, "is_threaded": true}
  ]
}
```

注意：请直接返回JSON，不要有其他文字说明！"""
        
        print(f"[DoubaoRecognizer] 正在调用豆包API分析图纸...")
        
        result = self.call_api(image_path, prompt)
        
        # 提取响应内容
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            parsed = self.parse_response(content)
            print(f"[DoubaoRecognizer] 识别完成: {parsed.get('part_number', '未知')}")
            return parsed
        
        raise Exception(f"API响应格式异常: {result}")
    
    def recognize_from_pdf_images(self, image_dir: str) -> Dict:
        """从多页图片识别（PDF转换后的图片）"""
        image_files = sorted(Path(image_dir).glob("blueprint-*.png"))
        
        if not image_files:
            # 尝试其他命名
            image_files = sorted(Path(image_dir).glob("*.png"))
        
        all_features = []
        part_info = {}
        
        for img_path in image_files:
            print(f"[DoubaoRecognizer] 处理: {img_path.name}")
            
            try:
                result = self.recognize_from_image(str(img_path))
                
                # 合并特征
                if 'features' in result:
                    all_features.extend(result['features'])
                
                # 获取零件信息（取第一个有效值）
                if not part_info and 'part_number' in result:
                    part_info = {
                        'part_number': result.get('part_number', ''),
                        'part_name': result.get('part_name', ''),
                        'dimensions': result.get('dimensions', {}),
                        'technical': result.get('technical', {})
                    }
                    
            except Exception as e:
                print(f"[DoubaoRecognizer] 处理 {img_path.name} 失败: {e}")
        
        return {
            'part_number': part_info.get('part_number', 'UNKNOWN'),
            'part_name': part_info.get('part_name', '自动识别零件'),
            'features': all_features,
            'dimensions': part_info.get('dimensions', {}),
            'technical': part_info.get('technical', {})
        }


def recognize_with_doubao(pdf_path: str = None, image_dir: str = None) -> Dict:
    """
    使用豆包识别图纸的便捷函数
    
    Args:
        pdf_path: PDF文件路径（可选）
        image_dir: 图片目录（PDF转换后的图片）
    
    Returns:
        识别结果字典
    """
    recognizer = DoubaoBlueprintRecognizer()
    
    # 优先使用图片目录
    if image_dir:
        return recognizer.recognize_from_pdf_images(image_dir)
    
    # 如果只有PDF，先转换
    if pdf_path:
        # 转换为图片
        import subprocess
        output_dir = Path(pdf_path).parent
        subprocess.run([
            'pdftoppm', '-png', '-r', '150',
            pdf_path,
            str(output_dir / 'blueprint')
        ], capture_output=True)
        
        return recognizer.recognize_from_pdf_images(str(output_dir))
    
    raise ValueError("需要提供 pdf_path 或 image_dir")


if __name__ == "__main__":
    # 测试
    import sys
    
    if len(sys.argv) > 1:
        image_dir = sys.argv[1]
        result = recognize_with_doubao(image_dir=image_dir)
        
        print("\n=== 豆包AI识别结果 ===")
        print(f"零件型号: {result.get('part_number')}")
        print(f"零件名称: {result.get('part_name')}")
        print(f"特征数量: {len(result.get('features', []))}")
        
        for i, feat in enumerate(result.get('features', []), 1):
            print(f"  孔{i}: φ{feat.get('diameter')}mm, 位置({feat.get('position', {}).get('x')}, {feat.get('position', {}).get('y')}), 螺纹: {feat.get('is_threaded')}")
    else:
        print("用法: python doubao_recognizer.py <图片目录>")
