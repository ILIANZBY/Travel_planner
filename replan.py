import json
from typing import Dict, Any, List
import math

def get_departure_time(transport_info: Dict[str, Any]) -> str:
    """Get departure time handling both DepTime and DepartureTime fields"""
    return transport_info.get("DepartureTime") or transport_info.get("DepTime") or ""

def get_arrival_time(transport_info: Dict[str, Any]) -> str:
    """Get arrival time handling both ArrivalTime and ArrTime fields"""
    return transport_info.get("ArrivalTime") or transport_info.get("ArrTime") or ""

def parse_transport_info(info_string: str) -> Dict[str, Any]:
    """Parse transportation information string into a dictionary"""
    if info_string.strip() == "-":
        return "-"
    
    parts = [part.strip() for part in info_string.split(',')]
    transport_info = {}
    
    for part in parts:
        if ':' in part:
            key, value = part.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            if key == "TrainNumber":
                value = value.split(',')[0].strip()
            
            transport_info[key] = value
            
    return transport_info

def parse_accommodation_info(info_string: str) -> Dict[str, Any]:
    """Parse accommodation information string into a dictionary"""
    if info_string.strip() == "-":
        return "-"
    
    parts = [part.strip() for part in info_string.split(',')]
    if len(parts) == 1:
        return {"HotelName": parts[0], "HouseRules": None}
    return {"HotelName": parts[0], "HouseRules": parts[1]}

def parse_local_constraint(local_constraint: str) -> Dict[str, str]:
    """Parse local constraint string into a dictionary"""
    constraints = {}
    if not local_constraint:
        return constraints
        
    for item in local_constraint.split(","):
        if ':' in item:
            key, value = item.split(":", 1)
            constraints[key.strip()] = value.strip()
    return constraints

def is_valid_go_transport(transport_info: str, test_entry: dict) -> bool:
    """Validate outbound transportation"""
    if transport_info == "-":
        return False
        
    org_city = test_entry["org"]
    dest_city = test_entry["dest"]
    transport_data = parse_transport_info(transport_info)
    
    try:
        ref_info = json.loads(test_entry["reference_information"])
        
        if "TrainNumber" in transport_data:
            go_transportations = ref_info.get(f"从{org_city}到{dest_city}的列车", [])
            for train in go_transportations:
                if (train["TrainNumber"] == transport_data["TrainNumber"] and
                    get_departure_time(train) == get_departure_time(transport_data) and
                    get_arrival_time(train) == get_arrival_time(transport_data)):
                    return True
        elif "FlightNumber" in transport_data:
            go_flights = ref_info.get(f"从{org_city}到{dest_city}的航班", [])
            for flight in go_flights:
                if (flight["FlightNumber"] == transport_data["FlightNumber"] and
                    get_departure_time(flight) == get_departure_time(transport_data) and
                    get_arrival_time(flight) == get_arrival_time(transport_data)):
                    return True
    except (KeyError, TypeError, json.JSONDecodeError):
        pass
        
    return False

def is_valid_return_transport(transport_info: str, test_entry: dict) -> bool:
    """Validate return transportation"""
    if transport_info == "-":
        return False
        
    org_city = test_entry["org"]
    dest_city = test_entry["dest"]
    transport_data = parse_transport_info(transport_info)
    
    try:
        ref_info = json.loads(test_entry["reference_information"])
        
        if "TrainNumber" in transport_data:
            return_transportations = ref_info.get(f"从{dest_city}到{org_city}的列车", [])
            for train in return_transportations:
                if (train["TrainNumber"] == transport_data["TrainNumber"] and
                    get_departure_time(train) == get_departure_time(transport_data) and
                    get_arrival_time(train) == get_arrival_time(transport_data)):
                    return True
        elif "FlightNumber" in transport_data:
            return_flights = ref_info.get(f"从{dest_city}到{org_city}的航班", [])
            for flight in return_flights:
                if (flight["FlightNumber"] == transport_data["FlightNumber"] and
                    get_departure_time(flight) == get_departure_time(transport_data) and
                    get_arrival_time(flight) == get_arrival_time(transport_data)):
                    return True
    except (KeyError, TypeError, json.JSONDecodeError):
        pass
        
    return False

