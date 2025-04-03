# app.py
import json
from datetime import datetime, timedelta
from SolePlanning import Get_LLM_Planning
from BuildPrompt import BuildQuery, Prompts
from flask import Flask, jsonify, request
from flask_cors import CORS
from srp import JsonReact
app = Flask(__name__)
CORS(app)  # 解决跨域问题



@app.route('/api/generate-plan', methods=['POST'])
def generate_plan():
    try:
        # 1. 获取前端参数
        data = request.get_json()
        origin = data['origin']
        destination = data['destination']
        start_date_str = data['start_date']
        travel_days = int(data['days'])  # 确保是整数
        budget = float(data['budget'])    # 确保是数字

        # 2. 将 start_date 转换为 datetime 对象
        try:
            # 统一日期格式处理
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        except ValueError:
            try:
                # 尝试处理其他格式
                start_date = datetime.strptime(start_date_str, '%Y/%m/%d')
            except ValueError:
                return jsonify({
                    "status": "error",
                    "message": "Invalid date format. Please use YYYY-MM-DD or YYYY/MM/DD"
                }), 400

        # 3. 计算 end_date (使用 datetime 对象进行计算)
        end_date = start_date + timedelta(days=travel_days - 1)
        
        # 4. 转换日期为字符串格式
        start_date_formatted = start_date.strftime('%Y-%m-%d')
        end_date_formatted = end_date.strftime('%Y-%m-%d')

        # 5. 调用业务逻辑
        prompt = Prompts(
            Origin_City=origin,
            Dest_City=destination,
            Begin_Date=start_date_formatted,
            Final_Date=end_date_formatted,
            Duration=travel_days,
            Budget=budget
        )

        plan = Get_LLM_Planning(prompt)
        
        # 6. 返回结果
        try:
            return jsonify({
                "status": "success",
                "plan": json.loads(plan)
            })
        except json.JSONDecodeError:
            return jsonify({
                "status": "error",
                "message": "Invalid JSON response from LLM"
            }), 400
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@app.route('/api/replan', methods=['POST'])
def replan():
    try:
        # 1. 获取前端参数
        data = request.get_json()
        origin = data['origin']
        destination = data['destination']
        start_date_str = data['start_date']
        travel_days = int(data['days'])
        budget = float(data['budget'])
        previous_plan = data.get('previous_plan', None)

        # 2. 日期处理
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        except ValueError:
            try:
                start_date = datetime.strptime(start_date_str, '%Y/%m/%d')
            except ValueError:
                return jsonify({
                    "status": "error",
                    "message": "Invalid date format"
                }), 400

        end_date = start_date + timedelta(days=travel_days - 1)
        
        # 3. 构建测试数据
        test_entry = {
            "org": origin,
            "dest": destination,
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "days": travel_days,
            "budget": budget,
            "previous_plan": previous_plan
        }

        # 4. 创建JsonReact实例并运行
        reactor = JsonReact()
        prompt = Prompts(
            Origin_City=origin,
            Dest_City=destination,
            Begin_Date=start_date.strftime('%Y-%m-%d'),
            Final_Date=end_date.strftime('%Y-%m-%d'),
            Duration=travel_days,
            Budget=budget
        )
        
        # 5. 运行反馈规划
        new_plan = reactor.run(str(prompt), "Generate travel plan", test_entry)
        
        # 6. 返回结果
        if isinstance(new_plan, str):
            try:
                return jsonify({
                    "status": "success",
                    "plan": json.loads(new_plan)
                })
            except json.JSONDecodeError:
                return jsonify({
                    "status": "error",
                    "message": "Invalid JSON response from replanning"
                }), 400
        else:
            return jsonify({
                "status": "success",
                "plan": new_plan
            })
            
    except Exception as e:
        print(f"Error in replan: {str(e)}")  # 添加调试信息
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)