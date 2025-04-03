import requests
import json
import time

# 高德地图 API Key
API_KEY = 'e4df5437e6dd4eb7696fb6b9fd0494da'  # 请替换成您自己的 API Key

# 高德地图 Place 文本搜索接口 URL
url = "https://restapi.amap.com/v3/place/text"

# 查询参数
params = {
    'key': API_KEY,
    'keywords': '美食',  # 查询的关键词
    'types': '050000',  # POI分类代码，050000代表餐饮服务
    'city': '山海关',  # 城市名，可以是城市名称、citycode 或 adcode
    'children': 1,  # 是否按照层级展示子 POI 数据
    'offset': 20,  # 每页返回的结果数，最大为 30
    'page': 1,  # 当前页码，从 1 开始
    'extensions': 'all'  # 返回结果包含POI的详细信息
}

def GetRestaurantData():
    filtered_data = []  # 用于存储过滤后的餐饮商户信息
    page = 1
    max_page = 2
    while True:
        params['page'] = page
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == '1' and data['pois']:
                # 过滤数据
                for item in data['pois']:
                    type_cleaned = item.get("type", "").replace("餐饮服务;", "").strip()
                    filtered_item = {
                        "Name": item.get("name"),
                        "City": item.get("cityname"),
                        "Cuisines": type_cleaned,
                        "Average Cost": item.get("biz_ext", {}).get("cost"),
                        "Aggregate Rating": item.get("biz_ext", {}).get("rating")
                    }
                    filtered_data.append(filtered_item)

                #print(f"获取第 {page} 页餐饮商户信息，当前共获得 {len(filtered_data)} 个餐饮信息")

                # 如果当前页的数据少于设定的每页返回数据条数，说明已经获取完所有数据
                if len(data['pois']) < params['offset']:
                    break
                #page += 1
                time.sleep(1)  # 设置请求间隔，避免频繁请求
            else:
                print(f"请求失败，错误信息: {data.get('info')}")
                break
        else:
            print(f"请求失败，HTTP状态码: {response.status_code}")
            break
        
        if page == 2:
            break
        else:
            page += 1
        #break

    return filtered_data


if __name__ == "__main__":
    # 调用函数获取并过滤餐厅信息
    filtered_restaurants = GetRestaurantData()

    # 将过滤后的数据保存为 JSON 文件
    output_file = 'filtered_data.json'
    # with open(output_file, 'w', encoding='utf-8') as f:
    #     json.dump(filtered_restaurants, f, ensure_ascii=False, indent=4)

    # print(f"\n过滤后的餐饮商户信息已保存到 {output_file}")

    # 直接打印 filtered_restaurants 的内容
    print("\n过滤后的餐饮商户信息如下：")
    print(json.dumps(filtered_restaurants, ensure_ascii=False, indent=4))