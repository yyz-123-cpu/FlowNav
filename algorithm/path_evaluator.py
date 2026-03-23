"""
路径综合评估模块
提供多维度的路径质量评估指标和推荐系统
"""

from typing import Dict, List, Tuple, Optional, Any
from algorithm.models import PathResult, PathComparison
import datetime


class PathEvaluator:
    """路径综合评估器"""

    def __init__(self):
        """初始化评估器"""
        # 评估权重配置
        self.weights = {
            'distance': 0.4,      # 距离权重
            'congestion': 0.4,    # 拥堵权重
            'complexity': 0.1,    # 复杂度权重（节点数）
            'time_sensitivity': 0.1  # 时间敏感性权重
        }

        # 评分范围定义
        self.score_ranges = {
            'excellent': (8.0, 10.0),    # 优秀
            'good': (6.0, 8.0),          # 良好
            'average': (4.0, 6.0),       # 一般
            'poor': (2.0, 4.0),          # 较差
            'bad': (0.0, 2.0)            # 差
        }

    def evaluate_single_path(self, path_result: PathResult) -> Dict[str, Any]:
        """
        评估单条路径的综合质量

        返回包含多个评估维度的详细报告
        """
        if not path_result or not path_result.segments:
            return {"error": "无效的路径结果"}

        # 1. 基础指标
        total_distance = path_result.total_distance
        total_cost = path_result.total_actual_cost
        congestion_cost = path_result.congestion_cost
        avg_congestion = path_result.average_congestion
        node_count = len(path_result.nodes)

        # 2. 计算各维度评分（0-10分）
        # 距离评分：距离越短评分越高
        distance_score = self._calculate_distance_score(total_distance)

        # 拥堵评分：拥堵成本越低评分越高
        congestion_score = self._calculate_congestion_score(congestion_cost, total_distance)

        # 复杂度评分：节点数越少评分越高（路径越简单）
        complexity_score = self._calculate_complexity_score(node_count)

        # 时间敏感性评分：路径对时间变化的稳定性
        time_sensitivity_score = self._calculate_time_sensitivity_score(path_result)

        # 3. 综合评分
        weighted_score = (
            distance_score * self.weights['distance'] +
            congestion_score * self.weights['congestion'] +
            complexity_score * self.weights['complexity'] +
            time_sensitivity_score * self.weights['time_sensitivity']
        )

        # 4. 评级和建议
        rating = self._get_rating(weighted_score)
        recommendation = self._get_recommendation(rating, path_result)

        return {
            # 基础指标
            "total_distance": total_distance,
            "total_cost": total_cost,
            "congestion_cost": congestion_cost,
            "average_congestion": avg_congestion,
            "node_count": node_count,
            "alpha": path_result.alpha,

            # 维度评分
            "dimension_scores": {
                "distance": round(distance_score, 2),
                "congestion": round(congestion_score, 2),
                "complexity": round(complexity_score, 2),
                "time_sensitivity": round(time_sensitivity_score, 2)
            },

            # 综合评估
            "weighted_score": round(weighted_score, 2),
            "rating": rating,
            "recommendation": recommendation,

            # 详细分析
            "strengths": self._identify_strengths(distance_score, congestion_score),
            "weaknesses": self._identify_weaknesses(distance_score, congestion_score),
            "improvement_suggestions": self._get_improvement_suggestions(
                distance_score, congestion_score, path_result.alpha
            )
        }

    def compare_multiple_paths(self, path_comparison: PathComparison) -> Dict[str, Any]:
        """
        比较多条路径，推荐最佳选择

        参数:
            path_comparison: 包含多条路径的对比结果

        返回:
            包含对比分析和推荐的字典
        """
        if not path_comparison or not path_comparison.comparisons:
            return {"error": "无效的路径对比结果"}

        # 评估每条路径
        evaluations = {}
        for alpha, path in path_comparison.comparisons.items():
            evaluations[alpha] = self.evaluate_single_path(path)

        # 找出各项最佳
        best_by_score = max(evaluations.items(),
                          key=lambda x: x[1]['weighted_score'])
        best_by_distance = min(path_comparison.comparisons.items(),
                             key=lambda x: x[1].total_distance)
        best_by_cost = min(path_comparison.comparisons.items(),
                         key=lambda x: x[1].total_actual_cost)

        # 计算差异分析
        alphas = sorted(evaluations.keys())
        if len(alphas) >= 2:
            score_diffs = {}
            for i in range(len(alphas) - 1):
                alpha1, alpha2 = alphas[i], alphas[i + 1]
                score1 = evaluations[alpha1]['weighted_score']
                score2 = evaluations[alpha2]['weighted_score']
                score_diffs[f"{alpha1}_to_{alpha2}"] = round(score2 - score1, 2)

        # 生成推荐理由
        recommendation_reason = self._generate_recommendation_reason(
            best_by_score, best_by_distance, best_by_cost
        )

        return {
            "evaluations": evaluations,
            "best_paths": {
                "by_score": {
                    "alpha": best_by_score[0],
                    "score": best_by_score[1]['weighted_score'],
                    "rating": best_by_score[1]['rating']
                },
                "by_distance": {
                    "alpha": best_by_distance[0],
                    "distance": best_by_distance[1].total_distance
                },
                "by_cost": {
                    "alpha": best_by_cost[0],
                    "cost": best_by_cost[1].total_actual_cost
                }
            },
            "recommendation": {
                "alpha": best_by_score[0],
                "reason": recommendation_reason,
                "score": best_by_score[1]['weighted_score'],
                "rating": best_by_score[1]['rating']
            },
            "tradeoff_analysis": self._analyze_tradeoffs(evaluations),
            "alpha_sensitivity": self._analyze_alpha_sensitivity(evaluations)
        }

    def _calculate_distance_score(self, distance: float) -> float:
        """计算距离评分（0-10分）"""
        # 基准距离：假设500米为中等距离
        base_distance = 500.0

        if distance <= 0:
            return 10.0

        # 使用指数衰减函数：距离越短评分越高
        # 当distance=base_distance时，score=5.0
        score = 10.0 * (base_distance / (base_distance + distance * 0.5))
        return max(0.0, min(10.0, score))

    def _calculate_congestion_score(self, congestion_cost: float, total_distance: float) -> float:
        """计算拥堵评分（0-10分）"""
        if total_distance <= 0:
            return 10.0

        # 计算单位距离拥堵成本
        unit_congestion = congestion_cost / total_distance if total_distance > 0 else 0

        # 基准值：假设单位拥堵成本0.5为中等
        base_congestion = 0.5

        # 单位拥堵成本越低评分越高
        if unit_congestion <= 0:
            return 10.0
        elif unit_congestion <= 0.1:
            return 9.0
        elif unit_congestion <= 0.3:
            return 7.0
        elif unit_congestion <= 0.5:
            return 5.0
        elif unit_congestion <= 1.0:
            return 3.0
        else:
            return 1.0

    def _calculate_complexity_score(self, node_count: int) -> float:
        """计算复杂度评分（0-10分）"""
        # 节点数越少评分越高
        if node_count <= 3:
            return 10.0
        elif node_count <= 5:
            return 8.0
        elif node_count <= 8:
            return 6.0
        elif node_count <= 12:
            return 4.0
        else:
            return 2.0

    def _calculate_time_sensitivity_score(self, path_result: PathResult) -> float:
        """计算时间敏感性评分"""
        # 通过路径段拥堵系数方差评估时间稳定性
        if not path_result.segments:
            return 5.0

        congestion_factors = [seg.congestion_factor for seg in path_result.segments]

        if len(congestion_factors) <= 1:
            return 5.0

        # 计算变异系数：标准差/平均值
        import numpy as np
        mean_congestion = np.mean(congestion_factors)
        std_congestion = np.std(congestion_factors)

        if mean_congestion <= 0:
            return 10.0

        cv = std_congestion / mean_congestion

        # 变异系数越小（越稳定）评分越高
        if cv <= 0.1:
            return 10.0
        elif cv <= 0.3:
            return 8.0
        elif cv <= 0.5:
            return 6.0
        elif cv <= 1.0:
            return 4.0
        else:
            return 2.0

    def _get_rating(self, score: float) -> str:
        """根据综合评分获取评级"""
        if score >= self.score_ranges['excellent'][0]:
            return "优秀"
        elif score >= self.score_ranges['good'][0]:
            return "良好"
        elif score >= self.score_ranges['average'][0]:
            return "一般"
        elif score >= self.score_ranges['poor'][0]:
            return "较差"
        else:
            return "差"

    def _get_recommendation(self, rating: str, path_result: PathResult) -> str:
        """根据评级生成推荐建议"""
        recommendations = {
            "优秀": "强烈推荐！这条路径在距离、拥堵和稳定性方面表现优异。",
            "良好": "推荐使用。这条路径综合表现良好，适合大多数情况。",
            "一般": "可以考虑。这条路径在某些方面表现一般，可能需要根据具体需求选择。",
            "较差": "谨慎选择。这条路径存在明显缺点，建议考虑其他选项。",
            "差": "不推荐。这条路径在多个维度表现不佳，建议选择其他路径。"
        }

        base_recommendation = recommendations.get(rating, "无法评估")

        # 根据α值添加额外建议
        if path_result.alpha == 0:
            base_recommendation += " (当前α=0，优先考虑最短距离)"
        elif path_result.alpha >= 1.5:
            base_recommendation += " (当前α值较高，优先避开拥堵)"

        return base_recommendation

    def _identify_strengths(self, distance_score: float, congestion_score: float) -> List[str]:
        """识别路径优势"""
        strengths = []

        if distance_score >= 8.0:
            strengths.append("距离优势明显")
        elif distance_score >= 6.0:
            strengths.append("距离适中")

        if congestion_score >= 8.0:
            strengths.append("拥堵程度低")
        elif congestion_score >= 6.0:
            strengths.append("拥堵控制良好")

        if not strengths:
            strengths.append("无显著优势")

        return strengths

    def _identify_weaknesses(self, distance_score: float, congestion_score: float) -> List[str]:
        """识别路径劣势"""
        weaknesses = []

        if distance_score <= 4.0:
            weaknesses.append("距离较长")
        elif distance_score <= 6.0:
            weaknesses.append("距离偏长")

        if congestion_score <= 4.0:
            weaknesses.append("拥堵严重")
        elif congestion_score <= 6.0:
            weaknesses.append("存在拥堵")

        if not weaknesses:
            weaknesses.append("无明显劣势")

        return weaknesses

    def _get_improvement_suggestions(self, distance_score: float,
                                   congestion_score: float, alpha: float) -> List[str]:
        """获取改进建议"""
        suggestions = []

        if distance_score < 6.0:
            suggestions.append("考虑选择距离更短的路线")

        if congestion_score < 6.0:
            if alpha < 1.0:
                suggestions.append("尝试增大α值以避开拥堵")
            else:
                suggestions.append("当前α值已较高，拥堵仍然存在，可能需要寻找替代路线")

        if distance_score >= 8.0 and congestion_score >= 8.0:
            suggestions.append("当前路径已接近最优，无需调整")

        if not suggestions:
            suggestions.append("路径表现良好，保持当前设置即可")

        return suggestions

    def _generate_recommendation_reason(self, best_by_score, best_by_distance,
                                      best_by_cost) -> str:
        """生成推荐理由"""
        best_alpha = best_by_score[0]
        best_score = best_by_score[1]['weighted_score']

        # 判断是否与最短距离路径相同
        if best_alpha == best_by_distance[0]:
            return f"α={best_alpha}的路径既是综合评分最高({best_score:.1f})，也是距离最短，强烈推荐"

        # 判断是否与最低成本路径相同
        if best_alpha == best_by_cost[0]:
            return f"α={best_alpha}的路径既是综合评分最高({best_score:.1f})，也是总成本最低，推荐使用"

        # 一般情况
        return f"α={best_alpha}的路径综合评分最高({best_score:.1f})，在距离、拥堵和稳定性之间取得了最佳平衡"

    def _analyze_tradeoffs(self, evaluations: Dict[float, Dict]) -> Dict[str, Any]:
        """分析不同α值之间的权衡"""
        if len(evaluations) < 2:
            return {"message": "需要至少两个α值进行权衡分析"}

        alphas = sorted(evaluations.keys())
        analysis = []

        for i in range(len(alphas) - 1):
            alpha1, alpha2 = alphas[i], alphas[i + 1]
            eval1, eval2 = evaluations[alpha1], evaluations[alpha2]

            distance_diff = eval2['total_distance'] - eval1['total_distance']
            congestion_diff = eval2['congestion_cost'] - eval1['congestion_cost']
            score_diff = eval2['weighted_score'] - eval1['weighted_score']

            if distance_diff > 0 and congestion_diff < 0:
                tradeoff = f"α从{alpha1}增加到{alpha2}: 距离增加{distance_diff:.1f}m，但拥堵减少{abs(congestion_diff):.1f}"
            elif distance_diff < 0 and congestion_diff > 0:
                tradeoff = f"α从{alpha1}增加到{alpha2}: 距离减少{abs(distance_diff):.1f}m，但拥堵增加{congestion_diff:.1f}"
            else:
                tradeoff = f"α从{alpha1}增加到{alpha2}: 距离变化{distance_diff:.1f}m，拥堵变化{congestion_diff:.1f}"

            analysis.append({
                "alpha_range": f"{alpha1}-{alpha2}",
                "tradeoff": tradeoff,
                "score_change": score_diff,
                "recommendation": "推荐增加α" if score_diff > 0 else "推荐减少α"
            })

        return {
            "tradeoffs": analysis,
            "summary": f"分析了{len(alphas)}个α值之间的{len(analysis)}个权衡关系"
        }

    def _analyze_alpha_sensitivity(self, evaluations: Dict[float, Dict]) -> Dict[str, Any]:
        """分析路径对α值的敏感性"""
        if len(evaluations) < 2:
            return {"message": "需要至少两个α值进行敏感性分析"}

        alphas = sorted(evaluations.keys())
        scores = [evaluations[alpha]['weighted_score'] for alpha in alphas]

        # 计算敏感性指标
        score_range = max(scores) - min(scores)
        avg_score = sum(scores) / len(scores)

        if score_range <= 1.0:
            sensitivity = "低敏感性：α值变化对综合评分影响不大"
        elif score_range <= 3.0:
            sensitivity = "中等敏感性：α值变化对综合评分有一定影响"
        else:
            sensitivity = "高敏感性：α值变化对综合评分影响显著"

        # 找到最优α区间
        max_score = max(scores)
        optimal_alphas = [alphas[i] for i, score in enumerate(scores) if score >= max_score - 0.5]

        return {
            "sensitivity_level": sensitivity,
            "score_range": round(score_range, 2),
            "average_score": round(avg_score, 2),
            "optimal_alpha_range": f"{min(optimal_alphas)}-{max(optimal_alphas)}",
            "optimal_score": round(max_score, 2),
            "recommendation": f"建议α值设置在{min(optimal_alphas)}-{max(optimal_alphas)}之间以获得最佳综合表现"
        }


