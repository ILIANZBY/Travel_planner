from langchain.prompts import PromptTemplate


ZEROSHOT_REACT_INSTRUCTION = """Collect information for a query plan using interleaving 'Thought', 'Action', and 'Observation' steps. Ensure you gather valid information related to transportation, dining, attractions, and accommodation. All information should be written in Notebook, which will then be input into the Planner tool. Note that the nested use of tools is prohibited. 'Thought' can reason about the current situation, and 'Action' can have 8 different types:
(1) FlightSearch[Departure City, Destination City, Date]:
Description: A flight information retrieval tool.
Parameters:
Departure City: The city you'll be flying out from.
Destination City: The city you aim to reach.
Date: The date of your travel in YYYY-MM-DD format.
Example: FlightSearch[New York, London, 2022-10-01] would fetch flights from New York to London on October 1, 2022.

(2) GoogleDistanceMatrix[Origin, Destination, Mode]:
Description: Estimate the distance, time and cost between two cities.
Parameters:
Origin: The departure city of your journey.
Destination: The destination city of your journey.
Mode: The method of transportation. Choices include 'self-driving' and 'taxi'.
Example: GoogleDistanceMatrix[Paris, Lyon, self-driving] would provide driving distance, time and cost between Paris and Lyon.

(3) AccommodationSearch[City]:
Description: Discover accommodations in your desired city.
Parameter: City - The name of the city where you're seeking accommodation.
Example: AccommodationSearch[Rome] would present a list of hotel rooms in Rome.

(4) RestaurantSearch[City]:
Description: Explore dining options in a city of your choice.
Parameter: City – The name of the city where you're seeking restaurants.
Example: RestaurantSearch[Tokyo] would show a curated list of restaurants in Tokyo.

(5) AttractionSearch[City]:
Description: Find attractions in a city of your choice.
Parameter: City – The name of the city where you're seeking attractions.
Example: AttractionSearch[London] would return attractions in London.

(6) CitySearch[State]
Description: Find cities in a state of your choice.
Parameter: State – The name of the state where you're seeking cities.
Example: CitySearch[California] would return cities in California.

(7) NotebookWrite[Short Description]
Description: Writes a new data entry into the Notebook tool with a short description. This tool should be used immediately after FlightSearch, AccommodationSearch, AttractionSearch, RestaurantSearch or GoogleDistanceMatrix. Only the data stored in Notebook can be seen by Planner. So you should write all the information you need into Notebook.
Parameters: Short Description - A brief description or label for the stored data. You don't need to write all the information in the description. The data you've searched for will be automatically stored in the Notebook.
Example: NotebookWrite[Flights from Rome to Paris in 2022-02-01] would store the informatrion of flights from Rome to Paris in 2022-02-01 in the Notebook.

(8) Planner[Query]
Description: A smart planning tool that crafts detailed plans based on user input and the information stroed in Notebook.
Parameters: 
Query: The query from user.
Example: Planner[Give me a 3-day trip plan from Seattle to New York] would return a detailed 3-day trip plan.
You should use as many as possible steps to collect engough information to input to the Planner tool. 

Each action only calls one function once. Do not add any description in the action.

Query: {query}{scratchpad}"""



zeroshot_react_agent_prompt = PromptTemplate(
                        input_variables=["query", "scratchpad"],
                        template=ZEROSHOT_REACT_INSTRUCTION,
                        )

PLANNER_INSTRUCTION = """You are a proficient planner. Based on the provided information and query, please give me a detailed plan, including specifics such as flight numbers (e.g., F0123456), restaurant names, and accommodation names. Note that all the information in your plan should be derived from the provided data. You must adhere to the format given in the example. Additionally, all details should align with commonsense. The symbol '-' indicates that information is unnecessary. For example, in the provided sample, you do not need to plan after returning to the departure city. When you travel to two cities in one day, you should note it in the 'Current City' section as in the example (i.e., from A to B).

***** Example *****
Query: Could you create a travel plan for 7 people from Ithaca to Charlotte spanning 3 days, from March 8th to March 14th, 2022, with a budget of $30,200?
Travel Plan:
Day 1:
Current City: from Ithaca to Charlotte
Transportation: Flight Number: F3633413, from Ithaca to Charlotte, Departure Time: 05:38, Arrival Time: 07:46
Breakfast: Nagaland's Kitchen, Charlotte
Attraction: The Charlotte Museum of History, Charlotte
Lunch: Cafe Maple Street, Charlotte
Dinner: Bombay Vada Pav, Charlotte
Accommodation: Affordable Spacious Refurbished Room in Bushwick!, Charlotte

Day 2:
Current City: Charlotte
Transportation: -
Breakfast: Olive Tree Cafe, Charlotte
Attraction: The Mint Museum, Charlotte;Romare Bearden Park, Charlotte.
Lunch: Birbal Ji Dhaba, Charlotte
Dinner: Pind Balluchi, Charlotte
Accommodation: Affordable Spacious Refurbished Room in Bushwick!, Charlotte

Day 3:
Current City: from Charlotte to Ithaca
Transportation: Flight Number: F3786167, from Charlotte to Ithaca, Departure Time: 21:42, Arrival Time: 23:26
Breakfast: Subway, Charlotte
Attraction: Books Monument, Charlotte.
Lunch: Olive Tree Cafe, Charlotte
Dinner: Kylin Skybar, Charlotte
Accommodation: -

***** Example Ends *****

Given information: {text}
Query: {query}
Travel Plan:"""


