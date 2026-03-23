#!/usr/bin/env python3
"""
FlowNav 校园动态导航系统 - 主程序入口
"""

import sys
import argparse
import datetime
from algorithm.path_planner import PathPlanner, default_planner


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="FlowNav 校园动态导航系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s plan --start "第一教学楼" --goal "第一食堂"
  %(prog)s plan --start TB1 --goal CA1 --alpha 1.5 --time "12:00"
  %(prog)s compare --start TB1 --goal CA1 --alphas 0,0.5,1.0,1.5,2.0
  %(prog)s info
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # plan 子命令：规划路径
    plan_parser = subparsers.add_parser('plan', help='规划路径')
    plan_parser.add_argument('--start', required=True, help='起点节点ID或名称')
    plan_parser.add_argument('--goal', required=True, help='终点节点ID或名称')
    plan_parser.add_argument('--alpha', type=float, default=1.0, help='用户偏好权重α (默认: 1.0)')
    plan_parser.add_argument('--time', help='规划时间 (格式: "YYYY-MM-DD HH:MM" 或 "HH:MM"，默认: 当前时间)')
    plan_parser.add_argument('--output', choices=['text', 'json', 'detailed'], default='text',
                            help='输出格式 (默认: text)')

    # compare 子命令：比较路径
    compare_parser = subparsers.add_parser('compare', help='比较不同α值的路径')
    compare_parser.add_argument('--start', required=True, help='起点节点ID或名称')
    compare_parser.add_argument('--goal', required=True, help='终点节点ID或名称')
    compare_parser.add_argument('--alphas', default='0,0.5,1.0,1.5,2.0',
                               help='α值列表，逗号分隔 (默认: "0,0.5,1.0,1.5,2.0")')
    compare_parser.add_argument('--time', help='规划时间 (格式: "YYYY-MM-DD HH:MM" 或 "HH:MM"，默认: 当前时间)')

    # info 子命令：显示系统信息
    info_parser = subparsers.add_parser('info', help='显示系统信息')

    # analyze 子命令：分析路线
    analyze_parser = subparsers.add_parser('analyze', help='分析路线在不同时间点的表现')
    analyze_parser.add_argument('--start', required=True, help='起点节点ID或名称')
    analyze_parser.add_argument('--goal', required=True, help='终点节点ID或名称')
    analyze_parser.add_argument('--alpha', type=float, default=1.0, help='用户偏好权重α (默认: 1.0)')
    analyze_parser.add_argument('--date', help='分析日期 (格式: "YYYY-MM-DD"，默认: 今天)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        # 创建路径规划器
        planner = default_planner

        if args.command == 'info':
            # 显示系统信息
            info = planner.get_campus_info()
            print("=" * 60)
            print("FlowNav 校园动态导航系统")
            print("=" * 60)

            graph_info = info['graph_info']
            print(f"\n校园地图信息:")
            print(f"  • 节点总数: {graph_info['node_count']}")
            print(f"  • 边总数: {graph_info['edge_count']}")
            print(f"  • 图是否连通: {graph_info['is_connected']}")

            print(f"\n关键节点:")
            key_nodes = info['key_nodes']
            for category, nodes in key_nodes.items():
                names = [n['name'] for n in nodes[:3]]  # 只显示前3个
                if len(nodes) > 3:
                    names.append(f"...等{len(nodes)}个")
                print(f"  • {category}: {', '.join(names)}")

            print(f"\n算法信息:")
            algo_info = info['algorithm_info']
            print(f"  • 名称: {algo_info['name']}")
            print(f"  • 公式: {algo_info['formula']}")
            print(f"  • 描述: {algo_info['description']}")

            print(f"\n使用示例:")
            print("  python main.py plan --start '第一教学楼' --goal '第一食堂'")
            print("  python main.py compare --start TB1 --goal CA1 --alphas '0,1.0,2.0'")
            print("  python main.py analyze --start '图书馆' --goal '第一宿舍楼'")

        elif args.command == 'plan':
            # 解析时间
            if args.time:
                try:
                    if ' ' in args.time:
                        time_obj = datetime.datetime.strptime(args.time, '%Y-%m-%d %H:%M')
                    else:
                        # 只有时间，使用今天日期
                        today = datetime.date.today()
                        time_str = f"{today} {args.time}"
                        time_obj = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M')
                except ValueError:
                    print(f"错误: 时间格式不正确 '{args.time}'，请使用 'YYYY-MM-DD HH:MM' 或 'HH:MM'")
                    return 1
            else:
                time_obj = datetime.datetime.now()

            # 规划路径
            path = planner.plan_path(args.start, args.goal, args.alpha, time_obj)

            if not path:
                print(f"错误: 未找到从 '{args.start}' 到 '{args.goal}' 的路径")
                return 1

            if args.output == 'text':
                # 文本输出
                print("=" * 60)
                print("路径规划结果")
                print("=" * 60)
                print(f"起点: {args.start}")
                print(f"终点: {args.goal}")
                print(f"规划时间: {time_obj.strftime('%Y-%m-%d %H:%M')}")
                print(f"α参数: {args.alpha}")
                print(f"高峰期状态: {planner.rule_engine.get_peak_period_info(time_obj)['description']}")
                print()
                print(f"路径节点序列: {' → '.join(path.nodes)}")
                print()
                print(f"统计信息:")
                print(f"  • 总距离: {path.total_distance:.1f} 米")
                print(f"  • 总成本: {path.total_actual_cost:.1f}")
                print(f"  • 拥堵成本: {path.congestion_cost:.1f}")
                print(f"  • 平均拥挤系数: {path.average_congestion:.2f}")
                print(f"  • 节点数量: {len(path.nodes)}")
                print(f"  • 边数量: {len(path.edges)}")

                if path.segments:
                    print()
                    print(f"详细路径段:")
                    for i, segment in enumerate(path.segments, 1):
                        print(f"  {i:2d}. {segment.edge.from_node} → {segment.edge.to_node}")
                        print(f"       距离: {segment.distance:.1f}m")
                        print(f"       拥挤系数: {segment.congestion_factor:.1f}")
                        print(f"       实际成本: {segment.actual_cost:.1f}")

            elif args.output == 'json':
                # JSON输出
                import json
                details = planner.get_path_details(path)
                print(json.dumps(details, indent=2, ensure_ascii=False))

            elif args.output == 'detailed':
                # 详细报告
                report = planner.export_path_report(path, 'text')
                print(report)

        elif args.command == 'compare':
            # 解析α值
            try:
                alphas = [float(a.strip()) for a in args.alphas.split(',')]
            except ValueError:
                print(f"错误: α值格式不正确 '{args.alphas}'，请使用逗号分隔的数字，如 '0,0.5,1.0,1.5,2.0'")
                return 1

            # 解析时间
            if args.time:
                try:
                    if ' ' in args.time:
                        time_obj = datetime.datetime.strptime(args.time, '%Y-%m-%d %H:%M')
                    else:
                        today = datetime.date.today()
                        time_str = f"{today} {args.time}"
                        time_obj = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M')
                except ValueError:
                    print(f"错误: 时间格式不正确 '{args.time}'")
                    return 1
            else:
                time_obj = datetime.datetime.now()

            # 比较路径
            comparison = planner.compare_paths(args.start, args.goal, alphas, time_obj)

            print("=" * 60)
            print("路径对比结果")
            print("=" * 60)
            print(f"起点: {args.start}")
            print(f"终点: {args.goal}")
            print(f"规划时间: {time_obj.strftime('%Y-%m-%d %H:%M')}")
            print(f"高峰期状态: {planner.rule_engine.get_peak_period_info(time_obj)['description']}")
            print()

            print(f"{'α值':<6} {'距离(m)':<10} {'总成本':<10} {'拥堵成本':<12} {'节点序列'}")
            print("-" * 80)

            for alpha in sorted(comparison.comparisons.keys()):
                path = comparison.comparisons[alpha]
                # 缩短节点序列显示
                nodes_str = str(path.nodes)
                if len(nodes_str) > 30:
                    nodes_str = nodes_str[:27] + "..."

                print(f"{alpha:<6.1f} {path.total_distance:<10.1f} "
                      f"{path.total_actual_cost:<10.1f} {path.congestion_cost:<12.1f} {nodes_str}")

            print()
            print("最佳路径:")
            best_by_distance = comparison.get_best_by("total_distance")
            best_by_cost = comparison.get_best_by("total_actual_cost")
            print(f"  • 距离最短: α={best_by_distance[0]}, 距离={best_by_distance[1].total_distance:.1f}m")
            print(f"  • 成本最低: α={best_by_cost[0]}, 成本={best_by_cost[1].total_actual_cost:.1f}")

        elif args.command == 'analyze':
            # 解析日期
            if args.date:
                try:
                    date_obj = datetime.datetime.strptime(args.date, '%Y-%m-%d').date()
                except ValueError:
                    print(f"错误: 日期格式不正确 '{args.date}'，请使用 'YYYY-MM-DD'")
                    return 1
            else:
                date_obj = datetime.date.today()

            # 生成时间点（全天，每2小时）
            time_points = []
            for hour in range(8, 22, 2):  # 8:00-20:00，每2小时
                time_points.append(datetime.datetime.combine(date_obj, datetime.time(hour, 0)))

            # 分析路线
            analysis = planner.analyze_route(args.start, args.goal, time_points)

            print("=" * 60)
            print("路线时间敏感性分析")
            print("=" * 60)
            print(f"路线: {args.start} → {args.goal} (α={args.alpha})")
            print(f"分析日期: {date_obj}")
            print(f"时间点数量: {len(time_points)}")
            print()

            print(f"{'时间':<8} {'高峰期':<12} {'距离(m)':<10} {'拥堵成本':<12} {'节点数':<8}")
            print("-" * 60)

            total_distance = 0
            total_congestion = 0
            count = 0

            for result in analysis['analysis']:
                path_info = result['path']
                print(f"{result['time_str']:<8} {result['peak_period']:<12} "
                      f"{path_info['distance']:<10.1f} {path_info['congestion_cost']:<12.1f} "
                      f"{len(path_info['nodes']):<8}")

                total_distance += path_info['distance']
                total_congestion += path_info['congestion_cost']
                count += 1

            if count > 0:
                print("-" * 60)
                print(f"{'平均':<8} {'':<12} {total_distance/count:<10.1f} "
                      f"{total_congestion/count:<12.1f} {'':<8}")

            # 统计高峰期vs平峰期
            peak_stats = {'peak': {'count': 0, 'total_congestion': 0},
                         'off_peak': {'count': 0, 'total_congestion': 0}}

            for result in analysis['analysis']:
                if result['is_peak']:
                    key = 'peak'
                else:
                    key = 'off_peak'
                peak_stats[key]['count'] += 1
                peak_stats[key]['total_congestion'] += result['path']['congestion_cost']

            print()
            print("高峰期对比:")
            for key, stats in peak_stats.items():
                if stats['count'] > 0:
                    avg = stats['total_congestion'] / stats['count']
                    name = "高峰期" if key == 'peak' else "平峰期"
                    print(f"  • {name}: {stats['count']}个时间点，平均拥堵成本: {avg:.1f}")

        return 0

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())