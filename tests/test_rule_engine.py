"""
时空规则引擎单元测试
"""

import pytest
import datetime
from algorithm.rule_engine import TimeRuleEngine, PeakPeriod


class TestTimeRuleEngine:
    """时空规则引擎测试类"""

    def setup_method(self):
        """测试初始化"""
        self.engine = TimeRuleEngine(seed=42)  # 固定随机种子

    def test_peak_period_detection(self):
        """测试高峰期检测"""
        # 午餐高峰期 (11:50-12:30)
        lunch_peak = datetime.datetime(2024, 5, 20, 12, 0)
        assert self.engine.is_in_peak_period(lunch_peak) == PeakPeriod.LUNCH_PEAK

        # 晚餐高峰期 (17:30-18:30)
        dinner_peak = datetime.datetime(2024, 5, 20, 18, 0)
        assert self.engine.is_in_peak_period(dinner_peak) == PeakPeriod.DINNER_PEAK

        # 晚自习高峰期 (21:30-22:10)
        evening_peak = datetime.datetime(2024, 5, 20, 21, 45)
        assert self.engine.is_in_peak_period(evening_peak) == PeakPeriod.EVENING_STUDY_PEAK

        # 平峰期
        off_peak = datetime.datetime(2024, 5, 20, 14, 30)
        assert self.engine.is_in_peak_period(off_peak) == PeakPeriod.OFF_PEAK

    def test_congestion_factor_off_peak(self):
        """测试平峰期拥挤系数"""
        time_obj = datetime.datetime(2024, 5, 20, 14, 30)  # 平峰期

        # 无影响区域
        factor = self.engine.get_congestion_factor([], time_obj)
        assert factor == 1.0  # 规则C：平峰期C=1.0

        # 有影响区域但不在高峰期
        factor = self.engine.get_congestion_factor(["cafeteria_area"], time_obj)
        assert factor == 1.0

    def test_congestion_factor_lunch_peak(self):
        """测试午餐高峰期拥挤系数"""
        time_obj = datetime.datetime(2024, 5, 20, 12, 0)  # 午餐高峰期

        # 食堂区域应受严重影响
        factor = self.engine.get_congestion_factor(["cafeteria_area"], time_obj)
        assert 4.0 <= factor <= 5.0  # 规则A：严重拥堵 4.0-5.0

        # 非受影响区域
        factor = self.engine.get_congestion_factor(["dormitory_area"], time_obj)
        assert factor == 1.0  # 不应受影响

        # 混合区域
        factor = self.engine.get_congestion_factor(["cafeteria_area", "teaching_to_cafeteria"], time_obj)
        assert 4.0 <= factor <= 5.0

    def test_congestion_factor_dinner_peak(self):
        """测试晚餐高峰期拥挤系数"""
        time_obj = datetime.datetime(2024, 5, 20, 18, 0)  # 晚餐高峰期

        # 食堂区域应受严重影响
        factor = self.engine.get_congestion_factor(["cafeteria_area"], time_obj)
        assert 4.0 <= factor <= 5.0  # 规则A：严重拥堵 4.0-5.0

    def test_congestion_factor_evening_study_peak(self):
        """测试晚自习高峰期拥挤系数"""
        time_obj = datetime.datetime(2024, 5, 20, 21, 45)  # 晚自习高峰期

        # 宿舍区域应受影响
        factor = self.engine.get_congestion_factor(["dormitory_area"], time_obj)
        assert 3.0 <= factor <= 4.0  # 规则B：较拥堵 3.0-4.0

        # 图书馆到宿舍区域
        factor = self.engine.get_congestion_factor(["library_to_dormitory"], time_obj)
        assert 3.0 <= factor <= 4.0

        # 非受影响区域
        factor = self.engine.get_congestion_factor(["cafeteria_area"], time_obj)
        assert factor == 1.0  # 不应受影响

    def test_edge_congestion_details(self):
        """测试边拥挤系数详细信息"""
        time_obj = datetime.datetime(2024, 5, 20, 12, 0)  # 午餐高峰期
        areas = ["cafeteria_area"]

        details = self.engine.get_congestion_factor_for_edge(areas, time_obj)

        assert "congestion_factor" in details
        assert "peak_period" in details
        assert "is_peak" in details
        assert "affected_areas" in details
        assert "time" in details
        assert "description" in details

        assert details["peak_period"] == "lunch_peak"
        assert details["is_peak"] is True
        assert details["affected_areas"] == areas
        assert 4.0 <= details["congestion_factor"] <= 5.0

    def test_peak_period_info(self):
        """测试高峰期信息获取"""
        # 高峰期
        peak_time = datetime.datetime(2024, 5, 20, 12, 0)
        info = self.engine.get_peak_period_info(peak_time)

        assert info["peak_period"] == "lunch_peak"
        assert info["is_peak"] is True
        assert "description" in info
        assert "congestion_range" in info
        assert "affected_areas" in info

        # 平峰期
        off_peak_time = datetime.datetime(2024, 5, 20, 14, 30)
        info = self.engine.get_peak_period_info(off_peak_time)

        assert info["peak_period"] == "off_peak"
        assert info["is_peak"] is False
        assert "description" in info

    def test_rule_validation(self):
        """测试规则验证"""
        validation = self.engine.validate_rules()

        assert "valid" in validation
        assert "issues" in validation
        assert "peak_periods" in validation
        assert "congestion_ranges" in validation
        assert "area_mapping" in validation

        # 规则应该有效
        assert validation["valid"] is True
        assert len(validation["issues"]) == 0

    def test_time_boundary_cases(self):
        """测试时间边界情况"""
        # 午餐高峰期边界
        lunch_start = datetime.datetime(2024, 5, 20, 11, 50)
        lunch_end = datetime.datetime(2024, 5, 20, 12, 30)

        assert self.engine.is_in_peak_period(lunch_start) == PeakPeriod.LUNCH_PEAK
        assert self.engine.is_in_peak_period(lunch_end) == PeakPeriod.LUNCH_PEAK

        # 边界外1分钟
        lunch_before = datetime.datetime(2024, 5, 20, 11, 49)
        lunch_after = datetime.datetime(2024, 5, 20, 12, 31)

        assert self.engine.is_in_peak_period(lunch_before) == PeakPeriod.OFF_PEAK
        assert self.engine.is_in_peak_period(lunch_after) == PeakPeriod.OFF_PEAK

    def test_daily_congestion_pattern(self):
        """测试全天拥堵模式"""
        date = datetime.date(2024, 5, 20)
        pattern = self.engine.get_daily_congestion_pattern(date)

        assert isinstance(pattern, list)
        assert len(pattern) == 24 * 4  # 每小时4个时间点（0, 15, 30, 45）

        # 检查包含必要字段
        sample = pattern[0]
        assert "peak_period" in sample
        assert "is_peak" in sample
        assert "time" in sample
        assert "description" in sample

    def test_randomness_control(self):
        """测试随机性控制（固定种子）"""
        time_obj = datetime.datetime(2024, 5, 20, 12, 0)
        areas = ["cafeteria_area"]

        # 相同种子应产生相同结果
        factor1 = self.engine.get_congestion_factor(areas, time_obj)

        # 创建新引擎（相同种子）
        engine2 = TimeRuleEngine(seed=42)
        factor2 = engine2.get_congestion_factor(areas, time_obj)

        assert factor1 == factor2

        # 不同种子可能产生不同结果（在范围内）
        engine3 = TimeRuleEngine(seed=123)
        factor3 = engine3.get_congestion_factor(areas, time_obj)

        assert 4.0 <= factor3 <= 5.0  # 仍在范围内

    def test_area_peak_mapping(self):
        """测试区域与高峰期的映射"""
        validation = self.engine.validate_rules()
        area_mapping = validation["area_mapping"]

        # 检查关键映射
        assert "cafeteria_area" in area_mapping
        assert "lunch_peak" in area_mapping["cafeteria_area"]
        assert "dinner_peak" in area_mapping["cafeteria_area"]

        assert "dormitory_area" in area_mapping
        assert "evening_study_peak" in area_mapping["dormitory_area"]

    def test_congestion_description(self):
        """测试拥挤程度描述"""
        time_obj = datetime.datetime(2024, 5, 20, 12, 0)
        areas = ["cafeteria_area"]

        details = self.engine.get_congestion_factor_for_edge(areas, time_obj)

        # 根据拥挤系数检查描述
        factor = details["congestion_factor"]
        description = details["description"]

        if factor >= 4.0:
            assert description == "严重拥堵"
        elif factor >= 3.0:
            assert description == "较拥堵"
        elif factor >= 2.0:
            assert description == "轻微拥堵"
        else:
            assert description == "畅通"


if __name__ == "__main__":
    # 手动运行测试
    test = TestTimeRuleEngine()
    test.setup_method()

    print("运行时空规则引擎测试...")
    test.test_peak_period_detection()
    test.test_congestion_factor_off_peak()
    test.test_congestion_factor_lunch_peak()
    test.test_congestion_factor_dinner_peak()
    test.test_congestion_factor_evening_study_peak()
    test.test_rule_validation()
    test.test_time_boundary_cases()

    print("所有测试通过!")