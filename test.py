import boto3

bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-west-2")

messages = [
    {"role": "user", "content": [{"text": "짧은 시를 한 편 써줘"}]}
]

response = bedrock_runtime.converse_stream(  # converse 대신 converse_stream 사용
    modelId="us.amazon.nova-pro-v1:0",
    messages=messages,
    inferenceConfig={
        "temperature": 0.0,
        "maxTokens": 5000,
    }
)

# 스트리밍 응답 처리
for event in response['stream']:
    if 'contentBlockDelta' in event:
        print(event['contentBlockDelta']['delta']['text'], end='', flush=True)
