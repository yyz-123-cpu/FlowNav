"""
高级使用示例
展示FlowNav校园动态导航系统的高级功能和自定义配置
"""

import datetime
import json
from algorithm.path_planner import PathPlanner
from algorithm.graph_builder import CampusGraph, create_campus_graph
from algorithm.rule_engine import TimeRuleEngine
from algorithm.a_star_algorithm import DynamicAStar
from visualization.path_visualizer import PathVisualizer
from visualization.comparison_plot import ComparisonPlot
from data.campus_map import CampusMapGenerator
from data.test_data import TestDataGenerator


def example_1_custom_campus_map():
    """示例1: 自定义校园地图"""
    print("=" * 60)
    print("示例1: 自定义校园地图")
    print("=" * 60)

    print("1. 创建自定义校园地图生成器...")
    generator = CampusMapGenerator(seed=123)

    # 获取地图数据
    nodes, edges = generator.get_campus_data()
    print(f"  • 生成节点数: {len(nodes)}")
    print(f"  • 生成边数: {len(edges)}")

    print("\n2. 查看区域信息:")
    region_info = generator.get_region_info()
    for region, info in region_info.items():
        print(f"  • {region}: {info['description']}")
        print(f"    节点: {info['nodes']}")

    print("\n3. 查看高峰期场景:")
    peak_scenarios = generator.get_peak_scenarios()
    for name, scenario in peak_scenarios.items():
        print(f"  • {name}: {scenario['description']}")
        print(f"    时间: {scenario['time_range']}")
        print(f"    影响区域: {scenario['affected_areas']}")

    print("\n4. 查看示例路线:")
    sample_routes = generator.get_sample_routes()
    for route in sample_routes:
        print(f"  • {route['name']}: {route['start']} → {route['goal']}")

    return generator


def example_2_custom_rule_engine():
    """示例2: 自定义规则引擎"""
    print("\n" + "=" * 60)
    print("示例2: 自定义规则引擎")
    print("=" * 60)

    print("1. 创建自定义规则引擎...")
    # 可以修改随机种子以确保可重复性
    rule_engine = TimeRuleEngine(seed=999)

    print("2. 验证规则:")
    validation = rule_engine.validate_rules()
    print(f"  • 规则有效: {validation['valid']}")
    if validation['issues']:
        print(f"  • 发现问题: {validation['issues']}")

    print("\n3. 测试自定义规则:")
    test_times = [
        ("平峰期", datetime.datetime(2024, 5, 20, 10, 0)),
        ("午餐高峰期", datetime.datetime(2024, 5, 20, 12, 15)),
        ("晚餐高峰期", datetime.datetime(2024, 5, 20, 18, 15)),
        ("晚自习高峰期", datetime.datetime(2024, 5, 20, 21, 45)),
    ]

    for time_name, time_obj in test_times:
        info = rule_engine.get_peak_period_info(time_obj)
        print(f"  • {time_name} ({time_obj.strftime('%H:%M')}):")
        print(f"    高峰期类型: {info['peak_period']}")
        print(f"    描述: {info['description']}")
        if info['is_peak']:
            print(f"    拥堵范围: {info['congestion_range']}")
            print(f"    影响区域: {info['affected_areas']}")

    return rule_engine


def example_3_custom_graph_and_algorithm():
    """示例3: 自定义图和算法"""
    print("\n" + "=" * 60)
    print("示例3: 自定义图和算法")
    print("=" * 60)

    print("1. 创建自定义校园图...")
    graph = create_campus_graph()

    print("2. 获取图信息:")
    info = graph.get_graph_info()
    print(f"  • 节点数: {info['node_count']}")
    print(f"  • 边数: {info['edge_count']}")
    print(f"  • 是否连通: {info['is_connected']}")

    print("\n3. 节点类型统计:")
    for node_type, count in info['node_types'].items():
        print(f"  • {node_type}: {count}")

    print("\n4. 道路类型统计:")
    for road_type, count in info['road_types'].items():
        print(f"  • {road_type}: {count}")

    print("\n5. 创建自定义算法...")
    rule_engine = TimeRuleEngine(seed=42)
    algorithm = DynamicAStar(graph, rule_engine)

    print("6. 验证算法:")
    validation = algorithm.validate_algorithm()
    print(f"  • 所有测试通过: {validation['all_passed']}")
    for test in validation['tests']:
        status = "✓" if test['passed'] else "✗"
        print(f"    {status} {test['name']}")

    return graph, algorithm


