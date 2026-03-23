"""
动态惩罚A*算法单元测试
"""

import pytest
import datetime
from algorithm.graph_builder import create_campus_graph
from algorithm.a_star_algorithm import DynamicAStar
from algorithm.models import PathResult


class TestDynamicAStar:
    """动态惩罚A*算法测试类"""

    def setup_method(self):
        """测试初始化"""
        self.graph = create_campus_graph()
        self.algorithm = DynamicAStar(self.graph)

    def test_algorithm_initialization(self):
        """测试算法初始化"""
        assert self.algorithm.graph == self.graph
        assert self.algorithm.rule_engine is not None
        assert isinstance(self.algorithm.heuristic_cache, dict)

    def test_heuristic_function(self):
        """测试启发函数"""
        # 测试已知节点
        distance = self.algorithm.heuristic("TB1", "TB2")
        assert isinstance(distance, (int, float))
        assert distance >= 0

        # 测试相同节点
        distance = self.algorithm.heuristic("TB1", "TB1")
        assert distance == 0

        # 测试不存在的节点（应返回0）
        distance = self.algorithm.heuristic("TB1", "NON_EXISTENT")
        assert distance == 0

    def test_calculate_edge_cost(self):
        """测试边成本计算"""
        # 获取一条边
        edge = self.graph.get_edge("TB1", "TC")
        assert edge is not None

        # 测试时间：使用一个确保不是高峰期的时间（避免随机拥挤系数影响测试）
        # 使用凌晨时间（所有高峰期之外）
        test_time = datetime.datetime(2024, 5, 20, 3, 0)  # 凌晨3点，确保是平峰期
        cost, congestion = self.algorithm.calculate_edge_cost(edge, alpha=1.0, time_obj=test_time)

        # 验证公式: g_new(e) = d(e) × [1 + effective_weight × (C(e,t) - 1)]
        sensitivity = self.algorithm.SENSITIVITY_FACTOR
        # 计算有效权重（与算法中的非线性逻辑一致：alpha^1.5）
        effective_weight = (1.0 ** 1.5) * sensitivity  # alpha=1.0, 1.0^1.5=1.0
        expected_cost = edge.distance * (1 + effective_weight * (congestion - 1))
        assert abs(cost - expected_cost) < 1e-9
        assert congestion >= 1.0  # 拥挤系数至少为1.0

        # α=0测试（只关注距离）
        cost, congestion = self.algorithm.calculate_edge_cost(edge, alpha=0, time_obj=test_time)
        # α=0时，成本应等于距离，无论拥挤系数如何（灵敏度因子不影响）
        assert abs(cost - edge.distance) < 1e-9
        assert congestion >= 1.0

        # α=2.0测试
        cost, congestion = self.algorithm.calculate_edge_cost(edge, alpha=2.0, time_obj=test_time)
        effective_weight = (2.0 ** 1.5) * sensitivity  # 2.0^1.5 ≈ 2.8284
        expected_cost = edge.distance * (1 + effective_weight * (congestion - 1))
        assert abs(cost - expected_cost) < 1e-9
        assert congestion >= 1.0

    def test_find_path_basic(self):
        """测试基本路径查找"""
        # 有效路径
        path = self.algorithm.find_path("TB1", "CA1", alpha=1.0)
        assert isinstance(path, PathResult)
        assert len(path.nodes) >= 2
        assert path.nodes[0] == "TB1"
        assert path.nodes[-1] == "CA1"
        assert path.total_distance > 0
        assert path.total_actual_cost >= path.total_distance
        assert path.alpha == 1.0

        # 验证路径连通性
        for i in range(len(path.nodes) - 1):
            edge = self.graph.get_edge(path.nodes[i], path.nodes[i+1])
            assert edge is not None

    def test_find_path_same_start_goal(self):
        """测试起点终点相同的情况"""
        path = self.algorithm.find_path("TB1", "TB1", alpha=1.0)
        assert isinstance(path, PathResult)
        assert path.nodes == ["TB1"]
        assert path.total_distance == 0
        assert path.total_actual_cost == 0
        assert len(path.edges) == 0
        assert len(path.segments) == 0

    def test_find_path_alpha_zero(self):
        """测试α=0的情况（应返回最短距离路径）"""
        # 获取最短距离路径
        shortest_nodes = self.algorithm.find_shortest_distance_path("TB1", "CA1")
        assert shortest_nodes is not None

        # α=0的路径
        path_alpha0 = self.algorithm.find_path("TB1", "CA1", alpha=0)

        assert path_alpha0 is not None
        assert path_alpha0.nodes == shortest_nodes

        # 验证成本等于距离
        assert abs(path_alpha0.total_actual_cost - path_alpha0.total_distance) < 1e-9

    def test_find_path_invalid_nodes(self):
        """测试无效节点"""
        # 起点不存在
        with pytest.raises(ValueError, match="起点节点.*不存在"):
            self.algorithm.find_path("NON_EXISTENT", "TB1", alpha=1.0)

        # 终点不存在
        with pytest.raises(ValueError, match="终点节点.*不存在"):
            self.algorithm.find_path("TB1", "NON_EXISTENT", alpha=1.0)

        # α为负数
        with pytest.raises(ValueError, match="alpha参数不能为负数"):
            self.algorithm.find_path("TB1", "CA1", alpha=-1.0)

    def test_compare_alphas(self):
        """测试不同α值的路径比较"""
        time_obj = datetime.datetime(2024, 5, 20, 12, 0)  # 午餐高峰期
        alpha_values = [0, 0.5, 1.0, 1.5]

        results = self.algorithm.compare_alphas("TB1", "CA1", alpha_values, time_obj)

        assert isinstance(results, dict)
        assert set(results.keys()) == set(alpha_values)

        for alpha, path in results.items():
            assert isinstance(path, PathResult)
            assert path.alpha == alpha

        # α值越大，算法越倾向于避开拥堵，拥堵成本可能减少
        # 不强制要求单调性，因为路径可能变化

    def test_analyze_path_sensitivity(self):
        """测试路径敏感性分析"""
        time_obj = datetime.datetime(2024, 5, 20, 12, 0)
        sensitivity = self.algorithm.analyze_path_sensitivity(
            "TB1", "CA1",
            alpha_range=(0, 1.0),
            step=0.2,
            time_obj=time_obj
        )

        assert "alphas" in sensitivity
        assert "paths" in sensitivity
        assert "distances" in sensitivity
        assert "costs" in sensitivity
        assert "congestion_costs" in sensitivity
        assert "change_points" in sensitivity
        assert "start" in sensitivity
        assert "goal" in sensitivity
        assert "time" in sensitivity

        assert len(sensitivity["alphas"]) == len(sensitivity["paths"])
        assert len(sensitivity["alphas"]) == len(sensitivity["distances"])

        # 至少应该有2个α值
        assert len(sensitivity["alphas"]) >= 2

    def test_path_reconstruction(self):
        """测试路径重建"""
        # 先找到一条路径
        path = self.algorithm.find_path("TB1", "CA1", alpha=1.0)
        assert path is not None

        # 验证路径段信息
        assert len(path.segments) == len(path.edges)
        for i, segment in enumerate(path.segments):
            assert segment.edge == path.edges[i]
            assert segment.distance == path.edges[i].distance
            assert segment.congestion_factor >= 1.0
            assert segment.actual_cost >= segment.distance

        # 验证总距离计算正确
        calculated_distance = sum(seg.distance for seg in path.segments)
        assert abs(path.total_distance - calculated_distance) < 1e-9

        # 验证总成本计算正确
        calculated_cost = sum(seg.actual_cost for seg in path.segments)
        assert abs(path.total_actual_cost - calculated_cost) < 1e-9

    def test_time_sensitivity(self):
        """测试时间敏感性"""
        # 平峰期
        off_peak = datetime.datetime(2024, 5, 20, 14, 30)
        path_off_peak = self.algorithm.find_path("TB1", "CA1", alpha=1.0, time_obj=off_peak)

        # 午餐高峰期
        lunch_peak = datetime.datetime(2024, 5, 20, 12, 0)
        path_lunch = self.algorithm.find_path("TB1", "CA1", alpha=1.0, time_obj=lunch_peak)

        # 路径可能不同，或者相同但成本不同
        if path_off_peak.nodes == path_lunch.nodes:
            # 相同路径，但拥堵成本应该不同
            assert path_off_peak.congestion_cost <= path_lunch.congestion_cost
        else:
            # 不同路径，高峰期应避开拥堵区域
            # 检查午餐高峰期路径是否包含拥堵区域
            lunch_path_edges = [self.graph.get_edge(path_lunch.nodes[i], path_lunch.nodes[i+1])
                              for i in range(len(path_lunch.nodes)-1)]
            # 这里可以添加更详细的检查

    def test_algorithm_validation(self):
        """测试算法验证"""
        validation = self.algorithm.validate_algorithm()

        assert "all_passed" in validation
        assert "tests" in validation
        assert "graph_info" in validation
        assert "rule_engine_validation" in validation

        # 所有测试应该通过
        assert validation["all_passed"] is True

        for test in validation["tests"]:
            assert test["passed"] is True

    def test_cache_usage(self):
        """测试启发值缓存"""
        # 清空缓存
        self.algorithm.heuristic_cache.clear()

        # 第一次计算应该添加到缓存
        distance1 = self.algorithm.heuristic("TB1", "CA1")
        assert ("TB1", "CA1") in self.algorithm.heuristic_cache
        assert self.algorithm.heuristic_cache[("TB1", "CA1")] == distance1

        # 第二次计算应该从缓存读取
        distance2 = self.algorithm.heuristic("TB1", "CA1")
        assert distance1 == distance2

        # 反向计算应该重新计算
        distance3 = self.algorithm.heuristic("CA1", "TB1")
        assert ("CA1", "TB1") in self.algorithm.heuristic_cache

    def test_edge_cost_formula(self):
        """测试边成本公式正确性"""
        edge = self.graph.get_edge("TB1", "TC")
        assert edge is not None

        time_obj = datetime.datetime(2024, 5, 20, 12, 0)  # 午餐高峰期
        areas = edge.peak_areas

        # 手动计算拥挤系数
        from algorithm.rule_engine import default_rule_engine
        congestion_factor = default_rule_engine.get_congestion_factor(areas, time_obj)

        # 测试不同α值
        test_alphas = [0, 0.5, 1.0, 1.5, 2.0]
        for alpha in test_alphas:
            cost, factor = self.algorithm.calculate_edge_cost(edge, alpha, time_obj)

            # 验证公式: g_new(e) = d(e) × [1 + effective_weight × (C(e,t) - 1)]
            sensitivity = self.algorithm.SENSITIVITY_FACTOR
            if alpha <= 0:
                expected_cost = edge.distance
            else:
                effective_weight = (alpha ** 1.5) * sensitivity
                expected_cost = edge.distance * (1 + effective_weight * (factor - 1))
            assert abs(cost - expected_cost) < 1e-9

            # 验证拥挤系数在合理范围内（由于随机性，不检查精确相等）
            # 注意：时间虽然是午餐高峰期，但边可能受影响或不受影响
            assert factor >= 1.0  # 拥挤系数至少为1.0

    def test_performance(self):
        """测试算法性能（基本）"""
        import time

        start_time = time.time()
        path = self.algorithm.find_path("TB1", "CA1", alpha=1.0)
        end_time = time.time()

        execution_time = end_time - start_time

        # 应该很快完成（< 0.1秒）
        assert execution_time < 0.1, f"路径规划耗时 {execution_time:.3f} 秒，超过预期"

        # 验证路径有效
        assert path is not None
        assert len(path.nodes) >= 2

    def test_path_validation(self):
        """测试路径验证功能"""
        # 测试有效路径 - 使用实际存在的节点
        valid_nodes = ["TB1", "TC", "X1"]
        is_valid, errors = self.algorithm._validate_path(valid_nodes)
        assert is_valid is True
        assert errors == []

        # 测试重复节点
        duplicate_nodes = ["TB1", "TC", "TC", "X1"]
        is_valid, errors = self.algorithm._validate_path(duplicate_nodes)
        assert is_valid is False
        assert "重复节点" in errors[0]

        # 测试不存在边
        invalid_edge_nodes = ["TB1", "DO1"]  # 假设没有直接连接
        is_valid, errors = self.algorithm._validate_path(invalid_edge_nodes)
        assert is_valid is False
        assert "不存在" in errors[0]

        # 测试路径长度不足
        short_nodes = ["TB1"]
        is_valid, errors = self.algorithm._validate_path(short_nodes)
        assert is_valid is False
        assert "至少需要2个节点" in errors[0]

        # 测试算法生成的路径应该通过验证
        path = self.algorithm.find_path("TB1", "CA1", alpha=1.0)
        assert path is not None
        is_valid, errors = self.algorithm._validate_path(path.nodes)
        assert is_valid is True, f"算法生成的路径验证失败: {errors}"


if __name__ == "__main__":
    # 手动运行测试
    test = TestDynamicAStar()
    test.setup_method()

    print("运行动态惩罚A*算法测试...")
    test.test_algorithm_initialization()
    test.test_heuristic_function()
    test.test_calculate_edge_cost()
    test.test_find_path_basic()
    test.test_find_path_same_start_goal()
    test.test_find_path_alpha_zero()
    test.test_compare_alphas()
    test.test_path_reconstruction()
    test.test_algorithm_validation()
    test.test_edge_cost_formula()

    print("所有测试通过!")