PLANNER_INSTRUCTION_JSON = """You are a proficient planner. 
Based on the provided information and query, please give me a detailed plan, including specifics such as flight numbers (e.g., F0123456), restaurant names, and accommodation names. 
Note that all the information in your plan should be derived from the provided data.  
Additionally, all details should align with commonsense. The symbol '-' indicates that information is unnecessary. For example, in the provided sample, you do not need to plan after returning to the departure city. When you travel to two cities in one day, you should note it in the 'Current City' section as in the example (i.e., from A to B).

You must adhere to the format given in the example.
Provide your answer in JSON structure like this example:

***** Example Starts *****
Query: Could you create a travel plan for 7 people from Ithaca to Charlotte spanning 3 days, from March 8th to March 14th, 2022, with a budget of $30,200?
Travel Plan in JSON format:
{{
  'travel_plan': [
  {{'days': 1,
  'current_city': 'from Ithaca to Charlotte',
  'transportation': 'Flight Number: F3633413, from Ithaca to Charlotte, Departure Time: 05:38, Arrival Time: 07:46',
  'breakfast': "Nagaland's Kitchen, Charlotte",
  'attraction': 'The Charlotte Museum of History, Charlotte',
  'lunch': 'Cafe Maple Street, Charlotte',
  'dinner': 'Bombay Vada Pav, Charlotte',
  'accommodation': 'Affordable Spacious Refurbished Room in Bushwick!, Charlotte'}},
 {{'days': 2,
  'current_city': 'Charlotte',
  'transportation': '-',
  'breakfast': 'Olive Tree Cafe, Charlotte',
  'attraction': 'The Mint Museum, Charlotte;Romare Bearden Park, Charlotte.',
  'lunch': 'Birbal Ji Dhaba, Charlotte',
  'dinner': 'Pind Balluchi, Charlotte',
  'accommodation': 'Affordable Spacious Refurbished Room in Bushwick!, Charlotte'}},
 {{'days': 3,
  'current_city': 'from Charlotte to Ithaca',
  'transportation': 'Flight Number: F3786167, from Charlotte to Ithaca, Departure Time: 21:42, Arrival Time: 23:26',
  'breakfast': 'Subway, Charlotte',
  'attraction': 'Books Monument, Charlotte.',
  'lunch': 'Olive Tree Cafe, Charlotte',
  'dinner': 'Kylin Skybar, Charlotte',
  'accommodation': '-'}}
 ]
}}
***** Example Ends *****

Given reference information: {text}
Query: {query}

Do not output any other content, please ensure that the output content can be parsed by json.loads()
Travel Plan in JSON format:"""


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

PLANNER_INSTRUCTION_JSON_CHECK = """您是一位熟练的规划师。
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

如果问题无法解决的话，不要输出json格式，输出"无法解决"，后面需要跟着无法解决的原因（比如预算给的太低了，没有对应的交通工具等）。
给定可用的参考信息: {text}
问题: {query}

请注意，您旅行计划中的所有信息（包括TrainNumber, accommodation, attraction, restaurants等）必须只能来自给定的参考信息中，同时您旅行计划中的餐厅，旅游景点不能出现重复。
请不要输出其他内容，请确保输出的内容可以被 json.loads() 解析。
在输出无法解决的情况前，必须确保问题没有解决方法，需要给出无法解决的原因。
Travel Plan in JSON format:"""



