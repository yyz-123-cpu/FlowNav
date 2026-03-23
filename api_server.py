#!/usr/bin/env python3
"""
FlowNav API 服务器
提供RESTful API接口，支持前端调用路径规划功能
"""

import sys
import json
import datetime
import argparse
import socket
import asyncio
import platform
import time
import os
from collections import defaultdict
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# 修复Windows上的socket错误
if platform.system() == 'Windows':
    # 使用SelectorEventLoopPolicy避免Windows上的socket错误
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# 导入项目模块
# 检查是否在PyInstaller打包的环境中运行
is_packaged = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

if is_packaged:
    # 在打包环境中，添加sys._MEIPASS到路径
    meipass_path = getattr(sys, '_MEIPASS', '')
    if meipass_path:
        sys.path.insert(0, meipass_path)
    print(f"[INFO] 打包环境: 添加 {meipass_path} 到Python路径")
else:
    # 在普通Python环境中，添加当前目录到路径
    sys.path.append('.')  # 确保可以导入项目模块

try:
    from algorithm.path_planner import PathPlanner, default_planner
    from algorithm.models import PathResult, PathComparison
    print("[SUCCESS] 成功导入FlowNav模块")
except ImportError as e:
    print(f"[ERROR] 导入FlowNav模块失败: {e}")
    if is_packaged:
        print(f"当前Python路径: {sys.path}")
        print(f"临时目录: {meipass_path}")
    else:
        print("请确保在项目根目录运行此脚本")
    sys.exit(1)

# 创建FastAPI应用
app = FastAPI(
    title="FlowNav API",
    description="校园动态导航系统API服务",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应限制来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API密钥验证中间件（可选）
@app.middleware("http")
async def api_key_auth(request: Request, call_next):
    """验证API密钥（如果设置了API_KEY环境变量）"""
    api_key = os.environ.get("API_KEY")

    # 如果没有设置API_KEY或为空字符串，跳过验证
    if not api_key or api_key.strip() == "":
        return await call_next(request)

    # 检查请求头中的API密钥
    provided_key = request.headers.get("X-API-Key")

    # 允许健康检查端点无需认证
    if request.url.path in ["/", "/api/health", "/docs", "/openapi.json"]:
        return await call_next(request)

    if not provided_key or provided_key != api_key:
        return JSONResponse(
            status_code=401,
            content={
                "success": False,
                "error": "无效或缺少API密钥",
                "detail": "请提供有效的X-API-Key请求头"
            }
        )

    return await call_next(request)

# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录HTTP请求和响应"""
    request_id = str(int(time.time() * 1000))[-8:]  # 生成简短的请求ID
    start_time = time.time()

    # 记录请求开始
    print(f"[{datetime.datetime.now().isoformat()}] [REQ:{request_id}] {request.method} {request.url.path}")

    # 处理请求
    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        # 记录响应
        print(f"[{datetime.datetime.now().isoformat()}] [RES:{request_id}] {request.method} {request.url.path} "
              f"status={response.status_code} duration={process_time:.3f}s")

        # 添加请求ID到响应头
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.3f}"

        return response
    except Exception as e:
        process_time = time.time() - start_time
        print(f"[{datetime.datetime.now().isoformat()}] [ERR:{request_id}] {request.method} {request.url.path} "
              f"error={str(e)} duration={process_time:.3f}s")
        raise

# 全局统计信息
api_stats = {
    "start_time": datetime.datetime.now().isoformat(),
    "requests": {
        "total": 0,
        "by_status": defaultdict(int),
        "by_endpoint": defaultdict(int),
        "response_times": []
    },
    "errors": {
        "total": 0,
        "by_type": defaultdict(int)
    }
}

# 全局路径规划器实例
planner = default_planner

# 请求/响应模型
class PlanPathRequest(BaseModel):
    start: str
    goal: str
    alpha: float = 1.0
    time: str  # ISO格式时间字符串

class ComparePathsRequest(BaseModel):
    start: str
    goal: str
    alphas: List[float]
    time: str  # ISO格式时间字符串

class AnalyzeRouteRequest(BaseModel):
    start: str
    goal: str
    time_points: List[str]  # ISO格式时间字符串列表

class ExportReportRequest(BaseModel):
    path_result: Dict[str, Any]
    format: str = "text"

