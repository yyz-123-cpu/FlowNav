"""
图构建模块
负责创建和管理校园路网图，提供图论计算基础功能
"""

import networkx as nx
from typing import Dict, List, Tuple, Optional, Set, Any
from algorithm.models import Node, Edge, NodeType, RoadType


class CampusGraph:
    """校园图类，封装NetworkX图并提供校园特定功能"""

    def __init__(self):
        """初始化空的校园图"""
        self.graph = nx.Graph()  # 使用无向图
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, Edge] = {}

    def add_node(self, node: Node) -> None:
        """添加节点到图中"""
        self.nodes[node.node_id] = node
        self.graph.add_node(
            node.node_id,
            name=node.name,
            node_type=node.node_type.value,
            coordinates=node.coordinates,
            description=node.description
        )

    def add_edge(self, edge: Edge) -> None:
        """添加边到图中"""
        edge_id = edge.edge_id
        self.edges[edge_id] = edge

        # 确保节点存在
        if edge.from_node not in self.nodes:
            raise ValueError(f"节点 {edge.from_node} 不存在")
        if edge.to_node not in self.nodes:
            raise ValueError(f"节点 {edge.to_node} 不存在")

        # 添加边到NetworkX图
        self.graph.add_edge(
            edge.from_node,
            edge.to_node,
            distance=edge.distance,
            road_type=edge.road_type.value,
            peak_areas=edge.peak_areas,
            edge_id=edge_id
        )

    def add_nodes_from_list(self, nodes: List[Node]) -> None:
        """批量添加节点"""
        for node in nodes:
            self.add_node(node)

    def add_edges_from_list(self, edges: List[Edge]) -> None:
        """批量添加边"""
        for edge in edges:
            self.add_edge(edge)

    def get_node(self, node_id: str) -> Optional[Node]:
        """获取节点"""
        return self.nodes.get(node_id)

    def get_edge(self, from_node: str, to_node: str) -> Optional[Edge]:
        """获取边"""
        edge_id = f"{from_node}->{to_node}"
        if edge_id in self.edges:
            return self.edges[edge_id]

        # 检查反向边
        reverse_id = f"{to_node}->{from_node}"
        return self.edges.get(reverse_id)

    def get_neighbors(self, node_id: str) -> List[Tuple[str, Edge]]:
        """获取节点的邻居节点和连接边"""
        if node_id not in self.graph:
            return []

        neighbors = []
        for neighbor in self.graph.neighbors(node_id):
            edge = self.get_edge(node_id, neighbor)
            if edge:
                neighbors.append((neighbor, edge))
        return neighbors

    def get_edge_data(self, from_node: str, to_node: str) -> Optional[Dict[str, Any]]:
        """获取边的数据"""
        if not self.graph.has_edge(from_node, to_node):
            return None
        return self.graph.get_edge_data(from_node, to_node)

    def calculate_distance(self, node1_id: str, node2_id: str) -> Optional[float]:
        """计算两个节点之间的物理距离"""
        edge = self.get_edge(node1_id, node2_id)
        if edge:
            return edge.distance
        return None

    def shortest_path_by_distance(self, start: str, goal: str) -> Optional[List[str]]:
        """使用Dijkstra算法计算最短距离路径（α=0的情况）"""
        try:
            path = nx.shortest_path(self.graph, start, goal, weight='distance')
            return path
        except (nx.NodeNotFound, nx.NetworkXNoPath):
            return None

    def shortest_path_length_by_distance(self, start: str, goal: str) -> Optional[float]:
        """计算最短距离路径的长度"""
        try:
            length = nx.shortest_path_length(self.graph, start, goal, weight='distance')
            return length
        except (nx.NodeNotFound, nx.NetworkXNoPath):
            return None

    def is_connected(self) -> bool:
        """检查图是否连通"""
        return nx.is_connected(self.graph)

    def get_connected_components(self) -> List[Set[str]]:
        """获取连通分量"""
        return list(nx.connected_components(self.graph))

    def get_node_coordinates(self, node_id: str) -> Optional[Tuple[float, float]]:
        """获取节点坐标"""
        node = self.get_node(node_id)
        return node.coordinates if node else None

    def calculate_euclidean_distance(self, node1_id: str, node2_id: str) -> Optional[float]:
        """计算两个节点之间的欧几里得距离（用于启发函数）"""
        node1 = self.get_node(node1_id)
        node2 = self.get_node(node2_id)
        if node1 and node2:
            return node1.distance_to(node2)
        return None

    def get_graph_info(self) -> Dict[str, Any]:
        """获取图的基本信息"""
        return {
            "node_count": self.graph.number_of_nodes(),
            "edge_count": self.graph.number_of_edges(),
            "is_connected": self.is_connected(),
            "connected_components": len(self.get_connected_components()),
            "node_types": self._count_node_types(),
            "road_types": self._count_road_types()
        }

    def _count_node_types(self) -> Dict[str, int]:
        """统计节点类型"""
        type_count = {}
        for node in self.nodes.values():
            node_type = node.node_type.value
            type_count[node_type] = type_count.get(node_type, 0) + 1
        return type_count

    def _count_road_types(self) -> Dict[str, int]:
        """统计道路类型"""
        type_count = {}
        for edge in self.edges.values():
            road_type = edge.road_type.value
            type_count[road_type] = type_count.get(road_type, 0) + 1
        return type_count

    def find_nodes_by_type(self, node_type: NodeType) -> List[Node]:
        """根据类型查找节点"""
        return [node for node in self.nodes.values() if node.node_type == node_type]

    def find_edges_in_area(self, area_tag: str) -> List[Edge]:
        """查找属于特定区域的边"""
        return [edge for edge in self.edges.values() if area_tag in edge.peak_areas]

    def get_subgraph(self, node_ids: Set[str]) -> 'CampusGraph':
        """获取子图"""
        subgraph = CampusGraph()
        for node_id in node_ids:
            node = self.get_node(node_id)
            if node:
                subgraph.add_node(node)

        # 添加连接这些节点的边
        for edge in self.edges.values():
            if edge.from_node in node_ids and edge.to_node in node_ids:
                subgraph.add_edge(edge)

        return subgraph

    def visualize_graph(self, save_path: Optional[str] = None) -> None:
        """可视化图（需要matplotlib）"""
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("需要matplotlib库来进行可视化")
            return

        pos = {node_id: self.get_node(node_id).coordinates
               for node_id in self.graph.nodes()}

        plt.figure(figsize=(12, 10))

        # 绘制节点
        node_colors = []
        for node_id in self.graph.nodes():
            node_type = self.get_node(node_id).node_type
            if node_type == NodeType.TEACHING_BUILDING:
                node_colors.append('blue')
            elif node_type == NodeType.CAFETERIA:
                node_colors.append('red')
            elif node_type == NodeType.DORMITORY:
                node_colors.append('green')
            elif node_type == NodeType.LIBRARY:
                node_colors.append('purple')
            else:
                node_colors.append('gray')

        nx.draw_networkx_nodes(self.graph, pos, node_color=node_colors,
                              node_size=300, alpha=0.8)

        # 绘制边
        edge_colors = []
        edge_widths = []
        for u, v in self.graph.edges():
            edge_data = self.get_edge_data(u, v)
            if edge_data and edge_data.get('road_type') == 'main_road':
                edge_colors.append('black')
                edge_widths.append(2.0)
            else:
                edge_colors.append('lightgray')
                edge_widths.append(1.0)

        nx.draw_networkx_edges(self.graph, pos, edge_color=edge_colors,
                              width=edge_widths, alpha=0.6)

        # 绘制标签
        labels = {node_id: self.get_node(node_id).name
                  for node_id in self.graph.nodes()}
        nx.draw_networkx_labels(self.graph, pos, labels, font_size=8)

        plt.title("校园路网图")
        plt.axis('equal')
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300)
            print(f"图已保存到: {save_path}")
        else:
            plt.show()


