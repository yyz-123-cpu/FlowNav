"""
校园地图模拟数据生成器
创建虚拟的校园地图节点和边数据，用于算法开发和测试
"""

from typing import List, Dict, Tuple
from algorithm.models import Node, NodeType, Edge, RoadType
import random


class CampusMapGenerator:
    """校园地图生成器"""

    def __init__(self, seed: int = 42):
        """初始化生成器"""
        self.seed = seed
        random.seed(seed)
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []

        # 定义区域中心坐标
        self.region_centers = {
            "teaching_area": (0, 0),        # 教学区中心
            "cafeteria_area": (300, 200),   # 食堂区中心
            "dormitory_area": (600, 0),     # 宿舍区中心
            "library_area": (150, 400),     # 图书馆区中心
            "sports_area": (-200, 150),     # 运动区中心
        }

        # 定义高峰期影响区域
        self.peak_areas = {
            "cafeteria_peak": ["cafeteria_area", "teaching_to_cafeteria"],
            "dormitory_peak": ["dormitory_area", "library_to_dormitory", "teaching_to_dormitory"],
        }

    def generate_nodes(self) -> Dict[str, Node]:
        """生成校园节点"""
        nodes = {}

        # ========== 教学区节点 ==========
        nodes["TB1"] = Node("TB1", "第一教学楼", NodeType.TEACHING_BUILDING, (0, 0))
        nodes["TB2"] = Node("TB2", "第二教学楼", NodeType.TEACHING_BUILDING, (-80, 50))
        nodes["TB3"] = Node("TB3", "第三教学楼", NodeType.TEACHING_BUILDING, (80, -30))
        nodes["TC"] = Node("TC", "教学区中心", NodeType.CROSSROAD, (0, 30))

        # ========== 食堂区节点 ==========
        nodes["CA1"] = Node("CA1", "第一食堂", NodeType.CAFETERIA, (300, 200))
        nodes["CA2"] = Node("CA2", "第二食堂", NodeType.CAFETERIA, (250, 250))
        nodes["CC"] = Node("CC", "食堂区中心", NodeType.CROSSROAD, (280, 180))

        # ========== 宿舍区节点 ==========
        nodes["DO1"] = Node("DO1", "第一宿舍楼", NodeType.DORMITORY, (600, 0))
        nodes["DO2"] = Node("DO2", "第二宿舍楼", NodeType.DORMITORY, (650, 50))
        nodes["DO3"] = Node("DO3", "第三宿舍楼", NodeType.DORMITORY, (550, -50))
        nodes["DO4"] = Node("DO4", "第四宿舍楼", NodeType.DORMITORY, (600, 100))
        nodes["DC"] = Node("DC", "宿舍区中心", NodeType.CROSSROAD, (600, 30))

        # ========== 图书馆节点 ==========
        nodes["LIB"] = Node("LIB", "中央图书馆", NodeType.LIBRARY, (150, 400))
        nodes["LC"] = Node("LC", "图书馆广场", NodeType.CROSSROAD, (130, 350))

        # ========== 运动场节点 ==========
        nodes["SP1"] = Node("SP1", "田径场", NodeType.SPORTS_FIELD, (-200, 150))
        nodes["SP2"] = Node("SP2", "篮球场", NodeType.SPORTS_FIELD, (-250, 100))

        # ========== 校门节点 ==========
        nodes["GATE_N"] = Node("GATE_N", "北门", NodeType.GATE, (0, 500))
        nodes["GATE_S"] = Node("GATE_S", "南门", NodeType.GATE, (0, -200))
        nodes["GATE_E"] = Node("GATE_E", "东门", NodeType.GATE, (700, 0))
        nodes["GATE_W"] = Node("GATE_W", "西门", NodeType.GATE, (-300, 0))

        # ========== 道路交叉点 ==========
        nodes["X1"] = Node("X1", "交叉点1", NodeType.CROSSROAD, (150, 100))
        nodes["X2"] = Node("X2", "交叉点2", NodeType.CROSSROAD, (300, 100))
        nodes["X3"] = Node("X3", "交叉点3", NodeType.CROSSROAD, (450, 100))
        nodes["X4"] = Node("X4", "交叉点4", NodeType.CROSSROAD, (150, 250))
        nodes["X5"] = Node("X5", "交叉点5", NodeType.CROSSROAD, (450, 250))

        # ========== 新增小路交叉点（增强路径多样性）==========
        nodes["X1a"] = Node("X1a", "小路交叉点1", NodeType.CROSSROAD, (140, 90))
        nodes["X2a"] = Node("X2a", "小路交叉点2", NodeType.CROSSROAD, (290, 90))
        nodes["X3a"] = Node("X3a", "小路交叉点3", NodeType.CROSSROAD, (480, 120))
        nodes["X4a"] = Node("X4a", "小路交叉点4", NodeType.CROSSROAD, (160, 270))
        nodes["X5a"] = Node("X5a", "小路交叉点5", NodeType.CROSSROAD, (460, 270))
        nodes["M1"] = Node("M1", "教学食堂连接点", NodeType.CROSSROAD, (100, 150))
        nodes["SP1a"] = Node("SP1a", "运动场小路连接点", NodeType.CROSSROAD, (-180, 130))

        self.nodes = nodes
        return nodes

    def generate_edges(self) -> List[Edge]:
        """生成校园边（连接路径）"""
        edges = []

        # 确保节点已生成
        if not self.nodes:
            self.generate_nodes()

        # ========== 教学区内连接 ==========
        edges.append(self._create_edge("TB1", "TC", 30, RoadType.MAIN_ROAD, ["class_change_area"]))
        edges.append(self._create_edge("TB2", "TC", 40, RoadType.SIDE_ROAD, ["class_change_area"]))
        edges.append(self._create_edge("TB3", "TC", 50, RoadType.SIDE_ROAD, ["class_change_area"]))

        # ========== 食堂区内连接 ==========
        edges.append(self._create_edge("CA1", "CC", 25, RoadType.MAIN_ROAD, ["cafeteria_area"]))
        edges.append(self._create_edge("CA2", "CC", 30, RoadType.SIDE_ROAD, ["cafeteria_area"]))

        # ========== 宿舍区内连接 ==========
        edges.append(self._create_edge("DO1", "DC", 30, RoadType.MAIN_ROAD, ["dormitory_area"]))
        edges.append(self._create_edge("DO2", "DC", 40, RoadType.SIDE_ROAD, ["dormitory_area"]))
        edges.append(self._create_edge("DO3", "DC", 35, RoadType.SIDE_ROAD, ["dormitory_area"]))
        edges.append(self._create_edge("DO4", "DC", 45, RoadType.SIDE_ROAD, ["dormitory_area"]))

        # ========== 图书馆连接 ==========
        edges.append(self._create_edge("LIB", "LC", 20, RoadType.MAIN_ROAD, ["library_peak"]))
        edges.append(self._create_edge("LC", "X4", 80, RoadType.MAIN_ROAD, ["library_to_dormitory"]))

        # ========== 运动场连接 ==========
        edges.append(self._create_edge("SP1", "SP2", 60, RoadType.PATH, ["sports_area"]))
        edges.append(self._create_edge("SP1", "GATE_W", 100, RoadType.SIDE_ROAD, ["sports_area", "gate_traffic"]))

        # ========== 主要干道连接 ==========
        # 教学区 -> 食堂区（高峰期拥堵主干道）
        edges.append(self._create_edge("TC", "X1", 80, RoadType.MAIN_ROAD, ["teaching_to_cafeteria"]))
        edges.append(self._create_edge("X1", "X2", 150, RoadType.MAIN_ROAD, ["teaching_to_cafeteria"]))
        edges.append(self._create_edge("X2", "CC", 100, RoadType.MAIN_ROAD, ["teaching_to_cafeteria", "cafeteria_area"]))

        # 教学区 -> 宿舍区（晚自习高峰期拥堵）
        edges.append(self._create_edge("TC", "X1", 80, RoadType.MAIN_ROAD, ["teaching_to_dormitory"]))  # 复用
        edges.append(self._create_edge("X1", "X3", 300, RoadType.MAIN_ROAD, ["teaching_to_dormitory"]))
        edges.append(self._create_edge("X3", "DC", 150, RoadType.MAIN_ROAD, ["teaching_to_dormitory", "dormitory_area"]))

        # 图书馆 -> 宿舍区（晚自习高峰期拥堵）
        edges.append(self._create_edge("LC", "X4", 80, RoadType.MAIN_ROAD, ["library_to_dormitory"]))  # 复用
        edges.append(self._create_edge("X4", "X5", 300, RoadType.MAIN_ROAD, ["library_to_dormitory"]))
        edges.append(self._create_edge("X5", "DC", 100, RoadType.MAIN_ROAD, ["library_to_dormitory", "dormitory_area"]))

        # 替代路径（小路，距离稍长但避开主干道）
        edges.append(self._create_edge("TC", "GATE_S", 120, RoadType.PATH, ["main_road_crossing"]))
        edges.append(self._create_edge("GATE_S", "X4", 180, RoadType.PATH, ["main_road_crossing"]))
        edges.append(self._create_edge("X4", "CC", 130, RoadType.PATH, ["main_road_crossing"]))

        edges.append(self._create_edge("TC", "SP1", 220, RoadType.PATH, ["teaching_to_sports"]))
        edges.append(self._create_edge("SP1", "X5", 250, RoadType.PATH, ["sports_area"]))
        edges.append(self._create_edge("X5", "DC", 120, RoadType.PATH))

        # ========== 新增替代路径（增加路径多样性）==========
        # 教学楼主楼到交叉点4的小路（避开主干道）
        edges.append(self._create_edge("TB1", "X4", 200, RoadType.PATH, ["class_change_area", "main_road_crossing"]))
        # 图书馆到食堂中心的小路（直接连接）
        edges.append(self._create_edge("LIB", "CC", 180, RoadType.PATH, ["library_peak", "cafeteria_area"]))
        # 运动场到主干道交叉点2的小路
        edges.append(self._create_edge("SP1", "X2", 220, RoadType.PATH, ["sports_area", "teaching_to_cafeteria"]))
        # 宿舍到食堂的小路（避开主干道）
        edges.append(self._create_edge("DO1", "CA1", 250, RoadType.PATH, ["dormitory_area", "cafeteria_area"]))

        # ========== 新增小路节点连接（增强alpha影响）==========
        # 平行小路：X1-X1a-X2a-X2（避开主干道拥堵）
        edges.append(self._create_edge("X1", "X1a", 20, RoadType.PATH))
        edges.append(self._create_edge("X1a", "X2a", 140, RoadType.PATH))
        edges.append(self._create_edge("X2a", "X2", 20, RoadType.PATH))
        # 宿舍区小路：X3-X3a-DC（避开晚自习拥堵）
        edges.append(self._create_edge("X3", "X3a", 30, RoadType.PATH))
        edges.append(self._create_edge("X3a", "DC", 130, RoadType.PATH))
        # 图书馆小路：X4-X4a-X5a-X5（避开晚自习拥堵）
        edges.append(self._create_edge("X4", "X4a", 20, RoadType.PATH))
        edges.append(self._create_edge("X4a", "X5a", 260, RoadType.PATH))
        edges.append(self._create_edge("X5a", "X5", 20, RoadType.PATH))
        # 教学区到食堂直接连接：TB1-M1-CA1（避开主干道）
        edges.append(self._create_edge("TB1", "M1", 120, RoadType.PATH, ["class_change_area"]))
        edges.append(self._create_edge("M1", "CA1", 85, RoadType.PATH, ["cafeteria_area"]))  # 从180减少到85，总距离205m
        # 运动场小路：SP1-SP1a-TC（替代路径）
        edges.append(self._create_edge("SP1", "SP1a", 20, RoadType.PATH))
        edges.append(self._create_edge("SP1a", "TC", 200, RoadType.PATH, ["teaching_to_sports"]))
        # 连接新节点到现有网络
        edges.append(self._create_edge("X1a", "M1", 60, RoadType.PATH))
        edges.append(self._create_edge("M1", "X4", 100, RoadType.PATH))

        # ========== 校门连接 ==========
        edges.append(self._create_edge("GATE_N", "LIB", 100, RoadType.MAIN_ROAD, ["gate_traffic"]))
        edges.append(self._create_edge("GATE_S", "TB3", 170, RoadType.MAIN_ROAD, ["gate_traffic"]))
        edges.append(self._create_edge("GATE_E", "DO1", 100, RoadType.MAIN_ROAD, ["gate_traffic"]))
        edges.append(self._create_edge("GATE_W", "SP1", 100, RoadType.MAIN_ROAD, ["gate_traffic", "sports_area"]))

        # ========== 新增关键连接（增强路径多样性）==========
        # 连接小路节点到主要建筑，使替代路径更有吸引力
        edges.append(self._create_edge("X1a", "TB1", 80, RoadType.PATH, ["class_change_area"]))
        edges.append(self._create_edge("X2a", "CA1", 80, RoadType.PATH, ["cafeteria_area"]))  # 从90减少到80，总距离190m
        edges.append(self._create_edge("X3a", "DO2", 70, RoadType.PATH, ["dormitory_area"]))
        edges.append(self._create_edge("X4a", "LIB", 120, RoadType.PATH, ["library_peak"]))
        edges.append(self._create_edge("X5a", "DO3", 100, RoadType.PATH, ["dormitory_area"]))
        edges.append(self._create_edge("SP1a", "GATE_W", 85, RoadType.PATH, ["gate_traffic", "sports_area"]))

        # 额外连接：创建更多平行路径
        edges.append(self._create_edge("X1a", "TC", 70, RoadType.PATH, ["class_change_area"]))
        edges.append(self._create_edge("X2a", "CC", 60, RoadType.PATH, ["cafeteria_area"]))
        edges.append(self._create_edge("X3a", "X1", 180, RoadType.PATH))
        edges.append(self._create_edge("X4a", "X2", 220, RoadType.PATH))
        edges.append(self._create_edge("X5a", "X3", 190, RoadType.PATH))
        edges.append(self._create_edge("SP1a", "X5", 240, RoadType.PATH, ["sports_area"]))

        # ========== 进一步优化：添加更多平行路径增强路径多样性 ==========
        # 1. X4→CA1直接连接（使TB1→X4→CA1路径完整）
        edges.append(self._create_edge("X4", "CA1", 160, RoadType.PATH, ["cafeteria_area", "main_road_crossing"]))

        # 2. TB1→X2a直接连接（创建更短替代路径）
        edges.append(self._create_edge("TB1", "X2a", 110, RoadType.PATH, ["class_change_area"]))

        # 3. GATE_S→LIB的替代路径：GATE_S→TB3→TC→X1a→M1→X4→LC→LIB的缩短版本
        edges.append(self._create_edge("GATE_S", "X4", 180, RoadType.PATH, ["gate_traffic", "main_road_crossing"]))  # 已有
        edges.append(self._create_edge("GATE_S", "LC", 280, RoadType.PATH, ["gate_traffic"]))  # 更直接

        # 4. LIB→CA1的替代路径（使LIB→CA1→DO1路径有更多选择）
        edges.append(self._create_edge("LIB", "CA1", 220, RoadType.PATH, ["library_peak", "cafeteria_area"]))

        # 5. 调整X1a→X2a距离使其更有竞争力（从140减少到120）
        # 注意：我们已经使用140，这里保持不变，但可以添加更短的平行路径
        edges.append(self._create_edge("X1a", "CA1", 130, RoadType.PATH, ["cafeteria_area"]))  # 从200减少到130，总距离210m

        # 6. 添加TB1→DO1的更直接路径（避开拥堵主干道）
        edges.append(self._create_edge("TB1", "X3a", 180, RoadType.PATH, ["class_change_area"]))

        # 7. 为SP1→CA1添加更多平行路径
        edges.append(self._create_edge("SP1", "CA1", 400, RoadType.PATH, ["sports_area", "cafeteria_area"]))  # 直接但稍远
        edges.append(self._create_edge("SP1", "X2a", 240, RoadType.PATH, ["sports_area", "teaching_to_cafeteria"]))

        # 8. 连接未充分利用的节点
        edges.append(self._create_edge("X3a", "CA1", 220, RoadType.PATH, ["cafeteria_area"]))
        edges.append(self._create_edge("X4a", "CA1", 210, RoadType.PATH, ["cafeteria_area"]))
        edges.append(self._create_edge("X5a", "CA1", 200, RoadType.PATH, ["cafeteria_area"]))

        # 9. 缩短一些现有路径的距离
        # X1a→X2a距离从140减少到120（添加平行更短路径）
        edges.append(self._create_edge("X1a", "X2a", 120, RoadType.PATH))

        # 10. 添加M1→X2a直接连接
        edges.append(self._create_edge("M1", "X2a", 70, RoadType.PATH, ["cafeteria_area"]))

        # 11. 添加TB1→CA1直接连接（低拥堵路径）
        # 这条路径假设通过建筑内部或隐蔽小路，避开食堂高峰期拥堵
        edges.append(self._create_edge("TB1", "CA1", 205, RoadType.PATH, ["class_change_area"]))

        # 调整一些现有小路的距离，使其更有竞争力
        # 更新X1a-X2a距离（从165减少到140）
        # 注意：我们将在后面覆盖，先删除原边，再添加新边
        # 实际上，我们将在生成边时直接使用新距离

        # 添加反向边（使图成为无向图）
        all_edges = edges.copy()
        for edge in edges:
            all_edges.append(edge.reverse())

        self.edges = all_edges
        return all_edges

    def _create_edge(self, from_node: str, to_node: str, distance: float,
                    road_type: RoadType, peak_areas: List[str] = None) -> Edge:
        """创建边对象"""
        if peak_areas is None:
            peak_areas = []
        return Edge(
            from_node=from_node,
            to_node=to_node,
            distance=distance,
            road_type=road_type,
            peak_areas=peak_areas
        )

    def get_campus_data(self) -> Tuple[Dict[str, Node], List[Edge]]:
        """获取完整的校园数据"""
        nodes = self.generate_nodes()
        edges = self.generate_edges()
        return nodes, edges

    def get_region_info(self) -> Dict[str, Dict[str, any]]:
        """获取区域信息"""
        return {
            "teaching_area": {
                "center": self.region_centers["teaching_area"],
                "nodes": ["TB1", "TB2", "TB3", "TC"],
                "description": "教学区，包含三栋教学楼"
            },
            "cafeteria_area": {
                "center": self.region_centers["cafeteria_area"],
                "nodes": ["CA1", "CA2", "CC"],
                "description": "食堂区，包含两个主要食堂"
            },
            "dormitory_area": {
                "center": self.region_centers["dormitory_area"],
                "nodes": ["DO1", "DO2", "DO3", "DO4", "DC"],
                "description": "宿舍区，包含四栋宿舍楼"
            },
            "library_area": {
                "center": self.region_centers["library_area"],
                "nodes": ["LIB", "LC"],
                "description": "图书馆区，包含中央图书馆"
            },
            "sports_area": {
                "center": self.region_centers["sports_area"],
                "nodes": ["SP1", "SP2"],
                "description": "运动区，包含田径场和篮球场"
            }
        }

    def get_peak_scenarios(self) -> Dict[str, Dict[str, any]]:
        """获取高峰期场景定义"""
        return {
            "lunch_peak": {
                "time_range": [(11, 50), (12, 30)],  # 11:50-12:30
                "affected_areas": ["cafeteria_area", "teaching_to_cafeteria"],
                "description": "午餐高峰期，食堂区和教学区到食堂的主干道拥堵"
            },
            "dinner_peak": {
                "time_range": [(17, 30), (18, 30)],  # 17:30-18:30
                "affected_areas": ["cafeteria_area", "teaching_to_cafeteria"],
                "description": "晚餐高峰期，食堂区和教学区到食堂的主干道拥堵"
            },
            "evening_study_peak": {
                "time_range": [(21, 30), (22, 10)],  # 21:30-22:10
                "affected_areas": ["dormitory_area", "library_to_dormitory", "teaching_to_dormitory"],
                "description": "晚自习高峰期，宿舍区、图书馆到宿舍区、教学区到宿舍区的主干道拥堵"
            }
        }


