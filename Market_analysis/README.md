# Market Analysis Tool Demo
__Problem & value proposition__: This project proposes a small agent-based application designed to support investors in making informed investment decisions. It saves time by collecting all the relevant data and gives a short summary to support business decision.

__Agent design approach__: This lightweight Streamlit app leverages GPT-4o-mini as LLM. The agent-driven workflow gathers relevant stock market data and recent news, analyzes the information, and produces a tailored investment recommendation. The application resides within the ```src``` directory. It is designed to be modular, so additional tools or modifications to the workflow can be easily added. The current implementation does not employ memory or state management.

__Usage__: Ask any question related to a publicly traded company or stock.

__Monitoring & logging__: Ask any question related to a publicly traded company or stock. The chart shows the usage within the session, groups successful and failed recommendation generations. A monitoring alert can be set up if the number of failed recommendations are higher than a predefined threshold.

## Usage
__Installation__
Type ```uv sync```<br/>
Then save your OpenAI API key here: ```configs/openai_api_key.txt```

__Running the app__
Activate the virtual environment<br/>
```source .venv/bin/activate```<br/>
Then run the following command: ```streamlit run src/main.py```

__Running unit tests__
```python -m unittest discover -s tests -p '*_test.py'```

## Hosting ideas
The recommended hosting solution for this Streamlit-based demo application is __Amazon EC2__ or __Amazon ECS__, as Streamlit requires a persistent runtime environment. The application can be containerized using Docker and deployed as a long-running service to ensure stability and scalability.

API tokens and other sensitive configuration values should be securely stored in __AWS Secrets Manager__, following best practices for credential management and access control.

If application state persistence is not required, the architecture could be adapted with minor modifications to a more serverless approach. In that case, the frontend could be deployed as a static web application on __Amazon S3__, while the backend logic (e.g., calls to an external LLM provider) could be implemented using __AWS Lambda__.

Logs can be saved into __AWS CloudWatch__.

## Other
The presentation is available <a href="docs/presentation.pptx">here</a>