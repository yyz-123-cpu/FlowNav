/* FlowNav 前端应用 - Vue.js 主文件 */

// 初始化ECharts实例
let chartInstance = null;

// 创建Vue应用
const { createApp } = Vue;

const app = createApp({
    data() {
        return {
            // 应用状态
            activeTab: 'planning',
            isLoading: false,
            apiConnected: false,

            // 校园数据
            campusNodes: [],
            campusInfo: null,

            // 路径规划参数
            startNode: 'TB1',
            goalNode: 'CA1',
            alpha: 1.0,
            planTime: this.getCurrentDateTime(),

            // 路径对比参数
            compareStart: 'TB1',
            compareGoal: 'CA1',
            alphaList: '0, 0.5, 1.0, 1.5, 2.0',

            // 时间分析参数
            analysisStart: 'TB1',
            analysisGoal: 'CA1',
            analysisTimes: [
                { time: '08:00', label: '早上' },
                { time: '12:00', label: '中午' },
                { time: '18:00', label: '晚餐' },
                { time: '21:45', label: '晚自习' }
            ],

            // 当前结果
            currentPath: null,
            comparisonResults: null,
            analysisResults: null,

            // 图表选项
            chartOption: null
        };
    },

    computed: {
        // 解析α值列表
        parsedAlphas() {
            try {
                return this.alphaList.split(',').map(a => parseFloat(a.trim())).filter(a => !isNaN(a));
            } catch (error) {
                return [0, 0.5, 1.0, 1.5, 2.0];
            }
        }
    },

    watch: {
        // 监听标签页切换，更新图表显示
        activeTab(newTab, oldTab) {
            console.log(`标签页切换: ${oldTab} -> ${newTab}`);

            // 延迟一点确保DOM更新完成
            setTimeout(() => {
                this.updateChartForTab();
            }, 50);
        }
    },

    async mounted() {
        console.log('Vue应用开始挂载...');

        try {
            // 检查Vue是否可用
            if (typeof Vue === 'undefined') {
                console.error('Vue未加载！请检查CDN链接');
                throw new Error('Vue.js未加载，请检查CDN链接或网络连接');
            }

            console.log('Vue版本:', Vue.version);

            // 初始化应用
            await this.initializeApp();

            // 初始化图表
            this.initChart();

            // 测试API连接
            await this.testApiConnection();

            // 加载初始数据（路径规划）
            await this.planPath();

            console.log('Vue应用挂载完成');
        } catch (error) {
            console.error('Vue应用初始化失败:', error);
            this.showError(`应用初始化失败: ${error.message}`);

            // 设置默认数据以便应用仍能运行
            this.campusNodes = [];
            this.currentPath = null;

            // 尝试从MockData获取数据（如果可用）
            if (typeof MockData !== 'undefined' && MockData.campusNodes) {
                this.campusNodes = MockData.campusNodes;
            }
        }
    },

    methods: {
        // 获取当前日期时间（用于时间输入）
        getCurrentDateTime() {
            const now = new Date();
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            return `${year}-${month}-${day}T${hours}:${minutes}`;
        },

        // 设置当前时间
        setCurrentTime() {
            this.planTime = this.getCurrentDateTime();
        },

        // 添加分析时间点
        addAnalysisTime() {
            this.analysisTimes.push({ time: '12:00', label: '新时间点' });
        },

        // 移除分析时间点
        removeAnalysisTime(index) {
            this.analysisTimes.splice(index, 1);
        },

        // 后端到前端节点ID映射（反向映射）
        getDisplayNodeId(backendNodeId) {
            // 后端ID -> 前端显示ID映射
            const reverseMapping = {
                'SP1': 'S1',      // 运动场
                'GATE_S': 'G1',   // 西门
                'GATE_E': 'G2',   // 东门
                'DO2': 'D2',      // 第二宿舍楼
                'X1': 'J1',       // 交叉点1
                'X2': 'J2',       // 交叉点2
                'X3': 'J3',       // 交叉点3
                // 其他交叉点保持原样
            };
            return reverseMapping[backendNodeId] || backendNodeId;
        },

        // 获取节点显示名称
        getNodeName(nodeId) {
            // 首先尝试映射到前端ID
            const displayId = this.getDisplayNodeId(nodeId);
            const node = this.campusNodes.find(n => n.id === displayId);
            if (node) {
                return node.name;
            }

            // 后备名称映射（对于未在campusNodes中定义的节点）
            const fallbackNames = {
                // 交叉点
                'X1': '交叉点1', 'X2': '交叉点2', 'X3': '交叉点3', 'X4': '交叉点4', 'X5': '交叉点5',
                'TC': '教学中心', 'CC': '食堂中心', 'DC': '宿舍中心', 'LC': '图书馆广场',
                'J1': '交叉点1', 'J2': '交叉点2', 'J3': '交叉点3',
                // 教学楼
                'TB1': '第一教学楼', 'TB2': '第二教学楼', 'TB3': '第三教学楼',
                // 食堂
                'CA1': '第一食堂', 'CA2': '第二食堂',
                // 宿舍
                'DO1': '第一宿舍楼', 'DO2': '第二宿舍楼', 'DO3': '第三宿舍楼', 'DO4': '第四宿舍楼',
                // 图书馆
                'LIB': '中央图书馆',
                // 运动场
                'SP1': '田径场', 'SP2': '篮球场', 'S1': '运动场',
                // 校门
                'GATE_N': '北门', 'GATE_S': '南门', 'GATE_E': '东门', 'GATE_W': '西门',
                'G1': '西门', 'G2': '东门',
                // 其他
                'D2': '第二宿舍楼'
            };

            return fallbackNames[displayId] || fallbackNames[nodeId] || displayId;
        },

        // 从时间字符串中提取HH:MM格式的时间
        extractTimeFromString(timeStr) {
            if (!timeStr) return '';

            // 如果包含空格则取时间部分（处理后端返回的完整时间戳）
            const parts = timeStr.split(' ');
            const timePart = parts.length > 1 ? parts[1] : timeStr;

            // 提取HH:MM格式（去除秒部分）
            const timeMatch = timePart.match(/^(\d{1,2}:\d{2})/);
            return timeMatch ? timeMatch[1] : timePart;
        },

        // 验证高峰期标记是否合理（凌晨时段应为平峰期）
        validatePeakPeriod(timeStr, isPeak) {
            if (!timeStr) return isPeak; // 如果没有时间字符串，保持原样

            // 提取小时
            const timeMatch = timeStr.match(/^(\d{1,2}):(\d{2})/);
            if (!timeMatch) return isPeak;

            const hour = parseInt(timeMatch[1], 10);

            // 凌晨0点到6点应该是平峰期
            if (hour >= 0 && hour < 6) {
                console.log(`高峰期验证: 时间 ${timeStr} (${hour}时) 为凌晨时段，强制设为平峰期`);
                return false; // 强制设为平峰期
            }

            // 其他时间段保持原样
            console.log(`高峰期验证: 时间 ${timeStr} (${hour}时) 高峰期标记为 ${isPeak}`);
            return isPeak;
        },

        // 根据当前标签页更新图表
        updateChartForTab() {
            if (!chartInstance) return;

            switch (this.activeTab) {
                case 'planning':
                    if (this.currentPath) {
                        this.updatePathChart();
                    } else {
                        // 显示空图表
                        this.initChart();
                    }
                    break;
                case 'comparison':
                    if (this.comparisonResults) {
                        this.updateComparisonChart();
                    } else {
                        this.initChart();
                    }
                    break;
                case 'analysis':
                    if (this.analysisResults) {
                        this.updateAnalysisChart();
                    } else {
                        this.initChart();
                    }
                    break;
                case 'about':
                    // 关于页面可以显示系统架构图或保持空图表
                    this.initChart();
                    break;
                default:
                    this.initChart();
            }
        },

        // 初始化应用
        async initializeApp() {
            try {
                // 获取校园节点
                const nodesResult = await ApiService.getCampusNodes();
                if (nodesResult.success) {
                    // API返回格式: {success: true, nodes: [...], count: ..., categories: [...]}
                    // 模拟数据返回格式: 直接是节点数组
                    this.campusNodes = nodesResult.data.nodes || nodesResult.data;
                    console.log(`加载节点数据: ${this.campusNodes.length}个节点，来源: ${nodesResult.source}`);
                }

                // 获取校园信息
                const infoResult = await ApiService.getCampusInfo();
                if (infoResult.success) {
                    // API返回格式: {success: true, data: {...}}
                    // 模拟数据返回格式: 直接是校园信息对象
                    this.campusInfo = infoResult.data.data || infoResult.data;
                    console.log('校园信息加载成功');
                }
            } catch (error) {
                console.error('初始化失败:', error);
                this.showError('应用初始化失败，使用模拟数据');
            }
        },

        // 测试API连接
        async testApiConnection() {
            const result = await ApiService.testConnection();
            this.apiConnected = result.connected;

            if (!this.apiConnected && !ApiService.config.useMockData) {
                this.showWarning('无法连接到后端API，已切换到模拟数据模式');
                ApiService.setMockMode(true);
            }
        },

        // 切换API模式
        async toggleApiMode() {
            const newMode = !ApiService.config.useMockData;
            ApiService.setMockMode(newMode);

            // 测试新模式的连接
            await this.testApiConnection();

            if (newMode) {
                this.showInfo('已切换到模拟数据模式');
            } else {
                this.showInfo('尝试使用真实API模式');
            }
        },

        // 路径规划
        async planPath() {
            // 检查起点和终点是否相同
            if (this.startNode === this.goalNode) {
                this.showWarning('起点和终点相同，无需路径规划');
                return;
            }

            this.isLoading = true;
            try {
                // 解析时间
                const time = new Date(this.planTime);

                // 调用API
                const result = await ApiService.planPath(
                    this.startNode,
                    this.goalNode,
                    parseFloat(this.alpha),
                    time
                );

                if (result.success) {
                    // 调试：记录API返回的数据结构
                    console.log('API路径规划结果:', result);
                    console.log('result.data:', result.data);
                    console.log('result.data节点:', result.data.nodes);
                    console.log('result.data距离:', result.data.distance);
                    console.log('result.data总成本:', result.data.totalActualCost);
                    console.log('result.data拥堵成本:', result.data.congestionCost);
                    console.log('result.data平均拥堵:', result.data.averageCongestion);

                    // 安全提取API返回的数据，提供默认值并确保数值类型
                    const data = result.data || {};
                    const nodes = data.nodes || [];
                    const distance = parseFloat(data.distance) || 0;
                    const totalActualCost = parseFloat(data.totalActualCost) || 0;
                    const congestionCost = parseFloat(data.congestionCost) || 0;
                    const averageCongestion = parseFloat(data.averageCongestion) || 1.0;
                    const segmentDetails = data.segmentDetails || [];

                    this.currentPath = {
                        start: this.startNode,
                        goal: this.goalNode,
                        alpha: parseFloat(this.alpha),
                        time: this.planTime,
                        nodes: nodes,
                        distance: distance,
                        cost: totalActualCost,
                        congestionCost: congestionCost,
                        avgCongestion: averageCongestion,
                        nodeCount: nodes.length,
                        segmentDetails: segmentDetails
                    };

                    console.log('设置的currentPath:', this.currentPath);

                    // 更新图表
                    this.updatePathChart();

                    this.showSuccess('路径规划成功');
                } else {
                    // 使用分类后的错误信息（如果存在）
                    if (result.errorInfo) {
                        this.showDetailedError('路径规划失败', result.errorInfo);
                    } else {
                        this.showError(`路径规划失败: ${result.error || '未知错误'}`);
                    }
                }
            } catch (error) {
                console.error('路径规划异常:', error);
                this.showError('路径规划过程中发生错误');
            } finally {
                this.isLoading = false;
            }
        },

        // 路径对比
        async comparePaths() {
            // 检查起点和终点是否相同
            if (this.compareStart === this.compareGoal) {
                this.showWarning('起点和终点相同，无需路径对比');
                return;
            }

            this.isLoading = true;
            try {
                // 使用当前时间
                const time = new Date();

                // 调用API
                const result = await ApiService.comparePaths(
                    this.compareStart,
                    this.compareGoal,
                    this.parsedAlphas,
                    time
                );

                if (result.success) {
                    // 调试：记录API返回的对比结果数据结构
                    console.log('API路径对比结果:', result);
                    console.log('result.data:', result.data);
                    console.log('result.data.comparisons:', result.data?.comparisons);

                    // 安全提取数据
                    const data = result.data || {};
                    const comparisons = data.comparisons || {};

                    console.log(`对比结果数量: ${Object.keys(comparisons).length}`);
                    console.log('对比结果键:', Object.keys(comparisons));

                    this.comparisonResults = Object.entries(comparisons).map(([alpha, path]) => {
                        console.log(`α=${alpha} 的路径数据:`, path);
                        // 安全提取路径数据，提供默认值并确保数值类型
                        const safePath = path || {};

                        // 调试每个字段
                        console.log(`α=${alpha} 节点:`, safePath.nodes);
                        console.log(`α=${alpha} 距离:`, safePath.distance);
                        console.log(`α=${alpha} 总成本:`, safePath.totalActualCost);
                        console.log(`α=${alpha} 拥堵成本:`, safePath.congestionCost);
                        console.log(`α=${alpha} 平均拥挤:`, safePath.averageCongestion);

                        return {
                            alpha: parseFloat(alpha),
                            nodes: safePath.nodes || [],
                            distance: parseFloat(safePath.distance) || 0,
                            cost: parseFloat(safePath.totalActualCost) || 0,
                            congestionCost: parseFloat(safePath.congestionCost) || 0,
                            avgCongestion: parseFloat(safePath.averageCongestion) || 1.0,
                            nodeCount: (safePath.nodes || []).length
                        };
                    });

                    // 确保对比结果按α值升序排序
                    this.comparisonResults.sort((a, b) => a.alpha - b.alpha);

                    console.log('设置的comparisonResults (已排序):', this.comparisonResults);

                    // 检查是否有数据
                    if (this.comparisonResults.length === 0) {
                        console.warn('对比结果为空，请检查API返回的数据结构');
                    }

                    // 更新图表
                    this.updateComparisonChart();

                    this.showSuccess(`对比了 ${this.comparisonResults.length} 条路径`);
                } else {
                    // 使用分类后的错误信息（如果存在）
                    if (result.errorInfo) {
                        this.showDetailedError('路径对比失败', result.errorInfo);
                    } else {
                        this.showError(`路径对比失败: ${result.error || '未知错误'}`);
                    }
                }
            } catch (error) {
                console.error('路径对比异常:', error);
                this.showError('路径对比过程中发生错误');
            } finally {
                this.isLoading = false;
            }
        },

        // 路线分析
        async analyzeRoute() {
            // 检查起点和终点是否相同
            if (this.analysisStart === this.analysisGoal) {
                this.showWarning('起点和终点相同，无需路线分析');
                return;
            }

            this.isLoading = true;
            try {
                // 解析时间点（使用今天日期）
                const today = new Date();
                const year = today.getFullYear();
                const month = today.getMonth();
                const day = today.getDate();

                const timePoints = this.analysisTimes.map(t => {
                    const [hours, minutes] = t.time.split(':').map(Number);
                    return new Date(year, month, day, hours, minutes);
                });

                // 调用API
                const result = await ApiService.analyzeRoute(
                    this.analysisStart,
                    this.analysisGoal,
                    timePoints
                );

                if (result.success) {
                    // 调试：记录API返回的数据结构
                    console.log('API路线分析结果:', result);
                    console.log('result.data:', result.data);
                    console.log('result.data.analysis:', result.data?.analysis);

                    // 安全提取API返回的数据，提供默认值并确保数值类型
                    const data = result.data || {};
                    const analysisArray = data.analysis || [];

                    // 创建时间映射：将返回的时间与用户选择的时间匹配
                    const timeMap = new Map();

                    console.log('用户选择的时间点:', this.analysisTimes);
                    console.log('API返回的分析数据数量:', analysisArray.length);

                    // 首先尝试按索引匹配（假设顺序相同）
                    analysisArray.forEach((_item, index) => {
                        if (index < this.analysisTimes.length) {
                            timeMap.set(index, {
                                userTime: this.analysisTimes[index].time,
                                userLabel: this.analysisTimes[index].label
                            });
                        }
                    });

                    // 如果返回的时间有time_str，也尝试按时间值匹配
                    analysisArray.forEach((item, index) => {
                        const safeItem = item || {};
                        const timeStr = safeItem.time_str || '';

                        // 尝试从time_str中提取HH:MM格式
                        let extractedTime = '';
                        if (timeStr) {
                            const parts = timeStr.split(' ');
                            const timePart = parts.length > 1 ? parts[1] : timeStr;
                            const timeMatch = timePart.match(/^(\d{1,2}:\d{2})/);
                            extractedTime = timeMatch ? timeMatch[1] : timePart;
                        }

                        // 如果提取到时间，尝试在analysisTimes中查找匹配
                        if (extractedTime) {
                            const matchingTime = this.analysisTimes.find(t => t.time === extractedTime);
                            if (matchingTime && !timeMap.has(index)) {
                                timeMap.set(index, {
                                    userTime: matchingTime.time,
                                    userLabel: matchingTime.label
                                });
                            }
                        }
                    });

                    console.log('时间映射结果:');
                    timeMap.forEach((value, key) => {
                        console.log(`  索引 ${key}: 用户时间=${value.userTime}, 用户标签=${value.userLabel}`);
                    });

                    this.analysisResults = analysisArray.map((item, index) => {
                        const safeItem = item || {};
                        const safePath = safeItem.path || {};

                        // 获取匹配的用户时间
                        const timeInfo = timeMap.get(index);
                        const userTime = timeInfo ? timeInfo.userTime : '';
                        const userLabel = timeInfo ? timeInfo.userLabel : '';

                        return {
                            time: safeItem.time || '',
                            time_str: safeItem.time_str || '',
                            user_time: userTime, // 用户选择的时间
                            user_label: userLabel, // 用户选择的标签
                            display_time: userTime || (safeItem.time_str ? this.extractTimeFromString(safeItem.time_str) : ''),
                            peak_period: safeItem.peak_period || '',
                            // 验证高峰期标记是否合理（凌晨时段强制设为平峰期）
                            is_peak: this.validatePeakPeriod(
                                userTime || (safeItem.time_str ? this.extractTimeFromString(safeItem.time_str) : ''),
                                Boolean(safeItem.is_peak)
                            ),
                            path: {
                                nodes: safePath.nodes || [],
                                distance: parseFloat(safePath.distance) || 0,
                                cost: parseFloat(safePath.cost) || 0,
                                congestion_cost: parseFloat(safePath.congestion_cost) || 0,
                                average_congestion: parseFloat(safePath.average_congestion) || 1.0
                            }
                        };
                    });

                    console.log('设置的analysisResults:', this.analysisResults);

                    // 更新图表
                    this.updateAnalysisChart();

                    this.showSuccess(`分析了 ${this.analysisResults.length} 个时间点`);
                } else {
                    // 使用分类后的错误信息（如果存在）
                    if (result.errorInfo) {
                        this.showDetailedError('路线分析失败', result.errorInfo);
                    } else {
                        this.showError(`路线分析失败: ${result.error || '未知错误'}`);
                    }
                }
            } catch (error) {
                console.error('路线分析异常:', error);
                this.showError('路线分析过程中发生错误');
            } finally {
                this.isLoading = false;
            }
        },

        // 初始化图表
        initChart() {
            const chartDom = document.getElementById('chart');
            if (!chartDom) return;

            chartInstance = echarts.init(chartDom);

            // 初始空图表
            const initialOption = {
                title: {
                    text: 'FlowNav 校园动态导航系统',
                    subtext: '选择功能开始使用',
                    left: 'center'
                },
                tooltip: {
                    trigger: 'item'
                },
                legend: {
                    orient: 'vertical',
                    left: 'left'
                },
                series: [
                    {
                        name: '等待数据',
                        type: 'graph',
                        layout: 'none',
                        data: [],
                        links: [],
                        roam: true,
                        label: {
                            show: true
                        },
                        edgeLabel: {
                            show: false
                        },
                        edgeSymbol: ['none', 'arrow'],
                        lineStyle: {
                            width: 2
                        }
                    }
                ]
            };

            chartInstance.setOption(initialOption);

            // 响应窗口大小变化
            window.addEventListener('resize', () => {
                if (chartInstance) {
                    chartInstance.resize();
                }
            });
        },

        // 更新路径规划图表
        updatePathChart() {
            console.log('updatePathChart called, currentPath:', this.currentPath);
            console.log('campusNodes count:', this.campusNodes?.length);
            console.log('campusNodes sample:', this.campusNodes?.[0]);

            if (!chartInstance || !this.currentPath) {
                console.warn('updatePathChart: chartInstance or currentPath missing');
                return;
            }

            // 检查路径节点是否有重复
            const pathNodes = this.currentPath.nodes;
            const uniqueNodes = new Set(pathNodes);
            if (uniqueNodes.size !== pathNodes.length) {
                console.warn('路径包含重复节点，可能影响显示效果');
                console.warn('原始路径节点:', pathNodes);
                // 可以在这里尝试清理重复节点，但为了保持数据一致性，仅记录警告
            }

            // 准备节点数据
            const nodes = [];
            const edges = [];
            const nodeMap = new Map();

            // 添加校园节点
            console.log('Processing campus nodes for chart...');
            this.campusNodes.forEach((node, index) => {
                nodeMap.set(node.id, node);

                // 检查节点是否有坐标，如果没有则生成默认网格坐标
                let nodeX = node.x;
                let nodeY = node.y;

                if (nodeX === undefined || nodeY === undefined) {
                    console.log(`节点 ${node.id} (${node.name}) 缺少坐标，生成默认坐标`);
                    // 生成网格布局坐标（每行最多5个节点）
                    const cols = 5;
                    const row = Math.floor(index / cols);
                    const col = index % cols;
                    const spacing = 150; // 节点间距
                    const margin = 100;  // 边距

                    nodeX = margin + col * spacing;
                    nodeY = margin + row * spacing;
                    console.log(`生成的坐标: x=${nodeX}, y=${nodeY}`);
                }

                nodes.push({
                    id: node.id,
                    name: node.name,
                    x: nodeX,
                    y: nodeY,
                    symbolSize: 20,
                    itemStyle: {
                        color: this.getNodeColor(node.type)
                    },
                    label: {
                        show: true,
                        formatter: node.name
                    }
                });
            });
            console.log(`共添加 ${nodes.length} 个节点到图表`);

            // 步骤2: 确保所有路径节点都存在于图表中
            console.log('检查路径节点是否都在图表中...');
            const uniquePathNodes = [...new Set(pathNodes)]; // 去重
            let missingNodeCount = 0;

            uniquePathNodes.forEach((backendNodeId) => {
                if (!nodeMap.has(backendNodeId)) {
                    missingNodeCount++;
                    console.log(`路径节点 ${backendNodeId} 不在campusNodes中，创建临时节点`);

                    // 获取显示名称（使用反向映射）
                    const displayName = this.getNodeName(backendNodeId);

                    // 获取显示ID（用于类型猜测）
                    const displayId = this.getDisplayNodeId(backendNodeId);

                    // 基于显示ID猜测节点类型
                    let nodeType = 'junction'; // 默认为交叉点

                    if (displayId.startsWith('J') || displayId === 'TC' || displayId === 'CC' || displayId === 'DC' || displayId === 'LC') {
                        nodeType = 'junction';
                    } else if (displayId.startsWith('TB')) {
                        nodeType = 'teaching_building';
                    } else if (displayId.startsWith('CA')) {
                        nodeType = 'cafeteria';
                    } else if (displayId.startsWith('DO') || displayId === 'D2') {
                        nodeType = 'dormitory';
                    } else if (displayId === 'LIB') {
                        nodeType = 'library';
                    } else if (displayId.startsWith('SP') || displayId === 'S1') {
                        nodeType = 'sports';
                    } else if (displayId.startsWith('G') || displayId.startsWith('GATE_')) {
                        nodeType = 'gate';
                    }

                    // 生成网格坐标（从现有节点之后开始）
                    const baseIndex = nodes.length + missingNodeCount - 1;
                    const cols = 5;
                    const row = Math.floor(baseIndex / cols);
                    const col = baseIndex % cols;
                    const spacing = 150;
                    const margin = 100;
                    const nodeX = margin + col * spacing;
                    const nodeY = margin + row * spacing;

                    const tempNode = {
                        id: backendNodeId,
                        name: displayName,
                        x: nodeX,
                        y: nodeY,
                        type: nodeType
                    };

                    nodeMap.set(backendNodeId, tempNode);

                    nodes.push({
                        id: backendNodeId,
                        name: displayName,
                        x: nodeX,
                        y: nodeY,
                        symbolSize: 20,
                        itemStyle: {
                            color: this.getNodeColor(nodeType)
                        },
                        label: {
                            show: true,
                            formatter: displayName
                        }
                    });

                    console.log(`创建临时节点: ${backendNodeId} -> 显示为 "${displayName}", 类型: ${nodeType}, 坐标: (${nodeX}, ${nodeY})`);
                }
            });

            if (missingNodeCount > 0) {
                console.log(`添加了 ${missingNodeCount} 个缺失的路径节点到图表中`);
            } else {
                console.log('所有路径节点都已存在于图表中');
            }

            // 添加路径边
            // pathNodes 已在前面定义
            console.log(`开始创建路径边，路径节点: ${pathNodes.join(' → ')}`);
            console.log(`segmentDetails 数据:`, this.currentPath.segmentDetails);

            for (let i = 0; i < pathNodes.length - 1; i++) {
                const fromNode = pathNodes[i];
                const toNode = pathNodes[i + 1];
                console.log(`创建边: ${fromNode} → ${toNode}`);

                // 查找边的详细信息
                const segment = this.currentPath.segmentDetails?.find(s =>
                    s.from === fromNode && s.to === toNode
                );
                console.log(`找到的segment:`, segment);

                // 计算边距离：如果有segment详情则使用，否则使用默认值100m
                let edgeDistance = 100; // 默认距离
                if (segment && typeof segment.distance === 'number') {
                    edgeDistance = segment.distance;
                } else if (this.currentPath.distance && this.currentPath.nodes && this.currentPath.nodes.length > 1) {
                    // 如果总距离和节点数可用，估算每段距离
                    edgeDistance = this.currentPath.distance / (this.currentPath.nodes.length - 1);
                }

                const edgeLabel = `${edgeDistance.toFixed(0)}m`;

                console.log(`边 ${fromNode} → ${toNode}: 距离=${edgeDistance}, 标签="${edgeLabel}"`);

                edges.push({
                    source: fromNode,
                    target: toNode,
                    name: `${fromNode}→${toNode}`,
                    lineStyle: {
                        width: 7,
                        color: '#ff2222',
                        curveness: 0.1,
                        type: 'solid'
                    },
                    label: {
                        show: true,
                        formatter: edgeLabel
                    },
                    value: edgeDistance,
                    // 在边缘级别显式设置箭头
                    symbol: ['none', 'arrow'],
                    symbolSize: [0, 30],
                    symbolOffset: [0, -12], // 箭头向线条方向偏移，确保与节点平滑连接
                    itemStyle: {
                        color: '#ff2222',
                        borderColor: '#ff2222',
                        borderWidth: 0,
                        shadowBlur: 0,
                        shadowColor: 'transparent'
                    }
                });
            }

            // 高亮路径节点
            pathNodes.forEach(nodeId => {
                const nodeIndex = nodes.findIndex(n => n.id === nodeId);
                if (nodeIndex !== -1) {
                    nodes[nodeIndex].symbolSize = 30;
                    nodes[nodeIndex].itemStyle.color = '#ff3300';
                }
            });

            console.log(`边缘创建完成: 共 ${edges.length} 条边`);
            console.log('边缘数据详情:', edges);

            const option = {
                title: {
                    text: `路径规划: ${this.getNodeName(pathNodes[0])} → ${this.getNodeName(pathNodes[pathNodes.length - 1])}`,
                    subtext: `α=${this.currentPath.alpha} | 距离: ${this.currentPath.distance.toFixed(1)}m | 拥堵成本: ${this.currentPath.congestionCost.toFixed(1)}`,
                    left: 'center'
                },
                tooltip: {
                    formatter: function(params) {
                        if (params.dataType === 'node') {
                            return `${params.data.name}<br/>${params.data.id}`;
                        } else if (params.dataType === 'edge') {
                            return `${params.data.source} → ${params.data.target}`;
                        }
                    }
                },
                animationDurationUpdate: 1500,
                animationEasingUpdate: 'quinticInOut',
                series: [
                    {
                        type: 'graph',
                        layout: 'none',
                        data: nodes,
                        links: edges,
                        roam: true,
                        label: {
                            show: true,
                            position: 'right',
                            formatter: '{b}',
                            fontSize: 12
                        },
                        lineStyle: {
                            color: 'source',
                            width: 1,
                            opacity: 0.2
                        },
                        edgeSymbol: ['none', 'arrow'],
                        edgeSymbolSize: [0, 32],
                        edgeSymbolOffset: [0, 0],
                        edgeLabel: {
                            show: true,
                            formatter: '{c}',            // 使用数据中的value字段
                            fontSize: 11,
                            color: '#333'
                        },
                        emphasis: {
                            focus: 'adjacency',
                            lineStyle: {
                                width: 5,
                                color: '#ff4444'
                            },
                            edgeLabel: {
                                show: true,
                                fontWeight: 'bold'
                            }
                        },
                        // 动画效果
                        animation: true,
                        animationDuration: 1000,
                        animationEasing: 'cubicOut'
                    }
                ]
            };

            console.log('更新ECharts图表选项...');
            chartInstance.setOption(option, true);
        },

        // 更新对比图表
        updateComparisonChart() {
            if (!chartInstance || !this.comparisonResults) return;

            // 按α值升序排序
            const sortedResults = [...this.comparisonResults].sort((a, b) => a.alpha - b.alpha);

            const alphas = sortedResults.map(r => r.alpha);
            const distances = sortedResults.map(r => r.distance);
            const costs = sortedResults.map(r => r.cost);
            const congestionCosts = sortedResults.map(r => r.congestionCost);

            const option = {
                title: {
                    text: '路径对比分析',
                    subtext: `${this.getNodeName(this.compareStart)} → ${this.getNodeName(this.compareGoal)}`,
                    left: 'center'
                },
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'shadow'
                    }
                },
                legend: {
                    data: ['距离', '总成本', '拥堵成本'],
                    top: '10%'
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    top: '25%',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    data: alphas.map(a => `α=${a}`),
                    axisLabel: {
                        rotate: 45,
                        interval: 0 // 强制显示所有标签
                    }
                },
                yAxis: [
                    {
                        type: 'value',
                        name: '距离 (米)',
                        position: 'left'
                    },
                    {
                        type: 'value',
                        name: '成本',
                        position: 'right'
                    }
                ],
                series: [
                    {
                        name: '距离',
                        type: 'bar',
                        data: distances,
                        itemStyle: {
                            color: '#3498db'
                        },
                        yAxisIndex: 0
                    },
                    {
                        name: '总成本',
                        type: 'line',
                        data: costs,
                        itemStyle: {
                            color: '#ff3300'
                        },
                        yAxisIndex: 1
                    },
                    {
                        name: '拥堵成本',
                        type: 'line',
                        data: congestionCosts,
                        itemStyle: {
                            color: '#f39c12'
                        },
                        yAxisIndex: 1
                    }
                ]
            };

            console.log('更新ECharts图表选项...');
            chartInstance.setOption(option, true);
        },

        // 更新分析图表
        updateAnalysisChart() {
            if (!chartInstance || !this.analysisResults) return;

            console.log('updateAnalysisChart: analysisResults:', this.analysisResults);

            // 使用用户选择的时间或显示时间
            const times = this.analysisResults.map(r => {
                // 优先使用display_time，如果没有则使用用户时间，最后才使用time_str
                const displayTime = r.display_time || r.user_time || r.time_str || '';

                // 如果包含空格则取时间部分（处理后端返回的完整时间戳）
                const parts = displayTime.split(' ');
                const timePart = parts.length > 1 ? parts[1] : displayTime;

                // 提取HH:MM格式（去除秒部分）
                const timeMatch = timePart.match(/^(\d{1,2}:\d{2})/);
                return timeMatch ? timeMatch[1] : timePart;
            });

            console.log('图表X轴时间标签:', times);
            console.log('各时间点详细信息:');
            this.analysisResults.forEach((r, i) => {
                console.log(`  索引 ${i}: display_time="${r.display_time}", user_time="${r.user_time}", time_str="${r.time_str}"`);
            });

            const distances = this.analysisResults.map(r => r.path.distance);
            const congestionCosts = this.analysisResults.map(r => r.path.congestion_cost);
            const peakStatus = this.analysisResults.map(r => r.is_peak ? '高峰期' : '平峰期');

            const option = {
                title: {
                    text: '时间敏感性分析',
                    subtext: `${this.getNodeName(this.analysisStart)} → ${this.getNodeName(this.analysisGoal)}`,
                    left: 'center'
                },
                tooltip: {
                    trigger: 'axis',
                    formatter: function(params) {
                        const index = params[0].dataIndex;
                        const result = `
                            时间: ${times[index]}<br/>
                            距离: ${distances[index].toFixed(1)}m<br/>
                            拥堵成本: ${congestionCosts[index].toFixed(1)}<br/>
                            状态: ${peakStatus[index]}
                        `;
                        return result;
                    }
                },
                legend: {
                    data: ['距离', '拥堵成本'],
                    top: '10%'
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    top: '25%',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    data: times,
                    axisLabel: {
                        rotate: 45,
                        interval: 0, // 强制显示所有标签
                        formatter: function(value) {
                            // 如果标签太长，截断到10个字符
                            if (value && value.length > 10) {
                                return value.substring(0, 8) + '...';
                            }
                            return value;
                        }
                    }
                },
                yAxis: [
                    {
                        type: 'value',
                        name: '距离 (米)',
                        position: 'left'
                    },
                    {
                        type: 'value',
                        name: '拥堵成本',
                        position: 'right'
                    }
                ],
                series: [
                    {
                        name: '距离',
                        type: 'bar',
                        data: distances,
                        itemStyle: {
                            color: function(params) {
                                return peakStatus[params.dataIndex] === '高峰期' ? '#ff3300' : '#3498db';
                            }
                        },
                        yAxisIndex: 0
                    },
                    {
                        name: '拥堵成本',
                        type: 'line',
                        data: congestionCosts,
                        itemStyle: {
                            color: '#f39c12'
                        },
                        yAxisIndex: 1
                    }
                ]
            };

            console.log('更新ECharts图表选项...');
            chartInstance.setOption(option, true);
        },

        // 下载图表
        downloadChart() {
            if (!chartInstance) return;

            const url = chartInstance.getDataURL({
                type: 'png',
                pixelRatio: 2,
                backgroundColor: '#fff'
            });

            const link = document.createElement('a');
            link.href = url;
            link.download = `flownav_chart_${new Date().getTime()}.png`;
            link.click();

            this.showInfo('图表已下载');
        },

        // 节点类型颜色映射
        getNodeColor(type) {
            const colors = {
                'teaching_building': '#3498db',
                'cafeteria': '#ff3300',
                'dormitory': '#2ecc71',
                'library': '#9b59b6',
                'gate': '#f39c12',
                'sports': '#1abc9c',
                'junction': '#95a5a6'
            };
            return colors[type] || '#7f8c8d';
        },

        // 消息提示方法
        showSuccess(message) {
            this.showAlert(message, 'success');
        },

        showError(message) {
            this.showAlert(message, 'danger');
        },

        showWarning(message) {
            this.showAlert(message, 'warning');
        },

        showInfo(message) {
            this.showAlert(message, 'info');
        },

        showDetailedError(title, errorInfo) {
            // 创建详细的错误提示
            const errorHtml = `
                <div class="alert alert-danger" role="alert">
                    <h5 class="alert-heading">${title}</h5>
                    <p><strong>错误类型:</strong> ${errorInfo.type}</p>
                    <p><strong>错误信息:</strong> ${errorInfo.message}</p>
                    <p><strong>建议:</strong> ${errorInfo.suggestion}</p>
                    <hr>
                    <p class="mb-0">
                        <button class="btn btn-sm btn-outline-danger" onclick="this.closest('.alert').remove()">关闭</button>
                        ${errorInfo.type === 'network' ? '<button class="btn btn-sm btn-outline-primary ms-2" onclick="location.reload()">重试连接</button>' : ''}
                    </p>
                </div>
            `;

            // 在实际应用中，可以使用更优雅的通知系统
            // 这里简单使用alert的变体，实际应该显示在页面特定区域
            const alertContainer = document.getElementById('error-alerts');
            if (alertContainer) {
                alertContainer.innerHTML = errorHtml + alertContainer.innerHTML;
            } else {
                // 如果没有专门的容器，使用alert
                alert(`[${errorInfo.type.toUpperCase()}] ${errorInfo.message}\n\n建议: ${errorInfo.suggestion}`);
            }
        },

        showAlert(message, type) {
            // 在实际应用中，可以使用更优雅的通知系统
            alert(`[${type.toUpperCase()}] ${message}`);
        }
    }
});

// 挂载应用
try {
    app.mount('#app');
    console.log('Vue应用成功挂载到#app元素');
} catch (error) {
    console.error('Vue应用挂载失败:', error);
    // 显示错误信息给用户
    document.getElementById('app').innerHTML = `
        <div class="alert alert-danger m-4">
            <h4>应用加载失败</h4>
            <p>Vue应用初始化失败: ${error.message}</p>
            <p>请检查浏览器控制台获取详细信息。</p>
            <button onclick="location.reload()" class="btn btn-warning">重新加载页面</button>
        </div>
    `;
}