# 默认校园地图实例
default_campus = CampusMapGenerator()


def load_default_campus() -> Tuple[Dict[str, Node], List[Edge]]:
    """加载默认校园地图"""
    return default_campus.get_campus_data()


def get_sample_routes() -> List[Dict[str, str]]:
    """获取示例路线"""
    return [
        {"start": "TB1", "goal": "CA1", "name": "教学楼到食堂（午餐路线）"},
        {"start": "LIB", "goal": "DO1", "name": "图书馆到宿舍（晚自习路线）"},
        {"start": "TB1", "goal": "DO1", "name": "教学楼到宿舍（日常路线）"},
        {"start": "GATE_S", "goal": "LIB", "name": "南门到图书馆（访客路线）"},
        {"start": "SP1", "goal": "CA1", "name": "运动场到食堂（运动后路线）"},
    ]


if __name__ == "__main__":
    # 测试代码：生成并显示校园地图数据
    generator = CampusMapGenerator()
    nodes, edges = generator.get_campus_data()

    print("=== 校园地图节点 ===")
    for node_id, node in sorted(nodes.items()):
        print(f"{node_id}: {node.name} ({node.node_type.value}) at {node.coordinates}")

    print(f"\n=== 校园地图边 ===")
    print(f"总边数: {len(edges)}")

    # 按类型统计
    road_type_count = {}
    for edge in edges:
        rt = edge.road_type.value
        road_type_count[rt] = road_type_count.get(rt, 0) + 1

    for rt, count in road_type_count.items():
        print(f"{rt}: {count}条")

    print("\n=== 高峰期场景 ===")
    scenarios = generator.get_peak_scenarios()
    for name, scenario in scenarios.items():
        print(f"{name}: {scenario['description']}")

    print(f"\n=== 示例路线 ===")
    for route in get_sample_routes():
        print(f"{route['name']}: {route['start']} -> {route['goal']}")