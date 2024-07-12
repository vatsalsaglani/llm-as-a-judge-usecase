from llms.base import BaseLLM
from datetime import datetime
from mitigate.prompts import (CAN_ANSWER_WITH_INHERENT_KNOWLEDGE,
                              ANSWER_WITH_INHERENT_KNOWLEDGE_PROMPT,
                              VERIFY_SEARCH_TOOL_NEEDED,
                              SEARCH_RESPONSE_PROMPT, DEFINED_TOOL_CALL)
from mitigate.utils import calculateLinearProbability
from mitigate.search import brave_search
from typing import List, Dict
from configs import CLASSIFICATION_THRESHOLD
from mitigate.schemas import *


async def canUseInherentKnowledge(llm: BaseLLM, model: str,
                                  messages: List[Dict]):
    messages = [{
        'role':
        "system",
        "content":
        CAN_ANSWER_WITH_INHERENT_KNOWLEDGE.format(
            date=datetime.today().strftime('%d-%m-%Y'))
    }] + messages
    output = await llm.__complete__(messages,
                                    model,
                                    logprobs=True,
                                    top_logprobs=1,
                                    seed=42,
                                    temperature=0.2)
    # print(output)
    output_label, logprobs, usage = output
    linear_probability = calculateLinearProbability(logprobs[0])
    if linear_probability > CLASSIFICATION_THRESHOLD:
        return output_label, usage
    return None, usage


async def answerWithInherentKnowledge(llm: BaseLLM, model: str,
                                      messages: List[Dict]):
    messages = [{
        'role': "system",
        "content": ANSWER_WITH_INHERENT_KNOWLEDGE_PROMPT
    }] + messages
    function_call_available, function_call, usage = await llm.__function_call__(
        messages, model, avaialle_non_tool_answering, seed=42, temperature=0.2)
    if function_call_available:
        return function_call, usage
    return None, usage


async def verifySearchRequired(llm: BaseLLM, model: str, messages: List[Dict]):
    messages = [{
        'role':
        "system",
        "content":
        VERIFY_SEARCH_TOOL_NEEDED.format(
            date=datetime.today().strftime('%d-%m-%Y'))
    }] + messages
    output = await llm.__complete__(messages,
                                    model,
                                    logprobs=True,
                                    top_logprobs=1,
                                    seed=42,
                                    temperature=0.2)
    output_label, logprobs, usage = output
    # print(f"SEARCH REQUIRED LABEL: ", output_label)
    linear_probability = calculateLinearProbability(logprobs[0])
    if linear_probability > CLASSIFICATION_THRESHOLD:
        return output_label, usage
    return None, usage


async def searchGenAnswer(llm: BaseLLM, model: str, messages: List[Dict]):
    search_query = messages[-1].get("content")
    search_results = await brave_search(search_query)
    if not search_results:
        return False, "Unable to search! Please try again later!"
    messages[-1][
        "content"] += "\n\n" + "Search results: " + "\n" + f"```{search_results}```"
    messages = [{
        'role': "system",
        "content": SEARCH_RESPONSE_PROMPT
    }] + messages
    function_call_available, function_call, usage = await llm.__function_call__(
        messages, model, avaialle_non_tool_answering, seed=42, temperature=0.2)
    if function_call_available:
        return True, function_call, usage
    return False, "Unable to search! Please try again later!", usage


async def callDefinedAction(llm: BaseLLM, model: str, messages: List[Dict]):
    messages = [{'role': "system", "content": DEFINED_TOOL_CALL}] + messages
    function_call_available, function_call, usage = await llm.__function_call__(
        messages,
        model,
        available_domain_specific_tools,
        seed=42,
        temperature=0.2)
    if function_call_available:
        return function_call, usage
    return None, usage
