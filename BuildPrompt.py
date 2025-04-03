import random
import openai
import json
from datetime import datetime, timedelta
from langchain.prompts import PromptTemplate
from BuildReference import SearchReferenceData

PLANNER_INSTRUCTION_JSON_ZH = """您是一位熟练的规划师。
根据提供的信息和查询，请给我一个详细的计划，包括列车号（例如：T124）、住宿名称等具体信息。
请注意，您计划中的所有信息应来自提供的参考信息。
此外，所有细节应符合常识。符号 '-' 表示该信息不必要。例如，在提供的示例中，您不需要规划返回出发城市后的行程。当您在一天内前往两个城市时，应在“当前城市”部分注明，格式与示例中的相同（即，从 A 到 B）。

一些字段的输出格式解释
transportation: "TrainNumber: <TrainNumber>, <from_org_to_dest>, DepartureTime: <DepartureTime>, ArrivalTime: <ArrivalTime>"
attraction: "<Name>, <Address>"
accommodation: "<Name>"

您必须遵循示例中给出的格式。
请以 JSON 结构提供您的答案，如以下示例：

***** Example Starts *****
问题: 请设计一个从北京出发前往秦皇岛的旅行计划，为期3天，涵盖2024年4月1日至2024年4月3日，预算为2500人民币。
Travel Plan in JSON format:
{{
  'travel_plan': [
  {{'days': 1,
  'current_city': '从北京到秦皇岛',
  'transportation': 'TrainNumber: G9891, 从北京到秦皇岛, DepartureTime: 6:25, ArrivalTime: 08:56',
  'attraction': '鼓楼, 秦皇岛市山海关区龙海大道1号老龙头景区海神庙内',
  'breakfast': '任义烧烤(兴华商城1号楼店)',
  'lunch': '君临麻辣香锅(西顺城小区店)',
  'dinner': '',
  'accommodation': '山海关沐海安澜海景别墅(老龙头店)'}},
 {{'days': 2,
  'current_city': '秦皇岛',
  'transportation': '-',
  'attraction': '悬阳洞, 秦皇岛市山海关区三道关村附近长寿山景区内.',
  'breakfast': '小白楼汤馆(蓝天家园店)',
  'lunch': '老菜馆(教军场路店)',
  'dinner': '常品轩火锅烧烤',
  'accommodation': '山海关沐海安澜海景别墅(老龙头店)'}},
 {{'days': 3,
  'current_city': '从秦皇岛到北京',
  'transportation': 'TrainNumber: G9900, 从秦皇岛到北京, DepartureTime: 20:29, ArrivalTime: 22:10',
  'attraction': '孟姜女庙, 河北省秦皇岛市山海关区望夫石村.',
  'breakfast': '山海渔家(河南路)',
  'lunch': '依铭轩浑锅(唐子寨碧海龙源小区店)',
  'dinner': '金泽饭店',
  'accommodation': '-'}}
 ]
}}
***** Example Ends *****

给定可用的参考信息: {text}
问题: {query}

请注意，您旅行计划中的所有信息（包括TrainNumber, accommodation, attraction, restaurants等）必须只能来自给定的参考信息中，同时您旅行计划中的餐厅，旅游景点不能出现重复。
请不要输出其他内容，请确保输出的内容可以被 json.loads() 解析。
Travel Plan in JSON format:"""

PLANNER_INSTRUCTION_GET_REFERENCE_FROM_QUERY = """你是一个有能力的助手，用户将会给你提供一段关于旅游规划的咨询问题，请你分析出用户的咨询问题中的出发地，目的地，出发日期，返回日期，旅行天数和预算，并且将它们以json格式进行输出
您必须遵循示例中给出的格式。
请以 JSON 结构提供您的答案，如以下示例：

EXAMPLE INPUT:
问题: 请设计一个从北京出发前往秦皇岛的旅行计划，为期3天，涵盖2024年4月1日至2024年4月3日，预算为2500人民币。
EXAMPLE JSON OUTPUT:
{
    "Origin_City": "北京",
    "Dest_City": "秦皇岛",
    "Begin_Date": "2024-04-01",
    "Final_Date": "2024-04-03",
    "Duration": "3",
    "Budget": "2500"
}
其中，Origin_City表示出发地，Dest_City表示目的地，Begin_Date表示出发日期，Final_Date表示返回日期，Duration表示旅行天数，Budget表示预算
日期必须遵循YYYY-MM-DD的格式
"""

planner_json_agent_prompt = PromptTemplate(
                        input_variables=["text", "query"],
                        template = PLANNER_INSTRUCTION_JSON_ZH,
                        )

def get_datetime_from_user(prompt):
    date_str = input(prompt)
    try:
        # 按照 'YYYY-MM-DD' 格式输入日期
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt
    except ValueError:
        print("日期格式不正确，请按 'YYYY-MM-DD' 格式输入")
        return get_datetime_from_user(prompt)  # 递归调用直到输入正确
    
