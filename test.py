from dotenv import load_dotenv
from provider import paypal

# Loading env variables...
load_dotenv()


transactions = paypal.Gateway().get_plans()

print(f"Found {len(transactions)} recepits in that range")
