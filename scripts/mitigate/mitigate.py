from llms.base import BaseLLM
from mitigate.layers import *
from time import time


async def mitigateAndComplete(llm: BaseLLM, model: str, messages: List[Dict]):
    st_time = time()
    answer = -1
    token_usage = {
        'completion_tokens': 0,
        'prompt_tokens': 0,
        'total_tokens': 0
    }

    def updateUsage(usage):
        for k, v in usage.items():
            token_usage[k] += v

    reply_with_inherent_knowledge, usage = await canUseInherentKnowledge(
        llm, model, messages)
    updateUsage(usage)
    if reply_with_inherent_knowledge == "YES":
        answer, usage = await answerWithInherentKnowledge(llm, model, messages)
        updateUsage(usage)
        answer = answer
    elif reply_with_inherent_knowledge == "NO":
        need_search, usage = await verifySearchRequired(llm, model, messages)
        updateUsage(usage)
        if need_search == "YES":
            search_status, answer, usage = await searchGenAnswer(
                llm, model, messages)
            updateUsage(usage)
            if search_status:
                # return answer
                answer = answer
        elif need_search == "NO":
            defined_action, usage = await callDefinedAction(
                llm, model, messages)
            updateUsage(usage)
            answer = defined_action if defined_action else -1
    latency = time() - st_time
    return answer, token_usage, f'{latency:.4f}'
