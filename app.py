# app.py
import json
from datetime import datetime, timedelta
from SolePlanning import Get_LLM_Planning
from BuildPrompt import BuildQuery, Prompts, Prompts_With_RefInfo
from CalculateBudget import get_min_budget
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  

@app.route('/api/generate-plan', methods=['POST'])
def generate_plan():
    try:
        # 1. 获取前端参数
        data = request.get_json()
        origin = data['origin']
        destination = data['destination']
        start_date_str = data['start_date']
        travel_days = data['days']
        budget = data['budget']

        # 2. 将 start_date 转换为 datetime 对象
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')  
        except ValueError:
            return {"error": "Invalid date format. Please use 'YYYY-MM-DD'."}, 400

        # 3. 计算 end_date
        end_date = (start_date + timedelta(days=travel_days - 1)).strftime('%Y-%m-%d')
        
        # 4. 调用业务逻辑
        # prompt = Prompts(Origin_City=origin, Dest_City=destination, Begin_Date=start_date, Final_Date=end_date, Duration=travel_days, Budget=budget)
        prompt, ref_info = Prompts_With_RefInfo(Origin_City=origin, Dest_City=destination, Begin_Date=start_date, Final_Date=end_date, Duration=travel_days, Budget=budget)

        min_budget = get_min_budget(ref_info=ref_info, travel_days=travel_days)
        
        print("正在验证预算...")
        if min_budget > budget:
            print("提示错误预算...")
            return jsonify({"status": "error", "message": "您设置的预算太低了，无法生成旅行计划"}), 400
        
        plan = Get_LLM_Planning(prompt)
        
        # 5. 返回结构化的数据
        return jsonify({
            "status": "success",
            "plan": json.loads(plan),
            #"budget": calculate_budget(plan)
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    app.run(port=5000, debug=True)