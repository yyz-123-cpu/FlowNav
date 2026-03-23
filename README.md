# 基于改进A*算法的时空感知路径规划方法
**FlowNav校园动态导航系统**

## 作品简介

FlowNav 是一个针对校园微观出行场景的智能导航系统，解决了传统导航软件在"潮汐人流"场景下的"隐形拥堵"问题。通过融合常识规则引擎与改进的A*算法，实现轻量级、高效率的时空动态导航。

### 核心创新点

1. **时空规则引擎**：基于时间动态调整路段拥挤系数，无需实时监控数据
2. **动态惩罚A*算法**：改进的A*算法，考虑用户偏好权重α
3. **轻量级设计**：避免复杂的深度学习模型，易于部署和维护

## 设计思路

### 问题分析
传统导航软件在校园等封闭场景中存在"隐形拥堵"问题。物理距离最短的路径在高峰期可能因人流集中而通行效率低下。本项目针对"潮汐人流"特征，设计了一种时空动态导航方案。

### 技术路线
1. **图模型抽象**：将校园地图建模为有向加权图，节点代表地点，边代表路径
2. **时空规则引擎**：基于时间动态调整路段拥挤系数，模拟高峰期拥堵
3. **改进A*算法**：引入用户偏好权重α，平衡距离最短与拥堵避免
4. **分层架构设计**：算法层、数据层、可视化层分离，提高可维护性
5. **前后端分离**：Python后端提供算法API，Vue.js前端提供交互界面

### 关键设计决策
- **规则驱动而非数据驱动**：避免依赖实时监控数据，使用常识规则模拟拥堵
- **参数化用户偏好**：通过α值让用户控制"最短距离"与"最少拥堵"的平衡
- **确定性模拟**：保证相同输入产生相同输出，便于测试和验证
- **渐进式部署**：支持本地模拟、API模式、公网访问多种使用场景

## 设计重难点

### 主要难点
1. **时空动态建模**：如何将时间维度融入静态图模型中，实现动态权重调整
2. **算法改进平衡**：在A*算法中引入拥堵惩罚的同时保持算法的最优性和效率
3. **规则引擎设计**：设计合理的时空规则，准确模拟校园潮汐人流特征
4. **前后端数据同步**：确保前端模拟数据与后端算法数据结构的一致性
5. **公网部署配置**：ngrok内网穿透与nginx反向代理的协同工作

### 解决方案
1. **动态权重函数**：设计 $g_{new}(e) = d(e) \times [1 + \alpha \times (C(e, t) - 1)]$ 公式，将时间t和用户偏好α融入边权重
2. **启发函数保持**：保持A*算法的可纳性和一致性，仅修改代价函数g(n)
3. **基于经验的规则设计**：通过校园生活观察，制定就餐、自习等高峰期的拥堵规则
4. **数据模型标准化**：定义统一的节点、边、路径数据结构，前后端共用
5. **分层部署架构**：前端通过ngrok暴露，API通过nginx反向代理，实现安全访问

### 技术挑战克服
- **路径验证问题**：添加PathValidator类，检测重复节点、无效边，保证路径合理性
- **API错误处理**：完善FastAPI异常处理，将ValueError转换为400错误，提供清晰错误信息
- **可视化兼容性**：处理API模式下节点坐标缺失问题，自动生成网格布局坐标
- **箭头显示优化**：调整ECharts配置，确保API模式下路径箭头清晰可见

## 算法原理

### 数学模型

校园地图抽象为有向加权图 $G = (V, E)$，边权重升级为动态变量：

$$
g_{new}(e) = d(e) \times [ 1 + \alpha \times (C(e, t) - 1) ]
$$

- $d(e)$：路段物理距离
- $C(e, t)$：时间相关的拥挤系数（通过规则引擎获取）
- $\alpha$：用户个性化偏好权重（0=只关注距离，越大越避开拥挤）

### 时空规则

- **规则A（就餐高峰期 11:50-12:30, 17:30-18:30）**：食堂、核心教学楼路段 $C=4.0-5.0$
- **规则B（晚自习高峰期 21:30-22:10）**：图书馆/教学楼到宿舍区路段 $C=3.0-4.0$
- **规则C（平峰期）**：其他路段 $C=1.0$

