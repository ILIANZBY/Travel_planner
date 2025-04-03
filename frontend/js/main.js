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
        planMode: 'direct'
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

            try {
                setTimeout(() => this.currentStep = 2, 1000);

                const response = await fetch('http://localhost:5000/api/generate-plan', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(this.formData)
                });

                const data = await response.json();
                
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
            }
        },

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

            try {
                setTimeout(() => this.currentStep = 2, 1000);

                const response = await fetch('http://localhost:5000/api/replan', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        ...this.formData,
                        previous_plan: this.result
                    })
                });

                const data = await response.json();
                
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
            }
        },

        setMode(mode) {
            this.planMode = mode;
        }
    }
});