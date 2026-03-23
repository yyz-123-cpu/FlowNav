"""
时空规则引擎模块
根据时间动态计算路段的拥挤系数，实现项目方案中的规则A、B、C
"""

import datetime
import random
from typing import List, Optional, Tuple, Dict, Any
from enum import Enum


class PeakPeriod(Enum):
    """高峰期类型枚举"""
    LUNCH_PEAK = "lunch_peak"          # 午餐高峰期
    DINNER_PEAK = "dinner_peak"        # 晚餐高峰期
    EVENING_STUDY_PEAK = "evening_study_peak"  # 晚自习高峰期
    MORNING_CLASS_CHANGE = "morning_class_change"  # 上午课间高峰
    AFTERNOON_CLASS_CHANGE = "afternoon_class_change"  # 下午课间高峰
    SPORTS_CLASS = "sports_class"      # 体育课时间
    LIBRARY_OPENING = "library_opening" # 图书馆开馆时间
    GATE_TRAFFIC = "gate_traffic"      # 校门交通高峰
    OFF_PEAK = "off_peak"              # 平峰期


class TimeRuleEngine:
    """时空规则引擎"""

    def __init__(self, seed: int = 42):
        """初始化规则引擎"""
        self.seed = seed
        random.seed(seed)

        # 定义高峰期时间规则（基于项目方案）
        self.peak_periods = {
            PeakPeriod.LUNCH_PEAK: [
                # 规则A：午餐高峰期 11:50-12:30
                ((11, 50), (12, 30))
            ],
            PeakPeriod.DINNER_PEAK: [
                # 规则A：晚餐高峰期 17:30-18:30
                ((17, 30), (18, 30))
            ],
            PeakPeriod.EVENING_STUDY_PEAK: [
                # 规则B：晚自习高峰期 21:30-22:10
                ((21, 30), (22, 10))
            ],
            PeakPeriod.MORNING_CLASS_CHANGE: [
                # 上午课间高峰 9:50-10:10
                ((9, 50), (10, 10))
            ],
            PeakPeriod.AFTERNOON_CLASS_CHANGE: [
                # 下午课间高峰 16:05-16:25（避开体育课时间）
                ((16, 5), (16, 25))
            ],
            PeakPeriod.SPORTS_CLASS: [
                # 体育课时间 14:00-16:00
                ((14, 0), (16, 0))
            ],
            PeakPeriod.LIBRARY_OPENING: [
                # 图书馆开馆时间 8:05-8:35（完全避开校门交通高峰）
                ((8, 5), (8, 35))
            ],
            PeakPeriod.GATE_TRAFFIC: [
                # 校门交通高峰 7:30-8:00 (早上入校)
                ((7, 30), (8, 0)),
                # 校门交通高峰 16:50-17:20 (下午离校，避开晚餐高峰)
                ((16, 50), (17, 20))
            ]
        }

        # 定义拥挤系数范围（进一步优化以增强alpha影响，扩大差异）
        self.congestion_ranges = {
            PeakPeriod.LUNCH_PEAK: (2.0, 5.0),      # 严重拥堵（更大范围）
            PeakPeriod.DINNER_PEAK: (2.0, 5.0),     # 严重拥堵
            PeakPeriod.EVENING_STUDY_PEAK: (1.8, 4.5),  # 较拥堵
            PeakPeriod.MORNING_CLASS_CHANGE: (1.5, 4.0),  # 中等拥堵
            PeakPeriod.AFTERNOON_CLASS_CHANGE: (1.5, 4.0),  # 中等拥堵
            PeakPeriod.SPORTS_CLASS: (1.2, 3.5),    # 轻微拥堵
            PeakPeriod.LIBRARY_OPENING: (1.2, 3.5), # 轻微拥堵
            PeakPeriod.GATE_TRAFFIC: (1.8, 4.5),    # 较拥堵
            PeakPeriod.OFF_PEAK: (1.0, 1.5)         # 畅通（轻微波动）
        }

        # 定义区域与高峰期类型的映射
        self.area_peak_mapping = {
            # 原有区域
            "cafeteria_area": [PeakPeriod.LUNCH_PEAK, PeakPeriod.DINNER_PEAK],
            "teaching_to_cafeteria": [PeakPeriod.LUNCH_PEAK, PeakPeriod.DINNER_PEAK],
            "dormitory_area": [PeakPeriod.EVENING_STUDY_PEAK],
            "library_to_dormitory": [PeakPeriod.EVENING_STUDY_PEAK],
            "teaching_to_dormitory": [PeakPeriod.EVENING_STUDY_PEAK],
            # 新增区域
            "teaching_to_sports": [PeakPeriod.SPORTS_CLASS, PeakPeriod.MORNING_CLASS_CHANGE, PeakPeriod.AFTERNOON_CLASS_CHANGE],
            "gate_traffic": [PeakPeriod.GATE_TRAFFIC, PeakPeriod.MORNING_CLASS_CHANGE, PeakPeriod.AFTERNOON_CLASS_CHANGE],
            "library_peak": [PeakPeriod.LIBRARY_OPENING, PeakPeriod.EVENING_STUDY_PEAK],
            "class_change_area": [PeakPeriod.MORNING_CLASS_CHANGE, PeakPeriod.AFTERNOON_CLASS_CHANGE],
            "sports_area": [PeakPeriod.SPORTS_CLASS],
            "main_road_crossing": [PeakPeriod.MORNING_CLASS_CHANGE, PeakPeriod.AFTERNOON_CLASS_CHANGE, PeakPeriod.LUNCH_PEAK, PeakPeriod.DINNER_PEAK]
        }

    def is_in_peak_period(self, time_obj: datetime.datetime) -> PeakPeriod:
        """判断给定时间是否处于高峰期，返回高峰期类型"""
        hour = time_obj.hour
        minute = time_obj.minute

        # 检查优先级：按拥堵程度从高到低检查
        # 1. 校门交通高峰（优先级最高，因为会影响所有区域）
        for (start_h, start_m), (end_h, end_m) in self.peak_periods[PeakPeriod.GATE_TRAFFIC]:
            if self._is_time_in_range(hour, minute, start_h, start_m, end_h, end_m):
                return PeakPeriod.GATE_TRAFFIC

        # 2. 午餐高峰期
        for (start_h, start_m), (end_h, end_m) in self.peak_periods[PeakPeriod.LUNCH_PEAK]:
            if self._is_time_in_range(hour, minute, start_h, start_m, end_h, end_m):
                return PeakPeriod.LUNCH_PEAK

        # 3. 晚餐高峰期
        for (start_h, start_m), (end_h, end_m) in self.peak_periods[PeakPeriod.DINNER_PEAK]:
            if self._is_time_in_range(hour, minute, start_h, start_m, end_h, end_m):
                return PeakPeriod.DINNER_PEAK

        # 4. 晚自习高峰期
        for (start_h, start_m), (end_h, end_m) in self.peak_periods[PeakPeriod.EVENING_STUDY_PEAK]:
            if self._is_time_in_range(hour, minute, start_h, start_m, end_h, end_m):
                return PeakPeriod.EVENING_STUDY_PEAK

        # 5. 体育课时间
        for (start_h, start_m), (end_h, end_m) in self.peak_periods[PeakPeriod.SPORTS_CLASS]:
            if self._is_time_in_range(hour, minute, start_h, start_m, end_h, end_m):
                return PeakPeriod.SPORTS_CLASS

        # 6. 图书馆开馆时间
        for (start_h, start_m), (end_h, end_m) in self.peak_periods[PeakPeriod.LIBRARY_OPENING]:
            if self._is_time_in_range(hour, minute, start_h, start_m, end_h, end_m):
                return PeakPeriod.LIBRARY_OPENING

        # 7. 上午课间高峰
        for (start_h, start_m), (end_h, end_m) in self.peak_periods[PeakPeriod.MORNING_CLASS_CHANGE]:
            if self._is_time_in_range(hour, minute, start_h, start_m, end_h, end_m):
                return PeakPeriod.MORNING_CLASS_CHANGE

        # 8. 下午课间高峰
        for (start_h, start_m), (end_h, end_m) in self.peak_periods[PeakPeriod.AFTERNOON_CLASS_CHANGE]:
            if self._is_time_in_range(hour, minute, start_h, start_m, end_h, end_m):
                return PeakPeriod.AFTERNOON_CLASS_CHANGE

        return PeakPeriod.OFF_PEAK

    def _is_time_in_range(self, hour: int, minute: int,
                          start_h: int, start_m: int,
                          end_h: int, end_m: int) -> bool:
        """检查时间是否在指定范围内"""
        start_minutes = start_h * 60 + start_m
        end_minutes = end_h * 60 + end_m
        current_minutes = hour * 60 + minute

        return start_minutes <= current_minutes <= end_minutes

    def _get_deterministic_random(self, seed_string: str) -> float:
        """基于种子字符串生成确定性0-1之间的随机数"""
        import hashlib
        # 创建哈希
        hash_obj = hashlib.md5(seed_string.encode())
        hash_hex = hash_obj.hexdigest()
        # 取前8个字符转换为整数
        hash_int = int(hash_hex[:8], 16)
        # 归一化到0-1
        return (hash_int % 10000) / 10000.0

    def get_congestion_factor(self, peak_areas: List[str],
                             time_obj: datetime.datetime) -> float:
        """
        计算拥挤系数

        参数:
            peak_areas: 路段所属的高峰期影响区域列表
            time_obj: 当前时间

        返回:
            拥挤系数 C(e,t)，根据项目方案：
            - 规则A：就餐高峰期，食堂、核心教学楼路段 C=4.0-5.0
            - 规则B：晚自习高峰期，图书馆/教学楼到宿舍区路段 C=3.0-4.0
            - 规则C：其他时段 C=1.0
        """
        peak_period = self.is_in_peak_period(time_obj)

        # 创建确定性种子字符串
        # 使用区域列表（排序后确保一致性）和时间
        areas_key = ','.join(sorted(peak_areas))
        time_key = time_obj.strftime("%Y-%m-%d %H:%M")
        seed_string = f"{areas_key}|{time_key}|{self.seed}|{peak_period.value}"

        # 如果不在任何高峰期，返回平峰期系数（带轻微确定性波动）
        if peak_period == PeakPeriod.OFF_PEAK:
            min_c, max_c = self.congestion_ranges[PeakPeriod.OFF_PEAK]
            if min_c == max_c:
                return min_c
            else:
                # 在平峰期范围内确定性生成
                rand_val = self._get_deterministic_random(seed_string)
                factor = min_c + rand_val * (max_c - min_c)
                return round(factor, 2)

        # 检查路段是否受当前高峰期影响
        affected = False
        for area in peak_areas:
            if area in self.area_peak_mapping:
                if peak_period in self.area_peak_mapping[area]:
                    affected = True
                    break

        # 如果路段不受当前高峰期影响，返回平峰期系数（带轻微确定性波动）
        if not affected:
            min_c, max_c = self.congestion_ranges[PeakPeriod.OFF_PEAK]
            if min_c == max_c:
                return min_c
            else:
                # 在平峰期范围内确定性生成
                rand_val = self._get_deterministic_random(seed_string)
                factor = min_c + rand_val * (max_c - min_c)
                return round(factor, 2)

        # 根据高峰期类型返回相应的拥挤系数（加入确定性波动模拟实际情况）
        min_c, max_c = self.congestion_ranges[peak_period]
        if min_c == max_c:
            return min_c
        else:
            # 在范围内确定性生成
            rand_val = self._get_deterministic_random(seed_string)
            factor = min_c + rand_val * (max_c - min_c)
            return round(factor, 1)

    def get_congestion_factor_for_edge(self, edge_peak_areas: List[str],
                                      time_obj: datetime.datetime) -> Dict[str, Any]:
        """获取边的拥挤系数详细信息"""
        peak_period = self.is_in_peak_period(time_obj)
        congestion_factor = self.get_congestion_factor(edge_peak_areas, time_obj)

        return {
            "congestion_factor": congestion_factor,
            "peak_period": peak_period.value,
            "is_peak": peak_period != PeakPeriod.OFF_PEAK,
            "affected_areas": edge_peak_areas,
            "time": time_obj.strftime("%Y-%m-%d %H:%M"),
            "description": self._get_congestion_description(congestion_factor, peak_period)
        }

    def _get_congestion_description(self, congestion_factor: float,
                                   peak_period: PeakPeriod) -> str:
        """获取拥挤程度的文字描述"""
        if congestion_factor >= 4.0:
            return "严重拥堵"
        elif congestion_factor >= 3.0:
            return "较拥堵"
        elif congestion_factor >= 2.0:
            return "轻微拥堵"
        else:
            return "畅通"

    def get_peak_period_info(self, time_obj: datetime.datetime) -> Dict[str, Any]:
        """获取时间点的高峰期信息"""
        peak_period = self.is_in_peak_period(time_obj)
        is_peak = peak_period != PeakPeriod.OFF_PEAK

        info = {
            "peak_period": peak_period.value,
            "is_peak": is_peak,
            "time": time_obj.strftime("%Y-%m-%d %H:%M"),
            "description": self._get_peak_period_description(peak_period)
        }

        if is_peak:
            min_c, max_c = self.congestion_ranges[peak_period]
            info.update({
                "congestion_range": (min_c, max_c),
                "affected_areas": self._get_affected_areas_for_peak(peak_period)
            })

        return info

    def _get_peak_period_description(self, peak_period: PeakPeriod) -> str:
        """获取高峰期描述"""
        descriptions = {
            PeakPeriod.LUNCH_PEAK: "午餐高峰期 (11:50-12:30)",
            PeakPeriod.DINNER_PEAK: "晚餐高峰期 (17:30-18:30)",
            PeakPeriod.EVENING_STUDY_PEAK: "晚自习高峰期 (21:30-22:10)",
            PeakPeriod.MORNING_CLASS_CHANGE: "上午课间高峰 (9:50-10:10)",
            PeakPeriod.AFTERNOON_CLASS_CHANGE: "下午课间高峰 (16:05-16:25)",
            PeakPeriod.SPORTS_CLASS: "体育课时间 (14:00-16:00)",
            PeakPeriod.LIBRARY_OPENING: "图书馆开馆时间 (8:05-8:35)",
            PeakPeriod.GATE_TRAFFIC: "校门交通高峰 (7:30-8:00, 17:00-17:30)",
            PeakPeriod.OFF_PEAK: "平峰期"
        }
        return descriptions.get(peak_period, "未知")

    def _get_affected_areas_for_peak(self, peak_period: PeakPeriod) -> List[str]:
        """获取受指定高峰期影响的区域"""
        affected_areas = []
        for area, peaks in self.area_peak_mapping.items():
            if peak_period in peaks:
                affected_areas.append(area)
        return affected_areas

    def get_daily_congestion_pattern(self, date: datetime.date) -> List[Dict[str, Any]]:
        """获取全天的拥堵模式"""
        pattern = []
        for hour in range(0, 24):
            for minute in [0, 15, 30, 45]:
                time_obj = datetime.datetime.combine(date, datetime.time(hour, minute))
                info = self.get_peak_period_info(time_obj)
                pattern.append(info)
        return pattern

    def validate_rules(self) -> Dict[str, Any]:
        """验证规则设置是否正确"""
        issues = []

        # 检查时间范围是否重叠
        all_ranges = []
        for period, ranges in self.peak_periods.items():
            for (sh, sm), (eh, em) in ranges:
                all_ranges.append((period, sh * 60 + sm, eh * 60 + em))

        # 检查重叠
        for i in range(len(all_ranges)):
            for j in range(i + 1, len(all_ranges)):
                period1, start1, end1 = all_ranges[i]
                period2, start2, end2 = all_ranges[j]
                if max(start1, start2) <= min(end1, end2):
                    issues.append(f"{period1.value} 和 {period2.value} 时间范围重叠")

        # 检查拥挤系数范围是否合理
        for period, (min_c, max_c) in self.congestion_ranges.items():
            if min_c < 1.0:
                issues.append(f"{period.value} 的最小拥挤系数 {min_c} 小于1.0")
            if max_c < min_c:
                issues.append(f"{period.value} 的最大拥挤系数 {max_c} 小于最小系数 {min_c}")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "peak_periods": {p.value: r for p, r in self.peak_periods.items()},
            "congestion_ranges": {p.value: r for p, r in self.congestion_ranges.items()},
            "area_mapping": {area: [p.value for p in peaks]
                            for area, peaks in self.area_peak_mapping.items()}
        }