def get_station_from_user(prompt):
    station = input(prompt)
    return station.strip()  # 去除首尾空格

def get_duration_from_user():

    # 获取用户输入的持续天数
    while True:
        try:
            duration = int(input("请输入旅行天数："))
            if duration < 0:
                raise ValueError("旅行天数不能为负数")
            break
        except ValueError as e:
            print(e)
            print("请重新输入有效的旅行天数")

    return duration

def get_random_budget(start, end, is_integer=True):
    """
    从指定区间 [start, end] 中随机取一个数。
    
    参数:
        start (float or int): 区间的起始值（包含）。
        end (float or int): 区间的结束值（包含）。
        is_integer (bool): 是否返回整数，默认为 True。如果为 False，则返回浮点数。
    
    返回:
        int 或 float: 随机生成的数。
    """
    if is_integer:
        # 如果需要整数，使用 random.randint
        return random.randint(start, end)
    else:
        # 如果需要浮点数，使用 random.uniform
        return random.uniform(start, end)

def get_requirement():
    Origin_City = get_station_from_user("请输入出发地:")
    Dest_City = get_station_from_user("请输入目的地:")
    Begin_Date = get_datetime_from_user("请输入出发日期:")
    Duration = get_duration_from_user()

    Final_Date = (Begin_Date + timedelta(days=Duration - 1)).strftime('%Y-%m-%d')
    Begin_Date = Begin_Date.strftime('%Y-%m-%d')

    Budget = get_random_budget(1500, 3000)

    return Origin_City, Dest_City, Begin_Date, Final_Date, Duration, Budget

def BuildQuery(Origin_City, Dest_City, Begin_Date, Final_Date, Duration, Budget):



    #Origin_City, Dest_City, Begin_Date, Final_Date, Duration, Budget = get_requirement()

    query = f"请设计一个从{Origin_City}出发前往{Dest_City}的旅行计划，为期{Duration}天，涵盖{Begin_Date}至{Final_Date}，预算为{Budget}人民币。"
    
    #print(query)

    return query

def MakePrompts():
    Origin_City, Dest_City, Begin_Date, Final_Date, Duration, Budget = get_requirement()

    query = BuildQuery(Origin_City, Dest_City, Begin_Date, Final_Date, Duration, Budget)

    print(query)

    ref_info = SearchReferenceData(dStation=Origin_City, aStation=Dest_City, Begin_Date=Begin_Date, Final_Date=Final_Date,Duration=Duration)

    # 将 query 和 ref_info 填入模板
    final_prompt = planner_json_agent_prompt.format(text=ref_info, query=query)

    print(final_prompt)

    return final_prompt

def Prompts(Origin_City, Dest_City, Begin_Date, Final_Date, Duration, Budget):

    query = BuildQuery(Origin_City, Dest_City, Begin_Date, Final_Date, Duration, Budget)
    ref_info = SearchReferenceData(dStation=Origin_City, aStation=Dest_City, Begin_Date=Begin_Date, Final_Date=Final_Date,Duration=Duration)

    # 将 query 和 ref_info 填入模板
    final_prompt = planner_json_agent_prompt.format(text=ref_info, query=query)

    #print(final_prompt)

    return final_prompt

def Prompts_With_RefInfo(Origin_City, Dest_City, Begin_Date, Final_Date, Duration, Budget):

    query = BuildQuery(Origin_City, Dest_City, Begin_Date, Final_Date, Duration, Budget)
    ref_info = SearchReferenceData(dStation=Origin_City, aStation=Dest_City, Begin_Date=Begin_Date, Final_Date=Final_Date,Duration=Duration)

    # 将 query 和 ref_info 填入模板
    final_prompt = planner_json_agent_prompt.format(text=ref_info, query=query)

    return final_prompt, ref_info

def Get_Reference_Key(prompt):

    openai.api_base = "https://api.deepseek.com/v1"
    openai.api_key = "sk-abc4f46251954d7c84f4b4c6fab7aea6"

    

    #prompt = "请设计一个从广州出发前往秦皇岛的旅行计划，为期5天，涵盖2025-03-10至2025-03-14，预算为3000人民币。"

    response = openai.ChatCompletion.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content":PLANNER_INSTRUCTION_GET_REFERENCE_FROM_QUERY},
            {"role": "user", "content": prompt}
        ],
        response_format={
            'type': 'json_object'
        }
    )

    data = json.loads(response.choices[0].message.content)

    Origin_City = data['Origin_City']
    Dest_City = data['Dest_City']
    Begin_Date = data['Begin_Date']
    Final_Date = data['Final_Date']
    Duration = data['Duration']
    Budget = data['Budget']

    print(data)
    
    return Origin_City, Dest_City, Begin_Date, Final_Date, Duration, Budget
    
    #print(json.loads(response.choices[0].message.content))

if __name__ == '__main__':
    #Get_Reference_Key()
    MakePrompts()

#BuildQuery()