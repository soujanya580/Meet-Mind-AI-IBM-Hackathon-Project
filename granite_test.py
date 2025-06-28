import requests
import json

ACCESS_TOKEN ="eyJraWQiOiIyMDE5MDcyNCIsImFsZyI6IlJTMjU2In0.eyJpYW1faWQiOiJJQk1pZC02OTIwMDA3N1o1IiwiaWQiOiJJQk1pZC02OTIwMDA3N1o1IiwicmVhbG1pZCI6IklCTWlkIiwianRpIjoiYWNkNGMyNTItYTAxYS00MmQ3LWJhMGYtNjc5YjNkYWE4YTkzIiwiaWRlbnRpZmllciI6IjY5MjAwMDc3WjUiLCJnaXZlbl9uYW1lIjoiU291amFueWEiLCJmYW1pbHlfbmFtZSI6IlMiLCJuYW1lIjoiU291amFueWEgUyIsImVtYWlsIjoic291amFueWFzNTgwQGdtYWlsLmNvbSIsInN1YiI6InNvdWphbnlhczU4MEBnbWFpbC5jb20iLCJhdXRobiI6eyJzdWIiOiJzb3VqYW55YXM1ODBAZ21haWwuY29tIiwiaWFtX2lkIjoiSUJNaWQtNjkyMDAwNzdaNSIsIm5hbWUiOiJTb3VqYW55YSBTIiwiZ2l2ZW5fbmFtZSI6IlNvdWphbnlhIiwiZmFtaWx5X25hbWUiOiJTIiwiZW1haWwiOiJzb3VqYW55YXM1ODBAZ21haWwuY29tIn0sImFjY291bnQiOnsidmFsaWQiOnRydWUsImJzcyI6ImQ2NGRhNjhhYzdlYzRhNDQ5MDA1NTUzNDc5NDYwOTkxIiwiaW1zX3VzZXJfaWQiOiIxMzkwMDc0OSIsImZyb3plbiI6dHJ1ZSwiaW1zIjoiMjk5OTE2NiJ9LCJtZmEiOnsiaW1zIjp0cnVlfSwiaWF0IjoxNzUxMTM2NTI5LCJleHAiOjE3NTExNDAxMjksImlzcyI6Imh0dHBzOi8vaWFtLmNsb3VkLmlibS5jb20vaWRlbnRpdHkiLCJncmFudF90eXBlIjoidXJuOmlibTpwYXJhbXM6b2F1dGg6Z3JhbnQtdHlwZTphcGlrZXkiLCJzY29wZSI6ImlibSBvcGVuaWQiLCJjbGllbnRfaWQiOiJkZWZhdWx0IiwiYWNyIjoxLCJhbXIiOlsicHdkIl19.m7YctTujI7RNsL4TbrD8j2n451BwRPgTa4VRLSvBfAkA-DxMhyfsFsHcpIHpEj3PI-SXNzIXI3G3R7lhci_-UUDfkMbLKVfK6oLoIxUrcqzkxxKRhL2ZrW1RKkr3rhUoA9QOCi3BaeFUxor8m6OkCZ2DsLBJPTrMP3HEtvUKkNfyOVbPCIx3S5EXISU6iJY_whTxJmt7ZhWVh5Poc5cLIZWXBflgPqamfGIsu-t0j7v85-G0GxcuJc06kf1cuHVSt72klG1Tm_CXXMYwVDHdRtbeAoKErcZwxq2e_xmwMWEUIifabM4lUFgzGb1xpj4KMjEMFJnWN5wYJ_fD4j9Zcg"
PROJECT_ID = "beeb36cb-848c-4ab8-a7f6-9a72e95c3df1"
MODEL_ID = "ibm/granite-3-3-8b-instruct"
API_URL = "https://us-south.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# 🧠 Prompt
prompt_text = """You are a smart assistant designed to process meeting conversations.
Summarize the following transcript in bullet points.
Then extract action items with who is responsible and any deadlines.

Transcript:
Manager: Welcome. John, complete the sales report by Friday.
Priya, coordinate with marketing.
I will review updates Monday."""

# 📦 Payload includes project_id
payload = {
    "model_id": MODEL_ID,
    "project_id": PROJECT_ID,
    "messages": [
        {"role": "user", "content": prompt_text}
    ],
    "parameters": {
        "decoding_method": "greedy",
        "max_new_tokens": 300,
        "temperature": 0,
        "top_p": 1
    }
}

# 🚀 API call
response = requests.post(API_URL, headers=headers, json=payload)

# ✅ Response handling
try:
    data = response.json()
    if response.status_code == 200 and "choices" in data:
        output = data["choices"][0]["message"]["content"]
        print("✅ AI Output:\n", output)
    else:
        print("❌ Something went wrong.")
        print("Status Code:", response.status_code)
        print("Message:", data)
except Exception as e:
    print("❌ Failed to parse response:")
    print(str(e))
    print("Raw response:", response.text)