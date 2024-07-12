import argparse
import json
from tqdm.auto import tqdm
import traceback
from mitigatedetect import mitigateCompleteValidate
from llms.openai.llm import OpenAILLM
from judge.judge import judgeResponse


def setup_argparse():
    parser = argparse.ArgumentParser(description="Evaluate conversations")
    parser.add_argument("--is_openai",
                        action="store_true",
                        help="Weather to use OpenAI Model APIs.")
    parser.add_argument("--model_name",
                        type=str,
                        required=True,
                        help="Name of the model to evaluate")
    parser.add_argument(
        "--open_router_base_url",
        type=str,
        default=None,
        help=
        "Base URL for open router or any other LLM API provider that works with `openai` library."
    )
    return parser.parse_args()


# response llm
# llm = OpenAILLM(model="gpt-4o", encoding_name="o200k_base")

# response llm llama-3-70B
# base url for open router
# llm = OpenAILLM(is_openai=False, base_url="https://openrouter.ai/api/v1")

# judge llm
# judge_llm = OpenAILLM(model="gpt-4-turbo")


async def evaluate(conversations, llm_config):
    ratings = []
    mitigate_complete_validate_token_usage = []
    mitigate_complete_validate_latency = 0
    rating_token_usage = []
    rating_latency = 0
    outputs = []
    print(f"IS OPENAI: ", llm_config.get("is_openai"))
    if llm_config.get("is_openai"):
        llm = OpenAILLM(model="gpt-4o", encoding_name="o200k_base")
    else:
        assert "base_url" in llm_config and len(
            llm_config.get("base_url")
        ) > 0, "When not using OpenAI the `open_router_base_url` cannot be empty."
        llm = OpenAILLM(is_openai=llm_config.get("is_openai"),
                        base_url=llm_config.get("base_url"))
    judge_llm = OpenAILLM(model="gpt-4-turbo")
    for _, conversation in enumerate(tqdm(conversations)):
        try:
            # output, token_usage, latency = await mitigateCompleteValidate(
            #     llm, "gpt-4o", conversation)
            # output, token_usage, latency = await mitigateCompleteValidate(
            #     llm, "meta-llama/llama-3-70b-instruct", conversation)
            output, token_usage, latency = await mitigateCompleteValidate(
                llm, llm_config.get("model_name"), conversation)
            outputs.append(output)
            mitigate_complete_validate_latency += float(latency)
            mitigate_complete_validate_token_usage.append(token_usage)
            if not output == -1:
                rating, usage, latency = await judgeResponse(
                    judge_llm, "gpt-4-turbo", conversation, output)
                rating_latency += float(latency)
                rating_token_usage.append(usage)
                ratings.append(rating)
            else:
                ratings.append({"rating": 0, "evaluation": ""})
        except Exception as err:
            print(traceback.format_exc())
            ratings.append({"rating": 0, "evaluation": "error in response"})
            outputs.append([])
            pass
    # return ratings, mitigate_complete_validate_token_usage, mitigate_complete_validate_latency, rating_token_usage, rating_latency, outputs
    combined_report = []
    for ix in range(len(ratings)):
        combined_report.append({
            "input":
            conversations[ix],
            "system_response":
            outputs[ix],
            "rating":
            ratings[ix],
            "token_usage":
            mitigate_complete_validate_token_usage[ix],
        })
    print("RATINGS: ", ratings)
    average_rating = sum(
        [rating.get("rating")
         for rating in ratings if rating["rating"]]) / len(ratings)
    combined_report = {
        "report":
        combined_report,
        "average_rating":
        average_rating,
        "total_time_for_generating_system_responses":
        mitigate_complete_validate_latency,
        "average_time_for_generating_system_responses":
        mitigate_complete_validate_latency / len(outputs),
        "total_time_for_evaluating":
        rating_latency,
        "average_rating_time":
        rating_latency / len(ratings)
    }
    with open(
            f"./evaluation_report_{llm_config.get('model_name').replace('/', '_')}.json",
            "w") as fp:
        json.dump(combined_report, fp, indent=4)


if __name__ == "__main__":
    import asyncio
    args = setup_argparse()
    llm_config = {"model_name": args.model_name}
    if args.is_openai:
        llm_config = {"model_name": args.model_name, "is_openai": True}
    else:
        llm_config = {"model_name": args.model_name, "is_openai": False}
    if args.open_router_base_url:
        llm_config["base_url"] = args.open_router_base_url
    conversations = json.loads(open("./conversations.json").read())
    print(f"TOTAL RECORDS: {len(conversations)}")
    asyncio.run(evaluate(conversations, llm_config))
