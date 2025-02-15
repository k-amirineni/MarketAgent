from smolagents import CodeAgent, HfApiModel,load_tool,tool
import datetime
import requests
import pytz
import yaml
from tools.final_answer import FinalAnswerTool
from tools.web_search import DuckDuckGoSearchTool

from Gradio_UI import GradioUI
from tools.visit_webpage import VisitWebpageTool
import yfinance as yf

# Below is an example of a tool that does nothing. Amaze us with your creativity !
@tool
def get_stock_price(ticker:str)-> str: 
    #Keep this format for the description / args / args description but feel free to modify the tool
    """A tool that gets the latest stock information for a given ticker symbol.
    Args:
        ticker: the first argument
    """
    end_date = datetime.datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.datetime.today() - datetime.timedelta(days=5)).strftime('%Y-%m-%d')
    data = yf.download(ticker, start=start_date, end=end_date)
    return data.head()

@tool
def analyze_prices(ticker: str) -> any:
    """A tool that analyzes and studies the stock information for a given ticker symbol and provides information on moving averages.
    Args:
        ticker: The stock ticker symbol (e.g., 'AAPL' for Apple).
    """
    try:
        # Fetch historical data
        data = yf.download(ticker, period="1mo", interval="1h") 
        # moving averages
        data['MA20'] = data['Close'].rolling(window=20).mean()
        data['MA50'] = data['Close'].rolling(window=50).mean()

        return data
    except Exception as e:
        return f"Error analyzing trend for {ticker}: {str(e)}"

@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """A tool that fetches the current local time in a specified timezone.
    Args:
        timezone: A string representing a valid timezone (e.g., 'America/New_York').
    """
    try:
        # Create timezone object
        tz = pytz.timezone(timezone)
        # Get current time in that timezone
        local_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return f"The current local time in {timezone} is: {local_time}"
    except Exception as e:
        return f"Error fetching time for timezone '{timezone}': {str(e)}"

# If the agent does not answer, the model is overloaded, please use another model or the following Hugging Face Endpoint that also contains qwen2.5 coder:
# model_id='https://pflgm2locj2t89co.us-east-1.aws.endpoints.huggingface.cloud' 

model = HfApiModel(
max_tokens=2096,
temperature=0.5,
model_id='Qwen/Qwen2.5-Coder-32B-Instruct',# it is possible that this model may be overloaded
custom_role_conversions=None,
)

visit_webpage = VisitWebpageTool()
web_search = DuckDuckGoSearchTool()
final_answer = FinalAnswerTool()


with open("prompts.yaml", 'r') as stream:
    prompt_templates = yaml.safe_load(stream)
    
agent = CodeAgent(
    model=model,
    tools=[final_answer, visit_webpage, web_search,get_stock_price, analyze_prices],
    max_steps=6,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name=None,
    description=None,
    prompt_templates=prompt_templates
)


GradioUI(agent).launch()