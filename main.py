import requests
from twilio.rest import Client
import html
import os


STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

URL = "https://www.alphavantage.co/query"
API_KEY = os.environ.get("API_KEY")


def sign_and_perc(values):
    difference = float(values[0]) - float(values[1])
    if difference > 0:
        sign = "🔺"
    else:
        sign = "🔻"
    perc = round((abs(difference)/float(values[1]))*100, 3)
    return f"{sign} {perc}%"


def check_fluctuation(values: list):
    diff = abs(float(values[0]) - float(values[1]))
    ratio = diff/(float(values[1]))
    perc = ratio * 100
    if perc >= 5:
        return True


def get_news():
    url = "https://newsapi.org/v2/everything"
    api_key = os.environ.get("NEWS_API_KEY")
    news_parameter = {
        "q": COMPANY_NAME,
        "searchIn": "title,description",
        "sortBy": "publishedAt",
        "language": "en",
        "apikey": api_key
    }

    r = requests.get(url, params=news_parameter)
    r.raise_for_status()
    news_data = r.json()
    latest_article_list = news_data["articles"][:3]
    return latest_article_list


def send_msg(news: list):
    account_sid = os.environ.get("ACC_SID")
    auth_token = os.environ.get("AUTH_TOKEN")
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        from_="+Number",
        to="+Number",
        body=f"""{STOCK}: {sign_and_perc(closed_values)}
Headline: {news[0]["title"]}
Brief: {html.unescape(news[0]["description"])}


{STOCK}: {sign_and_perc(closed_values)}
Headline: {news[1]["title"]}
Brief: {html.unescape(news[1]["description"])}


{STOCK}: {sign_and_perc(closed_values)}
Headline: {news[2]["title"]}
Brief: {html.unescape(news[2]["description"])}
"""
    )
    print(message.status)


parameters ={
    "function": "TIME_SERIES_DAILY_ADJUSTED",
    "symbol": STOCK,
    "apikey": API_KEY
}

response = requests.get(URL, params=parameters)
response.raise_for_status()
data = response.json()

daily_data = data["Time Series (Daily)"]
list_of_daily_data = [value for (key, value) in daily_data.items()]
last_two_days_value = list_of_daily_data[:2]
closed_values = [item["4. close"] for item in last_two_days_value]
print(closed_values)

# closed_values = [1000, 172.92]


if check_fluctuation(closed_values):
    send_msg(get_news())