def is_valid_transportation(test_entry: Dict[str, Any], 
                          predicted_entry: Dict[str, Any]) -> bool:
    """Validate all transportation in the plan"""
    plan = predicted_entry["plan"]
    
    # Check transportation constraints first
    local_constraint = test_entry.get("local_constraint", "")
    constraints = parse_local_constraint(local_constraint)
    transportation_constraint = constraints.get("transportation", None)
    
    # Validate each day's transportation
    for i, day in enumerate(plan):
        transport_info = day.get("transportation", "-").strip()
        
        # Skip empty transportation for intermediate days
        if 0 < i < len(plan)-1:
            if transport_info != "-":
                return False
            continue
            
        # Parse transportation data
        transport_data = parse_transport_info(transport_info)
        if transport_data == "-":
            return False
            
        # Check transportation type constraint
        if transportation_constraint:
            transport_type = None
            if "TrainNumber" in transport_data:
                transport_type = "坐火车"
            elif "FlightNumber" in transport_data:
                transport_type = "坐飞机"
                
            if transport_type:
                if (transportation_constraint == "不要坐火车" and transport_type == "坐火车") or \
                   (transportation_constraint == "不要坐飞机" and transport_type == "坐飞机"):
                    return False
                elif (transportation_constraint == "坐火车" and transport_type != "坐火车") or \
                     (transportation_constraint == "坐飞机" and transport_type != "坐飞机"):
                    return False
        
        # Validate specific transportation
        if i == 0:  # Outbound trip
            if not is_valid_go_transport(transport_info, test_entry):
                return False
        elif i == len(plan)-1:  # Return trip
            if not is_valid_return_transport(transport_info, test_entry):
                return False
                
    return True

def is_valid_accommodation(test_entry: Dict[str, Any], 
                         predicted_entry: Dict[str, Any]) -> bool:
    """Validate accommodation information"""
    plan = predicted_entry["plan"]
    dest_city = test_entry["dest"]
    
    try:
        ref_info = json.loads(test_entry["reference_information"])
        accommodations = ref_info.get(f"在{dest_city}的酒店", [])
        valid_hotels = {acc["HotelName"] for acc in accommodations}
    except (KeyError, json.JSONDecodeError):
        return False
        
    for i, day in enumerate(plan):
        acc_info = day.get("accommodation", "-").strip()
        if acc_info == "-":
            if i != len(plan)-1:  # Only last day can have no accommodation
                return False
            continue
            
        acc_data = parse_accommodation_info(acc_info)
        if isinstance(acc_data, dict) and acc_data["HotelName"] not in valid_hotels:
            return False
            
    return True

def is_valid_attractions(test_entry: Dict[str, Any],
                        predicted_entry: Dict[str, Any]) -> bool:
    """Validate attractions in the plan"""
    plan = predicted_entry["plan"]
    dest_city = test_entry["dest"]
    
    try:
        ref_info = json.loads(test_entry["reference_information"])
        attractions = ref_info.get(f"在{dest_city}的景点", [])
        valid_attractions = {attr["Name"] for attr in attractions}
    except (KeyError, json.JSONDecodeError):
        return False
        
    for day in plan:
        attr_info = day.get("attraction", "-").strip()
        if attr_info != "-":
            attr_name = attr_info.split(",")[0].strip()
            if attr_name not in valid_attractions:
                return False
                
    return True

def is_valid_restaurants(test_entry: Dict[str, Any],
                        predicted_entry: Dict[str, Any]) -> bool:
    """Validate restaurants in the plan"""
    plan = predicted_entry["plan"]
    dest_city = test_entry["dest"]
    used_restaurants = set()
    
    try:
        ref_info = json.loads(test_entry["reference_information"])
        restaurants = ref_info.get(f"在{dest_city}的餐厅", [])
        valid_restaurants = {rest["Name"] for rest in restaurants}
    except (KeyError, json.JSONDecodeError):
        return False
        
    for day in plan:
        for meal in ['breakfast', 'lunch', 'dinner']:
            rest_info = day.get(meal, "-").strip()
            if rest_info != "-":
                if rest_info in used_restaurants:
                    return False
                if rest_info not in valid_restaurants:
                    return False
                used_restaurants.add(rest_info)
                
    return True

def is_valid_days(test_entry: Dict[str, Any], 
                 predicted_entry: Dict[str, Any]) -> bool:
    """Validate number of days matches"""
    return test_entry["days"] == len(predicted_entry["plan"])

def is_reasonable_visiting_city(test_entry: Dict[str, Any], 
                              predicted_entry: Dict[str, Any]) -> bool:
    """Validate city visiting sequence is reasonable"""
    plan = predicted_entry["plan"]
    org_city = test_entry["org"]
    dest_city = test_entry["dest"]
    
    for i, day in enumerate(plan):
        current_city = day.get("current_city", "")
        
        if i == 0:  # First day should be from origin to destination
            if not (current_city == f"从{org_city}到{dest_city}" or 
                   org_city in current_city.split("到")[0]):
                return False
        elif i == len(plan)-1:  # Last day should be from destination back to origin
            if not (current_city == f"从{dest_city}到{org_city}" or 
                   dest_city in current_city.split("到")[0]):
                return False
        else:  # Middle days should be at destination
            if current_city != dest_city:
                return False
                
    return True