REVISED_PROMPT = """
You are a proficient planner. Based on the provided information and query, please give me a detailed plan, including specifics such as flight numbers (e.g., F0123456), restaurant names, and accommodation names. Note that all the information in your plan should be derived from the provided data. You must adhere to the format given in the example. Additionally, all details should align with commonsense. The symbol '-' indicates that information is unnecessary. For example, in the provided sample, you do not need to plan after returning to the departure city. When you travel to two cities in one day, you should note it in the 'Current City' section as in the example (i.e., from A to B).

***** Example *****
Query: Could you create a travel plan for 7 people from Ithaca to Charlotte spanning 3 days, from March 8th to March 14th, 2022, with a budget of $30,200?
Travel Plan:
Day 1:
Current City: from Ithaca to Charlotte
Transportation: Flight Number: F3633413, from Ithaca to Charlotte, Departure Time: 05:38, Arrival Time: 07:46
Breakfast: Nagaland's Kitchen, Charlotte
Attraction: The Charlotte Museum of History, Charlotte
Lunch: Cafe Maple Street, Charlotte
Dinner: Bombay Vada Pav, Charlotte
Accommodation: Affordable Spacious Refurbished Room in Bushwick!, Charlotte

Day 2:
Current City: Charlotte
Transportation: -
Breakfast: Olive Tree Cafe, Charlotte
Attraction: The Mint Museum, Charlotte; Romare Bearden Park, Charlotte.
Lunch: Birbal Ji Dhaba, Charlotte
Dinner: Pind Balluchi, Charlotte
Accommodation: Affordable Spacious Refurbished Room in Bushwick!, Charlotte

Day 3:
Current City: from Charlotte to Ithaca
Transportation: Flight Number: F3786167, from Charlotte to Ithaca, Departure Time: 21:42, Arrival Time: 23:26
Breakfast: Subway, Charlotte
Attraction: Books Monument, Charlotte.
Lunch: Olive Tree Cafe, Charlotte
Dinner: Kylin Skybar, Charlotte
Accommodation: -

***** Example Ends *****

Given information: {text}
Query: {query}

Previous Plan:
{revised_plan}

Feedback:
{budget_feedback}

Your task is to revise the plan accordingly. Ensure that the revised plan respects the given budget and includes all necessary details, following the same format and structure as shown in the example above.
Revised Travel Plan:"""


COT_PLANNER_INSTRUCTION = """You are a proficient planner. Based on the provided information and query, please give me a detailed plan, including specifics such as flight numbers (e.g., F0123456), restaurant names, and hotel names. Note that all the information in your plan should be derived from the provided data. You must adhere to the format given in the example. Additionally, all details should align with common sense. Attraction visits and meals are expected to be diverse. The symbol '-' indicates that information is unnecessary. For example, in the provided sample, you do not need to plan after returning to the departure city. When you travel to two cities in one day, you should note it in the 'Current City' section as in the example (i.e., from A to B). 

***** Example *****
Query: Could you create a travel plan for 7 people from Ithaca to Charlotte spanning 3 days, from March 8th to March 14th, 2022, with a budget of $30,200?
Travel Plan:
Day 1:
Current City: from Ithaca to Charlotte
Transportation: Flight Number: F3633413, from Ithaca to Charlotte, Departure Time: 05:38, Arrival Time: 07:46
Breakfast: Nagaland's Kitchen, Charlotte
Attraction: The Charlotte Museum of History, Charlotte
Lunch: Cafe Maple Street, Charlotte
Dinner: Bombay Vada Pav, Charlotte
Accommodation: Affordable Spacious Refurbished Room in Bushwick!, Charlotte

Day 2:
Current City: Charlotte
Transportation: -
Breakfast: Olive Tree Cafe, Charlotte
Attraction: The Mint Museum, Charlotte;Romare Bearden Park, Charlotte.
Lunch: Birbal Ji Dhaba, Charlotte
Dinner: Pind Balluchi, Charlotte
Accommodation: Affordable Spacious Refurbished Room in Bushwick!, Charlotte

Day 3:
Current City: from Charlotte to Ithaca
Transportation: Flight Number: F3786167, from Charlotte to Ithaca, Departure Time: 21:42, Arrival Time: 23:26
Breakfast: Subway, Charlotte
Attraction: Books Monument, Charlotte.
Lunch: Olive Tree Cafe, Charlotte
Dinner: Kylin Skybar, Charlotte
Accommodation: -

***** Example Ends *****

Given information: {text}
Query: {query}
Travel Plan: Let's think step by step. First, """

