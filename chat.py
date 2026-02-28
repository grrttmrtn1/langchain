from langchain.tools import tool
from langchain.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

GoogleModel = ChatGoogleGenerativeAI(
    model="gemini-3.1-pro-preview",
    temperature=1.0,  # Gemini 3.0+ defaults to 1.0
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# Define the tool
@tool(description="Get the current weather in a given location")
def get_weather(location: str) -> str:
    return "It's sunny."


# Initialize and bind (potentially multiple) tools to the model
model_with_tools = ChatGoogleGenerativeAI(model=GoogleModel).bind_tools([get_weather])

# Step 1: Model generates tool calls
messages = [HumanMessage("What's the weather in Boston?")]
ai_msg = model_with_tools.invoke(messages)
messages.append(ai_msg)

# Check the tool calls in the response
print(ai_msg.tool_calls)

# Step 2: Execute tools and collect results
for tool_call in ai_msg.tool_calls:
    # Execute the tool with the generated arguments
    tool_result = get_weather.invoke(tool_call)
    messages.append(tool_result)

# Step 3: Pass results back to model for final response
final_response = model_with_tools.invoke(messages)
final_response