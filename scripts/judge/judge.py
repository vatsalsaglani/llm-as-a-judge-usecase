from time import time
from llms.base import BaseLLM
from typing import List, Dict
from judge.prompts import JUDGE_PROMPT
from judge.schema import judge_functions


async def judgeResponse(llm: BaseLLM, model: str, messages: List[Dict],
                        system_generated_response: List[Dict]):
    st_time = time()
    messages = [{
        "role": "system",
        "content": JUDGE_PROMPT
    }] + messages + [{
        "role":
        "assistant",
        "content":
        f"System Generated Response: '{system_generated_response}'"
    }]
    fc_available, function_call, usage = await llm.__function_call__(
        messages, model, judge_functions)
    if not fc_available:
        return {"rating": 0, "evaluation": "Unable to rank!"}
    ranking_parameters = function_call[0].get('parameters')
    latency = time() - st_time
    return ranking_parameters, usage, f'{latency:.4f}'