# 全局异常处理器
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理未捕获的异常，返回统一的错误格式"""
    import traceback

    error_details = traceback.format_exc()
    request_id = request.headers.get("X-Request-ID", "unknown")

    print(f"[{datetime.datetime.now().isoformat()}] [UNHANDLED:{request_id}] "
          f"Unhandled exception: {str(exc)}")
    print(f"[{datetime.datetime.now().isoformat()}] [UNHANDLED:{request_id}] "
          f"Exception details:\n{error_details}")

    # 如果是HTTPException，直接传递
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": exc.detail,
                "request_id": request_id
            }
        )

    # 其他未处理异常
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "服务器内部错误",
            "request_id": request_id,
            "detail": str(exc)  # 在生产环境中可能应该隐藏
        }
    )

# API端点
@app.get("/")
async def root():
    """API根端点"""
    return {
        "name": "FlowNav API",
        "version": "1.0.0",
        "description": "校园动态导航系统API服务",
        "endpoints": {
            "/api/nodes": "获取校园节点列表",
            "/api/campus-info": "获取校园信息",
            "/api/plan-path": "路径规划",
            "/api/compare-paths": "路径比较",
            "/api/analyze-route": "路线分析",
            "/api/export-report": "导出报告",
            "/api/health": "健康检查"
        }
    }

@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    try:
        # 测试规划器是否正常工作
        info = planner.get_campus_info()
        return {
            "status": "healthy",
            "timestamp": datetime.datetime.now().isoformat(),
            "system_info": {
                "graph_nodes": info.get("graph_info", {}).get("node_count", 0),
                "graph_edges": info.get("graph_info", {}).get("edge_count", 0),
                "rule_engine_valid": info.get("rule_engine_info", {}).get("valid", False)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"系统异常: {str(e)}")

@app.get("/api/nodes")
async def get_campus_nodes():
    """获取校园节点列表"""
    try:
        info = planner.get_campus_info()
        key_nodes = info.get("key_nodes", {})

        # 将所有节点合并到一个列表中
        all_nodes = []
        for category, nodes in key_nodes.items():
            for node in nodes:
                node["category"] = category
                all_nodes.append(node)

        # 添加节点类型映射
        node_types = {
            "teaching_building": "教学楼",
            "cafeteria": "食堂",
            "dormitory": "宿舍楼",
            "library": "图书馆",
            "gate": "校门",
            "sports": "运动场",
            "junction": "交叉点"
        }

        # 为每个节点添加中文类型
        for node in all_nodes:
            node["type_name"] = node_types.get(node["type"], "未知")

        return {
            "success": True,
            "nodes": all_nodes,
            "count": len(all_nodes),
            "categories": list(key_nodes.keys())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取节点数据失败: {str(e)}")

@app.get("/api/campus-info")
async def get_campus_info():
    """获取校园信息"""
    try:
        info = planner.get_campus_info()
        return {
            "success": True,
            "data": info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取校园信息失败: {str(e)}")

@app.post("/api/plan-path")
async def plan_path(request: PlanPathRequest):
    """路径规划"""
    try:
        # 解析时间
        try:
            time_obj = datetime.datetime.fromisoformat(request.time.replace('Z', '+00:00'))
        except ValueError:
            time_obj = datetime.datetime.now()

        # 验证参数
        if request.alpha < 0:
            raise HTTPException(status_code=400, detail="alpha参数不能为负数")

        # 执行路径规划
        path = planner.plan_path(request.start, request.goal, request.alpha, time_obj)

        if not path:
            raise HTTPException(status_code=404, detail=f"未找到从 {request.start} 到 {request.goal} 的路径")

        # 转换为字典格式
        result = {
            "start": request.start,
            "goal": request.goal,
            "alpha": request.alpha,
            "time": time_obj.isoformat(),
            "nodes": path.nodes,
            "distance": path.total_distance,
            "totalActualCost": path.total_actual_cost,
            "congestionCost": path.congestion_cost,
            "averageCongestion": path.average_congestion,
            "nodeCount": len(path.nodes),
            "edgeCount": len(path.edges),
            "segmentDetails": []
        }

        # 添加路径段详细信息
        if hasattr(path, 'segments') and path.segments:
            for segment in path.segments:
                result["segmentDetails"].append({
                    "from": segment.edge.from_node if hasattr(segment.edge, 'from_node') else "未知",
                    "to": segment.edge.to_node if hasattr(segment.edge, 'to_node') else "未知",
                    "distance": segment.distance,
                    "congestionFactor": segment.congestion_factor,
                    "actualCost": segment.actual_cost
                })

        return {
            "success": True,
            "data": result
        }

    except HTTPException:
        raise
    except ValueError as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] 路径规划参数错误: {str(e)}")
        print(f"[ERROR] 异常详情:\n{error_details}")
        raise HTTPException(status_code=400, detail=f"参数错误: {str(e)}")
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] 路径规划失败: {str(e)}")
        print(f"[ERROR] 异常详情:\n{error_details}")
        raise HTTPException(status_code=500, detail=f"路径规划失败: {str(e)}")

@app.post("/api/compare-paths")
async def compare_paths(request: ComparePathsRequest):
    """路径比较"""
    try:
        # 解析时间
        try:
            time_obj = datetime.datetime.fromisoformat(request.time.replace('Z', '+00:00'))
        except ValueError:
            time_obj = datetime.datetime.now()

        # 验证α值
        invalid_alphas = [a for a in request.alphas if a < 0]
        if invalid_alphas:
            raise HTTPException(status_code=400, detail=f"α值不能为负数: {invalid_alphas}")

        # 执行路径比较
        comparison = planner.compare_paths(request.start, request.goal, request.alphas, time_obj)

        if not comparison or not hasattr(comparison, 'comparisons'):
            raise HTTPException(status_code=500, detail="路径比较失败")

        # 构建响应
        comparisons = {}
        for alpha, path in comparison.comparisons.items():
            comparisons[alpha] = {
                "nodes": path.nodes,
                "distance": path.total_distance,
                "totalActualCost": path.total_actual_cost,
                "congestionCost": path.congestion_cost,
                "averageCongestion": path.average_congestion,
                "nodeCount": len(path.nodes)
            }

        # 查找最佳路径
        best_by_distance = None
        best_by_cost = None

        if comparisons:
            # 按距离排序
            sorted_by_distance = sorted(comparisons.items(), key=lambda x: x[1]["distance"])
            if sorted_by_distance:
                best_by_distance = {
                    "alpha": sorted_by_distance[0][0],
                    "distance": sorted_by_distance[0][1]["distance"]
                }

            # 按成本排序
            sorted_by_cost = sorted(comparisons.items(), key=lambda x: x[1]["totalActualCost"])
            if sorted_by_cost:
                best_by_cost = {
                    "alpha": sorted_by_cost[0][0],
                    "cost": sorted_by_cost[0][1]["totalActualCost"]
                }

        result = {
            "start": request.start,
            "goal": request.goal,
            "time": time_obj.isoformat(),
            "comparisons": comparisons,
            "summary": {
                "bestByDistance": best_by_distance,
                "bestByCost": best_by_cost
            }
        }

        return {
            "success": True,
            "data": result
        }

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"参数错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"路径比较失败: {str(e)}")

@app.post("/api/analyze-route")
async def analyze_route(request: AnalyzeRouteRequest):
    """路线分析"""
    try:
        # 解析时间点
        time_points = []
        for time_str in request.time_points:
            try:
                time_obj = datetime.datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                time_points.append(time_obj)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"无效的时间格式: {time_str}")

        if not time_points:
            raise HTTPException(status_code=400, detail="至少需要一个有效的时间点")

        # 执行路线分析（使用默认α=1.0）
        analysis = planner.analyze_route(request.start, request.goal, time_points)

        if not analysis or 'analysis' not in analysis:
            raise HTTPException(status_code=500, detail="路线分析失败")

        # 构建响应
        analysis_results = []
        for item in analysis['analysis']:
            analysis_results.append({
                "time": item["time"],
                "time_str": item.get("time_str", item["time"]),
                "peak_period": item["peak_period"],
                "is_peak": item["is_peak"],
                "path": {
                    "nodes": item["path"]["nodes"],
                    "distance": item["path"]["distance"],
                    "cost": item["path"]["cost"],
                    "congestion_cost": item["path"]["congestion_cost"],
                    "average_congestion": item["path"]["average_congestion"]
                }
            })

        # 时间范围
        if time_points:
            min_time = min(time_points)
            max_time = max(time_points)
        else:
            min_time = max_time = datetime.datetime.now()

        result = {
            "start": request.start,
            "goal": request.goal,
            "analysis": analysis_results,
            "time_range": {
                "start": min_time.isoformat(),
                "end": max_time.isoformat(),
                "count": len(time_points)
            }
        }

        return {
            "success": True,
            "data": result
        }

    except HTTPException:
        raise
    except ValueError as e:
        # 处理参数验证错误（如节点不存在）
        raise HTTPException(status_code=400, detail=f"参数错误: {str(e)}")
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] 路线分析失败: {str(e)}")
        print(f"[ERROR] 异常详情:\n{error_details}")
        raise HTTPException(status_code=500, detail=f"路线分析失败: {str(e)}")

@app.post("/api/export-report")
async def export_report(request: ExportReportRequest):
    """导出报告"""
    try:
        # 获取路径结果
        path_result = request.path_result

        # 生成文本报告
        if request.format == "json":
            report = json.dumps(path_result, indent=2, ensure_ascii=False)
        else:
            # 文本格式报告
            report = "校园动态导航路径规划报告\n"
            report += "============================\n"
            report += f"起点: {path_result.get('start', '未知')}\n"
            report += f"终点: {path_result.get('goal', '未知')}\n"
            report += f"α值: {path_result.get('alpha', 1.0)}\n"

            # 格式化时间
            time_str = path_result.get('time', '')
            if time_str:
                try:
                    time_obj = datetime.datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                    report += f"时间: {time_obj.strftime('%Y-%m-%d %H:%M:%S')}\n"
                except:
                    report += f"时间: {time_str}\n"

            report += f"总距离: {path_result.get('distance', 0):.1f} 米\n"
            report += f"总成本: {path_result.get('totalActualCost', 0):.1f}\n"
            report += f"拥堵成本: {path_result.get('congestionCost', 0):.1f}\n"
            report += f"平均拥挤系数: {path_result.get('averageCongestion', 1.0):.2f}\n"

            nodes = path_result.get('nodes', [])
            if nodes:
                report += f"节点序列: {' → '.join(nodes)}\n"

        return {
            "success": True,
            "data": report,
            "format": request.format
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出报告失败: {str(e)}")


def is_port_available(host: str, port: int) -> bool:
    """检查端口是否可用"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result != 0  # 0表示端口被占用
    except:
        return False