# 默认规则引擎实例
default_rule_engine = TimeRuleEngine()


if __name__ == "__main__":
    # 测试代码
    engine = TimeRuleEngine()

    print("=== 规则验证 ===")
    validation = engine.validate_rules()
    print(f"规则是否有效: {validation['valid']}")
    if validation['issues']:
        print("发现问题:")
        for issue in validation['issues']:
            print(f"  - {issue}")
    else:
        print("所有规则检查通过")

    print(f"\n=== 高峰期时间规则 ===")
    for period, ranges in validation['peak_periods'].items():
        print(f"{period}: {ranges}")

    print(f"\n=== 拥挤系数范围 ===")
    for period, ranges in validation['congestion_ranges'].items():
        print(f"{period}: {ranges}")

    print(f"\n=== 测试不同时间点的拥挤系数 ===")
    test_times = [
        datetime.datetime(2024, 5, 20, 8, 0),   # 平峰期
        datetime.datetime(2024, 5, 20, 12, 0),  # 午餐高峰期
        datetime.datetime(2024, 5, 20, 18, 0),  # 晚餐高峰期
        datetime.datetime(2024, 5, 20, 21, 45), # 晚自习高峰期
    ]

    test_areas = [
        [],  # 无影响区域
        ["cafeteria_area"],  # 食堂区
        ["dormitory_area"],  # 宿舍区
        ["cafeteria_area", "teaching_to_cafeteria"],  # 食堂相关区域
    ]

    for time_obj in test_times:
        print(f"\n时间: {time_obj.strftime('%Y-%m-%d %H:%M')}")
        peak_info = engine.get_peak_period_info(time_obj)
        print(f"  高峰期类型: {peak_info['peak_period']} ({peak_info['description']})")

        for areas in test_areas:
            result = engine.get_congestion_factor_for_edge(areas, time_obj)
            print(f"  区域 {areas}: 拥挤系数={result['congestion_factor']}, 描述={result['description']}")

    print(f"\n=== 全天拥堵模式示例 (整点) ===")
    date = datetime.date(2024, 5, 20)
    for hour in range(7, 23):  # 7:00-22:00
        time_obj = datetime.datetime.combine(date, datetime.time(hour, 0))
        info = engine.get_peak_period_info(time_obj)
        if info['is_peak']:
            print(f"  {hour:02d}:00 - {info['description']}")