def get_total_cost(test_entry: Dict[str, Any], 
                 predicted_entry: Dict[str, Any]) -> float:
    """Calculate total cost of the trip with consideration of people number"""
    plan = predicted_entry["plan"]
    total_cost = 0.0
    people_number = test_entry.get("people_number", 1)
    DEFAULT_RESTAURANT_PRICE = 80 
    
    # Transportation costs
    for i, day in enumerate(plan):
        transport_info = day.get("transportation", "-").strip()
        if transport_info == "-":
            continue
            
        transport_data = parse_transport_info(transport_info)
        if transport_data == "-":
            continue
            
        try:
            ref_info = json.loads(test_entry["reference_information"])
            
            if i == 0:  # Outbound trip
                if "TrainNumber" in transport_data:
                    trains = ref_info.get(f"从{test_entry['org']}到{test_entry['dest']}的列车", [])
                    for train in trains:
                        if (train["TrainNumber"] == transport_data["TrainNumber"] and
                            get_departure_time(train) == get_departure_time(transport_data)):
                            total_cost += float(train["Price"]) * people_number
                            break
                elif "FlightNumber" in transport_data:
                    flights = ref_info.get(f"从{test_entry['org']}到{test_entry['dest']}的航班", [])
                    for flight in flights:
                        if (flight["FlightNumber"] == transport_data["FlightNumber"] and
                            get_departure_time(flight) == get_departure_time(transport_data)):
                            total_cost += float(flight["Price"]) * people_number
                            break
            elif i == len(plan)-1:  # Return trip
                if "TrainNumber" in transport_data:
                    trains = ref_info.get(f"从{test_entry['dest']}到{test_entry['org']}的列车", [])
                    for train in trains:
                        if (train["TrainNumber"] == transport_data["TrainNumber"] and
                            get_departure_time(train) == get_departure_time(transport_data)):
                            total_cost += float(train["Price"]) * people_number
                            break
                elif "FlightNumber" in transport_data:
                    flights = ref_info.get(f"从{test_entry['dest']}到{test_entry['org']}的航班", [])
                    for flight in flights:
                        if (flight["FlightNumber"] == transport_data["FlightNumber"] and
                            get_departure_time(flight) == get_departure_time(transport_data)):
                            total_cost += float(flight["Price"]) * people_number
                            break
        except (KeyError, ValueError, json.JSONDecodeError):
            continue
    
    # Accommodation costs
    try:
        ref_info = json.loads(test_entry["reference_information"])
        hotels = ref_info.get(f"在{test_entry['dest']}的酒店", [])
        hotel_prices = {}
        hotel_capacity = {}
        
        for hotel in hotels:
            try:
                price_str = hotel.get("Price", "¥0").replace('¥', '').replace(',', '')
                hotel_prices[hotel["HotelName"]] = float(price_str)
                hotel_capacity[hotel["HotelName"]] = int(hotel.get("MaximumOccupancy", 2))
            except (ValueError, KeyError):
                continue
                
    except (KeyError, json.JSONDecodeError):
        hotel_prices = {}
        hotel_capacity = {}
        
    for day in plan:
        acc_info = day.get("accommodation", "-").strip()
        if acc_info == "-":
            continue
            
        acc_data = parse_accommodation_info(acc_info)
        if isinstance(acc_data, dict) and acc_data["HotelName"] in hotel_prices:
            price = hotel_prices[acc_data["HotelName"]]
            capacity = hotel_capacity.get(acc_data["HotelName"], 2)
            # Calculate number of rooms needed
            num_rooms = max(1, math.ceil(people_number / capacity))
            total_cost += price * num_rooms
    

    try:
        ref_info = json.loads(test_entry["reference_information"])
        restaurants = ref_info.get(f"在{test_entry['dest']}的餐厅", [])
        restaurant_prices = {}
        
        for restaurant in restaurants:
            try:
                avg_cost = restaurant.get("Average Cost", "")
                if not avg_cost or avg_cost == "[]":
                    # 价格为空时使用默认值80
                    avg_cost = DEFAULT_RESTAURANT_PRICE
                elif isinstance(avg_cost, str):
                    # 处理字符串格式的价格
                    avg_cost = avg_cost.replace('¥', '').replace(',', '').strip()
                    avg_cost = float(avg_cost) if avg_cost else DEFAULT_RESTAURANT_PRICE
                else:
                    # 直接使用数字价格
                    avg_cost = float(avg_cost)
                
                restaurant_prices[restaurant["Name"]] = float(avg_cost)
            except (ValueError, KeyError):
                # 解析失败时使用默认值80
                restaurant_prices[restaurant["Name"]] = DEFAULT_RESTAURANT_PRICE
                
    except (KeyError, json.JSONDecodeError):
        restaurant_prices = {}
        
    for day in plan:
        for meal in ['breakfast', 'lunch', 'dinner']:
            rest_info = day.get(meal, "-").strip()
            if rest_info != "-":
                # 如果餐厅在参考信息中，使用其价格；否则使用默认价格80
                meal_price = restaurant_prices.get(rest_info, DEFAULT_RESTAURANT_PRICE)
                total_cost += meal_price * people_number
    
    return total_cost