def find_available_port(host: str, start_port: int, max_attempts: int = 10) -> int:
    """查找可用端口"""
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(host, port):
            return port
    return None


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="FlowNav API 服务器")
    parser.add_argument("--host", default="localhost", help="绑定主机 (默认: localhost)")
    parser.add_argument("--port", type=int, default=8000, help="绑定端口 (默认: 8000)")
    parser.add_argument("--max-port-attempts", type=int, default=10,
                       help="端口占用时最大尝试次数 (默认: 10)")
    return parser.parse_args()

def main():
    """API服务器主函数"""
    import uvicorn

    # 解析命令行参数
    args = parse_args()
    host = args.host
    port = args.port
    max_attempts = args.max_port_attempts

    # 检查端口是否可用
    if not is_port_available(host, port):
        print(f"[警告] 端口 {port} 已被占用，正在查找可用端口...")
        available_port = find_available_port(host, port + 1, max_attempts)

        if available_port is None:
            print(f"[错误] 未找到可用端口（尝试范围: {port+1}-{port+max_attempts}）")
            print("建议:")
            print("  1. 停止占用端口的进程")
            print("  2. 使用 --port 参数指定其他端口")
            print("  3. 增加 --max-port-attempts 参数值")
            sys.exit(1)

        print(f"[提示] 使用端口 {available_port} 代替 {port}")
        port = available_port

    print("=" * 60)
    print("FlowNav API 服务器")
    print("=" * 60)
    print("启动参数:")
    print(f"  主机: {host}")
    print(f"  端口: {port}")
    print(f"  API地址: http://{host}:{port}")
    print(f"  文档地址: http://{host}:{port}/docs")
    print("=" * 60)
    print("按 Ctrl+C 停止服务器")
    print("=" * 60)

    # Windows兼容性修复
    if platform.system() == 'Windows':
        print("[INFO] Windows系统: 应用兼容性修复")
        # 确保使用Selector事件循环
        try:
            # 显式设置事件循环
            loop = asyncio.get_event_loop_policy().new_event_loop()
            asyncio.set_event_loop(loop)

            # 对于Windows，使用localhost而不是127.0.0.1
            if host == "127.0.0.1":
                host = "localhost"
                print(f"[INFO] Windows: 主机改为 {host}")
        except Exception as e:
            print(f"[WARNING] Windows事件循环设置失败: {e}")

    # 运行Uvicorn服务器
    try:
        uvicorn.run(
            app,
            host=host,
            port=port,
            loop="asyncio",
            reload=False,
            log_level="info",
            http="auto"
        )
    except Exception as e:
        print(f"[ERROR] 服务器启动失败: {e}")
        if platform.system() == 'Windows':
            print("[TROUBLESHOOTING] Windows socket错误常见解决方案:")
            print("  1. 尝试使用 'localhost' 而不是 '127.0.0.1'")
            print("  2. 尝试使用 '0.0.0.0' 绑定所有接口（注意安全）")
            print("  3. 检查防火墙设置")
            print("  4. 尝试不同的端口（如8080、5000等）")
        sys.exit(1)


if __name__ == "__main__":
    main()