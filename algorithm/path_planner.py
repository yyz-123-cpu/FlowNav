"""
路径规划主控制器
整合图构建、规则引擎和A*算法，提供统一的路径规划接口
"""

import datetime
from typing import List, Dict, Optional, Tuple, Any
from algorithm.models import PathResult, PathComparison
from algorithm.graph_builder import CampusGraph, create_campus_graph
from algorithm.rule_engine import TimeRuleEngine, default_rule_engine
from algorithm.a_star_algorithm import DynamicAStar


class PathPlanner:
    """路径规划主控制器"""

    def __init__(self, graph: Optional[CampusGraph] = None,
                 rule_engine: Optional[TimeRuleEngine] = None):
        """初始化路径规划器"""
        self.graph = graph or create_campus_graph()
        self.rule_engine = rule_engine or default_rule_engine
        self.algorithm = DynamicAStar(self.graph, self.rule_engine)
        self._cache: Dict[Tuple[str, str, float, str], PathResult] = {}

    def plan_path(self, start: str, goal: str, alpha: float = 1.0,
                  time: Optional[datetime.datetime] = None) -> Optional[PathResult]:
        """
        规划路径

        参数:
            start: 起点节点ID或名称
            goal: 终点节点ID或名称
            alpha: 用户偏好权重（0.0-2.0），默认1.0
            time: 规划时间，默认为当前时间

        返回:
            PathResult对象，包含路径详细信息
        """
        # 标准化输入
        start_id = self._standardize_node_input(start)
        goal_id = self._standardize_node_input(goal)

        if time is None:
            time = datetime.datetime.now()

        # 检查缓存
        cache_key = (start_id, goal_id, alpha, time.isoformat())
        if cache_key in self._cache:
            return self._cache[cache_key]

        # 执行路径规划
        path_result = self.algorithm.find_path(start_id, goal_id, alpha, time)

        # 缓存结果
        if path_result:
            self._cache[cache_key] = path_result

        return path_result

    def compare_paths(self, start: str, goal: str,
                     alpha_values: List[float] = None,
                     time: Optional[datetime.datetime] = None) -> PathComparison:
        """
        比较不同α值的路径

        参数:
            start: 起点节点ID或名称
            goal: 终点节点ID或名称
            alpha_values: α值列表，默认为[0, 0.5, 1.0, 1.5, 2.0]
            time: 规划时间，默认为当前时间

        返回:
            PathComparison对象，包含所有α值的路径结果
        """
        if alpha_values is None:
            alpha_values = [0, 0.5, 1.0, 1.5, 2.0]

        if time is None:
            time = datetime.datetime.now()

        start_id = self._standardize_node_input(start)
        goal_id = self._standardize_node_input(goal)

        # 获取不同α值的路径结果
        comparisons = {}
        for alpha in alpha_values:
            path = self.plan_path(start_id, goal_id, alpha, time)
            if path:
                comparisons[alpha] = path

        return PathComparison(
            start=start_id,
            goal=goal_id,
            time=time,
            comparisons=comparisons
        )

    def get_path_details(self, path_result: PathResult) -> Dict[str, Any]:
        """获取路径的详细信息"""
        if not path_result:
            return {"error": "路径结果为空"}

        details = {
            "summary": path_result.summary(),
            "node_sequence": path_result.nodes,
            "edge_sequence": [
                {
                    "from": edge.from_node,
                    "to": edge.to_node,
                    "distance": edge.distance,
                    "road_type": edge.road_type.value,
                    "peak_areas": edge.peak_areas
                }
                for edge in path_result.edges
            ],
            "segment_details": [
                {
                    "edge": f"{seg.edge.from_node}->{seg.edge.to_node}",
                    "distance": seg.distance,
                    "congestion_factor": seg.congestion_factor,
                    "actual_cost": seg.actual_cost
                }
                for seg in path_result.segments
            ],
            "time_info": self.rule_engine.get_peak_period_info(path_result.planning_time)
        }

        # 添加节点详细信息
        node_details = []
        for node_id in path_result.nodes:
            node = self.graph.get_node(node_id)
            if node:
                node_details.append({
                    "id": node.node_id,
                    "name": node.name,
                    "type": node.node_type.value,
                    "coordinates": node.coordinates
                })
        details["node_details"] = node_details

        return details

    def analyze_route(self, start: str, goal: str,
                     time_points: List[datetime.datetime] = None) -> Dict[str, Any]:
        """分析路线在不同时间点的表现"""
        start_id = self._standardize_node_input(start)
        goal_id = self._standardize_node_input(goal)

        if time_points is None:
            # 生成全天的时间点（每2小时）
            date = datetime.date.today()
            time_points = []
            for hour in range(8, 22, 2):  # 8:00-20:00
                time_points.append(datetime.datetime.combine(date, datetime.time(hour, 0)))

        results = []
        for time_obj in time_points:
            # 使用中等α值（1.0）进行分析
            path = self.plan_path(start_id, goal_id, alpha=1.0, time=time_obj)
            if path:
                time_info = self.rule_engine.get_peak_period_info(time_obj)
                results.append({
                    "time": time_obj.isoformat(),
                    "time_str": time_obj.strftime("%H:%M"),
                    "peak_period": time_info["peak_period"],
                    "is_peak": time_info["is_peak"],
                    "path": {
                        "nodes": path.nodes,
                        "distance": path.total_distance,
                        "cost": path.total_actual_cost,
                        "congestion_cost": path.congestion_cost,
                        "average_congestion": path.average_congestion
                    }
                })

        return {
            "start": start_id,
            "goal": goal_id,
            "analysis": results,
            "time_range": {
                "start": time_points[0].isoformat() if time_points else None,
                "end": time_points[-1].isoformat() if time_points else None,
                "count": len(time_points)
            }
        }

    def find_alternative_routes(self, start: str, goal: str,
                               alpha: float = 1.0,
                               time: Optional[datetime.datetime] = None,
                               max_alternatives: int = 3) -> List[PathResult]:
        """查找替代路线"""
        if time is None:
            time = datetime.datetime.now()

        start_id = self._standardize_node_input(start)
        goal_id = self._standardize_node_input(goal)

        # 主要路径
        main_path = self.plan_path(start_id, goal_id, alpha, time)
        if not main_path:
            return []

        alternatives = []
        visited_paths = {tuple(main_path.nodes)}

        # 简单实现：通过禁止某些边来寻找替代路径
        # 注意：这是一个简化的实现，实际应用中可能需要更复杂的算法
        for i in range(len(main_path.edges)):
            if len(alternatives) >= max_alternatives:
                break

            # 临时禁止一条边
            edge_to_avoid = main_path.edges[i]
            original_distance = edge_to_avoid.distance

            # 临时修改边的距离（使其非常大）
            edge_to_avoid.distance = float('inf')

            try:
                alt_path = self.plan_path(start_id, goal_id, alpha, time)
                if alt_path and tuple(alt_path.nodes) not in visited_paths:
                    alternatives.append(alt_path)
                    visited_paths.add(tuple(alt_path.nodes))
            finally:
                # 恢复边的原始距离
                edge_to_avoid.distance = original_distance

        return alternatives

    def get_campus_info(self) -> Dict[str, Any]:
        """获取校园地图信息"""
        graph_info = self.graph.get_graph_info()
        rule_validation = self.rule_engine.validate_rules()

        # 获取关键节点
        key_nodes = {
            "teaching_buildings": [
                {"id": node.node_id, "name": node.name}
                for node in self.graph.find_nodes_by_type("teaching_building")
            ],
            "cafeterias": [
                {"id": node.node_id, "name": node.name}
                for node in self.graph.find_nodes_by_type("cafeteria")
            ],
            "dormitories": [
                {"id": node.node_id, "name": node.name}
                for node in self.graph.find_nodes_by_type("dormitory")
            ],
            "libraries": [
                {"id": node.node_id, "name": node.name}
                for node in self.graph.find_nodes_by_type("library")
            ]
        }

        return {
            "graph_info": graph_info,
            "rule_engine_info": rule_validation,
            "key_nodes": key_nodes,
            "algorithm_info": {
                "name": "动态惩罚A*算法",
                "formula": "g_new(e) = d(e) × [1 + α × (C(e,t) - 1)]",
                "description": "考虑时间相关拥挤成本和用户偏好权重的改进A*算法"
            }
        }

    def clear_cache(self) -> None:
        """清空路径缓存"""
        self._cache.clear()

    def _standardize_node_input(self, node_input: str) -> str:
        """标准化节点输入（支持节点ID或名称）"""
        # 前端到后端节点ID映射（解决数据不一致问题）
        node_id_mapping = {
            # 运动场
            'S1': 'SP1',    # 前端S1 -> 后端SP1
            # 校门
            'G1': 'GATE_S', # 前端G1 -> 后端GATE_S（西门）
            'G2': 'GATE_E', # 前端G2 -> 后端GATE_E（东门）
            # 宿舍楼
            'D2': 'DO2',    # 前端D2 -> 后端DO2
            # 交叉点
            'J1': 'X1',     # 前端J1 -> 后端X1
            'J2': 'X2',     # 前端J2 -> 后端X2
            'J3': 'X3',     # 前端J3 -> 后端X3
        }

        # 首先检查映射
        mapped_id = node_id_mapping.get(node_input)
        if mapped_id:
            node = self.graph.get_node(mapped_id)
            if node:
                return mapped_id

        # 其次尝试作为节点ID
        node = self.graph.get_node(node_input)
        if node:
            return node_input

        # 尝试通过名称查找
        for node_id, node_obj in self.graph.nodes.items():
            if node_obj.name == node_input:
                return node_id

        # 如果都没找到，返回原始输入（将由下层处理错误）
        return node_input

    def export_path_report(self, path_result: PathResult,
                          output_format: str = "text") -> str:
        """导出路径报告"""
        if output_format == "text":
            return self._export_text_report(path_result)
        elif output_format == "json":
            import json
            return json.dumps(self.get_path_details(path_result), indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"不支持的输出格式: {output_format}")

    def _export_text_report(self, path_result: PathResult) -> str:
        """生成文本格式的路径报告"""
        details = self.get_path_details(path_result)
        summary = details["summary"]
        time_info = details["time_info"]

        report = []
        report.append("=" * 60)
        report.append("校园动态导航路径规划报告")
        report.append("=" * 60)
        report.append("")

        # 基本信息
        report.append("【基本信息】")
        report.append(f"  起点: {path_result.nodes[0] if path_result.nodes else 'N/A'}")
        report.append(f"  终点: {path_result.nodes[-1] if path_result.nodes else 'N/A'}")
        report.append(f"  规划时间: {summary['planning_time']}")
        report.append(f"  高峰期状态: {time_info['description']}")
        report.append(f"  用户偏好α值: {summary['alpha']}")
        report.append("")

        # 路径统计
        report.append("【路径统计】")
        report.append(f"  节点数量: {summary['node_count']}")
        report.append(f"  边数量: {summary['edge_count']}")
        report.append(f"  总物理距离: {summary['total_distance']:.1f} 米")
        report.append(f"  总实际成本: {summary['total_actual_cost']:.1f}")
        report.append(f"  拥堵成本: {summary['congestion_cost']:.1f}")
        report.append(f"  平均拥挤系数: {summary['average_congestion']:.2f}")
        report.append("")

        # 节点序列
        report.append("【节点序列】")
        node_names = []
        for node_id in path_result.nodes:
            node = self.graph.get_node(node_id)
            if node:
                node_names.append(f"{node.name}({node_id})")
            else:
                node_names.append(node_id)
        report.append("  → ".join(node_names))
        report.append("")

        # 详细路径段
        if details["segment_details"]:
            report.append("【详细路径段】")
            for i, segment in enumerate(details["segment_details"], 1):
                report.append(f"  {i:2d}. {segment['edge']}:")
                report.append(f"       距离: {segment['distance']:.1f}m, "
                            f"拥挤系数: {segment['congestion_factor']:.1f}, "
                            f"实际成本: {segment['actual_cost']:.1f}")

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)