def is_valid_budget(test_entry: Dict[str, Any], 
                   predicted_entry: Dict[str, Any]) -> bool:
    """Validate if total cost is within budget"""
    budget = float(test_entry["budget"])
    total_cost = get_total_cost(test_entry, predicted_entry)
    return total_cost <= budget

def eval_commonsense_constraint(test_entry: Dict[str, Any], 
                              predicted_entry: Dict[str, Any]) -> Dict[str, bool]:
    """Evaluate commonsense constraints"""
    return {
        "is_valid_days": is_valid_days(test_entry, predicted_entry),
        "is_reasonable_visiting_city": is_reasonable_visiting_city(test_entry, predicted_entry),
        "is_valid_attractions": is_valid_attractions(test_entry, predicted_entry),
        "is_valid_transportation": is_valid_transportation(test_entry, predicted_entry),
        "is_valid_restaurant": is_valid_restaurants(test_entry, predicted_entry),
        "is_valid_accommodation": is_valid_accommodation(test_entry, predicted_entry)
    }

def eval_hard_constraint(test_entry: Dict[str, Any], 
                       predicted_entry: Dict[str, Any]) -> Dict[str, bool]:
    """Evaluate hard constraints"""
    return {
        "is_valid_budget": is_valid_budget(test_entry, predicted_entry),
    }

