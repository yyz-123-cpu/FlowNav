"""
路径可视化模块
使用matplotlib绘制校园地图、路径和拥堵情况
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from algorithm.models import PathResult, NodeType, RoadType
from algorithm.graph_builder import CampusGraph
from algorithm.path_planner import PathPlanner

# 设置中文字体，避免警告
try:
    # Windows常用中文字体
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'KaiTi', 'SimSun', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
except Exception as e:
    print(f"字体设置失败: {e}，中文字符可能显示为方框")


class PathVisualizer:
    """路径可视化器"""

    def __init__(self, planner: Optional[PathPlanner] = None):
        """初始化可视化器"""
        self.planner = planner or PathPlanner()
        self.graph = self.planner.graph

        # 颜色配置
        self.node_colors = {
            NodeType.TEACHING_BUILDING: '#1f77b4',  # 蓝色
            NodeType.CAFETERIA: '#d62728',          # 红色
            NodeType.DORMITORY: '#2ca02c',          # 绿色
            NodeType.LIBRARY: '#9467bd',            # 紫色
            NodeType.CROSSROAD: '#7f7f7f',          # 灰色
            NodeType.GATE: '#8c564b',               # 棕色
            NodeType.SPORTS_FIELD: '#e377c2',       # 粉色
            NodeType.OTHER: '#bcbd22'               # 黄绿色
        }

        self.road_colors = {
            RoadType.MAIN_ROAD: '#000000',          # 黑色
            RoadType.SIDE_ROAD: '#666666',          # 深灰
            RoadType.PATH: '#999999',               # 浅灰
            RoadType.BRIDGE: '#1e90ff',             # 道奇蓝
            RoadType.TUNNEL: '#8b4513'              # 马鞍棕
        }

        # 拥堵颜色映射
        self.congestion_cmap = LinearSegmentedColormap.from_list(
            'congestion',
            ['#00ff00', '#ffff00', '#ff9900', '#ff0000']  # 绿->黄->橙->红
        )

    def plot_campus_map(self, save_path: Optional[str] = None,
                       show_labels: bool = True) -> plt.Figure:
        """绘制校园地图"""
        fig, ax = plt.subplots(figsize=(14, 12))

        # 绘制边
        self._plot_edges(ax)

        # 绘制节点
        self._plot_nodes(ax, show_labels)

        # 设置图形属性
        ax.set_title("校园路网图", fontsize=16, fontweight='bold')
        ax.set_xlabel("X坐标 (米)", fontsize=12)
        ax.set_ylabel("Y坐标 (米)", fontsize=12)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.axis('equal')

        # 添加图例
        self._add_legend(ax)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"校园地图已保存到: {save_path}")

        return fig

    def plot_path(self, path_result: PathResult,
                  save_path: Optional[str] = None,
                  show_congestion: bool = True) -> plt.Figure:
        """绘制单条路径"""
        fig, ax = plt.subplots(figsize=(14, 12))

        # 绘制校园地图背景
        self._plot_edges(ax, alpha=0.3)
        self._plot_nodes(ax, show_labels=False, alpha=0.5)

        # 高亮显示路径
        self._highlight_path(ax, path_result, show_congestion)

        # 设置图形属性
        title = f"路径规划: {path_result.nodes[0]} → {path_result.nodes[-1]}"
        if show_congestion:
            title += f" (α={path_result.alpha}, 拥堵成本: {path_result.congestion_cost:.1f})"

        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel("X坐标 (米)", fontsize=12)
        ax.set_ylabel("Y坐标 (米)", fontsize=12)
        ax.grid(True, alpha=0.2, linestyle='--')
        ax.axis('equal')

        # 添加图例
        self._add_path_legend(ax, path_result, show_congestion)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"路径图已保存到: {save_path}")

        return fig

    def plot_path_comparison(self, comparison_results: Dict[float, PathResult],
                            save_path: Optional[str] = None) -> plt.Figure:
        """绘制多条路径对比"""
        num_paths = len(comparison_results)
        if num_paths == 0:
            raise ValueError("没有可比较的路径")

        # 创建子图
        fig, axes = plt.subplots(1, num_paths, figsize=(6 * num_paths, 10))
        if num_paths == 1:
            axes = [axes]

        alphas = sorted(comparison_results.keys())

        for idx, alpha in enumerate(alphas):
            path_result = comparison_results[alpha]
            ax = axes[idx]

            # 绘制校园地图背景
            self._plot_edges(ax, alpha=0.2)
            self._plot_nodes(ax, show_labels=False, alpha=0.3)

            # 高亮显示路径
            self._highlight_path(ax, path_result, show_congestion=True)

            # 设置子图属性
            ax.set_title(f"α = {alpha}\n"
                        f"距离: {path_result.total_distance:.1f}m\n"
                        f"拥堵成本: {path_result.congestion_cost:.1f}",
                        fontsize=12)
            ax.set_xlabel("X坐标 (米)", fontsize=10)
            ax.set_ylabel("Y坐标 (米)", fontsize=10)
            ax.grid(True, alpha=0.1, linestyle='--')
            ax.axis('equal')

        # 添加总标题
        start = comparison_results[alphas[0]].nodes[0]
        goal = comparison_results[alphas[0]].nodes[-1]
        fig.suptitle(f"路径对比: {start} → {goal}", fontsize=16, fontweight='bold')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"路径对比图已保存到: {save_path}")

        return fig

    def plot_congestion_heatmap(self, time_obj,
                               save_path: Optional[str] = None) -> plt.Figure:
        """绘制拥堵热力图"""
        fig, ax = plt.subplots(figsize=(14, 12))

        # 绘制所有边，根据拥堵程度着色
        self._plot_congestion_edges(ax, time_obj)

        # 绘制节点
        self._plot_nodes(ax, show_labels=True)

        # 设置图形属性
        time_str = time_obj.strftime("%Y-%m-%d %H:%M")
        ax.set_title(f"校园拥堵热力图\n时间: {time_str}", fontsize=16, fontweight='bold')
        ax.set_xlabel("X坐标 (米)", fontsize=12)
        ax.set_ylabel("Y坐标 (米)", fontsize=12)
        ax.grid(True, alpha=0.2, linestyle='--')
        ax.axis('equal')

        # 添加颜色条
        self._add_colorbar(ax)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"拥堵热力图已保存到: {save_path}")

        return fig

    def _plot_edges(self, ax, alpha: float = 0.6):
        """绘制所有边"""
        for edge in self.graph.edges.values():
            from_node = self.graph.get_node(edge.from_node)
            to_node = self.graph.get_node(edge.to_node)

            if from_node and to_node:
                # 根据道路类型选择颜色和宽度
                color = self.road_colors.get(edge.road_type, '#888888')
                width = 2.0 if edge.road_type == RoadType.MAIN_ROAD else 1.0

                ax.plot([from_node.x, to_node.x],
                       [from_node.y, to_node.y],
                       color=color, linewidth=width, alpha=alpha,
                       solid_capstyle='round')

    def _plot_congestion_edges(self, ax, time_obj):
        """根据拥堵程度绘制边"""
        from algorithm.rule_engine import default_rule_engine

        edges_to_plot = []
        congestion_values = []

        for edge in self.graph.edges.values():
            from_node = self.graph.get_node(edge.from_node)
            to_node = self.graph.get_node(edge.to_node)

            if from_node and to_node:
                # 计算拥堵系数
                congestion = default_rule_engine.get_congestion_factor(
                    edge.peak_areas, time_obj
                )
                edges_to_plot.append((from_node, to_node, edge))
                congestion_values.append(congestion)

        if congestion_values:
            # 归一化拥堵值用于颜色映射（固定范围1.0-5.0）
            # 拥堵系数定义：1.0畅通，2.0轻微拥堵，3.0较拥堵，4.0严重拥堵，5.0极度拥堵
            for (from_node, to_node, edge), congestion in zip(edges_to_plot, congestion_values):
                # 计算颜色，使用固定范围1.0-5.0
                norm_congestion = max(0.0, min(1.0, (congestion - 1.0) / 4.0))
                color = self.congestion_cmap(norm_congestion)

                # 根据拥堵程度设置线宽
                width = 1.0 + (congestion - 1.0) * 0.5  # 1.0-3.5

                ax.plot([from_node.x, to_node.x],
                       [from_node.y, to_node.y],
                       color=color, linewidth=width, alpha=0.8,
                       solid_capstyle='round')

    def _plot_nodes(self, ax, show_labels: bool = True, alpha: float = 1.0):
        """绘制所有节点"""
        for node in self.graph.nodes.values():
            color = self.node_colors.get(node.node_type, '#888888')
            size = 100 if node.node_type in [NodeType.TEACHING_BUILDING,
                                           NodeType.CAFETERIA,
                                           NodeType.DORMITORY,
                                           NodeType.LIBRARY] else 50

            ax.scatter(node.x, node.y, color=color, s=size,
                      alpha=alpha, edgecolors='black', linewidth=1)

            if show_labels:
                # 显示节点名称
                label = f"{node.name}\n({node.node_id})"
                ax.text(node.x, node.y + 10, label,
                       fontsize=8, ha='center', va='bottom',
                       alpha=alpha, fontweight='bold')

    def _highlight_path(self, ax, path_result: PathResult, show_congestion: bool):
        """高亮显示路径"""
        if not path_result.segments:
            return

        # 绘制路径边
        for segment in path_result.segments:
            from_node = self.graph.get_node(segment.edge.from_node)
            to_node = self.graph.get_node(segment.edge.to_node)

            if from_node and to_node:
                if show_congestion:
                    # 根据拥堵程度着色
                    congestion = segment.congestion_factor
                    # 归一化到0-1范围（假设拥堵系数1.0-5.0）
                    norm_congestion = max(0.0, min(1.0, (congestion - 1.0) / 4.0))
                    color = self.congestion_cmap(norm_congestion)
                    width = 3.0 + (congestion - 1.0) * 0.5  # 3.0-5.0
                else:
                    color = '#ff0000'  # 红色
                    width = 3.0

                ax.plot([from_node.x, to_node.x],
                       [from_node.y, to_node.y],
                       color=color, linewidth=width, alpha=0.9,
                       solid_capstyle='round', zorder=5)

        # 高亮路径节点
        path_nodes = []
        for node_id in path_result.nodes:
            node = self.graph.get_node(node_id)
            if node:
                path_nodes.append(node)

        if path_nodes:
            xs = [node.x for node in path_nodes]
            ys = [node.y for node in path_nodes]

            # 绘制节点
            ax.scatter(xs, ys, color='#ff0000', s=150,
                      alpha=0.9, edgecolors='black', linewidth=2, zorder=10)

            # 标记起点和终点
            if len(path_nodes) >= 2:
                # 起点
                ax.scatter(xs[0], ys[0], color='#00ff00', s=200,
                          alpha=0.9, edgecolors='black', linewidth=2, zorder=11,
                          marker='s')  # 正方形
                # 终点
                ax.scatter(xs[-1], ys[-1], color='#0000ff', s=200,
                          alpha=0.9, edgecolors='black', linewidth=2, zorder=11,
                          marker='^')  # 三角形

    def _add_legend(self, ax):
        """添加图例"""
        legend_patches = []

        # 节点类型图例
        for node_type, color in self.node_colors.items():
            if node_type in [NodeType.TEACHING_BUILDING, NodeType.CAFETERIA,
                           NodeType.DORMITORY, NodeType.LIBRARY]:
                patch = mpatches.Patch(color=color,
                                      label=node_type.value.replace('_', ' ').title())
                legend_patches.append(patch)

        # 道路类型图例
        for road_type, color in self.road_colors.items():
            if road_type in [RoadType.MAIN_ROAD, RoadType.SIDE_ROAD, RoadType.PATH]:
                patch = mpatches.Patch(color=color,
                                      label=road_type.value.replace('_', ' ').title())
                legend_patches.append(patch)

        if legend_patches:
            ax.legend(handles=legend_patches, loc='upper left',
                     bbox_to_anchor=(1.05, 1), borderaxespad=0.)

    def _add_path_legend(self, ax, path_result: PathResult, show_congestion: bool):
        """添加路径图例"""
        legend_patches = []

        # 起点和终点
        start_patch = mpatches.Patch(color='#00ff00', label='起点')
        end_patch = mpatches.Patch(color='#0000ff', label='终点')
        legend_patches.extend([start_patch, end_patch])

        # 路径
        if show_congestion:
            path_patch = mpatches.Patch(color='#ff0000', label='规划路径（颜色表示拥堵程度）')
        else:
            path_patch = mpatches.Patch(color='#ff0000', label='规划路径')

        legend_patches.append(path_patch)

        # 添加统计信息
        stats_text = (f"总距离: {path_result.total_distance:.1f}m\n"
                     f"总成本: {path_result.total_actual_cost:.1f}\n"
                     f"拥堵成本: {path_result.congestion_cost:.1f}\n"
                     f"平均拥堵: {path_result.average_congestion:.2f}\n"
                     f"α参数: {path_result.alpha}")

        ax.text(1.05, 0.5, stats_text, transform=ax.transAxes,
               verticalalignment='center', fontsize=10,
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        ax.legend(handles=legend_patches, loc='upper left',
                 bbox_to_anchor=(1.05, 1), borderaxespad=0.)

    def _add_colorbar(self, ax):
        """添加颜色条"""
        # 创建颜色条
        norm = plt.Normalize(1, 5)  # 拥堵系数范围1.0-5.0
        sm = plt.cm.ScalarMappable(cmap=self.congestion_cmap, norm=norm)
        sm.set_array([])

        cbar = plt.colorbar(sm, ax=ax, orientation='vertical',
                           fraction=0.03, pad=0.04)
        cbar.set_label('拥堵系数', fontsize=12)
        cbar.ax.tick_params(labelsize=10)

        # 添加描述标签
        ticks = [1, 2, 3, 4, 5]
        tick_labels = ['畅通', '轻微拥堵', '较拥堵', '严重拥堵', '极度拥堵']
        cbar.set_ticks(ticks)
        cbar.set_ticklabels(tick_labels)

    def create_animation(self, start: str, goal: str,
                        alpha: float = 1.0,
                        time_points: List = None,
                        save_path: Optional[str] = None) -> None:
        """创建路径随时间变化的动画（需要额外依赖）"""
        try:
            from matplotlib.animation import FuncAnimation
        except ImportError:
            print("创建动画需要 matplotlib.animation 模块")
            return

        if time_points is None:
            # 生成全天时间点
            import datetime
            date = datetime.date.today()
            time_points = []
            for hour in range(8, 22, 2):  # 8:00-20:00，每2小时
                time_points.append(datetime.datetime.combine(date, datetime.time(hour, 0)))

        fig, ax = plt.subplots(figsize=(14, 12))
        frames_data = []

        # 预计算所有帧的数据
        for time_obj in time_points:
            path = self.planner.plan_path(start, goal, alpha, time_obj)
            frames_data.append((time_obj, path))

        # 初始化
        self._plot_edges(ax, alpha=0.3)
        self._plot_nodes(ax, show_labels=False, alpha=0.5)

        # 创建动画函数
        def update(frame_idx):
            ax.clear()
            time_obj, path = frames_data[frame_idx]

            # 重绘背景
            self._plot_edges(ax, alpha=0.3)
            self._plot_nodes(ax, show_labels=False, alpha=0.5)

            # 绘制路径
            if path:
                self._highlight_path(ax, path, show_congestion=True)

            # 设置标题
            time_str = time_obj.strftime("%H:%M")
            title = f"路径随时间变化: {start} → {goal} (α={alpha})\n时间: {time_str}"
            if path:
                title += f"\n距离: {path.total_distance:.1f}m, 拥堵成本: {path.congestion_cost:.1f}"

            ax.set_title(title, fontsize=14)
            ax.set_xlabel("X坐标 (米)", fontsize=10)
            ax.set_ylabel("Y坐标 (米)", fontsize=10)
            ax.grid(True, alpha=0.2, linestyle='--')
            ax.axis('equal')

            return ax,

        # 创建动画
        anim = FuncAnimation(fig, update, frames=len(frames_data),
                           interval=1000, blit=False)

        if save_path:
            anim.save(save_path, writer='pillow', fps=1, dpi=100)
            print(f"动画已保存到: {save_path}")
        else:
            plt.show()


def visualize_example():
    """可视化示例"""
    import datetime

    visualizer = PathVisualizer()

    print("1. 绘制校园地图...")
    visualizer.plot_campus_map()
    plt.show()

    print("2. 绘制路径示例...")
    planner = PathPlanner()
    time_obj = datetime.datetime(2024, 5, 20, 12, 0)  # 午餐高峰期
    path = planner.plan_path("TB1", "CA1", alpha=1.0, time=time_obj)

    if path:
        visualizer.plot_path(path, show_congestion=True)
        plt.show()

    print("3. 绘制路径对比...")
    alphas = [0, 0.5, 1.0, 1.5]
    comparison = planner.compare_paths("TB1", "CA1", alphas, time_obj)
    if comparison.comparisons:
        visualizer.plot_path_comparison(comparison.comparisons)
        plt.show()

    print("4. 绘制拥堵热力图...")
    visualizer.plot_congestion_heatmap(time_obj)
    plt.show()


if __name__ == "__main__":
    visualize_example()