## 系统架构

```
FlowNav/
├── algorithm/           # 算法层
│   ├── models.py           # 数据模型定义
│   ├── graph_builder.py    # 图构建模块
│   ├── rule_engine.py      # 时空规则引擎
│   ├── a_star_algorithm.py # 动态惩罚A*算法
│   └── path_planner.py     # 路径规划主控制器
├── data/               # 数据层
│   ├── campus_map.py       # 校园地图模拟数据
│   └── test_data.py        # 测试数据生成器
├── tests/              # 测试层
│   ├── test_rule_engine.py
│   ├── test_a_star.py
│   └── test_integration.py
├── visualization/      # 可视化层
│   ├── path_visualizer.py  # 路径可视化
│   └── comparison_plot.py  # 对比分析图
├── examples/           # 使用示例
│   ├── basic_usage.py
│   └── advanced_usage.py
├── requirements.txt    # 依赖包
└── README.md          # 项目说明
```

## 开源代码与组件使用情况说明

本项目基于以下开源软件和组件构建，遵循各自的许可证要求：

### 后端算法组件
- **NetworkX (3.0+)**: 图论计算库，用于构建校园有向加权图，执行图遍历和路径分析
- **Matplotlib (3.7+)**: 数据可视化库，用于生成路径对比图、拥堵热力图等分析图表
- **FastAPI (0.104+)**: 现代Web框架，用于构建RESTful API服务器，提供路径规划接口
- **Uvicorn (0.24+)**: ASGI服务器，用于部署FastAPI应用
- **Pydantic (2.5+)**: 数据验证库，用于API请求/响应模型验证

### 前端界面组件
- **Vue.js 3**: 渐进式JavaScript框架，构建响应式前端界面
- **Bootstrap 5**: CSS框架，提供现代化UI组件和响应式布局
- **ECharts 5**: 可视化图表库，用于校园地图展示、路径可视化
- **axios**: HTTP客户端，用于前端与后端API通信

### 开发工具
- **Python 3.9+**: 主要开发语言
- **Node.js/npm**: 前端依赖管理
- **pytest**: Python测试框架
- **Git**: 版本控制系统

### 部署工具
- **ngrok**: 内网穿透工具，将本地前端暴露到公网
- **nginx**: Web服务器，用于反向代理API请求
- **uvicorn**: Python ASGI服务器，部署FastAPI应用

### 许可证合规性
所有使用的开源组件均采用兼容的许可证（MIT、BSD、Apache 2.0等），本项目采用MIT许可证，符合各组件许可证要求。具体依赖版本见 `requirements.txt` 文件。

## 作品安装说明

### 环境要求
- Python 3.9 或更高版本
- Node.js 16+ (仅前端开发需要)
- Git (用于克隆仓库)

### 1. 获取源代码
```bash
# 克隆仓库
git clone https://github.com/yyz-123-cpu/FlowNav.git
cd FlowNav
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 基本使用

```python
from algorithm.path_planner import PathPlanner
import datetime

# 创建路径规划器
planner = PathPlanner()

# 规划路径（午餐高峰期）
time_obj = datetime.datetime(2024, 5, 20, 12, 0)
path = planner.plan_path("第一教学楼", "第一食堂", alpha=1.0, time=time_obj)

if path:
    print(f"路径: {path.nodes}")
    print(f"总距离: {path.total_distance:.1f}m")
    print(f"拥堵成本: {path.congestion_cost:.1f}")
```

### 运行示例

```bash
# 基础示例
python examples/basic_usage.py

# 高级示例
python examples/advanced_usage.py
```

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_a_star.py -v
```

## 功能特性

### 1. 动态路径规划
- 考虑时间相关的拥堵情况
- 支持用户偏好权重α调节
- 提供最短距离和最低拥堵等多种优化目标

### 2. 路径对比分析
- 比较不同α值的路径效果
- 分析时间敏感性
- 生成对比报告和图表

### 3. 可视化展示
- 校园地图可视化
- 路径高亮显示
- 拥堵热力图
- 对比分析图表

### 4. 测试验证
- 完整的单元测试套件
- 集成测试验证
- 性能基准测试

## 使用示例