def create_campus_graph() -> CampusGraph:
    """创建默认的校园图"""
    from data.campus_map import load_default_campus

    campus_graph = CampusGraph()
    nodes, edges = load_default_campus()

    campus_graph.add_nodes_from_list(list(nodes.values()))
    campus_graph.add_edges_from_list(edges)

    return campus_graph


if __name__ == "__main__":
    # 测试代码
    graph = create_campus_graph()

    print("=== 校园图信息 ===")
    info = graph.get_graph_info()
    for key, value in info.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
        else:
            print(f"{key}: {value}")

    print(f"\n=== 节点示例 ===")
    sample_node = graph.get_node("TB1")
    if sample_node:
        print(f"节点 TB1: {sample_node.name} ({sample_node.node_type.value})")

    print(f"\n=== 边示例 ===")
    sample_edge = graph.get_edge("TB1", "TC")
    if sample_edge:
        print(f"边 TB1->TC: 距离={sample_edge.distance}m, 类型={sample_edge.road_type.value}")

    print(f"\n=== 连通性测试 ===")
    print(f"图是否连通: {graph.is_connected()}")
    print(f"连通分量数量: {len(graph.get_connected_components())}")

    print(f"\n=== 最短路径测试 (TB1 -> CA1) ===")
    path = graph.shortest_path_by_distance("TB1", "CA1")
    if path:
        print(f"最短路径: {' -> '.join(path)}")
        length = graph.shortest_path_length_by_distance("TB1", "CA1")
        print(f"路径长度: {length}m")
    else:
        print("未找到路径")

    print(f"\n=== 节点类型统计 ===")
    teaching_nodes = graph.find_nodes_by_type(NodeType.TEACHING_BUILDING)
    print(f"教学楼节点: {[node.name for node in teaching_nodes]}")