import openai
import json
import re
from datetime import datetime, timedelta
from BuildPrompt import MakePrompts, Prompts, Get_Reference_Key
from openai import OpenAI



def Get_LLM_Planning(prompt):

    # # 设置基础URL
    # openai.api_base = 'https://api.deepbricks.ai/v1'
    # # 设置API密钥
    # openai.api_key = 'sk-GPu5b7DsJFXadLt5gHMsqm9EJXGYCT8QClOl7tiUm9QJI0s0'

    # openai.api_base = "https://api.deepseek.com/v1"
    # openai.api_key = "sk-abc4f46251954d7c84f4b4c6fab7aea6"

    # response = openai.ChatCompletion.create(
    #     #model="gpt-4o",
    #     model="deepseek-chat",
    #     messages=[
    #         {"role": "user", "content": prompt}
    #     ]
    # )
    client = OpenAI(api_key="sk-b76592d22c684cc791b0cf5273fed995", base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": prompt},
        ],
        stream=False
    )
    # 获取生成的查询
    # generated_plan = response['choices'][0]['message']['content'].strip()
    generated_plan =response.choices[0].message.content.strip()
    generated_plan_cleaned = re.sub(r"```(?:json)?\n?|```", "", generated_plan).strip()

    # 打印查询结果
    print(generated_plan_cleaned)

    return generated_plan_cleaned

if __name__=="__main__":
    now = datetime.now()
    Duration = 5
    Begin_Date = (now + timedelta(days=7)).strftime('%Y-%m-%d')
    Final_Date = (now + timedelta(days=7+Duration-1)).strftime('%Y-%m-%d')

    query_prompt = input("旅行规划:")

    Origin_City, Dest_City, Begin_Date, Final_Date, Duration, Budget = Get_Reference_Key(query_prompt)
    # prompts = Prompts(Origin_City, Dest_City, Begin_Date, Final_Date, Duration, Budget)

    # with open("prompt_output.txt","w",encoding="utf-8") as file:
    #     file.write(prompts)

    # with open("prompt_output.txt", "r", encoding="utf-8") as file:
    #     content = file.read()

    

    # plan = Get_LLM_Planning(content)

    # with open("plan_output.txt","w",encoding="utf-8") as file:
    #     file.write(plan)


    #print(plan)