REACT_PLANNER_INSTRUCTION = """You are a proficient planner. Based on the provided information and query, please give me a detailed plan, including specifics such as flight numbers (e.g., F0123456), restaurant names, and hotel names. Note that all the information in your plan should be derived from the provided data. You must adhere to the format given in the example. Additionally, all details should align with common sense. Attraction visits and meals are expected to be diverse. The symbol '-' indicates that information is unnecessary. For example, in the provided sample, you do not need to plan after returning to the departure city. When you travel to two cities in one day, you should note it in the 'Current City' section as in the example (i.e., from A to B). Solve this task by alternating between Thought, Action, and Observation steps. The 'Thought' phase involves reasoning about the current situation. The 'Action' phase can be of two types:
(1) CostEnquiry[Sub Plan]: This function calculates the cost of a detailed sub plan, which you need to input the people number and plan in JSON format. The sub plan should encompass a complete one-day plan. An example will be provided for reference.
(2) Finish[Final Plan]: Use this function to indicate the completion of the task. You must submit a final, complete plan as an argument.
***** Example *****
Query: Could you create a travel plan for 7 people from Ithaca to Charlotte spanning 3 days, from March 8th to March 14th, 2022, with a budget of $30,200?
You can call CostEnquiry like CostEnquiry[{{"people_number": 7,"day": 1,"current_city": "from Ithaca to Charlotte","transportation": "Flight Number: F3633413, from Ithaca to Charlotte, Departure Time: 05:38, Arrival Time: 07:46","breakfast": "Nagaland's Kitchen, Charlotte","attraction": "The Charlotte Museum of History, Charlotte","lunch": "Cafe Maple Street, Charlotte","dinner": "Bombay Vada Pav, Charlotte","accommodation": "Affordable Spacious Refurbished Room in Bushwick!, Charlotte"}}]
You can call Finish like Finish[Day: 1
Current City: from Ithaca to Charlotte
Transportation: Flight Number: F3633413, from Ithaca to Charlotte, Departure Time: 05:38, Arrival Time: 07:46
Breakfast: Nagaland's Kitchen, Charlotte
Attraction: The Charlotte Museum of History, Charlotte
Lunch: Cafe Maple Street, Charlotte
Dinner: Bombay Vada Pav, Charlotte
Accommodation: Affordable Spacious Refurbished Room in Bushwick!, Charlotte

Day 2:
Current City: Charlotte
Transportation: -
Breakfast: Olive Tree Cafe, Charlotte
Attraction: The Mint Museum, Charlotte;Romare Bearden Park, Charlotte.
Lunch: Birbal Ji Dhaba, Charlotte
Dinner: Pind Balluchi, Charlotte
Accommodation: Affordable Spacious Refurbished Room in Bushwick!, Charlotte

Day 3:
Current City: from Charlotte to Ithaca
Transportation: Flight Number: F3786167, from Charlotte to Ithaca, Departure Time: 21:42, Arrival Time: 23:26
Breakfast: Subway, Charlotte
Attraction: Books Monument, Charlotte.
Lunch: Olive Tree Cafe, Charlotte
Dinner: Kylin Skybar, Charlotte
Accommodation: -]
***** Example Ends *****

You must use Finish to indict you have finished the task. And each action only calls one function once.
Given information: {text}
Query: {query}{scratchpad} """

REFLECTION_HEADER = 'You have attempted to give a sub plan before and failed. The following reflection(s) give a suggestion to avoid failing to answer the query in the same way you did previously. Use them to improve your strategy of correctly planning.\n'

REFLECT_INSTRUCTION = """You are an advanced reasoning agent that can improve based on self refection. You will be given a previous reasoning trial in which you were given access to an automatic cost calculation environment, a travel query to give plan and relevant information. Only the selection whose name and city match the given information will be calculated correctly. You were unsuccessful in creating a plan because you used up your set number of reasoning steps. In a few sentences, Diagnose a possible reason for failure and devise a new, concise, high level plan that aims to mitigate the same failure. Use complete sentences.  

Given information: {text}

Previous trial:
Query: {query}{scratchpad}

Reflection:"""

