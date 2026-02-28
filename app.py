from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
import aws

GoogleModel = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=1.0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

@tool
def get_public_s3():
    """Get S3 buckets that are publicly exposed"""
    return f"There are {aws.getS3BucketCount()} public s3 buckets!"

@tool
def get_data_in_s3(name: str):
    """Get file names of data within an s3 bucket
    Args:
        name: The name of the S3 bucket to inspect.
    """
    fileList = '\n'.join(aws.getS3Files(name))
    return f"These are the files within the called S3 bucket {fileList}"

@tool
def get_IAM_permissions(name: str):
    """Get permissions of a user
    Args:
        name: The IAM username.
    """
    return f"The user has the following permissions from all policies {aws.getUserPermissions(name)}"

@tool
def get_EC2_Info(IP: str):
    """Get the ec2 size type
    Args:
        IP: The IP address of the instance.
    """
    return f"The resource size found is {aws.getEC2ResourceSize(IP)}"

agent = create_agent(
    model=GoogleModel,
    tools=[get_public_s3, get_data_in_s3, get_IAM_permissions,get_EC2_Info],
    system_prompt="You are an expert AWS assistant",
)

tools = [get_public_s3, get_data_in_s3, get_IAM_permissions, get_EC2_Info]
agent = create_agent(GoogleModel, tools)

inputs = {"messages": [("user", "How many buckets are publicly exposed? What are the files in the 'TestBucket1'. What are the permissions of 'testuser' and what is the size of the EC2 at 10.0.1.3")]}

for chunk in agent.stream(inputs, stream_mode="values"):
    if "messages" in chunk:
        final_message = chunk["messages"][-1]

print(final_message.content)
'''
The project involves building a natural language chatbot that is capable of 
answering questions about an AWS account. You should be using the LangChain 
framework (https://python.langchain.com/docs/introduction/) and, more specifically, 
adding various AWS APIs in the form of custom 
Tools (https://python.langchain.com/docs/modules/agents/tools/custom_tools). 

Here are a few sample questions the chatbot should be able to answer:


When you return the problem, please include the code, a readme, 
    requirements.txt, and some sample output in a zip file.
'''