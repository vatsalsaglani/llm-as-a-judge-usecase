import os
import re
import json
from llms.base import BaseLLM
from llms.openai.context import MessageManagement
from configs import OPENAI_API_KEY, OPEN_ROUTER_API_KEY
from openai import AsyncOpenAI, RateLimitError, APIConnectionError
from typing import List, Dict, Union

FUNCTION_CALLING_SYSTEM_PROMPT = """You are a helpful assistant with access to the following functions:

    {functions}

    To use these functions respond with:
    <multiplefunctions>
        <functioncall> {{fn}} </functioncall>
        <functioncall> {{fn}} </functioncall>
        ...
    </multiplefunctions>

    Edge cases you must handle:
    - If there are no functions that match the user request, you will respond politely that you cannot help.<|im_end|>

    Refer the below provided output example for function calling
    Question: What's the weather difference in NY and LA?
    <multiplefunctions>
        <functioncall> {{"name": "getWeather", "parameters": {{"city": "NY"}}}} </functioncall>
        <functioncall> {{"name": "getWeather", "parameters": {{"city": "LA"}}}} </functioncall>
    </multiplefunctions>

    Note: You can even select only <functioncall> inside <multiplefunctions> block if needed.
    """


def extractUsingRegEx(output_text: str):
    pattern = r"<functioncall>\s*(\{.*?\})\s*</functioncall>"
    matches = re.findall(pattern, output_text, re.DOTALL)

    results = []
    for json_string in matches:
        try:
            json_data = json.loads(json_string)
            results.append(json_data)
        except json.JSONDecodeError as err:
            print(f"Error decoding JSON: {str(err)}")
            continue
    return results


class OpenAILLM(BaseLLM):

    def __init__(self, **kwargs):
        self.is_openai = kwargs.get("is_openai", True)
        self.base_url = None
        api_key = OPENAI_API_KEY if self.is_openai else OPEN_ROUTER_API_KEY
        if "base_url" in kwargs:
            self.base_url = kwargs.get("base_url")
        if self.base_url:
            self.client = AsyncOpenAI(api_key=api_key, base_url=self.base_url)
        else:
            self.client = AsyncOpenAI(api_key=api_key)
        if self.is_openai:
            self.ctx = MessageManagement(kwargs.get("model"),
                                         kwargs.get("encoding_name", None))
        else:
            self.ctx = None

    async def __complete__(self, messages: List[Dict], model: str, **kwargs):
        if self.is_openai:
            managed_messages = self.ctx(messages, 110_000)
        else:
            managed_messages = messages
        output = await self.client.chat.completions.create(
            messages=managed_messages, model=model, **kwargs)
        # print("OUTPUT: ", output)
        usage = output.usage.__dict__
        output_content = output.choices[0].message.content
        if "logprobs" in kwargs:
            if self.is_openai:
                return output_content, [
                    o.logprob
                    for o in output.choices[0].logprobs.content[0].top_logprobs
                ], usage
            else:
                if "logprobs" in kwargs:
                    return output_content, [-0.014], usage
        return output_content, None, usage

    async def __stream__(self, messages: List[Dict], model: str, **kwargs):
        if self.is_openai:
            managed_messages = self.ctx(messages, 110_000)
        else:
            managed_messages = messages
        stream = await self.client.chat.completions.create(
            model=model, messages=managed_messages, stream=True, **kwargs)
        async for chunk in stream:
            yield chunk.choices[0].delta.content or ""

    async def __function_call__(self, messages: List[Dict], model: str,
                                tools: List[Dict], **kwargs):
        system_message = list(
            filter(lambda message: message.get("role") == "system", messages))
        if len(system_message) > 0:
            system_message = system_message[0]
            system_message["content"] = FUNCTION_CALLING_SYSTEM_PROMPT.format(
                functions=tools
            ) + "\n\n" + "Task: " + "\n\n" + system_message.get("content")

        else:
            system_message = {
                "role": "system",
                "content":
                FUNCTION_CALLING_SYSTEM_PROMPT.format(functions=tools)
            }
        non_system_messages = list(
            filter(lambda message: message.get("role") != "system", messages))
        messages = [system_message] + non_system_messages
        output_content, _, usage = await self.__complete__(messages, model)
        function_calls = extractUsingRegEx(output_content)
        if function_calls:
            return True, function_calls, usage
        print(f"OUTPUT CONTENT: ", output_content)
        return False, output_content, usage
