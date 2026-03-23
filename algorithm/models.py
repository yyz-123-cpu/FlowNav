"""
数据模型定义模块
定义校园导航系统中的核心数据结构：节点、边、路径等
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any
from enum import Enum
import datetime


class NodeType(Enum):
    """节点类型枚举"""
    TEACHING_BUILDING = "teaching_building"  # 教学楼
    CAFETERIA = "cafeteria"                  # 食堂
    DORMITORY = "dormitory"                  # 宿舍
    LIBRARY = "library"                      # 图书馆
    CROSSROAD = "crossroad"                  # 道路交叉点
    GATE = "gate"                            # 校门
    SPORTS_FIELD = "sports_field"            # 运动场
    OTHER = "other"                          # 其他


class RoadType(Enum):
    """道路类型枚举"""
    MAIN_ROAD = "main_road"      # 主干道
    SIDE_ROAD = "side_road"      # 支路
    PATH = "path"                # 小路
    BRIDGE = "bridge"            # 桥梁
    TUNNEL = "tunnel"            # 隧道


@dataclass
class Node:
    """节点类，表示校园地图中的一个位置点"""
    node_id: str                    # 节点ID
    name: str                       # 节点名称
    node_type: NodeType             # 节点类型
    coordinates: Tuple[float, float]  # 坐标(x, y)，单位：米
    description: str = ""           # 节点描述

    def __post_init__(self):
        """验证坐标格式"""
        if len(self.coordinates) != 2:
            raise ValueError("Coordinates must be a tuple of (x, y)")

    @property
    def x(self) -> float:
        """X坐标"""
        return self.coordinates[0]

    @property
    def y(self) -> float:
        """Y坐标"""
        return self.coordinates[1]

    def distance_to(self, other: 'Node') -> float:
        """计算到另一个节点的欧几里得距离"""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


@dataclass
class Edge:
    """边类，表示两个节点之间的连接路径"""
    from_node: str          # 起点节点ID
    to_node: str            # 终点节点ID
    distance: float         # 物理距离，单位：米
    road_type: RoadType     # 道路类型
    peak_areas: List[str] = None  # 高峰期影响区域标记（如：cafeteria_area, teaching_area）

    def __post_init__(self):
        """初始化列表"""
        if self.peak_areas is None:
            self.peak_areas = []

    @property
    def edge_id(self) -> str:
        """边的唯一标识符"""
        return f"{self.from_node}->{self.to_node}"

    def reverse(self) -> 'Edge':
        """返回反向边"""
        return Edge(
            from_node=self.to_node,
            to_node=self.from_node,
            distance=self.distance,
            road_type=self.road_type,
            peak_areas=self.peak_areas.copy()
        )


@dataclass
class PathSegment:
    """路径段，包含一条边及其成本信息"""
    edge: Edge                      # 边对象
    distance: float                 # 物理距离
    congestion_factor: float        # 拥挤系数
    actual_cost: float              # 实际成本 = distance * (1 + alpha * (congestion_factor - 1))

    def __str__(self) -> str:
        return f"{self.edge.from_node}->{self.edge.to_node} (距离: {self.distance:.1f}m, 拥挤: {self.congestion_factor:.1f}, 成本: {self.actual_cost:.1f})"


@dataclass
class PathResult:
    """路径规划结果"""
    nodes: List[str]                # 路径节点ID序列
    edges: List[Edge]               # 路径边序列
    segments: List[PathSegment]     # 详细路径段信息
    total_distance: float           # 总物理距离
    total_actual_cost: float        # 总实际成本
    alpha: float                    # 用户偏好权重
    planning_time: datetime.datetime  # 规划时间

    @property
    def congestion_cost(self) -> float:
        """拥堵成本 = 总实际成本 - 总距离"""
        return self.total_actual_cost - self.total_distance

    @property
    def average_congestion(self) -> float:
        """平均拥挤系数"""
        if not self.segments:
            return 1.0
        total_weighted = sum(seg.distance * seg.congestion_factor for seg in self.segments)
        return total_weighted / self.total_distance if self.total_distance > 0 else 1.0

    def summary(self) -> Dict[str, Any]:
        """返回路径摘要信息"""
        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "total_distance": self.total_distance,
            "total_actual_cost": self.total_actual_cost,
            "congestion_cost": self.congestion_cost,
            "average_congestion": self.average_congestion,
            "alpha": self.alpha,
            "planning_time": self.planning_time.isoformat()
        }

    def __str__(self) -> str:
        summary = self.summary()
        return (
            f"路径规划结果:\n"
            f"  节点序列: {self.nodes}\n"
            f"  总距离: {summary['total_distance']:.1f}m\n"
            f"  总成本: {summary['total_actual_cost']:.1f}\n"
            f"  拥堵成本: {summary['congestion_cost']:.1f}\n"
            f"  平均拥挤系数: {summary['average_congestion']:.2f}\n"
            f"  α参数: {summary['alpha']}\n"
            f"  规划时间: {summary['planning_time']}"
        )


@dataclass
class PathComparison:
    """路径对比结果，用于比较不同α值的路径"""
    start: str                      # 起点
    goal: str                       # 终点
    time: datetime.datetime         # 规划时间
    comparisons: Dict[float, PathResult]  # α值到路径结果的映射

    def get_best_by(self, metric: str = "total_actual_cost") -> Tuple[float, PathResult]:
        """根据指定指标获取最佳路径"""
        if metric == "total_actual_cost":
            best_alpha = min(self.comparisons.keys(),
                           key=lambda a: self.comparisons[a].total_actual_cost)
        elif metric == "total_distance":
            best_alpha = min(self.comparisons.keys(),
                           key=lambda a: self.comparisons[a].total_distance)
        elif metric == "congestion_cost":
            best_alpha = min(self.comparisons.keys(),
                           key=lambda a: self.comparisons[a].congestion_cost)
        else:
            raise ValueError(f"未知指标: {metric}")

        return best_alpha, self.comparisons[best_alpha]

    def summary(self) -> Dict[str, Any]:
        """返回对比摘要"""
        alphas = sorted(self.comparisons.keys())
        return {
            "start": self.start,
            "goal": self.goal,
            "time": self.time.isoformat(),
            "alphas": alphas,
            "distances": [self.comparisons[a].total_distance for a in alphas],
            "costs": [self.comparisons[a].total_actual_cost for a in alphas],
            "congestion_costs": [self.comparisons[a].congestion_cost for a in alphas],
            "best_by_distance": self.get_best_by("total_distance")[0],
            "best_by_cost": self.get_best_by("total_actual_cost")[0],
        }