# 默认路径规划器实例
default_planner = PathPlanner()


if __name__ == "__main__":
    # 测试代码
    planner = PathPlanner()

    print("=== 路径规划器测试 ===")

    print("1. 校园信息:")
    campus_info = planner.get_campus_info()
    print(f"   节点总数: {campus_info['graph_info']['node_count']}")
    print(f"   边总数: {campus_info['graph_info']['edge_count']}")
    print(f"   图是否连通: {campus_info['graph_info']['is_connected']}")

    print(f"\n2. 关键节点:")
    for category, nodes in campus_info['key_nodes'].items():
        print(f"   {category}: {[n['name'] for n in nodes]}")

    print(f"\n3. 路径规划示例 (第一教学楼 -> 第一食堂):")

    # 测试不同时间
    test_cases = [
        ("平峰期", datetime.datetime(2024, 5, 20, 14, 30), 1.0),
        ("午餐高峰期", datetime.datetime(2024, 5, 20, 12, 0), 1.0),
        ("午餐高峰期 (α=0)", datetime.datetime(2024, 5, 20, 12, 0), 0),
        ("午餐高峰期 (α=2.0)", datetime.datetime(2024, 5, 20, 12, 0), 2.0),
    ]

    for name, time_obj, alpha in test_cases:
        path = planner.plan_path("第一教学楼", "第一食堂", alpha, time_obj)
        if path:
            print(f"\n   {name} (α={alpha}):")
            print(f"     路径: {path.nodes}")
            print(f"     距离: {path.total_distance:.1f}m")
            print(f"     成本: {path.total_actual_cost:.1f}")
            print(f"     拥堵成本: {path.congestion_cost:.1f}")
        else:
            print(f"\n   {name}: 未找到路径")

    print(f"\n4. 路径对比 (图书馆 -> 第一宿舍楼, 晚自习高峰期):")
    time_obj = datetime.datetime(2024, 5, 20, 21, 45)
    comparison = planner.compare_paths("图书馆", "第一宿舍楼", time=time_obj)

    print(f"   对比α值: {sorted(comparison.comparisons.keys())}")
    for alpha, path in comparison.comparisons.items():
        print(f"     α={alpha}: 距离={path.total_distance:.1f}m, "
              f"拥堵成本={path.congestion_cost:.1f}")

    print(f"\n5. 路径分析报告示例:")
    if test_cases:
        _, time_obj, alpha = test_cases[1]  # 午餐高峰期，α=1.0
        path = planner.plan_path("第一教学楼", "第一食堂", alpha, time_obj)
        if path:
            report = planner.export_path_report(path, "text")
            # 只打印前20行
            lines = report.split('\n')[:25]
            print('\n'.join(lines))
            print("...")