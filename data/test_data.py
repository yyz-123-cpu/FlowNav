"""
测试数据生成器
生成各种测试场景和参数组合，用于算法验证和性能测试
"""

import datetime
from typing import List, Dict, Tuple, Any
from algorithm.models import NodeType, RoadType
from data.campus_map import CampusMapGenerator, get_sample_routes


class TestDataGenerator:
    """测试数据生成器"""

    def __init__(self, seed: int = 123):
        """初始化生成器"""
        self.seed = seed
        self.campus_generator = CampusMapGenerator(seed=seed)

    def get_test_scenarios(self) -> List[Dict[str, Any]]:
        """获取测试场景列表"""
        scenarios = []

        # 场景1：午餐高峰期从教学楼到食堂
        scenarios.append({
            "id": "scenario_1",
            "name": "午餐高峰期教学楼到食堂",
            "description": "测试规则A：就餐高峰期(11:50-12:30)，食堂区和主干道应严重拥堵",
            "start": "TB1",  # 第一教学楼
            "goal": "CA1",   # 第一食堂
            "time": datetime.datetime(2024, 5, 20, 12, 0),  # 12:00，午餐高峰期
            "alphas": [0, 0.5, 1.0, 1.5, 2.0],  # 测试不同α值
            "expected_behavior": "α值越大，路径应越倾向于绕开食堂区主干道"
        })

        # 场景2：晚餐高峰期从教学楼到食堂
        scenarios.append({
            "id": "scenario_2",
            "name": "晚餐高峰期教学楼到食堂",
            "description": "测试规则A：晚餐高峰期(17:30-18:30)，食堂区和主干道应严重拥堵",
            "start": "TB2",  # 第二教学楼
            "goal": "CA2",   # 第二食堂
            "time": datetime.datetime(2024, 5, 20, 18, 0),  # 18:00，晚餐高峰期
            "alphas": [0, 0.5, 1.0, 1.5],
            "expected_behavior": "与午餐高峰期类似，应避开拥堵区域"
        })

        # 场景3：晚自习高峰期从图书馆到宿舍
        scenarios.append({
            "id": "scenario_3",
            "name": "晚自习高峰期图书馆到宿舍",
            "description": "测试规则B：晚自习高峰期(21:30-22:10)，宿舍区和相关主干道应较拥堵",
            "start": "LIB",  # 图书馆
            "goal": "DO1",   # 第一宿舍楼
            "time": datetime.datetime(2024, 5, 20, 21, 45),  # 21:45，晚自习高峰期
            "alphas": [0, 0.5, 1.0, 1.5, 2.0],
            "expected_behavior": "α值越大，路径应越倾向于绕开宿舍区主干道"
        })

        # 场景4：平峰期从教学楼到宿舍
        scenarios.append({
            "id": "scenario_4",
            "name": "平峰期教学楼到宿舍",
            "description": "测试规则C：平峰期，所有路段应畅通，α=0和α>0的路径应相同（最短距离）",
            "start": "TB1",  # 第一教学楼
            "goal": "DO1",   # 第一宿舍楼
            "time": datetime.datetime(2024, 5, 20, 14, 30),  # 14:30，平峰期
            "alphas": [0, 1.0, 2.0],
            "expected_behavior": "所有α值的路径应该相同（都是最短距离路径）"
        })

        # 场景5：复杂路径（跨多个区域）
        scenarios.append({
            "id": "scenario_5",
            "name": "跨区域复杂路径",
            "description": "测试算法处理复杂路径的能力，从运动场到图书馆",
            "start": "SP1",  # 田径场
            "goal": "LIB",   # 图书馆
            "time": datetime.datetime(2024, 5, 20, 16, 0),  # 16:00，平峰期
            "alphas": [0, 0.3, 0.7, 1.0, 1.3],
            "expected_behavior": "应能找到合理路径，α值影响路径选择"
        })

        # 场景6：边界测试（相同起点终点）
        scenarios.append({
            "id": "scenario_6",
            "name": "相同起点终点",
            "description": "测试起点和终点相同时的边界情况",
            "start": "TB1",
            "goal": "TB1",
            "time": datetime.datetime(2024, 5, 20, 12, 0),
            "alphas": [0, 1.0],
            "expected_behavior": "应返回空路径或单节点路径"
        })

        # 场景7：不可达测试
        scenarios.append({
            "id": "scenario_7",
            "name": "孤岛节点测试",
            "description": "测试从连通图到孤立节点的路径（预期不可达）",
            "start": "TB1",
            "goal": "ISOLATED",  # 孤立节点（不存在于图中）
            "time": datetime.datetime(2024, 5, 20, 12, 0),
            "alphas": [0, 1.0],
            "expected_behavior": "应返回None或抛出异常"
        })

        return scenarios

    def get_performance_test_cases(self, count: int = 10) -> List[Dict[str, Any]]:
        """生成性能测试用例"""
        test_cases = []
        nodes, _ = self.campus_generator.get_campus_data()
        node_ids = list(nodes.keys())

        # 固定随机种子以确保可重复性
        import random
        random.seed(self.seed)

        for i in range(count):
            # 随机选择起点和终点（确保不同）
            start = random.choice(node_ids)
            goal = random.choice([nid for nid in node_ids if nid != start])

            # 随机选择时间
            hour = random.randint(8, 22)  # 8:00-22:00
            minute = random.randint(0, 59)
            time = datetime.datetime(2024, 5, 20, hour, minute)

            # 随机选择α值
            alpha = round(random.uniform(0, 2.0), 1)

            test_cases.append({
                "id": f"perf_{i+1:03d}",
                "start": start,
                "goal": goal,
                "time": time,
                "alpha": alpha,
                "description": f"随机测试用例 {i+1}: {start}->{goal} at {time.strftime('%H:%M')}, α={alpha}"
            })

        return test_cases

    def get_alpha_sensitivity_test(self) -> List[Dict[str, Any]]:
        """生成α敏感性测试用例"""
        test_cases = []

        # 固定路线，变化α值
        base_cases = [
            {"start": "TB1", "goal": "CA1", "time": datetime.datetime(2024, 5, 20, 12, 0), "name": "午餐高峰期"},
            {"start": "LIB", "goal": "DO1", "time": datetime.datetime(2024, 5, 20, 21, 45), "name": "晚自习高峰期"},
            {"start": "TB1", "goal": "DO1", "time": datetime.datetime(2024, 5, 20, 14, 30), "name": "平峰期"},
        ]

        alpha_values = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0,
                       1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]

        for base in base_cases:
            test_cases.append({
                "id": f"alpha_sens_{base['name']}",
                "name": f"α敏感性测试 - {base['name']}",
                "start": base["start"],
                "goal": base["goal"],
                "time": base["time"],
                "alphas": alpha_values,
                "description": f"测试α值从0到2.0对路径选择的影响，场景：{base['name']}"
            })

        return test_cases

    def get_time_sensitivity_test(self) -> List[Dict[str, Any]]:
        """生成时间敏感性测试用例"""
        test_cases = []

        # 固定路线和α值，变化时间
        base_cases = [
            {"start": "TB1", "goal": "CA1", "alpha": 1.0, "name": "教学楼到食堂"},
            {"start": "LIB", "goal": "DO1", "alpha": 1.0, "name": "图书馆到宿舍"},
        ]

        # 测试全天不同时间点
        time_points = []
        for hour in range(7, 23):  # 7:00-22:00
            for minute in [0, 15, 30, 45]:
                if hour == 22 and minute > 0:  # 22:00之后不测试
                    continue
                time_points.append(datetime.datetime(2024, 5, 20, hour, minute))

        for base in base_cases:
            test_cases.append({
                "id": f"time_sens_{base['name']}",
                "name": f"时间敏感性测试 - {base['name']}",
                "start": base["start"],
                "goal": base["goal"],
                "alpha": base["alpha"],
                "times": time_points,
                "description": f"测试全天不同时间对路径选择的影响，场景：{base['name']}"
            })

        return test_cases

    def get_validation_dataset(self) -> Dict[str, Any]:
        """获取验证数据集"""
        return {
            "scenarios": self.get_test_scenarios(),
            "performance_cases": self.get_performance_test_cases(20),
            "alpha_sensitivity": self.get_alpha_sensitivity_test(),
            "time_sensitivity": self.get_time_sensitivity_test(),
            "sample_routes": get_sample_routes(),
            "campus_info": self.campus_generator.get_region_info(),
            "peak_scenarios": self.campus_generator.get_peak_scenarios()
        }

    def export_test_data(self, output_dir: str = ".") -> None:
        """导出测试数据到文件"""
        import json
        import os

        data = self.get_validation_dataset()

        # 转换datetime对象为字符串
        def datetime_serializer(obj):
            if isinstance(obj, datetime.datetime):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")

        output_file = os.path.join(output_dir, "test_data.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=datetime_serializer, ensure_ascii=False)

        print(f"测试数据已导出到: {output_file}")
        print(f"包含:")
        print(f"  - {len(data['scenarios'])} 个测试场景")
        print(f"  - {len(data['performance_cases'])} 个性能测试用例")
        print(f"  - {len(data['alpha_sensitivity'])} 个α敏感性测试")
        print(f"  - {len(data['time_sensitivity'])} 个时间敏感性测试")
        print(f"  - {len(data['sample_routes'])} 个示例路线")


if __name__ == "__main__":
    # 测试代码
    generator = TestDataGenerator()

    print("=== 测试场景 ===")
    scenarios = generator.get_test_scenarios()
    for scenario in scenarios:
        print(f"{scenario['id']}: {scenario['name']}")
        print(f"  描述: {scenario['description']}")
        print(f"  路线: {scenario['start']} -> {scenario['goal']}")
        print(f"  时间: {scenario['time'].strftime('%Y-%m-%d %H:%M')}")
        print(f"  α值: {scenario['alphas']}")
        print()

    print(f"\n=== 性能测试用例 (前5个) ===")
    perf_cases = generator.get_performance_test_cases(5)
    for case in perf_cases:
        print(f"{case['id']}: {case['description']}")

    print(f"\n=== 导出测试数据 ===")
    generator.export_test_data()