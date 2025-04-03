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
        currentStep: 0
    },
    methods: {
        async generatePlan() {
            this.loading = true;
            this.error = null;
            this.result = null;
            this.currentStep = 1;

            const formattedData = {
                ...this.formData,
                days: parseInt(this.formData.days),
                budget: parseFloat(this.formData.budget),
                start_date: this.formData.start_date.replace(/\//g, '-')
            };

            try {
                // 模拟第一步进度
                await this.sleep(1000);
                this.currentStep = 2;
                
                // 发送请求
                const response = await fetch('http://localhost:5000/api/generate-plan', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formattedData)
                });

                const data = await response.json();
                await this.sleep(500);
                this.currentStep = 3;
                
                if (data.status === 'success') {
                    this.result = data.plan;
                } else {
                    this.error = data.message || '生成计划失败';
                }
            } catch (err) {
                this.error = '网络请求失败: ' + err.message;
            } finally {
                this.loading = false;
                setTimeout(() => {
                    this.currentStep = 0;
                }, 1000);
            }
        },
        
        sleep(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }
    }
});