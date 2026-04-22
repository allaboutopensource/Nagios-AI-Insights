#!/bin/bash
export AWS_ACCESS_KEY_ID="Aasdfsadfsdfsdfsdfsdf"
export AWS_SECRET_ACCESS_KEY="WsdfdsfdsfdsfEnrdSqzNsdfdsfsddfsS/owYCsq"
export AWS_REGION="us-east-1"
export BEDROCK_MODEL_ID="us.anthropic.claude-sonnet-4-20250514-v1:0"
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/sdfdsfdsf/sdfsdfdsfH/06jwi6gj36FRpD"
export SLACK_BOT_TOKEN="xoxb-43543543254324324235-123142314234432-sdfsdfsdfsdfsdfdsgfdhfghB"

/usr/bin/python3 /usr/local/nagios/libexec/bedrock_event_handler.py "$@"
