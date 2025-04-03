import sys
import os
import json
import math
from typing import List, Dict, Any
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "..")))
from langchain.prompts import PromptTemplate
from prompts import (planner_agent_prompt, cot_planner_agent_prompt, react_planner_agent_prompt,planner_json_check_prompt,
                            reflect_prompt,react_reflect_planner_agent_prompt, planner_json_agent_prompt,planner_json_react_agent_prompt,REFLECTION_HEADER, REVISED_PROMPT)
# from langchain.chat_models import ChatOpenAI
from langchain.llms.base import BaseLLM
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
import re
import openai
import time
from enum import Enum
from typing import List, Union, Literal, Dict
import argparse
import json
from pydantic import BaseModel
from openai import OpenAI
from replan import evaluate_plan


class Plan(BaseModel):
    travel_plan: List[Dict]

plan_json_schema = Plan.model_json_schema()

class JsonReact:
    """
    A question answering ReAct Agent.
    """
    def __init__(self,
                 agent_prompt: PromptTemplate = planner_json_react_agent_prompt,
                 model_name: str = 'gpt-3.5-turbo-1106',
                 ) -> None:
        
        self.agent_prompt = agent_prompt
        self.query = None
        self.max_steps = 5
        self.reset()
        self.finished = False
        self.answer = ''
        # self.client=openai.Client(api_key='none', base_url="http://localhost:9997/v1")
        self.client = OpenAI(api_key="sk-b76592d22c684cc791b0cf5273fed995", base_url="https://api.deepseek.com")
        
    def llm(self, text):
        try:
            
            response=self.client.chat.completions.create(
                # model="qwen7b-sft-travel",
                # model="3000",
                model="deepseek-chat",
                messages=[{"role": "user", "content": text}],
                temperature=0,
                max_tokens=8000,
                extra_body={"guided_json": plan_json_schema}
                
                )
        except Exception as e:
            print(e)
            
        return response.choices[0].message
    
    def _build_agent_prompt(self) -> str:
        return planner_json_agent_prompt.format(
            text=self.text,
            query=self.query)
    def _build_agent_prompt2(self) -> str:
        return planner_json_react_agent_prompt.format(
            text=self.text,
            query=self.query,
            scratchpad=self.scratchpad)  
    def run(self, text, query,querydata, reset = True) -> None:

        self.query = query
        self.text = text
        self.querydata = querydata
        if reset:
            self.reset()
        

        while not (self.is_halted() or self.is_finished()):
            self.step()
        
        return self.answer


    
    
    def step(self) -> None:


        # Act
        # self.scratchpad += f'\nAction {self.curr_step}:'
        print(f'\nAction {self.curr_step}:')
        print(self.first_step)
        if self.first_step:
            # action = self.prompt_agent(planner_json_agent_prompt)
            # print(self._build_agent_prompt())
            action=self.llm(self._build_agent_prompt()).content
            self.first_step = False
            print(action)
        else:
            print(self._build_agent_prompt2())
            action=self.llm(self._build_agent_prompt2()).content
            
            print(action)
        # print(self.scratchpad.split('\n')[-1])
        self.scratchpad += f'\nAction {self.curr_step}:'+ ' ' + action

        if action.startswith('```json'):
            action = action[7:]  # Remove ```json
        if action.endswith('```'):
            action = action[:-3]  # Remove ```
            
        action = action.strip()
        action_data = json.loads(action)
        for day in action_data.get('travel_plan', []):
            if 'attraction' not in day:
                day['attraction'] = '-'
            if 'accommodation' not in day:
                day['accommodation'] = '-'
                
        result=evaluate_plan(action,self.querydata)
        print(result)
        if result=='pass':
            self.finished = True
            self.answer = action
        else:
            self.scratchpad += f'\nObservation {self.curr_step}: '
            self.scratchpad += result
            self.curr_step += 1
            self.answer=action
        self.first_step = False
    

    
    def is_finished(self) -> bool:
        return self.finished

    def is_halted(self) -> bool:
        return (self.curr_step > self.max_steps) and not self.finished

    def reset(self) -> None:
        self.scratchpad = ''
        self.answer = ''
        self.curr_step = 1
        self.finished = False
        self.first_step = True


