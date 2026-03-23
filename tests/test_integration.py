"""
集成测试
测试整个路径规划系统的集成功能
"""

import pytest
import datetime
import json
from algorithm.path_planner import PathPlanner
from algorithm.models import PathResult, PathComparison
from data.campus_map import CampusMapGenerator
from data.test_data import TestDataGenerator


class TestIntegration:
    """集成测试类"""

    def setup_method(self):
        """测试初始化"""
        self.planner = PathPlanner()
        self.test_generator = TestDataGenerator(seed=42)

    def test_end_to_end_path_planning(self):
        """测试端到端路径规划"""
        # 获取测试场景
        scenarios = self.test_generator.get_test_scenarios()
        assert len(scenarios) > 0

        for scenario in scenarios[:3]:  # 测试前3个场景
            start = scenario["start"]
            goal = scenario["goal"]
            time_obj = scenario["time"]
            alphas = scenario["alphas"]

            # 测试每个α值
            for alpha in alphas[:2]:  # 测试前2个α值
                path = self.planner.plan_path(start, goal, alpha, time_obj)

                assert path is not None, f"场景 {scenario['id']}, α={alpha}: 未找到路径"
                assert isinstance(path, PathResult)
                assert path.nodes[0] == start
                assert path.nodes[-1] == goal
                assert path.alpha == alpha
                assert path.total_distance > 0
                assert path.total_actual_cost >= path.total_distance

                # 验证路径细节
                details = self.planner.get_path_details(path)
                assert "summary" in details
                assert "node_sequence" in details
                assert "edge_sequence" in details
                assert "segment_details" in details
                assert "time_info" in details

    def test_path_comparison(self):
        """测试路径比较功能"""
        scenarios = self.test_generator.get_test_scenarios()

        for scenario in scenarios[:2]:  # 测试前2个场景
            start = scenario["start"]
            goal = scenario["goal"]
            time_obj = scenario["time"]
            alphas = scenario["alphas"]

            # 比较不同α值的路径
            comparison = self.planner.compare_paths(start, goal, alphas, time_obj)

            assert isinstance(comparison, PathComparison)
            assert comparison.start == start
            assert comparison.goal == goal
            assert comparison.time == time_obj
            assert set(comparison.comparisons.keys()) == set(alphas)

            # 验证每个路径
            for alpha, path in comparison.comparisons.items():
                assert path.alpha == alpha
                assert path.nodes[0] == start
                assert path.nodes[-1] == goal

            # 测试最佳路径查找
            best_by_cost = comparison.get_best_by("total_actual_cost")
            best_by_distance = comparison.get_best_by("total_distance")

            assert isinstance(best_by_cost, tuple)
            assert isinstance(best_by_distance, tuple)
            assert len(best_by_cost) == 2
            assert len(best_by_distance) == 2

            # 验证摘要信息
            summary = comparison.summary()
            assert summary["start"] == start
            assert summary["goal"] == goal
            assert summary["time"] == time_obj.isoformat()
            assert set(summary["alphas"]) == set(alphas)
            assert len(summary["distances"]) == len(alphas)
            assert len(summary["costs"]) == len(alphas)

    def test_route_analysis(self):
        """测试路线分析功能"""
        # 获取示例路线
        from data.campus_map import get_sample_routes
        sample_routes = get_sample_routes()
        assert len(sample_routes) > 0

        for route in sample_routes[:2]:  # 测试前2条路线
            start = route["start"]
            goal = route["goal"]

            # 生成时间点（今天的不同时间）
            date = datetime.date.today()
            time_points = [
                datetime.datetime.combine(date, datetime.time(8, 0)),   # 早上
                datetime.datetime.combine(date, datetime.time(12, 0)),  # 中午
                datetime.datetime.combine(date, datetime.time(18, 0)),  # 晚上
                datetime.datetime.combine(date, datetime.time(21, 45)), # 晚自习
            ]

            analysis = self.planner.analyze_route(start, goal, time_points)

            assert analysis["start"] == start
            assert analysis["goal"] == goal
            assert "analysis" in analysis
            assert "time_range" in analysis

            results = analysis["analysis"]
            assert len(results) == len(time_points)

            # 验证每个时间点的结果
            for i, result in enumerate(results):
                assert "time" in result
                assert "time_str" in result
                assert "peak_period" in result
                assert "is_peak" in result
                assert "path" in result

                path_info = result["path"]
                assert "nodes" in path_info
                assert "distance" in path_info
                assert "cost" in path_info
                assert "congestion_cost" in path_info
                assert "average_congestion" in path_info

    def test_campus_info(self):
        """测试校园信息获取"""
        info = self.planner.get_campus_info()

        assert "graph_info" in info
        assert "rule_engine_info" in info
        assert "key_nodes" in info
        assert "algorithm_info" in info

        # 验证图信息
        graph_info = info["graph_info"]
        assert "node_count" in graph_info
        assert "edge_count" in graph_info
        assert "is_connected" in graph_info
        assert graph_info["node_count"] > 0
        assert graph_info["edge_count"] > 0

        # 验证规则引擎信息
        rule_info = info["rule_engine_info"]
        assert rule_info["valid"] is True

        # 验证关键节点
        key_nodes = info["key_nodes"]
        assert "teaching_buildings" in key_nodes
        assert "cafeterias" in key_nodes
        assert "dormitories" in key_nodes
        assert "libraries" in key_nodes

        # 验证算法信息
        algo_info = info["algorithm_info"]
        assert algo_info["name"] == "动态惩罚A*算法"
        assert "formula" in algo_info
        assert "description" in algo_info

    def test_path_report_export(self):
        """测试路径报告导出"""
        # 创建一个路径
        time_obj = datetime.datetime(2024, 5, 20, 12, 0)
        path = self.planner.plan_path("TB1", "CA1", alpha=1.0, time=time_obj)
        assert path is not None

        # 导出文本报告
        text_report = self.planner.export_path_report(path, "text")
        assert isinstance(text_report, str)
        assert len(text_report) > 0
        assert "校园动态导航路径规划报告" in text_report
        assert "【基本信息】" in text_report
        assert "【路径统计】" in text_report
        assert "【节点序列】" in text_report

        # 导出JSON报告
        json_report = self.planner.export_path_report(path, "json")
        assert isinstance(json_report, str)

        # 验证JSON格式
        parsed = json.loads(json_report)
        assert "summary" in parsed
        assert "node_sequence" in parsed
        assert "edge_sequence" in parsed
        assert "segment_details" in parsed

    def test_cache_functionality(self):
        """测试缓存功能"""
        start, goal = "TB1", "CA1"
        alpha = 1.0
        time_obj = datetime.datetime(2024, 5, 20, 12, 0)

        # 第一次调用（应该计算）
        path1 = self.planner.plan_path(start, goal, alpha, time_obj)
        assert path1 is not None

        # 第二次调用相同参数（应该从缓存读取）
        path2 = self.planner.plan_path(start, goal, alpha, time_obj)
        assert path2 is not None
        assert path1.nodes == path2.nodes
        assert path1.total_distance == path2.total_distance

        # 清空缓存
        self.planner.clear_cache()

        # 第三次调用（应该重新计算）
        path3 = self.planner.plan_path(start, goal, alpha, time_obj)
        assert path3 is not None
        # 路径应该相同（算法确定性），但这是新的计算

    def test_alternative_routes(self):
        """测试替代路线查找"""
        start, goal = "TB1", "CA1"
        alpha = 1.0
        time_obj = datetime.datetime(2024, 5, 20, 12, 0)

        # 获取主要路径
        main_path = self.planner.plan_path(start, goal, alpha, time_obj)
        assert main_path is not None

        # 查找替代路线
        alternatives = self.planner.find_alternative_routes(start, goal, alpha, time_obj, max_alternatives=2)

        # 可能没有替代路线，或者有1-2条
        assert alternatives is not None
        assert len(alternatives) <= 2

        for alt_path in alternatives:
            assert isinstance(alt_path, PathResult)
            assert alt_path.nodes[0] == start
            assert alt_path.nodes[-1] == goal
            assert alt_path.nodes != main_path.nodes  # 应该不同

    def test_performance_scenarios(self):
        """测试性能场景"""
        performance_cases = self.test_generator.get_performance_test_cases(5)

        for case in performance_cases:
            start = case["start"]
            goal = case["goal"]
            time_obj = case["time"]
            alpha = case["alpha"]

            # 规划路径
            path = self.planner.plan_path(start, goal, alpha, time_obj)

            # 验证路径有效
            if path is not None:
                assert path.nodes[0] == start
                assert path.nodes[-1] == goal
                assert path.alpha == alpha
                assert path.total_distance >= 0

    def test_alpha_sensitivity_integration(self):
        """测试α敏感性集成"""
        sensitivity_tests = self.test_generator.get_alpha_sensitivity_test()

        for test in sensitivity_tests[:1]:  # 测试第一个
            start = test["start"]
            goal = test["goal"]
            time_obj = test["time"]
            alphas = test["alphas"][:5]  # 测试前5个α值

            results = {}
            for alpha in alphas:
                path = self.planner.plan_path(start, goal, alpha, time_obj)
                if path:
                    results[alpha] = path

            # 验证不同α值的结果
            assert len(results) > 0

            # 检查结果有效性
            sorted_alphas = sorted(results.keys())
            if len(sorted_alphas) > 1:
                # 拥堵成本不一定单调，因为路径可能改变
                # 只记录信息用于调试
                congestion_costs = [results[alpha].congestion_cost for alpha in sorted_alphas]
                print(f"α值: {sorted_alphas}, 拥堵成本: {congestion_costs}")

    def test_error_handling(self):
        """测试错误处理"""
        # 无效节点
        with pytest.raises(ValueError):
            self.planner.plan_path("INVALID_NODE", "TB1", alpha=1.0)

        # 无效α值
        with pytest.raises(ValueError):
            self.planner.plan_path("TB1", "CA1", alpha=-1.0)

        # 无效输出格式
        path = self.planner.plan_path("TB1", "CA1", alpha=1.0)
        with pytest.raises(ValueError, match="不支持的输出格式"):
            self.planner.export_path_report(path, "invalid_format")

    def test_data_consistency(self):
        """测试数据一致性"""
        # 验证校园地图数据一致性
        generator = CampusMapGenerator()
        nodes, edges = generator.get_campus_data()

        # 节点应该都在图中
        for node_id, node in nodes.items():
            graph_node = self.planner.graph.get_node(node_id)
            assert graph_node is not None
            assert graph_node.node_id == node.node_id
            assert graph_node.name == node.name

        # 边应该都在图中（或反向边）
        for edge in edges:
            graph_edge = self.planner.graph.get_edge(edge.from_node, edge.to_node)
            if graph_edge is None:
                # 检查反向边
                graph_edge = self.planner.graph.get_edge(edge.to_node, edge.from_node)
            assert graph_edge is not None

    def test_system_validation(self):
        """测试系统整体验证"""
        # 验证所有组件
        campus_info = self.planner.get_campus_info()

        # 图应该连通
        assert campus_info["graph_info"]["is_connected"] is True

        # 规则应该有效
        assert campus_info["rule_engine_info"]["valid"] is True

        # 算法应该通过验证
        validation = self.planner.algorithm.validate_algorithm()
        assert validation["all_passed"] is True

        # 测试关键功能
        test_scenarios = self.test_generator.get_test_scenarios()[:3]
        all_passed = True
        failures = []

        for scenario in test_scenarios:
            try:
                path = self.planner.plan_path(
                    scenario["start"],
                    scenario["goal"],
                    scenario["alphas"][0],
                    scenario["time"]
                )
                if path is None:
                    all_passed = False
                    failures.append(f"场景 {scenario['id']}: 未找到路径")
            except Exception as e:
                all_passed = False
                failures.append(f"场景 {scenario['id']}: 异常 {str(e)}")

        assert all_passed, f"系统验证失败: {failures}"