def example_4_custom_path_planner():
    """示例4: 自定义路径规划器"""
    print("\n" + "=" * 60)
    print("示例4: 自定义路径规划器")
    print("=" * 60)

    print("1. 使用自定义组件创建路径规划器...")
    graph = create_campus_graph()
    rule_engine = TimeRuleEngine(seed=777)
    planner = PathPlanner(graph, rule_engine)

    print("2. 测试自定义规划器:")
    time_obj = datetime.datetime(2024, 5, 20, 12, 0)

    # 测试不同场景
    test_cases = [
        ("教学楼到食堂", "TB1", "CA1", 1.0),
        ("图书馆到宿舍", "LIB", "DO1", 1.5),
        ("运动场到食堂", "SP1", "CA1", 0.5),
    ]

    for name, start, goal, alpha in test_cases:
        path = planner.plan_path(start, goal, alpha, time_obj)
        if path:
            print(f"  • {name} (α={alpha}):")
            print(f"    距离: {path.total_distance:.1f}m")
            print(f"    拥堵成本: {path.congestion_cost:.1f}")
            print(f"    节点数: {len(path.nodes)}")
        else:
            print(f"  • {name}: 未找到路径")

    return planner


def example_5_batch_processing():
    """示例5: 批处理和分析"""
    print("\n" + "=" * 60)
    print("示例5: 批处理和分析")
    print("=" * 60)

    print("1. 创建测试数据生成器...")
    test_generator = TestDataGenerator(seed=123)

    print("2. 生成测试场景:")
    scenarios = test_generator.get_test_scenarios()
    print(f"  • 测试场景数: {len(scenarios)}")

    for scenario in scenarios[:2]:  # 显示前2个
        print(f"\n  • {scenario['name']}:")
        print(f"    描述: {scenario['description']}")
        print(f"    路线: {scenario['start']} → {scenario['goal']}")
        print(f"    时间: {scenario['time'].strftime('%H:%M')}")
        print(f"    α值: {scenario['alphas']}")

    print("\n3. 生成性能测试用例:")
    perf_cases = test_generator.get_performance_test_cases(5)
    print(f"  • 性能测试用例数: {len(perf_cases)}")

    for case in perf_cases[:2]:  # 显示前2个
        print(f"  • {case['id']}: {case['description']}")

    print("\n4. 导出测试数据...")
    test_generator.export_test_data()

    return test_generator


def example_6_visualization_advanced():
    """示例6: 高级可视化"""
    print("\n" + "=" * 60)
    print("示例6: 高级可视化")
    print("=" * 60)

    print("1. 创建可视化器...")
    planner = PathPlanner()
    visualizer = PathVisualizer(planner)

    print("2. 绘制校园地图...")
    # 在实际使用中，可以取消注释以下代码
    # fig1 = visualizer.plot_campus_map(show_labels=True)
    # plt.show()

    print("3. 绘制路径示例...")
    time_obj = datetime.datetime(2024, 5, 20, 12, 0)
    path = planner.plan_path("TB1", "CA1", alpha=1.0, time=time_obj)

    if path:
        print(f"  • 路径找到: {len(path.nodes)} 个节点")
        # 在实际使用中，可以取消注释以下代码
        # fig2 = visualizer.plot_path(path, show_congestion=True)
        # plt.show()

        print("4. 绘制路径对比...")
        alphas = [0, 0.5, 1.0, 1.5]
        comparison = planner.compare_paths("TB1", "CA1", alphas, time_obj)

        if comparison.comparisons:
            print(f"  • 对比α值: {list(comparison.comparisons.keys())}")
            # 在实际使用中，可以取消注释以下代码
            # fig3 = visualizer.plot_path_comparison(comparison.comparisons)
            # plt.show()

    print("5. 绘制拥堵热力图...")
    # 在实际使用中，可以取消注释以下代码
    # fig4 = visualizer.plot_congestion_heatmap(time_obj)
    # plt.show()

    return visualizer


def example_7_comparison_analysis():
    """示例7: 对比分析"""
    print("\n" + "=" * 60)
    print("示例7: 对比分析")
    print("=" * 60)

    print("1. 创建对比分析图生成器...")
    plotter = ComparisonPlot()

    print("2. α敏感性分析...")
    time_obj = datetime.datetime(2024, 5, 20, 12, 0)
    # 在实际使用中，可以取消注释以下代码
    # fig1 = plotter.plot_alpha_sensitivity("TB1", "CA1", time_obj,
    #                                      alpha_range=(0, 2.0), step=0.2)
    # plt.show()

    print("3. 时间敏感性分析...")
    date = datetime.date(2024, 5, 20)
    # 在实际使用中，可以取消注释以下代码
    # fig2 = plotter.plot_time_sensitivity("TB1", "CA1", alpha=1.0, date=date)
    # plt.show()

    print("4. 算法对比...")
    # 在实际使用中，可以取消注释以下代码
    # fig3 = plotter.plot_algorithm_comparison("TB1", "CA1", time_obj)
    # plt.show()

    print("5. 性能基准测试...")
    test_generator = TestDataGenerator()
    test_cases = test_generator.get_performance_test_cases(10)
    # 在实际使用中，可以取消注释以下代码
    # fig4 = plotter.plot_performance_benchmark(test_cases)
    # plt.show()

    return plotter


