from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from langgraph.checkpoint.memory import InMemorySaver

import sys
sys.path.append('../')

from tools.base import SYSTEM_PROMPT
from tools.stock_reader import get_stock_value
from tools.news_reader import fetch_stock_news

## OpenAI
model = ChatOpenAI(
    model="gpt-4o-mini",  # or gpt-4o
    temperature=0
)

agent = create_agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[get_stock_value, fetch_stock_news],
    debug=False
)

def invoke_llm(question: str) -> str:
    response = agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
        config={"configurable": {"thread_id": "1"}, "recursion_limit": 10}
    )

    return response['messages'][-1].content, response['messages'][-1].response_metadata['finish_reason']