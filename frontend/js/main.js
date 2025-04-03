new Vue({
    el: '#app',
    data: {
        formData: {
            origin: '',
            destination: '',
            start_date: '',
            days: 1,
            budget: 0
        },
        result: null,
        error: null,
        loading: false,
        replanning: false,
        currentStep: 0,
        planMode: 'direct',
        // 添加爬虫结果数据
        crawlStats: {
            flights: { departure: 0, return: 0 },
            trains: { departure: 0, return: 0 },
            attractions: 0,
            hotels: 0
        },
        // 添加流式输出状态
        streamOutput: '',
        isStreaming: false
    },
    methods: {
        async startPlanning() {
            if (this.loading) return;
            
            if (this.planMode === 'direct') {
                await this.generatePlan();
            } else {
                await this.generateReactivePlan();
            }
        },

        async generatePlan() {
            if (this.loading) return;
            
            // 表单验证
            if (!this.formData.origin || !this.formData.destination || 
                !this.formData.start_date || !this.formData.days || 
                !this.formData.budget) {
                this.error = "请填写所有必填字段";
                return;
            }

            this.loading = true;
            this.error = null;
            this.currentStep = 1;
            this.streamOutput = '';
            this.isStreaming = true;

            try {
                // 获取爬虫统计数据
                const statsResponse = await fetch('http://localhost:5000/api/crawl-stats', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(this.formData)
                });
                
                const statsData = await statsResponse.json();
                if (statsData.status === 'success') {
                    this.crawlStats = statsData.stats;
                }

                // 开始生成计划（流式输出）
                const response = await fetch('http://localhost:5000/api/generate-plan-stream', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(this.formData)
                });

                const reader = response.body.getReader();
                const decoder = new TextDecoder();

                while (true) {
                    const {value, done} = await reader.read();
                    if (done) break;
                    
                    const text = decoder.decode(value);
                    this.streamOutput += text;
                }

                this.currentStep = 3;
                this.result = this.streamOutput;
                
            } catch (err) {
                this.error = '网络请求失败: ' + err.message;
            } finally {
                this.loading = false;
                this.isStreaming = false;
            }
        },

        // 修改generateReactivePlan方法也使用流式输出
        async generateReactivePlan() {
            if (this.loading) return;
            
            // 表单验证
            if (!this.formData.origin || !this.formData.destination || 
                !this.formData.start_date || !this.formData.days || 
                !this.formData.budget) {
                this.error = "请填写所有必填字段";
                return;
            }

            this.loading = true;
            this.error = null;
            this.currentStep = 1;
            this.streamOutput = '';
            this.isStreaming = true;

            try {
                // 获取爬虫统计数据
                const statsResponse = await fetch('http://localhost:5000/api/crawl-stats', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(this.formData)
                });
                
                const statsData = await statsResponse.json();
                if (statsData.status === 'success') {
                    this.crawlStats = statsData.stats;
                }

                // 开始生成计划（流式输出）
                const response = await fetch('http://localhost:5000/api/replan-stream', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        ...this.formData,
                        previous_plan: this.result
                    })
                });

                const reader = response.body.getReader();
                const decoder = new TextDecoder();

                while (true) {
                    const {value, done} = await reader.read();
                    if (done) break;
                    
                    const text = decoder.decode(value);
                    this.streamOutput += text;
                }

                this.currentStep = 3;
                this.result = this.streamOutput;
                
            } catch (err) {
                this.error = '网络请求失败: ' + err.message;
            } finally {
                this.loading = false;
                this.isStreaming = false;
            }
        },

        setMode(mode) {
            this.planMode = mode;
        }
    }
});