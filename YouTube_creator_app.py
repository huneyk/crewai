import os
import warningfilter

from dotenv import load_dotenv

load_dotenv()

serper_api_key = os.getenv("SERPER_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

print (f"SERPER KEY : {serper_api_key}")
print (f"openai key : {openai_api_key}")