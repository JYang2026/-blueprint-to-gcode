"""
Word文档生成模块
将图纸识别结果和G代码生成为Word文档
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import uuid


class WordDocumentGenerator:
    """Word文档生成器"""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir) if output_dir else Path("outputs")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_html(self, blueprint_data: Dict, gcode: str = "", plan_data: Dict = None) -> str:
        """
        生成HTML格式文档（可转换为Word）
        
        Args:
            blueprint_data: 图纸识别结果
            gcode: G代码内容
            plan_data: 加工计划数据（包含工序信息）
        
        Returns:
            HTML文档路径
        """
        # 提取数据
        part_number = blueprint_data.get('part_number', 'UNKNOWN')
        part_name = blueprint_data.get('part_name', '自动识别零件')
        dimensions = blueprint_data.get('dimensions', {})
        technical = blueprint_data.get('technical', {})
        features = blueprint_data.get('features', [])
        
        # 生成唯一文件名
        doc_id = uuid.uuid4().hex[:8]
        filename = f"{part_number}_{doc_id}.html"
        filepath = self.output_dir / filename
        
        # 构建HTML内容
        html = self._build_html(
            part_number=part_number,
            part_name=part_name,
            dimensions=dimensions,
            technical=technical,
            features=features,
            gcode=gcode,
            plan_data=plan_data
        )
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(filepath)
    
    def _build_html(self, part_number: str, part_name: str, 
                   dimensions: Dict, technical: Dict, 
                   features: list, gcode: str, plan_data: Dict = None) -> str:
        """构建HTML文档内容"""
        
        # 处理特征列表
        features_html = ""
        if features:
            for i, feat in enumerate(features, 1):
                feat_type = feat.get('type', 'unknown')
                diameter = feat.get('diameter', 'N/A')
                position = feat.get('position', {})
                x = position.get('x', 'N/A')
                y = position.get('y', 'N/A')
                depth = feat.get('depth', 'N/A')
                is_threaded = feat.get('is_threaded', False)
                
                features_html += f"""
                <tr>
                    <td>{i}</td>
                    <td>{feat_type}</td>
                    <td>Φ{diameter} mm</td>
                    <td>({x}, {y})</td>
                    <td>{depth} mm</td>
                    <td>{"是" if is_threaded else "否"}</td>
                </tr>
                """
        else:
            features_html = "<tr><td colspan='6'>无</td></tr>"
        
        # 处理尺寸
        dim_list = []
        for k, v in dimensions.items():
            dim_list.append(f"<tr><td>{k}</td><td>{v}</td></tr>")
        dimensions_html = "".join(dim_list) if dim_list else "<tr><td colspan='2'>无</td></tr>"
        
        # 处理技术要求
        tech_list = []
        for k, v in technical.items():
            tech_list.append(f"<tr><td>{k}</td><td>{v}</td></tr>")
        technical_html = "".join(tech_list) if tech_list else "<tr><td colspan='2'>无</td></tr>"
        
        # 处理工序列表
        operations_html = ""
        if plan_data and plan_data.get('operations'):
            for op in plan_data['operations']:
                operations_html += f"""
                <tr>
                    <td>{op.get('序号', '')}</td>
                    <td>{op.get('工序名称', '')}</td>
                    <td>{op.get('刀具', '')}</td>
                    <td>{op.get('刀具直径', '')} mm</td>
                    <td>{op.get('主轴转速', '')} rpm</td>
                    <td>{op.get('进给速度', '')} mm/min</td>
                </tr>
                """
        else:
            operations_html = "<tr><td colspan='6'>无工序数据</td></tr>"
        
        # G代码处理
        gcode_escaped = gcode.replace('<', '&lt;').replace('>', '&gt;')
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{part_name} - 加工技术文档</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: "宋体", "SimSun", "Times New Roman", serif;
            font-size: 12pt;
            line-height: 1.8;
            padding: 40px;
            max-width: 900px;
            margin: 0 auto;
            color: #333;
        }}
        h1 {{
            font-size: 22pt;
            text-align: center;
            font-weight: bold;
            margin-bottom: 30px;
            border-bottom: 2px solid #333;
            padding-bottom: 15px;
        }}
        h2 {{
            font-size: 14pt;
            font-weight: bold;
            border-left: 4px solid #0066cc;
            padding-left: 12px;
            margin-top: 25px;
            margin-bottom: 15px;
            background: #f5f5f5;
            padding: 8px 12px;
        }}
        h3 {{
            font-size: 12pt;
            font-weight: bold;
            margin-top: 15px;
            margin-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 11pt;
        }}
        th, td {{
            border: 1px solid #666;
            padding: 10px 12px;
            text-align: left;
        }}
        th {{
            background-color: #0066cc;
            color: white;
            font-weight: bold;
            text-align: center;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin: 20px 0;
        }}
        .info-box {{
            border: 1px solid #ccc;
            padding: 15px;
            background: #fafafa;
        }}
        .info-box .label {{
            font-weight: bold;
            color: #666;
            font-size: 10pt;
        }}
        .info-box .value {{
            font-size: 14pt;
            color: #0066cc;
            margin-top: 5px;
        }}
        pre {{
            background-color: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
            border-radius: 5px;
            overflow-x: auto;
            font-family: "Consolas", "Monaco", monospace;
            font-size: 10pt;
            line-height: 1.5;
            border: 1px solid #333;
        }}
        .code-comment {{ color: #6a9955; }}
        .code-keyword {{ color: #569cd6; }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ccc;
            text-align: center;
            color: #666;
            font-size: 10pt;
        }}
        @page {{
            margin: 2cm;
        }}
    </style>
</head>
<body>

<h1>{part_name} 加工技术文档</h1>

<div class="info-grid">
    <div class="info-box">
        <div class="label">零件型号</div>
        <div class="value">{part_number}</div>
    </div>
    <div class="info-box">
        <div class="label">零件名称</div>
        <div class="value">{part_name}</div>
    </div>
    <div class="info-box">
        <div class="label">生成时间</div>
        <div class="value">{datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
    </div>
</div>

<h2>一、零件基本信息</h2>

<h3>1.1 尺寸参数</h3>
<table>
    <tr><th>参数名称</th><th>数值</th></tr>
    {dimensions_html}
</table>

<h3>1.2 技术要求</h3>
<table>
    <tr><th>项目</th><th>要求</th></tr>
    {technical_html}
</table>

<h3>1.3 加工特征</h3>
<table>
    <tr>
        <th>序号</th>
        <th>类型</th>
        <th>直径</th>
        <th>位置(X,Y)</th>
        <th>深度</th>
        <th>螺纹孔</th>
    </tr>
    {features_html}
</table>

<h2>二、加工工艺流程</h2>

<h3>2.1 工艺参数</h3>
<table>
    <tr><th>项目</th><th>数值</th></tr>
    <tr><td>预计加工时间</td><td>{plan_data.get('total_time', 'N/A')} 分钟</td></tr>
    <tr><td>加工工序数</td><td>{plan_data.get('operations_count', 0)} 道</td></tr>
    <tr><td>工件材料</td><td>{plan_data.get('material', 'N/A')}</td></tr>
    <tr><td>工件尺寸</td><td>{plan_data.get('workpiece_size', 'N/A')}</td></tr>
</table>

<h3>2.2 加工工序明细</h3>
<table>
    <tr>
        <th>序号</th>
        <th>工序名称</th>
        <th>刀具</th>
        <th>刀具直径</th>
        <th>主轴转速</th>
        <th>进给速度</th>
    </tr>
    {operations_html}
</table>

<h2>三、数控加工G代码程序</h2>

<h3>2.1 程序说明</h3>
<ul>
    <li><strong>数控系统</strong>: FANUC</li>
    <li><strong>工件坐标系</strong>: 右端面为 Z0，X轴为直径方向</li>
    <li><strong>加工类型</strong>: 车削加工</li>
</ul>

<h3>2.2 G代码程序</h3>
<pre>{gcode_escaped}</pre>

<h2>三、注意事项</h2>
<ol>
    <li>实际加工需根据机床型号调整切削参数</li>
    <li>加工前请确认刀具补偿参数已正确设置</li>
    <li>首件加工建议进行空跑仿真验证</li>
    <li>定期检查刀具磨损情况，及时更换</li>
</ol>

<div class="footer">
    <p>—— 本文档由 Blueprint to G-Code 系统自动生成 ——</p>
    <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</div>

</body>
</html>"""
        
        return html
    
    def generate_from_result(self, result: Dict) -> str:
        """
        从处理结果生成文档
        
        Args:
            result: process_blueprint 返回的结果字典
        
        Returns:
            HTML文档路径
        """
        blueprint = result.get('blueprint', {})
        gcode = result.get('gcode', '')
        plan_data = result.get('plan', {})
        
        return self.generate_html(blueprint, gcode, plan_data)