### 示例1：简单路径规划

```python
from algorithm.path_planner import PathPlanner

planner = PathPlanner()
path = planner.plan_path("TB1", "CA1", alpha=1.0)

if path:
    print(f"节点序列: {path.nodes}")
    print(f"总距离: {path.total_distance:.1f}m")
    print(f"平均拥堵系数: {path.average_congestion:.2f}")
```

### 示例2：α值对比

```python
import datetime

planner = PathPlanner()
time_obj = datetime.datetime(2024, 5, 20, 12, 0)  # 午餐高峰期

# 比较不同α值
alphas = [0, 0.5, 1.0, 1.5, 2.0]
for alpha in alphas:
    path = planner.plan_path("TB1", "CA1", alpha, time_obj)
    if path:
        print(f"α={alpha}: 距离={path.total_distance:.1f}m, "
              f"拥堵成本={path.congestion_cost:.1f}")
```

### 示例3：时间敏感性分析

```python
from algorithm.path_planner import PathPlanner

planner = PathPlanner()
analysis = planner.analyze_route("TB1", "CA1")

for result in analysis['analysis']:
    print(f"时间: {result['time_str']}, "
          f"高峰期: {result['peak_period']}, "
          f"距离: {result['path']['distance']:.1f}m")
```

## 可视化功能

### 校园地图

```python
from visualization.path_visualizer import PathVisualizer

visualizer = PathVisualizer()
visualizer.plot_campus_map(show_labels=True)
```

### 路径可视化

```python
from algorithm.path_planner import PathPlanner
from visualization.path_visualizer import PathVisualizer

planner = PathPlanner()
visualizer = PathVisualizer(planner)

path = planner.plan_path("TB1", "CA1", alpha=1.0)
visualizer.plot_path(path, show_congestion=True)
```

### 对比分析图

```python
from visualization.comparison_plot import ComparisonPlot
import datetime

plotter = ComparisonPlot()
time_obj = datetime.datetime(2024, 5, 20, 12, 0)

# α敏感性分析
plotter.plot_alpha_sensitivity("TB1", "CA1", time_obj)
```

## API参考

### 主要类

#### `PathPlanner`
路径规划主控制器，提供统一的API接口。

**主要方法：**
- `plan_path(start, goal, alpha=1.0, time=None)`：规划路径
- `compare_paths(start, goal, alpha_values=None, time=None)`：比较不同α值的路径
- `analyze_route(start, goal, time_points=None)`：分析路线在不同时间点的表现
- `get_path_details(path_result)`：获取路径详细信息
- `get_campus_info()`：获取校园地图信息

#### `CampusGraph`
校园图类，封装NetworkX图并提供校园特定功能。

#### `TimeRuleEngine`
时空规则引擎，根据时间动态计算路段拥挤系数。

#### `DynamicAStar`
动态惩罚A*算法实现。

### 数据模型

#### `PathResult`
路径规划结果，包含：
- `nodes`：路径节点序列
- `edges`：路径边序列
- `total_distance`：总物理距离
- `total_actual_cost`：总实际成本
- `congestion_cost`：拥堵成本
- `average_congestion`：平均拥挤系数

## 测试

### 单元测试

```bash
# 测试规则引擎
python -m pytest tests/test_rule_engine.py -v

# 测试A*算法
python -m pytest tests/test_a_star.py -v
```

### 集成测试

```bash
# 运行集成测试
python -m pytest tests/test_integration.py -v

# 生成测试覆盖率报告
python -m pytest tests/ --cov=algorithm --cov-report=html
```

## 项目背景

### 问题痛点
传统导航软件在进行步行导航时，底层逻辑大多是"静态物理距离最短"规划。但在高校或封闭型景区中，人流具有极强的"潮汐特征"，导致物理距离最短的路段往往通行效率最低。

### 解决方案
本项目通过将常识规则引擎与经典启发式搜索算法（A*算法）进行深度融合，实现轻量级、高效率的"时空动态导航"。

### 应用场景
- 校园微观出行（教学楼、食堂、宿舍、图书馆之间的通勤）
- 节假日热门景区导航
- 大型展会场馆内部导航
- 医院内部路径规划

## 开发指南

