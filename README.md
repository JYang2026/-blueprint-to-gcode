# 智能零件加工图识别与G代码生成系统

## 系统架构设计

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           系统架构总览                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐           │
│  │   Web前端    │───▶│   Flask API   │───▶│  图像识别    │           │
│  │  (上传/预览) │◀───│   (后端服务)  │◀───│  (OCR+CV)    │           │
│  └──────────────┘    └──────────────┘    └──────────────┘           │
│                              │                      │                  │
│                              ▼                      ▼                  │
│                       ┌──────────────┐    ┌──────────────┐           │
│                       │  加工路径     │    │   几何解析    │           │
│                       │   生成器      │◀───│    引擎      │           │
│                       └──────────────┘    └──────────────┘           │
│                              │                                             │
│                              ▼                                             │
│                       ┌──────────────┐    ┌──────────────┐           │
│                       │   G代码      │    │   仿真渲染    │           │
│                       │   生成器      │───▶│  (Three.js)  │           │
│                       └──────────────┘    └──────────────┘           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## 技术栈

| 层次 | 技术选型 | 说明 |
|------|----------|------|
| 前端 | HTML5 + Three.js | 3D仿真可视化 |
| 后端 | Python Flask | API服务 |
| 图像识别 | OpenCV + Tesseract | 尺寸标注识别 |
| 几何解析 | Shapely + ezdxf | 几何特征提取 |
| G代码生成 | 自研模板引擎 | 兼容FANUC/Siemens |
| 部署 | Docker | 一键部署 |

## 核心功能模块

### 1. 图纸识别模块 (blueprint_recognizer)
- PDF/DWG图纸解析
- 尺寸标注自动提取（线性、角度、直径、半径）
- 几何特征识别（孔、槽、轮廓）
- 公差与表面粗糙度识别

### 2. 加工路径生成模块 (path_generator)
- 钻孔加工路径
- 铣削轮廓加工路径
- 镗孔加工路径
- 攻丝加工路径

### 3. G代码生成模块 (gcode_generator)
- 支持FANUC/Siemens/Mitsubishi
- 自动选择切削参数
- 刀具补偿与坐标系设置
- 冷却液控制

### 4. 仿真可视化模块 (simulation)
- 实时3D加工仿真
- 刀具轨迹显示
- 材料去除模拟
- 碰撞检测预警

### 5. Word文档生成模块 (word_generator)
- 自动生成加工技术文档
- 包含零件信息、尺寸、技术要求
- 集成G代码程序
- 导出为HTML格式（可用WPS/Word打开）

## API接口

### 文档下载接口

```
# 下载加工技术文档（HTML格式，可用WPS另存为.docx）
GET /api/download/word/<task_id>

# 直接从图纸数据生成文档
POST /api/generate/word
Content-Type: application/json

{
  "blueprint": {
    "part_number": "GZ-308",
    "part_name": "零件名称",
    "dimensions": {...},
    "technical": {...},
    "features": [...]
  },
  "gcode": "G代码内容..."
}
```

## 快速开始

### 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python api/app.py

# 访问 http://localhost:5000
```

### Docker部署

```bash
docker-compose up -d
```

## 使用流程

1. **上传图纸** → POST `/api/upload`
2. **获取结果** → 返回 task_id
3. **下载G代码** → GET `/api/download/gcode/<task_id>`
4. **下载加工文档** → GET `/api/download/word/<task_id>`

## 目录结构

```
blueprint-to-gcode/
├── api/                  # Flask API服务
│   └── app.py
├── core/                 # 核心引擎
│   ├── engine.py         # 主处理引擎
│   ├── doubao_recognizer.py  # 豆包AI识别
│   ├── pdf_recognizer.py     # PDF解析
│   └── word_generator.py     # Word文档生成
├── static/               # 前端静态文件
├── uploads/              # 上传文件
├── outputs/             # 输出文件
├── README.md
└── docker-compose.yml
```
