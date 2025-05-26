import boto3
import json

prompt="""
what is best book of data structure in computer science ? and output should not more than 3.
"""

bedrock=boto3.client(service_name="bedrock-runtime")

payload={
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 200,
    "top_k": 250,
    "stop_sequences": [],
    "temperature": 1,
    "top_p": 0.999,
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": prompt
          }
        ]
      }
    ]
  }

body=json.dumps(payload)
# We used model's Inference profile ID instead of model ID or we can also use AWS ARN of model.
model_id="apac.anthropic.claude-3-5-sonnet-20241022-v2:0"
content_type="application/json"

response=bedrock.invoke_model(
    modelId=model_id,
    contentType=content_type,
    accept=content_type,
    body=body
)

response_body=json.loads(response.get("body").read())
#print("response body=",response_body)

response_content=response_body['content']
#print("content=",response_content)

answer=response_content[0]["text"]
print("answer generated=",answer)