### 添加新节点类型
在 `algorithm/models.py` 中扩展 `NodeType` 枚举：

```python
class NodeType(Enum):
    NEW_TYPE = "new_type"  # 添加新类型
```

### 修改高峰期规则
在 `algorithm/rule_engine.py` 中调整 `peak_periods` 和 `congestion_ranges`：

```python
self.peak_periods = {
    PeakPeriod.NEW_PEAK: [
        ((8, 0), (9, 0))  # 新的高峰期时间
    ]
}

self.congestion_ranges = {
    PeakPeriod.NEW_PEAK: (2.0, 3.0)  # 新的拥挤系数范围
}
```

### 扩展可视化功能
在 `visualization/` 目录下创建新的可视化模块：

```python
class NewVisualizer:
    def plot_new_chart(self, data, save_path=None):
        # 实现新的图表类型
        pass
```

## 性能优化

### 缓存策略
- 启发值缓存：避免重复计算节点间的启发值
- 路径结果缓存：相同参数的路径规划结果缓存

### 算法优化
- 优先队列优化：使用heapq实现高效的开放集管理
- 启发函数优化：欧几里得距离作为启发值

## 路线图

### 短期目标
- [x] 完成核心算法实现
- [x] 实现基本可视化功能
- [x] 编写完整测试套件
- [x] 创建使用示例

### 中期目标
- [ ] 添加更多校园地图布局
- [ ] 优化算法性能
- [ ] 增加实时数据接口
- [ ] 开发Web界面

### 长期目标
- [ ] 支持多校园配置
- [ ] 集成实时人流量数据
- [ ] 开发移动端应用
- [ ] 支持多人协同路径规划

## 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## Web API 服务器

FlowNav 提供了一个RESTful API服务器，支持前端界面调用路径规划功能。

### 安装API依赖

```bash
pip install fastapi uvicorn pydantic
```

或更新 `requirements.txt` 后安装所有依赖：

```bash
pip install -r requirements.txt
```

### 启动API服务器

```bash
python api_server.py
```

服务器将在 `http://localhost:8000` 启动。支持以下命令行参数：

```bash
# 使用不同端口启动
python api_server.py --port 8080

# 在所有网络接口上启动（允许其他设备访问）
python api_server.py --host 0.0.0.0 --port 9000

# 端口被占用时自动尝试其他端口
python api_server.py --port 8000 --max-port-attempts 10

# 显示帮助信息
python api_server.py --help
```

### API状态检查

可以通过以下方式检查API服务器状态：

1. **检查健康端点**：
   ```bash
   curl http://localhost:8000/api/health
   ```
   或直接在浏览器中访问：`http://localhost:8000/api/health`

2. **检查可用端点**：
   ```bash
   curl http://localhost:8000/
   ```

3. **查看交互式文档**：
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

4. **检查端口占用**（Windows）：
   ```bash
   netstat -ano | findstr :8000
   ```

服务器将在 `http://localhost:8000` 启动，并提供以下API端点：

- `GET /` - API根端点，显示可用端点
- `GET /api/health` - 健康检查
- `GET /api/nodes` - 获取校园节点列表
- `GET /api/campus-info` - 获取校园信息
- `POST /api/plan-path` - 路径规划
- `POST /api/compare-paths` - 路径比较
- `POST /api/analyze-route` - 路线分析
- `POST /api/export-report` - 导出报告

### 前端连接API

1. 确保API服务器正在运行
2. 在前端界面点击"尝试连接API"按钮
3. 如果连接成功，状态栏将显示"已连接到后端API"

#### 连接问题解决

**常见错误及解决方法：**

1. **"无法连接到路径规划服务器"**
   - 检查API服务器是否启动（运行 `python api_server.py` 或访问 `http://localhost:8000/api/health`）
   - 检查端口8000是否被占用（运行 `netstat -ano | findstr :8000`）
   - 使用不同端口启动：`python api_server.py --port 8080`

2. **"API连接失败"**
   - 确保使用正确的API地址（默认 `http://localhost:8000/api`）
   - 检查防火墙设置，允许端口8000通信
   - 尝试切换到模拟数据模式测试前端功能

