from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel

load_dotenv()

llm = AzureChatOpenAI(model="gpt-4.1-mini")


# -----------------------------------------------------------------

template = ChatPromptTemplate.from_template(
    "You are an expert in {domain}. Answer this question: {question}"
)
messages = template.invoke(
    {"domain": "biology", "question": "How many bones in a human?"}
)


template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an expert in {domain}."),
        ("human", "{question}"),
    ]
)
messages = template.invoke({"domain": "astronomy", "question": "How big is the Sun?"})


print("Messages:", messages)
response = llm.invoke(messages)
print("Response:", response.content)

# -----------------------------------------------------------------
prompt = "Name one city."
chain = llm | StrOutputParser()
result = chain.invoke(prompt)
print(result)


prompt = ChatPromptTemplate.from_template("Name one city. Return the result as JSON.")
chain = prompt | llm | JsonOutputParser()
result = chain.invoke({})
print(result)


class City(BaseModel):
    name: str
    country: str


structured_llm = llm.with_structured_output(City, method="function_calling")
city: City = structured_llm.invoke("Name one city.")
print(city)
