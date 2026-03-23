"""
基础使用示例
展示FlowNav校园动态导航系统的基本使用方法
"""

import datetime
from algorithm.path_planner import PathPlanner
from algorithm.models import PathResult


def basic_path_planning():
    """基础路径规划示例"""
    print("=" * 60)
    print("FlowNav 校园动态导航系统 - 基础使用示例")
    print("=" * 60)

    # 创建路径规划器
    planner = PathPlanner()
    print("✓ 路径规划器初始化完成")

    # 获取校园信息
    campus_info = planner.get_campus_info()
    print(f"\n校园地图信息:")
    print(f"  • 节点总数: {campus_info['graph_info']['node_count']}")
    print(f"  • 边总数: {campus_info['graph_info']['edge_count']}")
    print(f"  • 图是否连通: {campus_info['graph_info']['is_connected']}")

    # 显示关键节点
    key_nodes = campus_info['key_nodes']
    print(f"\n关键节点:")
    for category, nodes in key_nodes.items():
        names = [n['name'] for n in nodes]
        print(f"  • {category}: {', '.join(names)}")

    return planner


def example_1_simple_path(planner):
    """示例1: 简单路径规划"""
    print("\n" + "=" * 60)
    print("示例1: 简单路径规划")
    print("=" * 60)

    # 使用当前时间
    current_time = datetime.datetime.now()
    print(f"当前时间: {current_time.strftime('%Y-%m-%d %H:%M')}")

    # 规划路径（默认α=1.0）
    start = "第一教学楼"  # 支持节点名称
    goal = "第一食堂"     # 支持节点名称

    print(f"\n规划路径: {start} → {goal} (α=1.0)")

    path = planner.plan_path(start, goal, alpha=1.0, time=current_time)

    if path:
        print(f"✓ 路径规划成功!")
        print(f"\n路径摘要:")
        print(f"  • 节点序列: {path.nodes}")
        print(f"  • 总距离: {path.total_distance:.1f} 米")
        print(f"  • 总成本: {path.total_actual_cost:.1f}")
        print(f"  • 拥堵成本: {path.congestion_cost:.1f}")
        print(f"  • 平均拥挤系数: {path.average_congestion:.2f}")
        print(f"  • 节点数量: {len(path.nodes)}")
        print(f"  • 边数量: {len(path.edges)}")

        # 显示详细路径段
        print(f"\n详细路径段:")
        for i, segment in enumerate(path.segments, 1):
            print(f"  {i:2d}. {segment.edge.from_node} → {segment.edge.to_node}")
            print(f"       距离: {segment.distance:.1f}m")
            print(f"       拥挤系数: {segment.congestion_factor:.1f}")
            print(f"       实际成本: {segment.actual_cost:.1f}")
    else:
        print("✗ 未找到路径")

    return path


def example_2_alpha_comparison(planner):
    """示例2: 不同α值对比"""
    print("\n" + "=" * 60)
    print("示例2: 不同α值路径对比")
    print("=" * 60)

    # 设置特定时间（午餐高峰期）
    lunch_time = datetime.datetime(2024, 5, 20, 12, 0)
    print(f"测试时间: {lunch_time.strftime('%Y-%m-%d %H:%M')} (午餐高峰期)")

    start = "TB1"  # 使用节点ID
    goal = "CA1"

    print(f"\n对比路径: {start} → {goal}")

    # 测试不同α值
    alpha_values = [0, 0.5, 1.0, 1.5, 2.0]

    print(f"\nα值对比 (0=只关注距离, 越大越避开拥堵):")
    print("α值 | 路径距离 | 总成本 | 拥堵成本 | 平均拥堵 | 节点序列")
    print("-" * 80)

    results = {}
    for alpha in alpha_values:
        path = planner.plan_path(start, goal, alpha, lunch_time)
        if path:
            results[alpha] = path
            print(f"{alpha:3.1f} | {path.total_distance:8.1f}m | {path.total_actual_cost:7.1f} | "
                  f"{path.congestion_cost:8.1f} | {path.average_congestion:8.2f} | {path.nodes}")

    # 分析最佳路径
    if results:
        print(f"\n分析:")
        # 按距离最短
        best_by_distance = min(results.items(), key=lambda x: x[1].total_distance)
        print(f"  • 距离最短: α={best_by_distance[0]}, 距离={best_by_distance[1].total_distance:.1f}m")

        # 按成本最低
        best_by_cost = min(results.items(), key=lambda x: x[1].total_actual_cost)
        print(f"  • 成本最低: α={best_by_cost[0]}, 成本={best_by_cost[1].total_actual_cost:.1f}")

        # 按拥堵最小
        if len(results) > 1:
            # 排除α=0的情况（可能没有拥堵成本）
            results_with_congestion = {a: p for a, p in results.items() if a > 0}
            if results_with_congestion:
                best_by_congestion = min(results_with_congestion.items(),
                                        key=lambda x: x[1].congestion_cost)
                print(f"  • 拥堵最小: α={best_by_congestion[0]}, "
                      f"拥堵成本={best_by_congestion[1].congestion_cost:.1f}")

    return results