REACT_REFLECT_PLANNER_INSTRUCTION = """You are a proficient planner. Based on the provided information and query, please give me a detailed plan, including specifics such as flight numbers (e.g., F0123456), restaurant names, and hotel names. Note that all the information in your plan should be derived from the provided data. You must adhere to the format given in the example. Additionally, all details should align with common sense. Attraction visits and meals are expected to be diverse. The symbol '-' indicates that information is unnecessary. For example, in the provided sample, you do not need to plan after returning to the departure city. When you travel to two cities in one day, you should note it in the 'Current City' section as in the example (i.e., from A to B). Solve this task by alternating between Thought, Action, and Observation steps. The 'Thought' phase involves reasoning about the current situation. The 'Action' phase can be of two types:
(1) CostEnquiry[Sub Plan]: This function calculates the cost of a detailed sub plan, which you need to input the people number and plan in JSON format. The sub plan should encompass a complete one-day plan. An example will be provided for reference.
(2) Finish[Final Plan]: Use this function to indicate the completion of the task. You must submit a final, complete plan as an argument.
***** Example *****
Query: Could you create a travel plan for 7 people from Ithaca to Charlotte spanning 3 days, from March 8th to March 14th, 2022, with a budget of $30,200?
You can call CostEnquiry like CostEnquiry[{{"people_number": 7,"day": 1,"current_city": "from Ithaca to Charlotte","transportation": "Flight Number: F3633413, from Ithaca to Charlotte, Departure Time: 05:38, Arrival Time: 07:46","breakfast": "Nagaland's Kitchen, Charlotte","attraction": "The Charlotte Museum of History, Charlotte","lunch": "Cafe Maple Street, Charlotte","dinner": "Bombay Vada Pav, Charlotte","accommodation": "Affordable Spacious Refurbished Room in Bushwick!, Charlotte"}}]
You can call Finish like Finish[Day: 1
Current City: from Ithaca to Charlotte
Transportation: Flight Number: F3633413, from Ithaca to Charlotte, Departure Time: 05:38, Arrival Time: 07:46
Breakfast: Nagaland's Kitchen, Charlotte
Attraction: The Charlotte Museum of History, Charlotte
Lunch: Cafe Maple Street, Charlotte
Dinner: Bombay Vada Pav, Charlotte
Accommodation: Affordable Spacious Refurbished Room in Bushwick!, Charlotte

Day 2:
Current City: Charlotte
Transportation: -
Breakfast: Olive Tree Cafe, Charlotte
Attraction: The Mint Museum, Charlotte;Romare Bearden Park, Charlotte.
Lunch: Birbal Ji Dhaba, Charlotte
Dinner: Pind Balluchi, Charlotte
Accommodation: Affordable Spacious Refurbished Room in Bushwick!, Charlotte

Day 3:
Current City: from Charlotte to Ithaca
Transportation: Flight Number: F3786167, from Charlotte to Ithaca, Departure Time: 21:42, Arrival Time: 23:26
Breakfast: Subway, Charlotte
Attraction: Books Monument, Charlotte.
Lunch: Olive Tree Cafe, Charlotte
Dinner: Kylin Skybar, Charlotte
Accommodation: -]
***** Example Ends *****

{reflections}

You must use Finish to indict you have finished the task. And each action only calls one function once.
Given information: {text}
Query: {query}{scratchpad} """

PLANNER_INSTRUCTION_REACT_JSON = """您是一位熟练的规划师。
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
失败记录与反思：{scratchpad}

如果失败记录中有反思，请根据反思调整你的计划。
请注意，您旅行计划中的所有信息（包括TrainNumber, accommodation, attraction, restaurants等）必须只能来自给定的参考信息中，同时您旅行计划中的餐厅，旅游景点不能出现重复。
请不要输出其他内容，请确保输出的内容可以被 json.loads() 解析。
Travel Plan in JSON format:"""



planner_agent_prompt = PromptTemplate(
                        input_variables=["text", "query"],
                        template = PLANNER_INSTRUCTION,
                        )

planner_json_agent_prompt = PromptTemplate(
                        input_variables=["text", "query"],
                        template = PLANNER_INSTRUCTION_JSON_ZH,
                        )

planner_json_check_prompt=PromptTemplate(
                        input_variables=["text", "query"],
                        template = PLANNER_INSTRUCTION_JSON_CHECK,
                        )

cot_planner_agent_prompt = PromptTemplate(
                        input_variables=["text","query"],
                        template = COT_PLANNER_INSTRUCTION,
                        )

react_planner_agent_prompt = PromptTemplate(
                        input_variables=["text","query", "scratchpad"],
                        template = REACT_PLANNER_INSTRUCTION,
                        )

reflect_prompt = PromptTemplate(
                        input_variables=["text", "query", "scratchpad"],
                        template = REFLECT_INSTRUCTION,
                        )

react_reflect_planner_agent_prompt = PromptTemplate(
                        input_variables=["text", "query", "reflections", "scratchpad"],
                        template = REACT_REFLECT_PLANNER_INSTRUCTION,
                        )


planner_json_react_agent_prompt = PromptTemplate(
                        input_variables=["text", "query", "scratchpad"],
                        template = PLANNER_INSTRUCTION_REACT_JSON,
                        )