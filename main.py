import requests
from datetime import datetime, timedelta
import smtplib
from twilio.rest import Client


# --------------------------------- CONSTANTS ------------------------- #
# Stock info
STOCKS = {
    "TSLA" : "Tesla Inc",
    "AAPL" : "Apple Inc",
    "ETSY" : "ETSY Inc"
    # ADD MORE STOCKS HERE IF YOU WOULD LIKE THEM TO BE TRACKED
}

# AV API INFO
AV_API_KEY = "Q8717TL6SNXCIASR"
AV_API_ENDPOINT = "https://www.alphavantage.co/query"
# NEWS API INFO
NEWS_API_KEY = "6fd67846e6a74c8b94822c6795c61f9e"
NEWS_API_ENDPOINT = "https://newsapi.org/v2/everything"
# EMAIL INFO -> FOR EMAIL FUNCTIONALITY
MY_EMAIL = "INSERT YOUR EMAIL"
MY_PASSWORD = "INSERT YOUR EMAIL PASSWORD"
# TWILIO INFO -> FOR TEXT MESSAGE FUNCTIONALITY
ACCOUNT_SID = "INSERT YOUR OWN TWILIO ACCOUNT SID" 
AUTH_TOKEN = "8d5b2fa3dbd2e9e05e3d338d7ce93fa8"
CODE_PHONENUMBER = "INSERT YOUR TWILIO NUMBER"
RECEIVER_PHONENUMBER = "INSERT YOUR NUMBER"

for STOCK in STOCKS:
# ------------------------- STOCK PRICE RETRIEVAL --------------------- #
    av_parameters = {
        "function": "TIME_SERIES_DAILY",
        "symbol": STOCK,
        "datatype": "json",
        "apikey": AV_API_KEY
    }

    response = requests.get(AV_API_ENDPOINT, params=av_parameters)
    response.raise_for_status()
    daily_data = response.json()

    # Getting today, yesterday and the day before yesterdays date
    today_date = str(datetime.now().date())
    yesterday_date = str((datetime.now() - timedelta(1)).date())
    before_yesterday_date = str((datetime.now() - timedelta(2)).date())

    # # Temporary code until AV api has 2021 stock data available
    # stock_price_yesterday = float(daily_data['Time Series (Daily)']["2020-12-30"]["4. close"])
    # stock_price_before_yd = float(daily_data['Time Series (Daily)']["2020-12-29"]["4. close"])

    # Actual code:
    stock_price_yesterday = float(daily_data['Time Series (Daily)'][yesterday_date]["4. close"])
    stock_price_before_yd = float(daily_data['Time Series (Daily)'][before_yesterday_date]["4. close"])

    # Percentage difference between the stocks
    percentage_difference = round(((stock_price_before_yd - stock_price_yesterday) / stock_price_yesterday) * 100, 2)
    print(f"{STOCK}: {percentage_difference}")

    if abs(percentage_difference) > 5.00:
        # --------------------------------------- GETTING NEWS ---------------------------------------- #
        news_parameters = {
            "qInTitle": STOCKS[STOCK],
            "apiKey": NEWS_API_KEY,
            "language": "en"
        }

        response = requests.get(NEWS_API_ENDPOINT, params=news_parameters)
        response.raise_for_status()
        news_data = response.json()["articles"]
        three_articles = news_data[0:3]

        # ----------------------------------- EMAIL SENDER -------------------------------------------- #
        if percentage_difference < 0:
            symbol = "UP"
        else:
            symbol = "DOWN"

        formatted_articles = [f"Headline: {article['title']}. \nBrief: {article['description']} \nMore at: {article['url']}"
                              for article in three_articles]
        # TO SEND AS AN EMAIL:
        # for article in formatted_articles:
        #     with smtplib.SMTP("smtp.gmail.com") as connection:
        #         connection.starttls()
        #         connection.login(user=MY_EMAIL, password=MY_PASSWORD)
        #         try:
        #             connection.sendmail(from_addr=MY_EMAIL, to_addrs=MY_EMAIL,
        #                                 msg=f"subject: {STOCK}: {symbol} by {abs(percentage_difference)}%\n\n{article}")
        #         except:
        #             pass
        #         else:
        #             # SMTP DOESN'T ALLOW NON ASCII CHARACTERS. IF THOSE ARE FOUND THE EMAIL is reformatted.
        #             connection.sendmail(from_addr=MY_EMAIL, to_addrs=MY_EMAIL,
        #                                 msg=f"subject: {STOCK}: {symbol} by {abs(percentage_difference)}%\n\n"
        #                                     f" {three_articles[0]['title']}, for more visit: {three_articles[0]['url']}")

        #TO SEND AS A TEXT MESSAGE:
        for article in formatted_articles:
            client = Client(ACCOUNT_SID, AUTH_TOKEN)
            message = client.messages \
                .create(
                body=f"{STOCK}: {symbol} by {abs(round(percentage_difference))}%\n{article}",
                from_=CODE_PHONENUMBER,
                to=RECEIVER_PHONENUMBER
            )

            print(message.status)
