import json
import random
from datetime import datetime, timedelta
from BuildReference import SearchReferenceData

def get_restaurant_price(restaurant):
    # 初始化变量
    max_cost = float('-inf')  # 最大值初始为负无穷
    min_cost = float('inf')   # 最小值初始为正无穷
    for item in restaurant:
        average_cost = item.get('Average Cost', [])

        if not average_cost:  # 如果为空列表或缺失
                average_cost = 50
        else:
            try:
                average_cost = float(average_cost)  # 将字符串转换为浮点数
            except ValueError:
                average_cost = 50  # 转换失败时设置为默认值 50

        max_cost = max(max_cost, average_cost)
        min_cost = min(min_cost, average_cost)

    return max_cost, min_cost

def get_hotel_price(hotel):
    # 初始化变量
    max_cost = float('-inf')  # 最大值初始为负无穷
    min_cost = float('inf')   # 最小值初始为正无穷

    for item in hotel:
        hotel_price = item.get('Price','HK$200')
        if hotel_price.startswith('HK$'):  # 检查是否以 ¥ 开头
            try:
                price = int(hotel_price[3:])  # 去掉 ¥ 并转换为整数
            except ValueError:
                price = 200  # 转换失败时设置为 150
        
        max_cost = max(max_cost, price)
        min_cost = min(min_cost, price)
        
    return max_cost, min_cost

def get_train_price(train):

    # 初始化变量
    max_cost = float('-inf')  # 最大值初始为负无穷
    min_cost = float('inf')   # 最小值初始为正无穷

    for item in train:
        train_price = item.get('Price', 300.0)
        try:
            price = float(train_price)
        except:
            price = 300.0
        
        max_cost = max(max_cost, price)
        min_cost = min(min_cost, price)
        
    return max_cost, min_cost

def get_min_budget(ref_info, travel_days):
    
    all_trains = []

    hotel = ref_info['在秦皇岛的酒店']
    restaurant = ref_info['在秦皇岛的餐厅']
    # 遍历所有键，查找以 "从" 开头且包含 "到" 的键
    for key, value in ref_info.items():
        if key.startswith("从") and "到" in key and "列车" in key:
            all_trains.extend(value)

        # for key, value in ref_info.items():
        #     if key.startswith("从") and "到" in key and "航班" in key:
        #         all_flights.extend(value)
    _, min_hotel_price = get_hotel_price(hotel)
    _, min_restaurant_price = get_restaurant_price(restaurant)
    _, min_train_price = get_train_price(all_trains)

    MinBudget = min_train_price * 2 + travel_days * (min_hotel_price + 3 * min_restaurant_price)

    return MinBudget


if __name__ == '__main__':
   

    now = datetime.now()
    Duration = 5
    Begin_Date = (now + timedelta(days=7)).strftime('%Y-%m-%d')
    Final_Date = (now + timedelta(days=7+Duration-1)).strftime('%Y-%m-%d')

    # ref_info = SearchReferenceData('广州', '秦皇岛', Begin_Date, Final_Date, Duration)

    # with open("C:\\Users\\86177\\Desktop\\ScrapyTools\\reference.jsonl","w",encoding="utf-8") as file:
    #     file.write(json.dumps(ref_info,ensure_ascii=False) + '\n')

    with open("C:\\Users\\86177\\Desktop\\ScrapyTools\\reference.jsonl","r", encoding='utf-8') as file:
        ref_info = json.load(file)

    min_budget = get_min_budget(ref_info, Duration)
    print(min_budget)


