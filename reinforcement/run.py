from Account import Account
from dotenv import load_dotenv

load_dotenv()
myAccount = Account(
    key="PAPER_API_KEY", secretKey="PAPER_API_KEY_SECRET", endpoint="PAPER_API_ENDPOINT"
)


class Trade_Options(Enum):
    buy = 1
    sell = -1
