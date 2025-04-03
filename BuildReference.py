import json
import random
import time
import os
import multiprocessing
from datetime import datetime, timedelta
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from twisted.internet.defer import DeferredList
from scrapy.utils.project import get_project_settings

from script.run_Train_script import GetTrainData
from script.run_Attraction_script import GetAttractionData
from script.run_Hotel_script import GetHotelData
from script.Plane_final_script import GetPlaneData
from script.run_Restaurant_script import GetRestaurantData

"""
    一条参考信息的内容如下: 
    酒店:5条数据
    餐厅:20条数据
    景点:10条数据

    火车:5条数据(来回分别计算)
    航班:
"""

def drop_key(entry, key):
    if key in entry.keys():
        entry.pop(key)
    return entry


def get_restaurant_ref_data(counts=20):

    restaurant_data = GetRestaurantData()
    # 从数据中随机抽取指定数量的数据项
    return random.sample(restaurant_data, counts)

def get_attraction_ref_data(counts=10):

    # 创建一个新的队列用于接收临时文件路径
    queue = multiprocessing.Queue()

    # 创建一个新的进程来运行爬虫
    p = multiprocessing.Process(target=GetAttractionData, args=(queue,))
    p.start()
    p.join()  # 等待子进程结束

    # 从队列中获取临时文件路径
    output_file_path = queue.get()

    # 检查文件是否存在并读取数据
    if os.path.exists(output_file_path):
        with open(output_file_path, 'r', encoding='utf-8') as file:
            attraction_data = json.load(file)
            #print(json.dumps(train_data, indent=4, ensure_ascii=False))
        
        # 删除临时文件
        os.remove(output_file_path)
        print(f"Temporary file {output_file_path} has been deleted.")
    else:
        print(f"Error: Output file {output_file_path} not found.")
    
    
    # 从数据中随机抽取指定数量的数据项
    return random.sample(attraction_data, counts)

def get_hotel_ref_data(counts=5):

    # 创建一个新的队列用于接收临时文件路径
    queue = multiprocessing.Queue()

    # 创建一个新的进程来运行爬虫
    p = multiprocessing.Process(target=GetHotelData, args=(queue,))
    p.start()
    p.join()  # 等待子进程结束

    # 从队列中获取临时文件路径
    output_file_path = queue.get()

    # 检查文件是否存在并读取数据
    if os.path.exists(output_file_path):
        with open(output_file_path, 'r', encoding='utf-8') as file:
            hotel_data = json.load(file)
            #print(json.dumps(train_data, indent=4, ensure_ascii=False))
        
        # 删除临时文件
        os.remove(output_file_path)
        print(f"Temporary file {output_file_path} has been deleted.")
    else:
        print(f"Error: Output file {output_file_path} not found.")
    
    # 从数据中随机抽取指定数量的数据项
    return random.sample(hotel_data, counts) 

def get_train_ref_data(dStation, aStation, travelDate, counts=10):

    # 创建一个新的队列用于接收临时文件路径
    queue = multiprocessing.Queue()

    # 创建一个新的进程来运行爬虫
    p = multiprocessing.Process(target=GetTrainData, args=(dStation, aStation, travelDate, queue))
    p.start()
    p.join()  # 等待子进程结束

    # 从队列中获取临时文件路径
    output_file_path = queue.get()
    # 检查文件是否存在并读取数据
    if os.path.exists(output_file_path):
        with open(output_file_path, 'r', encoding='utf-8') as file:
            train_data = json.load(file)
            #print(json.dumps(train_data, indent=4, ensure_ascii=False))
        
        # 删除临时文件
        os.remove(output_file_path)
        print(f"Temporary file {output_file_path} has been deleted.")
    else:
        print(f"Error: Output file {output_file_path} not found.")

    if len(train_data) < counts:
        return train_data
    else:
        return random.sample(train_data, counts)  

def SearchReferenceData(dStation, aStation, Begin_Date, Final_Date, Duration):


    # Final_Date = (Begin_Date + timedelta(days=Duration - 1)).strftime('%Y-%m-%d')
    # Begin_Date = Begin_Date.strftime('%Y-%m-%d')

    restaurant_data = get_restaurant_ref_data()
    attraction_data = get_attraction_ref_data()
    
    hotel_data = get_hotel_ref_data()
    
    go_train = get_train_ref_data(dStation, aStation, Begin_Date)
    return_train = get_train_ref_data(aStation, dStation, Final_Date)

    ref_info = {
            f"在{aStation}的景点": [drop_key(x, key="Website") for x in attraction_data],
            f"在{aStation}的酒店": hotel_data,
            f"在{aStation}的餐厅": restaurant_data,
            f"从{dStation}到{aStation}的列车": go_train,
            f"从{aStation}到{dStation}的列车": return_train
        }
    
    # print(ref_info)

    # print(len(return_train))

    # print(attraction_data)
    
    # print(hotel_data)

    # print(len(attraction_data))
    # print(go_train)
    # print(return_train)

    return ref_info





    
if __name__ == '__main__':
    multiprocessing.freeze_support()  # 在 Windows 上支持多进程时建议添加此行
    print(datetime.now().strftime('%Y-%m-%d'))

    now = datetime.now()
    Duration = 5
    Begin_Date = (now + timedelta(days=7)).strftime('%Y-%m-%d')
    Final_Date = (now + timedelta(days=7+Duration-1)).strftime('%Y-%m-%d')

    print(SearchReferenceData('广州', '秦皇岛', Begin_Date, Final_Date, Duration))

    #attraction_data = get_attraction_ref_data()
    # hotel_data = get_hotel_ref_data()
    # print(hotel_data)