def generate_tech_document(blueprint_data: Dict, gcode: str = "", plan_data: Dict = None, output_dir: str = None) -> str:
    """
    便捷函数：生成技术文档
    
    Args:
        blueprint_data: 图纸识别结果
        gcode: G代码
        plan_data: 加工计划数据
        output_dir: 输出目录
    
    Returns:
        生成的文档路径
    """
    generator = WordDocumentGenerator(output_dir)
    return generator.generate_html(blueprint_data, gcode, plan_data)


if __name__ == "__main__":
    # 测试
    test_data = {
        "part_number": "GZ-308",
        "part_name": "缠绕式轴UN2.5-550B",
        "dimensions": {
            "总长": "350 mm",
            "最大外径": "Φ114 mm",
            "中段外径": "Φ85 mm",
            "最小外径": "Φ34 mm"
        },
        "technical": {
            "表面粗糙度": "Ra3.2",
            "材料": "碳钢",
            "形位公差": "0.010 mm"
        },
        "features": [
            {"type": "光孔", "diameter": 10, "position": {"x": 0, "y": 0}, "depth": 150, "is_threaded": False}
        ]
    }
    
    test_gcode = """O0001 (测试程序)
G99 G21 G50 S2000
T0101
G00 X130 Z20
S800 M03
M30"""
    
    generator = WordDocumentGenerator()
    filepath = generator.generate_html(test_data, test_gcode)
    
    print(f"文档已生成: {filepath}")
    print("提示: 用WPS或Word打开HTML文件，另存为.docx即可")
