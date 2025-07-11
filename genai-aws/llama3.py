import boto3
import json

prompt="""
what is best book of data structure in computer science ? and output should not more than 3.
"""

bedrock=boto3.client(service_name="bedrock-runtime")

payload={
    "prompt":prompt,
    "max_gen_len":512,
    "temperature":0.5,
    "top_p":0.9
}
body=json.dumps(payload)
model_id="meta.llama3-8b-instruct-v1:0"
content_type="application/json"
response=bedrock.invoke_model(
    body=body,
    modelId=model_id,
    accept=content_type,
    contentType=content_type
)

response_body=json.loads(response.get("body").read())
#print("response body=",response_body)

answer=response_body['generation']
print("answer generated=",answer)