# ✈️ Airline Database Chatbot (Agentic AI on AWS)

An Agentic AI-powered Airline Chatbot that answers real airline flight queries using live MySQL (MariaDB) data, powered by Amazon Bedrock Agents, MCP Server, API Gateway, and a Streamlit UI.

## 🔗 Live Demo (Hugging Face Space)
https://huggingface.co/spaces/Pt-kunal-mishra/Database-Airline_chatbot

## 🧠 High-Level Architecture
```
User (Web / Mobile / Streamlit)
        |
        v
API Gateway (REST API)
        |
        v
AWS Lambda (Agent Invocation)
        |
        v
Amazon Bedrock Agent (Agentic AI)
        |
        v
Action Group (Lambda)
        |
        v
MCP Server (FastAPI)
        |
        v
MariaDB (MySQL View)
```

## 🗄️ Database Layer (MariaDB on EC2)

### Database Object Used
**View name:** `webiste_data.airline_chatbot_view`

**Columns:**
- flight_date
- airline_code_number
- origin_flight
- destination_flight
- cancelled
- arr_delay
- distance
- delay_reason

### Create a Read-Only DB User (Recommended)
```sql
CREATE USER 'mcp_reader'@'%' IDENTIFIED BY 'StrongPassword123!';
GRANT SELECT ON webiste_data.* TO 'mcp_reader'@'%';
FLUSH PRIVILEGES;
```

## 🔌 MCP Server (MySQL Control Plane)

### Purpose
- Secure execution of read-only SQL
- Prevents direct DB access from agents
- Acts as the data control plane

### Tech Stack
- Python
- FastAPI
- Uvicorn
- MariaDB Connector

### Run MCP Server
```bash
uvicorn mcp_server:app --host 0.0.0.0 --port 8080
```

### Run MCP as a Linux Service (Amazon Linux)
```bash
sudo systemctl start mcp
sudo systemctl enable mcp
```

### Test MCP Server
```bash
curl -X POST http://<EC2_PUBLIC_IP>:8080/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <MCP_KEY>" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "mysql_query",
    "params": {
      "sql": "SELECT * FROM webiste_data.airline_chatbot_view LIMIT 1"
    }
  }'
```

## 🤖 Amazon Bedrock Agent

### Agent Details
- **Name:** AirlineChatbot
- **Region:** ap-south-1
- **Type:** Agentic AI (no memory)
- **Language Support:** English (default), Hindi, Bengali

### Action Group
- **Name:** airline_mysql_queries
- **Lambda:** airline-mysql-mcp-bridge
- **Parameter:** sql (string, required)

### Agent Rules (Summary)
- Always call the action group
- Never answer from memory
- Always use SELECT
- Query only `webiste_data.airline_chatbot_view`
- Use LIKE for location matching
- Limit results to 5 rows
- Support date ranges with BETWEEN

## 🧩 Lambda (Agent → MCP Bridge)

### Purpose
- Receives agent tool invocation
- Extracts SQL query
- Calls MCP server
- Returns Bedrock-compliant response

### Required Environment Variables
```bash
MCP_URL=http://<EC2_PUBLIC_IP>:8080/mcp
MCP_KEY=MySecretAirlineKey2025!
```

### Response Format (MANDATORY)
```json
{
  "messageVersion": "1.0",
  "response": {
    "actionGroup": "airline_mysql_queries",
    "function": "queryFlights",
    "functionResponse": {
      "responseBody": {
        "TEXT": {
          "body": "Human readable flight details"
        }
      }
    }
  }
}
```

## 🌐 API Gateway

### Purpose
- Public HTTP entrypoint
- Used by web, mobile, and Streamlit frontend

### Endpoint
```
POST https://esqizm4qw8.execute-api.ap-south-1.amazonaws.com/chat
```

### Request Example
```json
{
  "question": "Flights with delays on January 1 2024"
}
```

### Response Example
```json
{
  "answer": "✈️ Here are the top 5 flights with delays on January 1, 2024..."
}
```

## 🖥️ Streamlit Frontend

### Features
- Chat-style UI
- Uses API Gateway
- Displays real-time flight data
- Handles:
  - Delay queries
  - Date & date-range queries
  - Route-based queries
  - Multilingual input

### Minimal Streamlit Code
```python
import streamlit as st
import requests

API_URL = "https://esqizm4qw8.execute-api.ap-south-1.amazonaws.com/chat"

st.title("✈️ Airline Chatbot")

query = st.text_input("Ask about airline flights")

if query:
    response = requests.post(API_URL, json={"question": query})
    st.write(response.json()["answer"])
```

## 🚢 Deployment (ECS Fargate – No ALB)

### Why No ALB?
- Lower cost
- Simpler setup
- Public IP access for demo

### Deployment Flow
1. Build Docker image
2. Push to ECR
3. Create ECS cluster
4. Register task definition
5. Create security group (port 7860)
6. Run ECS service with public IP

## 🌍 Language Support

| User Input Language | Bot Response |
|-------------------|-------------|
| English | English |
| Hindi | Hindi |
| Bengali | Bengali |

The bot responds only in the user's language.

## 🛡️ Guardrails & Safety

- Read-only DB access
- SQL injection prevention
- Strict tool grounding
- No hallucinated responses
- No off-topic answers

## 🧪 Example Queries

- Flights with delays on January 1 2024
- Is flight 4901 delayed on 2024-01-02?
- New York to Oklahoma flights between Jan 1 and Jan 3
- क्या 2 जनवरी 2024 को फ्लाइट में देरी है?

## 🛠️ Local Development

```bash
# Clone repository
git clone https://huggingface.co/spaces/Pt-kunal-mishra/Database-Airline_chatbot
cd Database-Airline_chatbot

# Install dependencies
pip install -r requirement.txt

# Run locally
streamlit run main.py
```

## 🐳 Docker Deployment

```bash
# Build image
docker build -t airline-chatbot .

# Run container
docker run -p 7860:8080 airline-chatbot
```