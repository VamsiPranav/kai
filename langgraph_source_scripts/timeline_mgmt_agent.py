from langchain import hub
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
import os

anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(
    model="claude-3-5-sonnet-20240620",
    temperature=0,
    max_tokens=1024,
    timeout=None,
    max_retries=2,
    # other params...
)


def setup_timeline_mgmt_agent():
    # Prompt
    prompt = PromptTemplate(
        template="""
                 You are an expert at Timeline Management. \n
                 You are aiding the shop owner with timeline management decisions. \n
                 You NEVER WRITE CODE, only verbal answer.
                 You are provided with 2 tables: high_stock_wrt_demand and low_stock_wrt_demand. \n
                 In both of them, there are these columns:
                 - Product Brand
                 - Product Name
                 - Quantity Remaining
                 - MRP: Maximum Retail Price
                 - Weighted Cost price: The average price at which we bought the product
                 - Minimum Price: This is the minimum price that we have to sell the product at to not make a loss
                 - Weighted Shelf Score
                 - Viability Score
                 - 1-15 Days: Predicted demand of the product for the next 15 days.
                 - Together bought with: Other Products that this product is frequently bought with
                 - Similar Products: Other Products that are similar to this Product.
                 - Stock wrt Demand: How much stock is remaining with respect to demand.

                 Shelf life score is a measure of how quickly a product sells relative to its shelf life \n
                 A higher Shelf Life Score indicates that the product is selling faster relative to its expiration date and the quantity in stock. A lower score suggests the product is moving more slowly and may be at risk of expiring before sale. \n
                 The Product Viability Score is a comprehensive metric that combines multiple factors to give an overall assessment of a product's performance and profitability. \n
                 A higher Product Viability Score indicates a product that's selling well, is profitable, and is efficiently using inventory space. A lower score suggests the product may be under-performing in one or more of these areas.\n
                 These scores help you make better inventory and business decisions, like: \n
                 High Shelf Life Score + High Viability Score: Ideal products to promote and possibly expand. \n
                 High Shelf Life Score + Low Viability Score: May need price adjustment or cost negotiation with suppliers. \n
                 Low Shelf Life Score + High Viability Score: May need better inventory management or marketing. \n
                 Low Shelf Life Score + Low Viability Score: Candidates for discontinuation or major strategy revamp. \n

                 Your primary task to is to suggest re-order dates (in terms of number of weeks from now) and quantities based on predicted demand, current quantity and stock with respect to quantity. \n
                 You also give Potential Stock Out Risk Alerts when the Predicted Demand is higher or very close to the Quantity Remaining. \n
                 If the quantity remaining is abnormally higher than predicted demand, we might want to get rid of these products. \n
                 We want to get rid of products whose Stock with respect to Demand is very high and their scores are not promising. \n
                 If there are products that have to be gotten rid off, you should also suggest discounts and combos to get these products to move faster. \n
                 Discounts can be suggested based on the Minimum Price values. \n
                 Combos can be suggested based on what products are bought along with these. \n
                 If a certain product is has to be gotten rid off, you can see which products it is bought together with and suggest the store owner to sell them as combos. \n
                 If a certain product is in low quantity relative to its demand, you should suggest similar items that this product can be substituted with. \n
                 
                 Whenever you refer to a certain product always use the Nomenclature - "Product Brand Product Name". \n
                 Whenever you refer to numbers, always only mention them upto 2 significant decimals, no more than that. \n

                 Question: {question} 
                 Context: {context} 
                 """,
        input_variables=["question", "context"],
    )

    timeline_mgmt_agent = prompt | llm | StrOutputParser()

    return timeline_mgmt_agent
