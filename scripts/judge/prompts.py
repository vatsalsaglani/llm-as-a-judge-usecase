JUDGE_PROMPT = """You will be provided with a system generated response for a set of user messages in the form of function calls that the system proposes to handle the user's request.
Your task is to evaluate how effectively the system generated response meets the user's needs as expressed by the user.

The responses could be functions calls for various actions such as 'MakeCall', 'CallInteraction', 'SendMessage', 'AudioInteraction', 'MapInteraction', and 'Answer'.
Each function call will have parameters detailing the action to be taken.

Here is the scale you should use to build your answer:
1: The response is completely inappropriate: it does not address the user's request at all or is grossly incorrect.
2: The response is partially appropriate: it addresses some aspects of the user's request but misses other important aspects.
3: The response is mostly appropriate: it adequately addresses the user's request but could include more precise parameters or additional relevant actions.
4: The response is excellent: it perfectly matches the user's request and includes all necessary details and parameters.

Apart from scoring you also need to provide you rationale behind the scoring as mentioned in the function schema.
Always output between the <functioncall></functioncall> block.
"""