def example_3_time_sensitivity(planner):
    """示例3: 时间敏感性分析"""
    print("\n" + "=" * 60)
    print("示例3: 时间敏感性分析")
    print("=" * 60)

    start = "图书馆"
    goal = "第一宿舍楼"
    alpha = 1.0

    print(f"分析路线: {start} → {goal} (α={alpha})")
    print(f"测试不同时间点的路径变化:")

    # 定义不同时间段
    time_points = [
        ("平峰期", datetime.datetime(2024, 5, 20, 14, 30)),
        ("午餐高峰期", datetime.datetime(2024, 5, 20, 12, 0)),
        ("晚餐高峰期", datetime.datetime(2024, 5, 20, 18, 0)),
        ("晚自习高峰期", datetime.datetime(2024, 5, 20, 21, 45)),
    ]

    previous_path = None
    path_changes = 0

    for time_name, time_obj in time_points:
        path = planner.plan_path(start, goal, alpha, time_obj)

        if path:
            peak_info = planner.rule_engine.get_peak_period_info(time_obj)

            print(f"\n{time_name} ({time_obj.strftime('%H:%M')}):")
            print(f"  • 高峰期状态: {peak_info['description']}")
            print(f"  • 路径距离: {path.total_distance:.1f}m")
            print(f"  • 拥堵成本: {path.congestion_cost:.1f}")
            print(f"  • 节点序列: {path.nodes}")

            if previous_path and path.nodes != previous_path.nodes:
                path_changes += 1
                print(f"  • 注意: 路径发生变化!")

            previous_path = path
        else:
            print(f"\n{time_name}: 未找到路径")

    print(f"\n总结: 在 {len(time_points)} 个时间点中，路径发生了 {path_changes} 次变化")


def example_4_path_details_and_export(planner):
    """示例4: 路径详情和导出"""
    print("\n" + "=" * 60)
    print("示例4: 路径详情获取和报告导出")
    print("=" * 60)

    # 创建一个路径
    time_obj = datetime.datetime(2024, 5, 20, 12, 0)
    path = planner.plan_path("第一教学楼", "第一食堂", alpha=1.0, time=time_obj)

    if not path:
        print("未找到路径，跳过此示例")
        return

    print("1. 获取路径详细信息:")
    details = planner.get_path_details(path)

    print(f"   • 摘要信息: {details['summary']}")
    print(f"   • 节点数量: {len(details['node_details'])}")
    print(f"   • 边数量: {len(details['edge_sequence'])}")
    print(f"   • 时间段信息: {details['time_info']['description']}")

    print("\n2. 显示节点详情 (前3个):")
    for i, node in enumerate(details['node_details'][:3], 1):
        print(f"   {i}. {node['name']} ({node['id']})")
        print(f"       类型: {node['type']}")
        print(f"       坐标: {node['coordinates']}")

    print("\n3. 导出文本报告:")
    text_report = planner.export_path_report(path, "text")
    # 只显示报告的前15行
    lines = text_report.split('\n')[:15]
    print('\n'.join(lines))
    print("...")

    print("\n4. 导出JSON报告:")
    json_report = planner.export_path_report(path, "json")
    print(f"  JSON报告长度: {len(json_report)} 字符")
    print("  (可使用json.loads()解析)")

    return details


def example_5_advanced_features(planner):
    """示例5: 高级功能"""
    print("\n" + "=" * 60)
    print("示例5: 高级功能")
    print("=" * 60)

    print("1. 路线分析 (全天不同时间):")
    analysis = planner.analyze_route("TB1", "CA1")

    print(f"   • 分析路线: {analysis['start']} → {analysis['goal']}")
    print(f"   • 时间点数量: {analysis['time_range']['count']}")

    if analysis['analysis']:
        sample = analysis['analysis'][0]
        print(f"   • 示例时间点: {sample['time_str']}")
        print(f"     高峰期: {sample['peak_period']}")
        print(f"     距离: {sample['path']['distance']:.1f}m")
        print(f"     拥堵成本: {sample['path']['congestion_cost']:.1f}")

    print("\n2. 查找替代路线:")
    time_obj = datetime.datetime(2024, 5, 20, 12, 0)
    alternatives = planner.find_alternative_routes("TB1", "CA1",
                                                  alpha=1.0,
                                                  time=time_obj,
                                                  max_alternatives=2)

    print(f"  找到 {len(alternatives)} 条替代路线:")
    for i, alt_path in enumerate(alternatives, 1):
        print(f"  替代路线 {i}:")
        print(f"    • 节点序列: {alt_path.nodes}")
        print(f"    • 距离: {alt_path.total_distance:.1f}m")
        print(f"    • 拥堵成本: {alt_path.congestion_cost:.1f}")

    print("\n3. 清空缓存:")
    planner.clear_cache()
    print("  ✓ 路径缓存已清空")


def main():
    """主函数"""
    try:
        # 初始化
        planner = basic_path_planning()

        # 运行示例
        example_1_simple_path(planner)
        example_2_alpha_comparison(planner)
        example_3_time_sensitivity(planner)
        example_4_path_details_and_export(planner)
        example_5_advanced_features(planner)

        print("\n" + "=" * 60)
        print("所有示例完成!")
        print("=" * 60)

        print("\n下一步建议:")
        print("1. 运行测试: python -m pytest tests/")
        print("2. 查看可视化: python -m visualization.path_visualizer")
        print("3. 查看对比分析: python -m visualization.comparison_plot")
        print("4. 探索更多功能: 查看API文档")

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()