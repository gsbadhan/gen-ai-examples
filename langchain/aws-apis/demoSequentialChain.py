from langchain_aws import BedrockLLM
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# Initialize Llama 3
llm = BedrockLLM(
    model_id="meta.llama3-8b-instruct-v1:0",
    region_name="ap-south-1",
    model_kwargs={"temperature": 0.5, "max_gen_len": 512}
)

# --- Step 1: Generate book list ---
book_list_prompt = PromptTemplate(
    input_variables=["topic", "number_of_books"],
    template="Suggest best book's name based on {topic}. Include top {number_of_books} books."
)
book_list_chain = book_list_prompt | llm 

# --- Step 2: Create summary of books ---
book_summary_prompt = PromptTemplate(
    input_variables=["book_list"],
    template="""Write 50 words description on {book_list}."""
)
book_summary_chain = book_summary_prompt | llm

# --- Step 3: Make conlusion ---
book_conclusion_prompt = PromptTemplate(
    input_variables=["book_summary"],
    template="""tell me which is top rating book from: {book_summary}."""
)
book_conclusion_chain = book_conclusion_prompt | llm



# Correct sequential chain construction
book_recommendation_chain = (
    RunnablePassthrough.assign(
        book_list=lambda x: book_list_chain.invoke({
            "topic": x["topic"],
            "number_of_books": x["number_of_books"]
        })
    )
    .assign(
        book_summary=lambda x: book_summary_chain.invoke({"book_list": x["book_list"]})
    )
    .assign(
        conclusion=lambda x: book_conclusion_chain.invoke({"book_summary": x["book_summary"]})
    )
)


# Execute properly
result = book_recommendation_chain.invoke({
    "topic": "data structure in computer science",
    "number_of_books": "3"
})
print(result)