def example_8_integration_and_export():
    """示例8: 集成和导出"""
    print("\n" + "=" * 60)
    print("示例8: 集成和导出")
    print("=" * 60)

    print("1. 创建完整的系统实例...")
    planner = PathPlanner()

    print("2. 执行复杂分析...")
    analysis = planner.analyze_route("TB1", "CA1")

    print(f"  • 分析路线: {analysis['start']} → {analysis['goal']}")
    print(f"  • 时间点数量: {analysis['time_range']['count']}")

    if analysis['analysis']:
        print("\n3. 导出分析结果到JSON...")
        # 转换datetime对象
        def datetime_serializer(obj):
            if isinstance(obj, datetime.datetime):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")

        json_output = json.dumps(analysis, indent=2, default=datetime_serializer, ensure_ascii=False)

        # 保存到文件
        output_file = "route_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_output)

        print(f"  • 分析结果已保存到: {output_file}")
        print(f"  • 文件大小: {len(json_output)} 字符")

        # 显示部分内容
        print("\n4. 显示部分分析结果:")
        sample = analysis['analysis'][0]
        print(f"  时间点: {sample['time_str']}")
        print(f"  高峰期: {sample['peak_period']}")
        print(f"  距离: {sample['path']['distance']:.1f}m")
        print(f"  拥堵成本: {sample['path']['congestion_cost']:.1f}")

    print("\n5. 生成完整系统报告...")
    campus_info = planner.get_campus_info()

    report = {
        "system_info": {
            "name": "FlowNav 校园动态导航系统",
            "version": "1.0.0",
            "generated_at": datetime.datetime.now().isoformat()
        },
        "campus_info": campus_info,
        "sample_analysis": analysis if 'analysis' in locals() else None
    }

    report_file = "system_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"  • 系统报告已保存到: {report_file}")

    return analysis


def example_9_custom_scenarios():
    """示例9: 自定义场景"""
    print("\n" + "=" * 60)
    print("示例9: 自定义场景")
    print("=" * 60)

    print("1. 定义自定义测试场景...")
    custom_scenarios = [
        {
            "name": "早餐高峰期到图书馆",
            "start": "DO1",  # 第一宿舍楼
            "goal": "LIB",   # 图书馆
            "time": datetime.datetime(2024, 5, 20, 7, 45),  # 早上7:45
            "alphas": [0, 1.0, 2.0],
            "description": "测试早餐后到图书馆的路线"
        },
        {
            "name": "体育课后到食堂",
            "start": "SP1",  # 田径场
            "goal": "CA1",   # 第一食堂
            "time": datetime.datetime(2024, 5, 20, 17, 0),  # 下午5:00
            "alphas": [0, 0.5, 1.0, 1.5],
            "description": "测试体育课后到食堂的路线（接近晚餐高峰期）"
        },
        {
            "name": "跨校区路线",
            "start": "GATE_W",  # 西门
            "goal": "GATE_E",   # 东门
            "time": datetime.datetime(2024, 5, 20, 15, 30),  # 下午3:30
            "alphas": [0, 1.0, 2.0],
            "description": "测试从西门到东门的跨校园路线"
        }
    ]

    print("2. 运行自定义场景...")
    planner = PathPlanner()

    for scenario in custom_scenarios:
        print(f"\n• {scenario['name']}:")
        print(f"  描述: {scenario['description']}")
        print(f"  时间: {scenario['time'].strftime('%H:%M')}")

        results = {}
        for alpha in scenario['alphas']:
            path = planner.plan_path(scenario['start'], scenario['goal'],
                                    alpha, scenario['time'])
            if path:
                results[alpha] = path
                print(f"  α={alpha}: 距离={path.total_distance:.1f}m, "
                      f"拥堵成本={path.congestion_cost:.1f}")

        # 分析最佳α值
        if results:
            best_by_cost = min(results.items(), key=lambda x: x[1].total_actual_cost)
            print(f"  推荐α值: {best_by_cost[0]} (成本最低)")

    return custom_scenarios


def main():
    """主函数"""
    try:
        print("FlowNav 校园动态导航系统 - 高级使用示例")
        print("=" * 60)

        # 运行高级示例
        example_1_custom_campus_map()
        example_2_custom_rule_engine()
        example_3_custom_graph_and_algorithm()
        example_4_custom_path_planner()
        example_5_batch_processing()
        example_6_visualization_advanced()
        example_7_comparison_analysis()
        example_8_integration_and_export()
        example_9_custom_scenarios()

        print("\n" + "=" * 60)
        print("所有高级示例完成!")
        print("=" * 60)

        print("\n高级功能总结:")
        print("1. 自定义校园地图和规则引擎")
        print("2. 批处理测试和性能分析")
        print("3. 高级可视化和对比分析")
        print("4. 数据导出和系统报告生成")
        print("5. 自定义场景和用例")

        print("\n进一步探索:")
        print("• 修改 data/campus_map.py 中的校园布局")
        print("• 调整 algorithm/rule_engine.py 中的高峰期规则")
        print("• 创建新的可视化图表类型")
        print("• 集成到Web应用或移动应用中")

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()