3. **"端口已被占用"**
   - 停止占用端口的进程：`taskkill /PID <进程ID> /F`
   - 使用不同端口启动：`python api_server.py --port 8080`
   - 或尝试其他端口：`python api_server.py --port 8001 --max-port-attempts 10`

4. **前端显示"api路径规划错误"**
   - 检查浏览器控制台（F12）查看详细错误信息
   - 确保API服务器返回正确格式的JSON数据
   - 切换到模拟数据模式验证前端功能正常

#### 验证真实A*算法

连接成功后，可以验证以下核心功能：

1. **α=0时最短距离路径**：验证算法不会强制经过不必要的交叉点
2. **α=2.0时拥堵避免**：验证算法会绕开高峰期拥堵区域
3. **时间敏感性**：测试不同时间点（早、中、晚）的路径变化

### API文档

启动服务器后，访问以下地址查看交互式API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 软件包装

FlowNav 已配置为可独立运行的软件，提供多种启动方式：

### 快速启动
1. **批处理文件**：双击 `run_flow_nav.bat` 自动启动所有服务
2. **Python启动器**：运行 `python launcher.py` 启动应用
3. **可执行文件**：使用 `build_exe.py` 构建独立可执行文件

### 主要功能
- **一键启动**：同时启动API服务器和前端服务器
- **自动依赖检查**：检查并安装缺少的Python依赖
- **端口冲突处理**：自动检测并切换可用端口
- **浏览器自动打开**：启动后自动在浏览器中打开应用界面
- **快捷方式创建**：支持创建桌面快捷方式（Windows/Linux/macOS）

### 详细指南
软件包装功能为可选高级功能，适用于将项目打包为独立可执行文件。对于常规使用，推荐使用 [公网部署方案](#公网部署方案)。

## 公网部署方案

本项目采用 **ngrok + nginx** 的轻量级公网部署方案，无需云服务器即可实现随时随地访问。

### 部署架构
```
用户浏览器 → ngrok公网URL → 本地前端服务器(8080)
                    ↓
              nginx反向代理 → 本地API服务器(8000)
```

### 1. ngrok 内网穿透 (前端暴露)
将本地前端服务器暴露到公网：
```bash
# 启动前端服务器 (端口8080)
python serve.py

# 启动ngrok隧道 (需要先安装ngrok并配置authtoken)
ngrok http 8080
```
ngrok将提供一个类似 `https://xxxx-xxx-xxx-xxx-xxx.ngrok-free.app` 的公网URL，任何设备均可访问。

### 2. nginx 反向代理 (API转发)
配置nginx将API请求转发到本地后端：
```nginx
# nginx配置示例 (nginx.conf)
server {
    listen 80;
    server_name localhost;

    # 前端静态文件
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API请求转发
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 3. 启动所有服务
完整部署流程：
```bash
# 第一步：启动后端API服务器
python api_server.py --port 8000

# 第二步：启动前端服务器
python serve.py --port 8080

# 第三步：启动nginx (以管理员身份运行)
nginx.exe

# 第四步：启动ngrok隧道
ngrok http 8080
```

### 4. 访问方式
- **本地访问**: http://localhost:8080
- **公网访问**: https://xxxx-xxx-xxx-xxx-xxx.ngrok-free.app
- **API端点**: 通过nginx代理，前端自动将API请求发送到正确地址

### 优势特点
- **零成本**: 使用ngrok免费版和nginx开源软件
- **快速部署**: 几分钟内即可完成公网访问配置
- **安全性**: ngrok提供HTTPS加密，nginx提供访问控制
- **灵活性**: 可随时切换回本地开发模式

### 注意事项
1. ngrok免费版有连接数和带宽限制，适合演示和测试
2. nginx需要正确配置，确保API请求正确转发
3. 本地计算机需保持开机和联网状态
4. 每次重启ngrok会获得新的公网URL

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 项目主页：https://github.com/yyz-123-cpu/FlowNav
- 问题跟踪：https://github.com/yyz-123-cpu/FlowNav/issues

## 致谢

- 感谢 NetworkX 团队提供优秀的图论计算库
- 感谢 Matplotlib 团队提供强大的可视化工具
- 感谢所有贡献者和用户的支持

---

**FlowNav - 让校园出行更智能，更高效**