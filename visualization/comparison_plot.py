"""
对比分析图模块
生成路径对比分析图表，展示算法性能和效果
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from algorithm.models import PathComparison, PathResult
from algorithm.path_planner import PathPlanner
import datetime

# 设置中文字体，避免警告
try:
    # Windows常用中文字体
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'KaiTi', 'SimSun', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
except Exception as e:
    print(f"字体设置失败: {e}，中文字符可能显示为方框")


class ComparisonPlot:
    """对比分析图生成器"""

    def __init__(self, planner: Optional[PathPlanner] = None):
        """初始化"""
        self.planner = planner or PathPlanner()

    def plot_alpha_sensitivity(self, start: str, goal: str,
                              time_obj: datetime.datetime,
                              alpha_range: Tuple[float, float] = (0, 2.0),
                              step: float = 0.1,
                              save_path: Optional[str] = None) -> plt.Figure:
        """
        绘制α敏感性分析图

        展示不同α值对路径距离、成本、拥堵成本的影响
        """
        # 获取敏感性分析数据
        sensitivity = self.planner.algorithm.analyze_path_sensitivity(
            start, goal, alpha_range, step, time_obj
        )

        alphas = sensitivity["alphas"]
        distances = sensitivity["distances"]
        costs = sensitivity["costs"]
        congestion_costs = sensitivity["congestion_costs"]
        change_points = sensitivity["change_points"]

        # 创建图形
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        ax1, ax2, ax3, ax4 = axes.flat

        # 1. 距离 vs α
        ax1.plot(alphas, distances, 'b-o', linewidth=2, markersize=4)
        ax1.set_xlabel('α值', fontsize=12)
        ax1.set_ylabel('路径距离 (米)', fontsize=12)
        ax1.set_title('路径距离随α值变化', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3, linestyle='--')

        # 标记路径变化点
        for cp in change_points:
            ax1.axvline(x=cp["alpha"], color='r', linestyle='--', alpha=0.5, linewidth=1)

        # 2. 总成本 vs α
        ax2.plot(alphas, costs, 'g-s', linewidth=2, markersize=4)
        ax2.set_xlabel('α值', fontsize=12)
        ax2.set_ylabel('总成本', fontsize=12)
        ax2.set_title('总成本随α值变化', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, linestyle='--')

        # 3. 拥堵成本 vs α
        ax3.plot(alphas, congestion_costs, 'r-^', linewidth=2, markersize=4)
        ax3.set_xlabel('α值', fontsize=12)
        ax3.set_ylabel('拥堵成本', fontsize=12)
        ax3.set_title('拥堵成本随α值变化', fontsize=14, fontweight='bold')
        ax3.grid(True, alpha=0.3, linestyle='--')

        # 4. 距离 vs 拥堵成本（帕累托前沿）
        scatter = ax4.scatter(distances, congestion_costs, c=alphas,
                             cmap='viridis', s=50, alpha=0.7)
        ax4.set_xlabel('路径距离 (米)', fontsize=12)
        ax4.set_ylabel('拥堵成本', fontsize=12)
        ax4.set_title('距离 vs 拥堵成本 (颜色表示α值)', fontsize=14, fontweight='bold')
        ax4.grid(True, alpha=0.3, linestyle='--')

        # 添加颜色条
        cbar = plt.colorbar(scatter, ax=ax4)
        cbar.set_label('α值', fontsize=12)

        # 设置总标题
        time_str = time_obj.strftime("%Y-%m-%d %H:%M")
        fig.suptitle(f'α敏感性分析: {start} → {goal}\n时间: {time_str}',
                    fontsize=16, fontweight='bold')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"α敏感性分析图已保存到: {save_path}")

        return fig

    def plot_time_sensitivity(self, start: str, goal: str,
                             alpha: float = 1.0,
                             date: datetime.date = None,
                             save_path: Optional[str] = None) -> plt.Figure:
        """
        绘制时间敏感性分析图

        展示同一路线在不同时间的表现
        """
        if date is None:
            date = datetime.date.today()

        # 生成全天时间点
        time_points = []
        for hour in range(7, 23):  # 7:00-22:00
            for minute in [0, 30]:
                if hour == 22 and minute == 30:  # 22:30之后不包含
                    continue
                time_points.append(datetime.datetime.combine(date, datetime.time(hour, minute)))

        # 收集数据
        times = []
        distances = []
        costs = []
        congestion_costs = []
        peak_periods = []

        for time_obj in time_points:
            path = self.planner.plan_path(start, goal, alpha, time_obj)
            if path:
                times.append(time_obj)
                distances.append(path.total_distance)
                costs.append(path.total_actual_cost)
                congestion_costs.append(path.congestion_cost)

                # 获取高峰期信息
                peak_info = self.planner.rule_engine.get_peak_period_info(time_obj)
                peak_periods.append(peak_info["peak_period"])

        if not times:
            raise ValueError(f"在指定时间范围内未找到从 {start} 到 {goal} 的路径")

        # 创建图形
        fig, axes = plt.subplots(3, 1, figsize=(14, 12))
        ax1, ax2, ax3 = axes

        # 转换时间为小时（用于x轴）
        time_hours = [t.hour + t.minute/60 for t in times]

        # 1. 距离随时间变化
        ax1.plot(time_hours, distances, 'b-o', linewidth=2, markersize=4)
        ax1.set_xlabel('时间 (小时)', fontsize=12)
        ax1.set_ylabel('路径距离 (米)', fontsize=12)
        ax1.set_title('路径距离随时间变化', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.set_xlim(7, 22)

        # 设置x轴标签为时间
        hour_ticks = list(range(7, 23, 2))
        ax1.set_xticks(hour_ticks)
        ax1.set_xticklabels([f"{h}:00" for h in hour_ticks])

        # 2. 拥堵成本随时间变化
        ax2.plot(time_hours, congestion_costs, 'r-^', linewidth=2, markersize=4)
        ax2.set_xlabel('时间 (小时)', fontsize=12)
        ax2.set_ylabel('拥堵成本', fontsize=12)
        ax2.set_title('拥堵成本随时间变化', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.set_xlim(7, 22)
        ax2.set_xticks(hour_ticks)
        ax2.set_xticklabels([f"{h}:00" for h in hour_ticks])

        # 3. 高峰期标注
        # 创建高峰期颜色映射
        period_colors = {
            'off_peak': 'green',
            'lunch_peak': 'red',
            'dinner_peak': 'orange',
            'evening_study_peak': 'purple'
        }

        for i, period in enumerate(peak_periods):
            color = period_colors.get(period, 'gray')
            ax3.bar(time_hours[i], 1, width=0.05, color=color, alpha=0.7)

        ax3.set_xlabel('时间 (小时)', fontsize=12)
        ax3.set_ylabel('高峰期类型', fontsize=12)
        ax3.set_title('高峰期分布', fontsize=14, fontweight='bold')
        ax3.set_xlim(7, 22)
        ax3.set_ylim(0, 2)
        ax3.set_xticks(hour_ticks)
        ax3.set_xticklabels([f"{h}:00" for h in hour_ticks])
        ax3.set_yticks([])

        # 添加图例
        legend_patches = []
        for period, color in period_colors.items():
            if period in peak_periods:
                label = period.replace('_', ' ').title()
                patch = plt.Rectangle((0, 0), 1, 1, color=color, alpha=0.7)
                legend_patches.append((patch, label))

        if legend_patches:
            patches, labels = zip(*legend_patches)
            ax3.legend(patches, labels, loc='upper right')

        # 设置总标题
        date_str = date.strftime("%Y-%m-%d")
        fig.suptitle(f'时间敏感性分析: {start} → {goal} (α={alpha})\n日期: {date_str}',
                    fontsize=16, fontweight='bold')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"时间敏感性分析图已保存到: {save_path}")

        return fig

    def plot_algorithm_comparison(self, start: str, goal: str,
                                 time_obj: datetime.datetime,
                                 save_path: Optional[str] = None) -> plt.Figure:
        """
        绘制算法对比图

        对比动态惩罚A*算法与传统最短路径算法
        """
        # 获取传统最短路径（α=0）
        traditional_path = self.planner.plan_path(start, goal, alpha=0, time=time_obj)

        # 获取动态路径（α=1.0，中等偏好）
        dynamic_path = self.planner.plan_path(start, goal, alpha=1.0, time=time_obj)

        if not traditional_path or not dynamic_path:
            raise ValueError("无法获取对比路径")

        # 准备对比数据
        algorithms = ['传统最短路径\n(α=0)', '动态惩罚A*\n(α=1.0)']
        distances = [traditional_path.total_distance, dynamic_path.total_distance]
        costs = [traditional_path.total_actual_cost, dynamic_path.total_actual_cost]
        congestion_costs = [traditional_path.congestion_cost, dynamic_path.congestion_cost]
        avg_congestion = [traditional_path.average_congestion, dynamic_path.average_congestion]

        # 计算改进百分比
        distance_diff = ((dynamic_path.total_distance - traditional_path.total_distance) /
                        traditional_path.total_distance * 100)
        cost_diff = ((dynamic_path.total_actual_cost - traditional_path.total_actual_cost) /
                    traditional_path.total_actual_cost * 100)
        congestion_diff = ((dynamic_path.congestion_cost - traditional_path.congestion_cost) /
                          traditional_path.congestion_cost * 100 if traditional_path.congestion_cost > 0 else 0)

        # 创建图形
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        ax1, ax2, ax3, ax4 = axes.flat

        x_pos = np.arange(len(algorithms))

        # 1. 距离对比
        bars1 = ax1.bar(x_pos, distances, color=['#1f77b4', '#ff7f0e'], alpha=0.8)
        ax1.set_xlabel('算法', fontsize=12)
        ax1.set_ylabel('路径距离 (米)', fontsize=12)
        ax1.set_title('路径距离对比', fontsize=14, fontweight='bold')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(algorithms, fontsize=11)
        ax1.grid(True, alpha=0.3, axis='y')

        # 添加数值标签
        for bar, distance in zip(bars1, distances):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{distance:.1f}', ha='center', va='bottom', fontsize=10)

        # 2. 拥堵成本对比
        bars2 = ax2.bar(x_pos, congestion_costs, color=['#1f77b4', '#ff7f0e'], alpha=0.8)
        ax2.set_xlabel('算法', fontsize=12)
        ax2.set_ylabel('拥堵成本', fontsize=12)
        ax2.set_title('拥堵成本对比', fontsize=14, fontweight='bold')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(algorithms, fontsize=11)
        ax2.grid(True, alpha=0.3, axis='y')

        for bar, cost in zip(bars2, congestion_costs):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{cost:.1f}', ha='center', va='bottom', fontsize=10)

        # 3. 平均拥堵系数对比
        bars3 = ax3.bar(x_pos, avg_congestion, color=['#1f77b4', '#ff7f0e'], alpha=0.8)
        ax3.set_xlabel('算法', fontsize=12)
        ax3.set_ylabel('平均拥堵系数', fontsize=12)
        ax3.set_title('平均拥堵系数对比', fontsize=14, fontweight='bold')
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(algorithms, fontsize=11)
        ax3.grid(True, alpha=0.3, axis='y')
        ax3.axhline(y=1.0, color='r', linestyle='--', alpha=0.5, label='畅通基准')

        for bar, congestion in zip(bars3, avg_congestion):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                    f'{congestion:.2f}', ha='center', va='bottom', fontsize=10)

        ax3.legend()

        # 4. 改进百分比雷达图
        categories = ['距离变化', '成本变化', '拥堵变化']
        N = len(categories)

        # 计算角度
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # 闭合图形

        # 准备数据（注意：负值表示改进）
        traditional_values = [0, 0, 0]  # 基准
        dynamic_values = [-distance_diff, -cost_diff, -congestion_diff]

        # 创建子图
        ax4 = fig.add_subplot(224, polar=True)
        ax4.set_theta_offset(np.pi / 2)
        ax4.set_theta_direction(-1)

        # 绘制传统算法（基准线）
        traditional_values += traditional_values[:1]
        ax4.plot(angles, traditional_values, 'o-', linewidth=2,
                label='传统算法 (基准)', color='#1f77b4')
        ax4.fill(angles, traditional_values, alpha=0.25, color='#1f77b4')

        # 绘制动态算法
        dynamic_values += dynamic_values[:1]
        ax4.plot(angles, dynamic_values, 'o-', linewidth=2,
                label='动态算法', color='#ff7f0e')
        ax4.fill(angles, dynamic_values, alpha=0.25, color='#ff7f0e')

        # 设置极坐标属性
        ax4.set_xticks(angles[:-1])
        ax4.set_xticklabels(categories, fontsize=11)
        ax4.set_ylim(min(min(traditional_values), min(dynamic_values)) - 10,
                    max(max(traditional_values), max(dynamic_values)) + 10)
        ax4.yaxis.grid(True)
        ax4.xaxis.grid(True)
        ax4.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))

        # 设置总标题
        time_str = time_obj.strftime("%Y-%m-%d %H:%M")
        fig.suptitle(f'算法性能对比: {start} → {goal}\n时间: {time_str}',
                    fontsize=16, fontweight='bold')

        # 添加总结文本框
        summary_text = (
            f"对比总结:\n"
            f"• 距离变化: {distance_diff:+.1f}%\n"
            f"• 成本变化: {cost_diff:+.1f}%\n"
            f"• 拥堵变化: {congestion_diff:+.1f}%\n"
            f"• 路径节点数:\n"
            f"  传统: {len(traditional_path.nodes)}\n"
            f"  动态: {len(dynamic_path.nodes)}"
        )

        fig.text(0.02, 0.02, summary_text, fontsize=10,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"算法对比图已保存到: {save_path}")

        return fig

    def plot_performance_benchmark(self, test_cases: List[Dict[str, Any]],
                                  save_path: Optional[str] = None) -> plt.Figure:
        """
        绘制性能基准测试图

        展示算法在不同测试用例下的性能
        """
        if not test_cases:
            raise ValueError("测试用例列表为空")

        import time

        execution_times = []
        path_lengths = []
        node_counts = []
        test_ids = []

        for i, test_case in enumerate(test_cases[:10]):  # 最多10个测试用例
            start = test_case["start"]
            goal = test_case["goal"]
            time_obj = test_case.get("time", datetime.datetime.now())
            alpha = test_case.get("alpha", 1.0)

            # 测量执行时间
            start_time = time.time()
            path = self.planner.plan_path(start, goal, alpha, time_obj)
            end_time = time.time()

            if path:
                execution_times.append((end_time - start_time) * 1000)  # 转换为毫秒
                path_lengths.append(path.total_distance)
                node_counts.append(len(path.nodes))
                test_ids.append(f"Test{i+1}")
            else:
                # 如果没有找到路径，使用占位值
                execution_times.append(0)
                path_lengths.append(0)
                node_counts.append(0)
                test_ids.append(f"Test{i+1}")

        # 创建图形
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        ax1, ax2, ax3, ax4 = axes.flat

        x_pos = np.arange(len(test_ids))

        # 1. 执行时间
        bars1 = ax1.bar(x_pos, execution_times, color='skyblue', alpha=0.8)
        ax1.set_xlabel('测试用例', fontsize=12)
        ax1.set_ylabel('执行时间 (毫秒)', fontsize=12)
        ax1.set_title('算法执行时间', fontsize=14, fontweight='bold')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(test_ids, fontsize=10, rotation=45)
        ax1.grid(True, alpha=0.3, axis='y')

        # 添加平均时间线
        avg_time = np.mean(execution_times)
        ax1.axhline(y=avg_time, color='r', linestyle='--', alpha=0.7,
                   label=f'平均: {avg_time:.2f}ms')
        ax1.legend()

        # 2. 路径长度分布
        ax2.hist(path_lengths, bins=10, color='lightgreen', alpha=0.8, edgecolor='black')
        ax2.set_xlabel('路径长度 (米)', fontsize=12)
        ax2.set_ylabel('频数', fontsize=12)
        ax2.set_title('路径长度分布', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')

        # 3. 节点数量分布
        unique_nodes = sorted(set(node_counts))
        node_freq = [node_counts.count(n) for n in unique_nodes]

        bars3 = ax3.bar(unique_nodes, node_freq, color='lightcoral', alpha=0.8, width=0.6)
        ax3.set_xlabel('路径节点数', fontsize=12)
        ax3.set_ylabel('频数', fontsize=12)
        ax3.set_title('路径节点数分布', fontsize=14, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')

        # 4. 执行时间 vs 路径长度散点图
        scatter = ax4.scatter(path_lengths, execution_times, c=node_counts,
                             cmap='viridis', s=100, alpha=0.7)
        ax4.set_xlabel('路径长度 (米)', fontsize=12)
        ax4.set_ylabel('执行时间 (毫秒)', fontsize=12)
        ax4.set_title('执行时间 vs 路径长度 (颜色表示节点数)', fontsize=14, fontweight='bold')
        ax4.grid(True, alpha=0.3)

        # 添加颜色条
        cbar = plt.colorbar(scatter, ax=ax4)
        cbar.set_label('节点数', fontsize=12)

        # 设置总标题
        fig.suptitle(f'算法性能基准测试\n测试用例数: {len(test_cases)}',
                    fontsize=16, fontweight='bold')

        # 添加性能摘要
        summary_text = (
            f"性能摘要:\n"
            f"• 平均执行时间: {np.mean(execution_times):.2f}ms\n"
            f"• 最长执行时间: {np.max(execution_times):.2f}ms\n"
            f"• 最短执行时间: {np.min(execution_times):.2f}ms\n"
            f"• 平均路径长度: {np.mean(path_lengths):.1f}m\n"
            f"• 平均节点数: {np.mean(node_counts):.1f}"
        )

        fig.text(0.02, 0.02, summary_text, fontsize=10,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"性能基准测试图已保存到: {save_path}")

        return fig


def plot_examples():
    """绘制示例图表"""
    import datetime

    plotter = ComparisonPlot()
    planner = PathPlanner()

    print("1. 绘制α敏感性分析图...")
    time_obj = datetime.datetime(2024, 5, 20, 12, 0)  # 午餐高峰期
    fig1 = plotter.plot_alpha_sensitivity("TB1", "CA1", time_obj,
                                         alpha_range=(0, 2.0), step=0.2)
    plt.show()

    print("2. 绘制时间敏感性分析图...")
    date = datetime.date(2024, 5, 20)
    fig2 = plotter.plot_time_sensitivity("TB1", "CA1", alpha=1.0, date=date)
    plt.show()

    print("3. 绘制算法对比图...")
    fig3 = plotter.plot_algorithm_comparison("TB1", "CA1", time_obj)
    plt.show()

    print("4. 绘制性能基准测试图...")
    from data.test_data import TestDataGenerator
    test_generator = TestDataGenerator()
    test_cases = test_generator.get_performance_test_cases(20)
    fig4 = plotter.plot_performance_benchmark(test_cases[:8])  # 前8个测试用例
    plt.show()


if __name__ == "__main__":
    plot_examples()