/* FlowNav API 服务封装
   支持模拟模式和真实API模式切换
*/

const ApiService = {
    // API配置
    config: {
        useMockData: true,  // 默认使用模拟数据
        apiBaseUrl: '/api',  // 后端API地址 http://localhost:8000/api
        timeout: 10000,  // 请求超时时间
    },

    // 错误分类函数
    classifyError: function(error) {
        if (!error) {
            return {
                type: 'unknown',
                message: '发生未知错误',
                suggestion: '请尝试刷新页面或切换到模拟数据模式'
            };
        }

        const msg = error.message || String(error);

        // 网络连接错误 - 最常见的API连接问题
        if (msg.includes('Network Error') || msg.includes('Failed to fetch') || msg.includes('ERR_CONNECTION_REFUSED')) {
            return {
                type: 'network',
                message: '无法连接到路径规划服务器',
                suggestion: '请检查：1) API服务器是否启动 2) 端口8000是否被占用 3) 防火墙设置'
            };
        }

        // 超时错误
        if (msg.includes('timeout') || msg.includes('Timeout')) {
            return {
                type: 'timeout',
                message: '服务器响应超时',
                suggestion: '服务器繁忙，请稍后重试或使用模拟数据模式'
            };
        }

        // 服务器内部错误
        if (msg.includes('500') || msg.includes('Internal Server')) {
            return {
                type: 'server_error',
                message: '服务器内部错误',
                suggestion: '服务器暂时不可用，请稍后再试或使用模拟数据模式'
            };
        }

        // 页面未找到错误
        if (msg.includes('404') || msg.includes('Not Found')) {
            return {
                type: 'not_found',
                message: '服务器地址不正确',
                suggestion: '请点击"尝试连接API"按钮重新测试，或使用模拟数据模式'
            };
        }

        // 认证错误（401）
        if (msg.includes('401') || msg.includes('Unauthorized')) {
            return {
                type: 'auth_error',
                message: 'API认证失败',
                suggestion: 'API需要认证密钥，请检查API密钥配置或联系管理员'
            };
        }

        // 其他错误
        return {
            type: 'other',
            message: '路径规划失败',
            suggestion: '请检查控制台获取详细信息，或切换到模拟数据模式继续使用'
        };
    },

    // 缓存机制
    cache: new Map(),

    // 生成缓存键
    _getCacheKey: function(start, goal, alpha, time) {
        const timeStr = time instanceof Date ? time.toISOString() : time;
        return `${start}-${goal}-${alpha}-${timeStr}`;
    },

    // 生成比较结果缓存键
    _getComparisonCacheKey: function(start, goal, alphas, time) {
        const timeStr = time instanceof Date ? time.toISOString() : time;
        // 排序alphas以确保一致的键
        const sortedAlphas = [...alphas].sort((a, b) => a - b);
        const alphasStr = sortedAlphas.join(',');
        return `compare-${start}-${goal}-${alphasStr}-${timeStr}`;
    },

    // 生成分析结果缓存键
    _getAnalysisCacheKey: function(start, goal, timePoints) {
        // 排序时间点以确保一致的键
        const sortedTimes = [...timePoints].sort();
        const timesStr = sortedTimes.join('|');
        return `analyze-${start}-${goal}-${timesStr}`;
    },

    // 清除缓存
    clearCache: function() {
        this.cache.clear();
        console.log('API缓存已清除');
    },

    // 获取缓存统计
    getCacheStats: function() {
        return {
            size: this.cache.size,
            keys: Array.from(this.cache.keys())
        };
    },

    // 切换API模式
    setMockMode: function(enabled) {
        this.config.useMockData = enabled;
        console.log(`API模式切换到: ${enabled ? '模拟数据' : '真实API'}`);
    },

    // 获取校园节点数据
    async getCampusNodes() {
        if (this.config.useMockData) {
            await MockData.simulateDelay(200);
            return {
                success: true,
                data: MockData.campusNodes,
                source: 'mock'
            };
        }

        try {
            const response = await axios.get(`${this.config.apiBaseUrl}/nodes`, {
                timeout: this.config.timeout
            });
            return {
                success: true,
                data: response.data,
                source: 'api'
            };
        } catch (error) {
            console.error('获取节点数据失败:', error);
            return {
                success: false,
                error: error.message,
                data: MockData.campusNodes,  // 失败时回退到模拟数据
                source: 'fallback'
            };
        }
    },

    // 获取校园信息
    async getCampusInfo() {
        if (this.config.useMockData) {
            await MockData.simulateDelay(300);
            return {
                success: true,
                data: MockData.getCampusInfo(),
                source: 'mock'
            };
        }

        try {
            const response = await axios.get(`${this.config.apiBaseUrl}/campus-info`, {
                timeout: this.config.timeout
            });
            return {
                success: true,
                data: response.data,
                source: 'api'
            };
        } catch (error) {
            console.error('获取校园信息失败:', error);
            return {
                success: false,
                error: error.message,
                data: MockData.getCampusInfo(),
                source: 'fallback'
            };
        }
    },

    // 路径规划
    async planPath(start, goal, alpha = 1.0, time = null) {
        // 如果没有提供时间，使用当前时间
        if (!time) {
            time = new Date().toISOString();
        } else if (time instanceof Date) {
            time = time.toISOString();
        }

        if (this.config.useMockData) {
            // 检查缓存
            const cacheKey = this._getCacheKey(start, goal, alpha, time);
            if (this.cache.has(cacheKey)) {
                console.log(`缓存命中: ${cacheKey}`);
                return this.cache.get(cacheKey);
            }

            await MockData.simulateDelay(800);  // 模拟计算延迟
            const result = {
                success: true,
                data: MockData.generatePathResult(start, goal, alpha, time),
                source: 'mock'
            };

            // 缓存结果
            this.cache.set(cacheKey, result);
            console.log(`缓存新增: ${cacheKey}`);
            return result;
        }

        try {
            const response = await axios.post(`${this.config.apiBaseUrl}/plan-path`, {
                start: start,
                goal: goal,
                alpha: alpha,
                time: time
            }, {
                timeout: this.config.timeout
            });
            return {
                success: true,
                data: response.data.data,  // 提取实际数据
                source: 'api'
            };
        } catch (error) {
            console.error('路径规划失败:', error);
            // 分类错误并提供用户友好的信息
            const errorInfo = this.classifyError(error);
            console.warn(`错误分类: ${errorInfo.type} - ${errorInfo.message}`);

            // 失败时使用模拟数据
            await MockData.simulateDelay(500);
            return {
                success: false,
                error: error.message,  // 原始错误信息（用于调试）
                errorInfo: errorInfo,  // 分类后的错误信息（用于显示）
                data: MockData.generatePathResult(start, goal, alpha, time),
                source: 'fallback'
            };
        }
    },

    // 路径比较
    async comparePaths(start, goal, alphas, time = null) {
        if (!time) {
            time = new Date().toISOString();
        } else if (time instanceof Date) {
            time = time.toISOString();
        }

        // 确保alphas是数组
        if (!Array.isArray(alphas)) {
            if (typeof alphas === 'string') {
                alphas = alphas.split(',').map(a => parseFloat(a.trim()));
            } else {
                alphas = [alphas];
            }
        }

        if (this.config.useMockData) {
            // 检查缓存（为比较结果生成特定键）
            const cacheKey = this._getComparisonCacheKey(start, goal, alphas, time);
            if (this.cache.has(cacheKey)) {
                console.log(`比较缓存命中: ${cacheKey}`);
                return this.cache.get(cacheKey);
            }

            await MockData.simulateDelay(1000);  // 模拟多路径计算延迟
            const result = {
                success: true,
                data: MockData.generateComparisonResult(start, goal, alphas, time),
                source: 'mock'
            };

            // 缓存结果
            this.cache.set(cacheKey, result);
            console.log(`比较缓存新增: ${cacheKey}`);
            return result;
        }

        try {
            const response = await axios.post(`${this.config.apiBaseUrl}/compare-paths`, {
                start: start,
                goal: goal,
                alphas: alphas,
                time: time
            }, {
                timeout: this.config.timeout
            });
            return {
                success: true,
                data: response.data.data,  // 提取实际数据
                source: 'api'
            };
        } catch (error) {
            console.error('路径比较失败:', error);
            // 分类错误并提供用户友好的信息
            const errorInfo = this.classifyError(error);
            console.warn(`错误分类: ${errorInfo.type} - ${errorInfo.message}`);

            await MockData.simulateDelay(800);
            return {
                success: false,
                error: error.message,  // 原始错误信息（用于调试）
                errorInfo: errorInfo,  // 分类后的错误信息（用于显示）
                data: MockData.generateComparisonResult(start, goal, alphas, time),
                source: 'fallback'
            };
        }
    },

    // 路线分析
    async analyzeRoute(start, goal, timePoints = null) {
        // 如果没有提供时间点，生成默认时间点
        if (!timePoints || !Array.isArray(timePoints) || timePoints.length === 0) {
            const now = new Date();
            timePoints = [
                new Date(now.getFullYear(), now.getMonth(), now.getDate(), 8, 0),   // 早上8点
                new Date(now.getFullYear(), now.getMonth(), now.getDate(), 12, 0),  // 中午12点
                new Date(now.getFullYear(), now.getMonth(), now.getDate(), 18, 0),  // 晚上6点
                new Date(now.getFullYear(), now.getMonth(), now.getDate(), 21, 45), // 晚自习时间
            ];
        }

        // 转换为ISO字符串
        const timePointsISO = timePoints.map(t => t instanceof Date ? t.toISOString() : t);

        if (this.config.useMockData) {
            // 检查缓存
            const cacheKey = this._getAnalysisCacheKey(start, goal, timePointsISO);
            if (this.cache.has(cacheKey)) {
                console.log(`分析缓存命中: ${cacheKey}`);
                return this.cache.get(cacheKey);
            }

            await MockData.simulateDelay(1200);  // 模拟多时间点分析延迟
            const result = {
                success: true,
                data: MockData.generateRouteAnalysis(start, goal, timePointsISO),
                source: 'mock'
            };

            // 缓存结果
            this.cache.set(cacheKey, result);
            console.log(`分析缓存新增: ${cacheKey}`);
            return result;
        }

        try {
            const response = await axios.post(`${this.config.apiBaseUrl}/analyze-route`, {
                start: start,
                goal: goal,
                time_points: timePointsISO
            }, {
                timeout: this.config.timeout
            });
            return {
                success: true,
                data: response.data.data,  // 提取嵌套的data字段
                source: 'api'
            };
        } catch (error) {
            console.error('路线分析失败:', error);
            // 分类错误并提供用户友好的信息
            const errorInfo = this.classifyError(error);
            console.warn(`错误分类: ${errorInfo.type} - ${errorInfo.message}`);

            await MockData.simulateDelay(1000);
            return {
                success: false,
                error: error.message,  // 原始错误信息（用于调试）
                errorInfo: errorInfo,  // 分类后的错误信息（用于显示）
                data: MockData.generateRouteAnalysis(start, goal, timePointsISO),
                source: 'fallback'
            };
        }
    },

    // 测试API连接
    async testConnection() {
        if (this.config.useMockData) {
            return {
                success: true,
                connected: false,
                message: '当前使用模拟数据模式',
                source: 'mock'
            };
        }

        try {
            const response = await axios.get(`${this.config.apiBaseUrl}/health`, {
                timeout: 3000
            });
            return {
                success: true,
                connected: response.status === 200,
                message: 'API连接正常',
                data: response.data,
                source: 'api'
            };
        } catch (error) {
            // 分类错误并提供用户友好的信息
            const errorInfo = this.classifyError(error);
            console.warn(`API连接错误分类: ${errorInfo.type} - ${errorInfo.message}`);

            return {
                success: false,
                connected: false,
                message: `API连接失败: ${errorInfo.message}`,
                errorInfo: errorInfo,  // 分类后的错误信息
                source: 'error'
            };
        }
    },

    // 导出路径报告
    async exportPathReport(pathResult, format = 'text') {
        if (this.config.useMockData) {
            await MockData.simulateDelay(300);

            let report;
            if (format === 'json') {
                report = JSON.stringify(pathResult, null, 2);
            } else {
                // 文本格式报告
                report = `校园动态导航路径规划报告\n`;
                report += `============================\n`;
                report += `起点: ${pathResult.start}\n`;
                report += `终点: ${pathResult.goal}\n`;
                report += `α值: ${pathResult.alpha}\n`;
                report += `时间: ${new Date(pathResult.time).toLocaleString('zh-CN')}\n`;
                report += `总距离: ${pathResult.distance.toFixed(1)} 米\n`;
                report += `总成本: ${pathResult.totalActualCost.toFixed(1)}\n`;
                report += `拥堵成本: ${pathResult.congestionCost.toFixed(1)}\n`;
                report += `平均拥挤系数: ${pathResult.averageCongestion.toFixed(2)}\n`;
                report += `节点序列: ${pathResult.nodes.join(' → ')}\n`;
            }

            return {
                success: true,
                data: report,
                format: format,
                source: 'mock'
            };
        }

        try {
            const response = await axios.post(`${this.config.apiBaseUrl}/export-report`, {
                path_result: pathResult,
                format: format
            }, {
                timeout: this.config.timeout
            });
            return {
                success: true,
                data: response.data,
                format: format,
                source: 'api'
            };
        } catch (error) {
            console.error('导出报告失败:', error);
            return {
                success: false,
                error: error.message,
                data: null,
                source: 'error'
            };
        }
    }
};