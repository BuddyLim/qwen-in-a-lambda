"""Main file for handling GGUF model"""

import json
from llama_cpp import Llama
from botocore.exceptions import ClientError

LOCAL_PATH = "./qwen2-1_5b-instruct-q5_k_m.gguf"

llm = Llama(
    model_path=LOCAL_PATH,
    flash_attn=True,
)


def lambda_handler(event, _):
    """Main handler for handling GGUF model"""
    try:
        body = json.loads(event["body"])
        prompt: str = body["prompt"]
        response = llm.create_chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant.",
                },
                {
                    "role": "user",
                    "content": f"""{prompt}""",
                },
            ],
            temperature=0,
        )["choices"][0]["message"]["content"]

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": response,
                }
            ),
            "headers": {
                "Access-Control-Allow-Origin": "*",  # Required for CORS support to work
                "Access-Control-Allow-Methods": "POST",
            },
        }
    except ClientError as e:
        return {
            "statusCode": 500,
            "body": e,
        }