if __name__ == "__main__":
    # 手动运行集成测试
    test = TestIntegration()
    test.setup_method()

    print("运行集成测试...")

    # 运行关键测试
    test.test_end_to_end_path_planning()
    test.test_path_comparison()
    test.test_campus_info()
    test.test_path_report_export()
    test.test_system_validation()

    print("\n集成测试通过!")
    print("\n系统功能验证:")
    campus_info = test.planner.get_campus_info()
    print(f"  节点总数: {campus_info['graph_info']['node_count']}")
    print(f"  边总数: {campus_info['graph_info']['edge_count']}")
    print(f"  图是否连通: {campus_info['graph_info']['is_connected']}")
    print(f"  规则引擎有效: {campus_info['rule_engine_info']['valid']}")

    # 测试一个示例场景
    test_scenarios = test.test_generator.get_test_scenarios()
    if test_scenarios:
        scenario = test_scenarios[0]
        print(f"\n示例场景测试 ({scenario['name']}):")
        path = test.planner.plan_path(
            scenario["start"],
            scenario["goal"],
            scenario["alphas"][0],
            scenario["time"]
        )
        if path:
            print(f"  路径找到: {len(path.nodes)} 个节点")
            print(f"  总距离: {path.total_distance:.1f}m")
            print(f"  总成本: {path.total_actual_cost:.1f}")
            print(f"  拥堵成本: {path.congestion_cost:.1f}")