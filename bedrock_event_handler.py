#!/usr/bin/env python3
import json
import os
import sys
import requests
import boto3

# When Nagios triggers an alert, it calls this script like: 
# ./bedrock_event_handler.py <host> <service> <state> <output> <attempt>
# For example:
# ./bedrock_event_handler.py "web-server-1" "HTTP" "CRITICAL" "HTTP CRITICAL - Unable to connect to port 80" "1"

# so it Sends alert details → AWS Bedrock (Claude model) processes the alert → Bedrock returns a summary(JSON), likely cause, and recommended actions → The script posts this info to a Slack channel.

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "nagios-ai-insights")

def ask_bedrock(host, service, state, output, attempt):
    prompt = f"""
You are an Nagios XI monitoring and alert AI assistant helping engineers respond to monitoring alerts on their system and services.
any hostname starting with iadoscomp is the openstack compute host which is KVM hypervisor based running on dell hardware
any hostname starting with iadossmq is the openstack control plane rabbitmq service running as virtual machine on vmware esxi
any hostname starting with iadosneu or iadosnagt is the openstack control plane neutron service running as virtual machine on vmware esxi
any hostname starting with iadosnov is the openstack control plane nova-compute service running as virtual machine on vmware esxi

Return STRICT JSON only with keys:
summary, likely_cause, recommended_actions
Alert:
Host: {host}
Service: {service}
State: {state}
Output: {output}
Attempt: {attempt}
"""
    client = boto3.client("bedrock-runtime", region_name=AWS_REGION)

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 400,
        "temperature": 0.1,
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": prompt}]}
        ]
    }

    response = client.invoke_model(  # Calls the invoke_model method of the Bedrock client to send the prompt and receive a response from the specified model.
        modelId=BEDROCK_MODEL_ID,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json"
    )
#so the llm receive something like this :
# Alert:
#Host: iadoscomp123
#Service: CPU Load
#State: CRITICAL
#Output: CPU CRITICAL - usage is 95%
#Attempt: 3

    payload = json.loads(response["body"].read())          # Reads the response body from the Bedrock model, decodes it from bytes to a string, and then parses it as JSON to get a Python dictionary.
    print("RAW PAYLOAD:", json.dumps(payload, indent=2))  #Converts Python dict → JSON string and prints it with indentation for readability.

    text = payload["content"][0]["text"]
    print("RAW TEXT:", repr(text))

    if text.startswith("```json"):
        text = text[len("```json"):]
    elif text.startswith("```"):
        text = text[len("```"):]

    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    try:
        return json.loads(text)    # Converts the cleaned text (which should be JSON) into a Python dictionary and returns it. If the text is not valid JSON, it raises a JSONDecodeError.
    except json.JSONDecodeError:
        return {
            "summary": "Model returned non-JSON output",
            "likely_cause": text,
            "recommended_actions": [
                "we need to check the aws Bedrock LLM model response in logs"
            ]
        }

def post_to_slack(host, service, state, output, ai):
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json; charset=utf-8",
    }

    text = (
        f"*Nagios Alert:* {state}\n"
        f"*Host:* {host}\n"
        f"*Service:* {service}\n"
        f"*Output:* {output}\n\n"
        f"*AI Summary:* {ai.get('summary')}\n"    #its an dictionary with keys summary, likely_cause, recommended_actions
        f"*Likely Cause:* {ai.get('likely_cause')}\n"
        f"*Recommended Actions:*\n- " + "\n- ".join(ai.get("recommended_actions", []))
    )

    payload = {
        "channel": SLACK_CHANNEL,
        "text": text
    }

    r = requests.post(url, headers=headers, json=payload, timeout=10)
    r.raise_for_status()
    data = r.json()
    if not data.get("ok"):
        raise RuntimeError(f"Slack API error: {data}")

def main():
    host = sys.argv[1]
    service = sys.argv[2]
    state = sys.argv[3]
    output = sys.argv[4]
    attempt = sys.argv[5]

    ai = ask_bedrock(host, service, state, output, attempt)  # it returns dictionary with the alert details to get the AI-generated summary, likely cause, and recommended actions based on the alert information.
    post_to_slack(host, service, state, output, ai)

if __name__ == "__main__":
    main()
