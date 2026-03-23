/* FlowNav 模拟数据服务 */

const MockData = {
    // 校园节点数据
    campusNodes: [
        { id: 'TB1', name: '第一教学楼', type: 'teaching_building', x: 100, y: 100 },
        { id: 'TB2', name: '第二教学楼', type: 'teaching_building', x: 200, y: 150 },
        { id: 'TB3', name: '第三教学楼', type: 'teaching_building', x: 300, y: 100 },
        { id: 'CA1', name: '第一食堂', type: 'cafeteria', x: 150, y: 300 },
        { id: 'CA2', name: '第二食堂', type: 'cafeteria', x: 250, y: 350 },
        { id: 'DO1', name: '第一宿舍楼', type: 'dormitory', x: 400, y: 200 },
        { id: 'D2', name: '第二宿舍楼', type: 'dormitory', x: 500, y: 250 },
        { id: 'LIB', name: '图书馆', type: 'library', x: 350, y: 400 },
        { id: 'G1', name: '西门', type: 'gate', x: 50, y: 200 },
        { id: 'G2', name: '东门', type: 'gate', x: 550, y: 100 },
        { id: 'S1', name: '运动场', type: 'sports', x: 400, y: 450 },
        { id: 'J1', name: '交叉点1', type: 'junction', x: 200, y: 200 },
        { id: 'J2', name: '交叉点2', type: 'junction', x: 300, y: 300 },
        { id: 'J3', name: '交叉点3', type: 'junction', x: 400, y: 350 },
    ],

    // 校园边（道路）数据
    campusEdges: [
        { from: 'TB1', to: 'J1', distance: 50, type: 'main_road' },
        { from: 'TB2', to: 'J1', distance: 40, type: 'main_road' },
        { from: 'TB3', to: 'J2', distance: 60, type: 'main_road' },
        { from: 'J1', to: 'CA1', distance: 80, type: 'main_road' },
        { from: 'J2', to: 'CA2', distance: 70, type: 'main_road' },
        { from: 'CA1', to: 'J2', distance: 90, type: 'branch_road' },
        { from: 'J2', to: 'DO1', distance: 100, type: 'main_road' },
        { from: 'DO1', to: 'LIB', distance: 80, type: 'small_road' },
        { from: 'LIB', to: 'S1', distance: 70, type: 'small_road' },
        { from: 'G1', to: 'TB1', distance: 60, type: 'main_road' },
        { from: 'G2', to: 'D2', distance: 80, type: 'main_road' },
        { from: 'D2', to: 'S1', distance: 90, type: 'branch_road' },
        { from: 'J1', to: 'J2', distance: 120, type: 'main_road' },
        { from: 'J2', to: 'J3', distance: 60, type: 'branch_road' },
        { from: 'J3', to: 'LIB', distance: 40, type: 'small_road' },
        { from: 'J3', to: 'CA1', distance: 100, type: 'branch_road' },
    ],

    // 高峰期定义
    peakPeriods: {
        'lunch': { name: '午餐高峰期', start: '11:50', end: '12:30', congestionRange: [4.0, 5.0] },
        'dinner': { name: '晚餐高峰期', start: '17:30', end: '18:30', congestionRange: [4.0, 5.0] },
        'evening_study': { name: '晚自习高峰期', start: '21:30', end: '22:10', congestionRange: [3.0, 4.0] }
    },

    // 确定性哈希函数（替代Math.random）
    deterministicHash: function(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // 转换为32位整数
        }
        return Math.abs(hash) / 2147483647; // 归一化到 [0, 1)
    },

    // 检查两个节点是否有直接连接
    hasDirectConnection: function(node1, node2) {
        return this.campusEdges.some(edge =>
            (edge.from === node1 && edge.to === node2) ||
            (edge.from === node2 && edge.to === node1)
        );
    },

    // 获取直接连接的距离
    getDirectDistance: function(node1, node2) {
        const edge = this.campusEdges.find(e =>
            (e.from === node1 && e.to === node2) ||
            (e.from === node2 && e.to === node1)
        );
        return edge ? edge.distance : null;
    },

    // 获取节点的所有邻居
    getNeighbors: function(node) {
        const neighbors = [];
        this.campusEdges.forEach(edge => {
            if (edge.from === node) {
                neighbors.push({ node: edge.to, distance: edge.distance });
            } else if (edge.to === node) {
                neighbors.push({ node: edge.from, distance: edge.distance });
            }
        });
        return neighbors;
    },

    // 查找通过共同节点的路径
    findPathThroughCommonNode: function(start, goal) {
        const startNeighbors = this.getNeighbors(start);
        const goalNeighbors = this.getNeighbors(goal);

        // 查找共同邻居
        for (const startNeighbor of startNeighbors) {
            for (const goalNeighbor of goalNeighbors) {
                if (startNeighbor.node === goalNeighbor.node) {
                    // 找到共同节点
                    const commonNode = startNeighbor.node;
                    const distance = startNeighbor.distance + goalNeighbor.distance;
                    return {
                        nodes: [start, commonNode, goal],
                        distance: distance,
                        hasCommon: true
                    };
                }
            }
        }

        return { nodes: null, distance: null, hasCommon: false };
    },

    // 模拟路径规划结果
    generatePathResult: function(start, goal, alpha, time) {
        // 根据参数生成不同的路径
        const pathId = `${start}-${goal}-${alpha}-${time}`;

        // 模拟不同的路径方案
        const pathOptions = {
            // TB1 -> CA1 路径
            'TB1-CA1-0-': { // α=0，最短距离（可能拥堵较高）
                nodes: ['TB1', 'J1', 'CA1'],
                distance: 130,
                baseCongestion: 2.0
            },
            'TB1-CA1-0.5-': { // α=0.5，稍长路径，拥堵稍低
                nodes: ['TB1', 'J1', 'J2', 'CA1'],
                distance: 260,
                baseCongestion: 1.9
            },
            'TB1-CA1-1-': { // α=1.0，避开拥堵
                nodes: ['TB1', 'J1', 'J2', 'CA1'],
                distance: 260,
                baseCongestion: 1.8
            },
            'TB1-CA1-1.2-': { // α=1.2，进一步避开拥堵
                nodes: ['TB1', 'J1', 'J2', 'DO1', 'CA1'],
                distance: 390,
                baseCongestion: 1.6
            },
            'TB1-CA1-1.5-': { // α=1.5，进一步避开拥堵
                nodes: ['TB1', 'J1', 'J2', 'DO1', 'CA1'],
                distance: 390,
                baseCongestion: 1.4
            },
            'TB1-CA1-2-': { // α=2.0，极力避开拥堵
                nodes: ['TB1', 'J1', 'J2', 'DO1', 'LIB', 'CA1'],
                distance: 460,
                baseCongestion: 1.2
            },
            // TB1 -> DO1 路径
            'TB1-DO1-0-': {
                nodes: ['TB1', 'J1', 'J2', 'DO1'],
                distance: 290,
                baseCongestion: 2.0  // 最短路径但拥堵较高
            },
            'TB1-DO1-0.5-': {
                nodes: ['TB1', 'J1', 'J2', 'DO1'],
                distance: 290,
                baseCongestion: 1.8  // 与α=0相同路径，拥堵稍低
            },
            'TB1-DO1-1-': {
                nodes: ['TB1', 'J1', 'CA1', 'J2', 'DO1'],
                distance: 320,
                baseCongestion: 1.5  // 较长路径但拥堵较低
            },
            'TB1-DO1-1.5-': {
                nodes: ['TB1', 'J1', 'CA1', 'J2', 'DO1'],
                distance: 320,
                baseCongestion: 1.3  // 与α=1.0相同路径，拥堵更低
            },
            // LIB -> DO1 路径
            'LIB-DO1-0-': {
                nodes: ['LIB', 'DO1'],
                distance: 80,
                baseCongestion: 2.0  // 最短路径但拥堵较高
            },
            'LIB-DO1-0.5-': {
                nodes: ['LIB', 'DO1'],
                distance: 80,
                baseCongestion: 1.8  // 与α=0相同路径，拥堵稍低
            },
            'LIB-DO1-1-': {
                nodes: ['LIB', 'J3', 'J2', 'DO1'],
                distance: 160,
                baseCongestion: 1.5  // 较长路径但拥堵较低
            },
            'LIB-DO1-1.5-': {
                nodes: ['LIB', 'J3', 'J2', 'DO1'],
                distance: 160,
                baseCongestion: 1.3  // 与α=1.0相同路径，拥堵更低
            },
        };

        // 查找匹配的路径方案，优先使用精确匹配，其次使用最接近的α预设，最后使用默认逻辑
        let pathKey = `${start}-${goal}-${alpha}-`;
        let pathConfig = pathOptions[pathKey];

        if (!pathConfig) {
            // 尝试找到最接近的α预设
            const prefix = `${start}-${goal}-`;
            let closestAlpha = null;
            let closestKey = null;
            let minDiff = Infinity;

            // 查找所有匹配前缀的键
            for (const key in pathOptions) {
                if (key.startsWith(prefix)) {
                    // 提取α值（键格式: "TB1-CA1-1.5-"）
                    const keyAlphaStr = key.substring(prefix.length).replace('-', '');
                    const keyAlpha = parseFloat(keyAlphaStr);
                    if (!isNaN(keyAlpha)) {
                        const diff = Math.abs(keyAlpha - alpha);
                        if (diff < minDiff) {
                            minDiff = diff;
                            closestAlpha = keyAlpha;
                            closestKey = key;
                        }
                    }
                }
            }

            if (closestKey) {
                // 使用最接近的α预设配置
                console.log(`未找到α=${alpha}的精确路径，使用最接近的α=${closestAlpha}路径`);
                pathConfig = pathOptions[closestKey];
            } else {
                // 没有预设路径，使用默认逻辑
                // 检查是否有直接连接
                const directDistance = this.getDirectDistance(start, goal);
                if (directDistance !== null) {
                    // 有直接连接，使用最短路径
                    pathConfig = {
                        nodes: [start, goal],
                        distance: directDistance,
                        baseCongestion: 1.0 + this.deterministicHash(`${pathId}-congestion`) * 0.5
                    };
                } else {
                    // 没有直接连接，尝试通过共同节点连接
                    const commonPath = this.findPathThroughCommonNode(start, goal);
                    if (commonPath.hasCommon) {
                        // 通过共同节点连接
                        pathConfig = {
                            nodes: commonPath.nodes,
                            distance: commonPath.distance,
                            baseCongestion: 1.0 + this.deterministicHash(`${pathId}-congestion`) * 0.5
                        };
                    } else {
                        // 没有共同节点，使用默认路径（可能经过交叉点）
                        pathConfig = {
                            nodes: [start, 'J1', 'J2', goal],
                            distance: 200 + this.deterministicHash(`${pathId}-distance`) * 100,
                            baseCongestion: 1.0 + this.deterministicHash(`${pathId}-congestion`) * 1.0
                        };
                    }
                }
            }
        }

        // 路径验证和清理
        let validatedNodes = pathConfig.nodes;
        const validationResult = this.PathValidator.validatePath(validatedNodes);

        if (!validationResult.valid) {
            console.warn(`路径验证失败: ${validationResult.errors.join(', ')}，尝试清理重复节点`);

            // 尝试清理重复节点
            validatedNodes = this.PathValidator.removeDuplicateNodes(validatedNodes);

            // 重新验证清理后的路径
            const revalidationResult = this.PathValidator.validatePath(validatedNodes);
            if (!revalidationResult.valid) {
                console.error(`路径清理后仍无效: ${revalidationResult.errors.join(', ')}，使用备用路径`);
                // 使用简单备用路径：起点 -> 终点（如果可能）
                if (this.hasDirectConnection(start, goal)) {
                    validatedNodes = [start, goal];
                } else {
                    // 使用默认交叉点路径
                    validatedNodes = [start, 'J1', 'J2', goal];
                }
            }

            // 更新pathConfig中的节点
            pathConfig.nodes = validatedNodes;
        } else {
            // 路径有效，但仍检查并清理可能的重复节点
            if (this.PathValidator.hasDuplicateNodes(validatedNodes)) {
                console.warn('路径包含重复节点，自动清理');
                validatedNodes = this.PathValidator.removeDuplicateNodes(validatedNodes);
                pathConfig.nodes = validatedNodes;
            }
        }

        // 根据时间调整拥堵系数
        const hour = new Date(time).getHours();
        const minute = new Date(time).getMinutes();
        const timeInMinutes = hour * 60 + minute;

        let timeFactor = 1.0;
        if ((timeInMinutes >= 11*60+50 && timeInMinutes <= 12*60+30) || // 午餐高峰期
            (timeInMinutes >= 17*60+30 && timeInMinutes <= 18*60+30)) { // 晚餐高峰期
            timeFactor = 4.0 + this.deterministicHash(`${pathId}-timefactor`);
        } else if (timeInMinutes >= 21*60+30 && timeInMinutes <= 22*60+10) { // 晚自习高峰期
            timeFactor = 3.0 + this.deterministicHash(`${pathId}-timefactor`);
        }

        // 计算最终拥堵系数（考虑基础拥堵和时间因素）
        const congestionFactor = pathConfig.baseCongestion * timeFactor;

        // 计算动态惩罚成本（与实际算法保持一致：非线性公式）
        const SENSITIVITY_FACTOR = 12.0; // 与实际算法一致
        const effectiveWeight = Math.pow(alpha, 1.5) * SENSITIVITY_FACTOR;
        const distance = pathConfig.distance;
        const actualCost = distance * (1 + effectiveWeight * (congestionFactor - 1));
        const congestionCost = actualCost - distance;

        return {
            id: pathId,
            start: start,
            goal: goal,
            alpha: alpha,
            time: new Date(time).toISOString(),
            nodes: pathConfig.nodes,
            distance: distance,
            totalActualCost: actualCost,
            congestionCost: congestionCost,
            averageCongestion: congestionFactor,
            segmentDetails: pathConfig.nodes.slice(0, -1).map((node, index) => ({
                from: node,
                to: pathConfig.nodes[index + 1],
                distance: distance / (pathConfig.nodes.length - 1),
                congestionFactor: congestionFactor * (0.8 + this.deterministicHash(`${pathId}-segment-${index}`) * 0.4), // 添加一些随机性
                actualCost: (distance / (pathConfig.nodes.length - 1)) * (1 + effectiveWeight * (congestionFactor * (0.8 + this.deterministicHash(`${pathId}-segment-${index}`) * 0.4) - 1))
            }))
        };
    },

    // 模拟路径比较结果
    generateComparisonResult: function(start, goal, alphas, time) {
        const comparisons = {};

        // 确保α值按升序排序，保证返回数据的一致性
        const sortedAlphas = [...alphas].sort((a, b) => a - b);

        sortedAlphas.forEach(alpha => {
            comparisons[alpha] = this.generatePathResult(start, goal, alpha, time);
        });

        return {
            start: start,
            goal: goal,
            time: new Date(time).toISOString(),
            comparisons: comparisons,
            summary: {
                bestByDistance: sortedAlphas.reduce((best, alpha) => {
                    const path = comparisons[alpha];
                    return (!best || path.distance < best.distance) ? { alpha, distance: path.distance } : best;
                }, null),
                bestByCost: sortedAlphas.reduce((best, alpha) => {
                    const path = comparisons[alpha];
                    return (!best || path.totalActualCost < best.cost) ? { alpha, cost: path.totalActualCost } : best;
                }, null),
                bestByCongestion: sortedAlphas.filter(a => a > 0).reduce((best, alpha) => {
                    const path = comparisons[alpha];
                    return (!best || path.congestionCost < best.congestion) ? { alpha, congestion: path.congestionCost } : best;
                }, null)
            }
        };
    },

    // 模拟路线分析结果
    generateRouteAnalysis: function(start, goal, timePoints) {
        const analysis = timePoints.map(time => {
            // 使用α=1.0进行分析
            const pathResult = this.generatePathResult(start, goal, 1.0, time);

            // 判断高峰期
            const hour = new Date(time).getHours();
            const minute = new Date(time).getMinutes();
            const timeInMinutes = hour * 60 + minute;

            let peakPeriod = '平峰期';
            let isPeak = false;

            if ((timeInMinutes >= 11*60+50 && timeInMinutes <= 12*60+30) ||
                (timeInMinutes >= 17*60+30 && timeInMinutes <= 18*60+30)) {
                peakPeriod = '就餐高峰期';
                isPeak = true;
            } else if (timeInMinutes >= 21*60+30 && timeInMinutes <= 22*60+10) {
                peakPeriod = '晚自习高峰期';
                isPeak = true;
            }

            return {
                time: new Date(time).toISOString(),
                time_str: new Date(time).toLocaleString('zh-CN'),
                peak_period: peakPeriod,
                is_peak: isPeak,
                path: {
                    nodes: pathResult.nodes,
                    distance: pathResult.distance,
                    cost: pathResult.totalActualCost,
                    congestion_cost: pathResult.congestionCost,
                    average_congestion: pathResult.averageCongestion
                }
            };
        });

        return {
            start: start,
            goal: goal,
            analysis: analysis,
            time_range: {
                start: new Date(Math.min(...timePoints.map(t => new Date(t).getTime()))).toISOString(),
                end: new Date(Math.max(...timePoints.map(t => new Date(t).getTime()))).toISOString(),
                count: timePoints.length
            }
        };
    },

    // 模拟校园信息
    getCampusInfo: function() {
        return {
            graph_info: {
                node_count: this.campusNodes.length,
                edge_count: this.campusEdges.length,
                is_connected: true
            },
            rule_engine_info: {
                valid: true,
                peak_periods: Object.keys(this.peakPeriods).length,
                description: '时空规则引擎（模拟数据）'
            },
            key_nodes: {
                teaching_buildings: this.campusNodes.filter(n => n.type === 'teaching_building'),
                cafeterias: this.campusNodes.filter(n => n.type === 'cafeteria'),
                dormitories: this.campusNodes.filter(n => n.type === 'dormitory'),
                libraries: this.campusNodes.filter(n => n.type === 'library')
            },
            algorithm_info: {
                name: '动态惩罚A*算法',
                formula: 'g_new(e) = d(e) × [1 + α × (C(e,t) - 1)]',
                description: '考虑时间相关拥堵系数和用户偏好权重的改进A*算法'
            }
        };
    },

    // 路径验证器
    PathValidator: {
        // 验证节点是否重复
        hasDuplicateNodes: function(nodes) {
            const seen = new Set();
            for (const node of nodes) {
                if (seen.has(node)) {
                    return true;
                }
                seen.add(node);
            }
            return false;
        },

        // 验证边是否存在
        validateEdgesExist: function(nodes) {
            const edges = MockData.campusEdges;
            for (let i = 0; i < nodes.length - 1; i++) {
                const from = nodes[i];
                const to = nodes[i + 1];
                const edgeExists = edges.some(e =>
                    (e.from === from && e.to === to) ||
                    (e.from === to && e.to === from)
                );
                if (!edgeExists) {
                    return { valid: false, missingEdge: `${from}->${to}` };
                }
            }
            return { valid: true, missingEdge: null };
        },

        // 清理重复节点
        removeDuplicateNodes: function(nodes) {
            const seen = new Set();
            const cleaned = [];
            let hasDuplicates = false;

            for (const node of nodes) {
                if (!seen.has(node)) {
                    seen.add(node);
                    cleaned.push(node);
                } else {
                    hasDuplicates = true;
                    console.warn(`检测到重复节点: ${node}，已自动移除`);
                }
            }

            // 确保路径至少有起点和终点
            if (cleaned.length < 2) {
                console.error('清理后路径无效，节点数不足2个');
                return nodes; // 返回原始路径
            }

            if (hasDuplicates) {
                console.log(`路径清理完成: 原始 ${nodes.length} 个节点 → 清理后 ${cleaned.length} 个节点`);
            }

            return cleaned;
        },

        // 完整路径验证
        validatePath: function(nodes) {
            // 检查节点数量
            if (!nodes || nodes.length < 2) {
                return { valid: false, errors: ['路径至少需要2个节点'] };
            }

            // 检查重复节点
            if (this.hasDuplicateNodes(nodes)) {
                return { valid: false, errors: ['路径包含重复节点'] };
            }

            // 检查边存在性
            const edgeCheck = this.validateEdgesExist(nodes);
            if (!edgeCheck.valid) {
                return { valid: false, errors: [`边 ${edgeCheck.missingEdge} 不存在`] };
            }

            return { valid: true, errors: [] };
        }
    },

    // 模拟API延迟
    simulateDelay: function(ms = 500) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
};