# 默认评估器实例
default_evaluator = PathEvaluator()


if __name__ == "__main__":
    # 测试代码
    from algorithm.path_planner import PathPlanner
    import datetime

    print("=== 路径综合评估器测试 ===")

    evaluator = PathEvaluator()
    planner = PathPlanner()

    # 测试单条路径评估
    print("\n1. 单条路径评估测试:")
    time_obj = datetime.datetime(2024, 5, 20, 12, 0)
    path = planner.plan_path("TB1", "CA1", alpha=1.0, time=time_obj)

    if path:
        evaluation = evaluator.evaluate_single_path(path)
        print(f"综合评分: {evaluation['weighted_score']} ({evaluation['rating']})")
        print(f"推荐建议: {evaluation['recommendation']}")
        print(f"优势: {', '.join(evaluation['strengths'])}")
        print(f"劣势: {', '.join(evaluation['weaknesses'])}")

    # 测试多条路径对比
    print("\n2. 多条路径对比测试:")
    comparison = planner.compare_paths("TB1", "CA1", time=time_obj)

    if comparison.comparisons:
        comparison_result = evaluator.compare_multiple_paths(comparison)
        best_alpha = comparison_result['recommendation']['alpha']
        print(f"推荐α值: {best_alpha}")
        print(f"推荐理由: {comparison_result['recommendation']['reason']}")

        # 显示权衡分析
        tradeoffs = comparison_result['tradeoff_analysis']['tradeoffs']
        if tradeoffs:
            print(f"\n权衡分析:")
            for item in tradeoffs[:3]:  # 只显示前3个
                print(f"  • {item['tradeoff']} (评分变化: {item['score_change']:.2f})")