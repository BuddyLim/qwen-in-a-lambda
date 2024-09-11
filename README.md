# Qwen in a Lambda

Updated at 11/09/2024

(Marking the date because of how fast LLM APIs in Python move and may introduce breaking changes by the time anyone else reads this!)

## Intro:

- This is a minor research on how we can put Qwen GGUF model files into AWS Lambda using Docker and SAM CLI

- Adapted from https://makit.net/blog/llm-in-a-lambda-function/
  - As of September '24, some required OS packages are not included in the above guide and subsequently in the Dockerfile as potentially the llama-cpp-python does not include the required OS packages (?)
  - Who knows if there's anything new and breaking that will appear in the future :shrugs:

## Motivation:

- I wanted to find out if I can reduce my AWS spending by only leveraging on the capabilities of Lambda and not Lambda + Bedrock as both services would incur more costs in the long run.

- The idea was to fit a small language model which wouldn't be as resource intensive relatively speaking and to, hopefully, receive subsecond to second latency on a 128 - 256 mb memory configuration

- I wanted to use also GGUF models to use different levels of quantization to find out which is the best performance / file size to be loaded into memory
  - My experimentation lead to me using Qwen2 1.5b Q5_K_M as it had the best "performance" and "latency" locally to receive prompt and spit out JSON structure using llama-cpp

## Prerequisites:

- Docker
- AWS SAM CLI
- AWS CLI
- Python 3.11
- ECR permissions
- Lambda permissions
- Download `qwen2-1_5b-instruct-q5_k_m.gguf` into `qwen_fuction/function/`
  - Or download any other .gguf models that you'd like and change your model path in `app.y / LOCAL_PATH`

## Setup Guide:

- Install pip packages under `qwen_function/function/requirements.txt` (preferably in a venv/conda env)
- Run `sam build` / `sam validate`
- Run `sam local start-api` to test locally
- Run `curl --header "Content-Type: application/json" \
--request POST \
--data '{"prompt":"hello"}' \
http://localhost:3000/generate` to prompt the LLM
  - Or use your preferred API clients
- Run `sam deploy --guided` to deploy to AWS

## Metrics

- Localhost - Macbook M3 Pro 32 GB

![alt text](/images/image.png)

- AWS

  - Initial config - 128mb, 30s timeout
    - Lambda timed out! Cold start was timing out the lambda
  - Adjusted config #1 - 512mb, 30s timeout

    - Lambda timed out! Cold start was timing out the lambda

  - Adjusted config #2 - 512mb, 30s timeout
    - Lambda timed out! Cold start was timing out the lambda

![alt text](/images/image-1.png)

- Adjusted config #3 - 3008mb, 30s timeout - cold start

![alt text](/images/image-2.png)

- Adjusted config #3 - 3008mb, 30s timeout - warm start

![alt text](/images/image-3.png)

## Observation

- Referring back to the pricing structure of Lambda,

  - [Pricing](<https://docs.aws.amazon.com/lambda/latest/operatorguide/computing-power.html#:~:text=Since%20the%20Lambda%20service%20charges,and%20duration%20(in%20seconds)>)
  - 1536 MB / 1.465 s / $0.024638 over 1000 Lambda invocations
    - Qwen2 1.5b had me cranking up the memory to 3008mb just to not time out and receive 4 - 11 seconds latency response!
  - Claude 3 Haiku / $0.00025 / $0.00125 over 1000 input tokens & 1000 tokens / Asia - Tokyo

- It may be cheaper to just use a hosted LLM using AWS Bedrock, etc.. on the cloud as the pricing structure for Lambda w/ Qwen does not look more competitive compared to Claude 3 Haiku

- Results via local is dependant on your machine specs!! and may heavily skew your perception, expectation vs reality

- Depending on your use case also, the latency per lambda invocation and responses might incur poor user experiences

### Conclusion

All in all, I think this was a fun little experiment even though it didn't quite pan out to the budget & latency requirement via Qwen 1.5b for my side project. Thanks to @makit again for the guide!
