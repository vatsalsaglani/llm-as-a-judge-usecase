from time import time
from typing import List, Dict
from llms.base import BaseLLM
from mitigate.mitigate import mitigateAndComplete
from detect.detect import verifyFunctionNameAndSchema


async def mitigateCompleteValidate(llm: BaseLLM, model: str,
                                   messages: List[Dict]):
    output = -1
    function_calls, token_usage, latency = await mitigateAndComplete(
        llm, model, messages)
    vst = time()
    # if not function_calls or function_calls == -1:
    #     return -1
    if all([
            verifyFunctionNameAndSchema(function_call)[0]
            for function_call in function_calls
    ]):
        # return function_calls
        output = function_calls
    # else:
    #     return -1
    latency = f"{(time() - vst + float(latency)):.4f}"
    return output, token_usage, latency


if __name__ == "__main__":
    import asyncio
    from llms.openai.llm import OpenAILLM
    base_url = "https://openrouter.ai/api/v1"
    llm = OpenAILLM(base_url=base_url, is_openai=False)
    messages = [{
        "role": "assistant",
        "content": "You are receiving a call from your Jane Doe."
    }, {
        "role":
        "user",
        "content":
        "Reject it and message her that I'm on my way. Also start navigation to Home, HSR Layout."
    }]
    print(
        asyncio.run(
            mitigateAndComplete(llm, "meta-llama/llama-3-70b-instruct",
                                messages)))