def evaluate_plan(input_string: str, test_entry: Dict[str, Any]) -> str:
    """Main evaluation function that returns pass/fail with detailed feedback"""
    try:
        # Parse the input travel plan
        json_start = input_string.find('{')
        json_end = input_string.rfind('}') + 1
        json_str = input_string[json_start:json_end]
        plan = json.loads(json_str).get('travel_plan', [])
        
        if not plan:
            return "输入的旅行计划格式无效，请检查 JSON 格式是否正确。"
            
        predicted_entry = {"plan": plan}
        
        # Evaluate all constraints
        commonsense_result = eval_commonsense_constraint(test_entry, predicted_entry)
        hard_result = eval_hard_constraint(test_entry, predicted_entry)
        all_checks = {**commonsense_result, **hard_result}
        
        if all(all_checks.values()):
            return 'pass'
        
        # Collect error messages for failures
        error_messages = []
        dest_city = test_entry["dest"]
        org_city = test_entry["org"]
        
        # 1. Check days
        if not all_checks['is_valid_days']:
            error_messages.append(f"行程天数不符合要求：期望 {test_entry['days']} 天，实际安排 {len(plan)} 天")
        
        # 2. Check city sequence
        if not all_checks['is_reasonable_visiting_city']:
            error_messages.append(f"城市行程安排有误：必须从 {org_city} 出发，在 {dest_city} 游览后返回 {org_city}")
        
        # 3. Check attractions
        if not all_checks['is_valid_attractions']:
            invalid_attractions = []
            try:
                attractions = json.loads(test_entry["reference_information"])[f"在{dest_city}的景点"]
                valid_attractions = [attr["Name"] for attr in attractions]
                
                for i, day in enumerate(plan):
                    attr = day.get("attraction", "-").strip()
                    if attr != "-":
                        attr_name = attr.split(",")[0]
                        if attr_name not in valid_attractions:
                            invalid_attractions.append(f"第{i+1}天的景点「{attr_name}」不在推荐列表中")
            except (KeyError, json.JSONDecodeError):
                invalid_attractions.append("无法验证景点信息")
                
            if invalid_attractions:
                error_messages.append("景点安排问题：" + "，".join(invalid_attractions))
        
        # 4. Check transportation
        if not all_checks['is_valid_transportation']:
            trans_errors = []
            local_constraint = test_entry.get("local_constraint", "")
            constraints = parse_local_constraint(local_constraint)
            transportation_constraint = constraints.get("transportation", None)
            
            # Check departure transportation
            if plan[0].get("transportation", "-").strip() == "-":
                trans_errors.append("缺少出发交通安排")
            elif not is_valid_go_transport(plan[0]["transportation"], test_entry):
                trans_errors.append("出发交通信息无效")
            
            # Check return transportation if multi-day trip
            if len(plan) > 1 and plan[-1].get("transportation", "-").strip() == "-":
                trans_errors.append("缺少返程交通安排")
            elif len(plan) > 1 and not is_valid_return_transport(plan[-1]["transportation"], test_entry):
                trans_errors.append("返程交通信息无效")
            
            # Check transportation constraints
            if transportation_constraint:
                transport_type = None
                first_transport = parse_transport_info(plan[0]["transportation"])
                if "TrainNumber" in first_transport:
                    transport_type = "火车"
                elif "FlightNumber" in first_transport:
                    transport_type = "航班"
                
                if transport_type:
                    if transportation_constraint == "不要坐火车" and transport_type == "火车":
                        trans_errors.append("约束要求不要坐火车，但计划使用了火车")
                    elif transportation_constraint == "不要坐飞机" and transport_type == "航班":
                        trans_errors.append("约束要求不要坐飞机，但计划使用了航班")
                    elif transportation_constraint == "坐火车" and transport_type != "火车":
                        trans_errors.append("约束要求坐火车，但计划没有使用火车")
                    elif transportation_constraint == "坐飞机" and transport_type != "航班":
                        trans_errors.append("约束要求坐飞机，但计划没有使用航班")
            
            if trans_errors:
                error_messages.append("交通安排问题：" + "，".join(trans_errors))
        
        # 5. Check budget
        if not all_checks['is_valid_budget']:
            try:
                total_cost = get_total_cost(test_entry, predicted_entry)
                error_messages.append(f"预算超支：总花费 {total_cost:.2f} 元，超过预算 {test_entry['budget']} 元")
            except Exception:
                error_messages.append("预算计算失败")
        
        # 6. Check restaurants
        if not all_checks['is_valid_restaurant']:
            restaurant_errors = []
            try:
                restaurants = json.loads(test_entry["reference_information"])[f"在{dest_city}的餐厅"]
                valid_restaurants = [rest["Name"] for rest in restaurants]
                used_restaurants = set()
                
                for i, day in enumerate(plan):
                    for meal in ['breakfast', 'lunch', 'dinner']:
                        rest = day.get(meal, "-").strip()
                        if rest != "-":
                            if rest not in valid_restaurants:
                                restaurant_errors.append(f"第{i+1}天的{get_meal_name(meal)}「{rest}」不在推荐列表中")
                            elif rest in used_restaurants:
                                restaurant_errors.append(f"第{i+1}天的{get_meal_name(meal)}「{rest}」重复预订")
                            used_restaurants.add(rest)
            except (KeyError, json.JSONDecodeError):
                restaurant_errors.append("无法验证餐厅信息")
                
            if restaurant_errors:
                error_messages.append("餐饮安排问题：" + "，".join(restaurant_errors))
        
        # 7. Check accommodation
        if not all_checks['is_valid_accommodation']:
            acc_errors = []
            try:
                hotels = json.loads(test_entry["reference_information"])[f"在{dest_city}的酒店"]
                valid_hotels = [hotel["HotelName"] for hotel in hotels]
                
                for i, day in enumerate(plan):
                    acc = day.get("accommodation", "-").strip()
                    if i != len(plan)-1 and acc == "-":
                        acc_errors.append(f"第{i+1}天缺少住宿安排")
                    elif acc != "-":
                        acc_name = parse_accommodation_info(acc)["HotelName"]
                        if acc_name not in valid_hotels:
                            acc_errors.append(f"第{i+1}天的住宿「{acc_name}」不在推荐列表中")
            except (KeyError, json.JSONDecodeError):
                acc_errors.append("无法验证住宿信息")
                
            if acc_errors:
                error_messages.append("住宿安排问题：" + "，".join(acc_errors))
        
        # Format final error message
        if error_messages:
            return "旅行计划存在以下问题：\n• " + "\n• ".join(error_messages) + \
                  "\n请根据参考信息重新制定计划。"
        
        return 'pass'
        
    except json.JSONDecodeError:
        return "无法解析旅行计划，请检查JSON格式是否正确。"
    except Exception as e:
        return f"评估过程中发生错误：{str(e)}"

def get_meal_name(meal: str) -> str:
    """Translate meal type to Chinese"""
    return {
        'breakfast': '早餐',
        'lunch': '午餐',
        'dinner': '晚餐'
    }.get(meal, meal)