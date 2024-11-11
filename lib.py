import requests
import csv
import requests
from bs4 import BeautifulSoup
import csv
import time

def fetch_saudi_stocks_to_csv():
    # Base URLs for fetching data
    base_url = "https://www.mubasher.info/api/1/listed-companies"
    first_page_url = f"{base_url}?country=sa"
    
    # Fetch the first page to get the number of pages
    response = requests.get(first_page_url)
    response_data = response.json()
    number_of_pages = response_data.get("numberOfPages", 1)
    
    # List to store all stock data
    all_stocks_data = []
    
    # Iterate through each page to fetch data
    for page in range(number_of_pages):
        page_url = f"{base_url}?country=sa&size=20&start={page * 20}"
        response = requests.get(page_url)
        
        # Check if the request was successful
        if response.status_code == 200:
            page_data = response.json()
            stocks = page_data.get("rows", [])
            for stock in stocks:
                # Append each stock's data to all_stocks_data list
                all_stocks_data.append({
                    "name": stock.get("name"),
                    "url": stock.get("url"),
                    "market": stock.get("market"),
                    "sector": stock.get("sector"),
                    "symbol": stock.get("symbol"),
                    "price": stock.get("price"),
                    "changePercentage": stock.get("changePercentage"),
                    "lastUpdate": stock.get("lastUpdate")
                })
        else:
            print(f"Failed to fetch data for page {page + 1}")
    return all_stocks_data

def fetch_additional_stock_data(all_stocks_data):
    # Base URLs for fetching stock data
    base_url_data = "https://www.mubasher.info/markets/TDWL/stocks/{stock_id}"
    base_url_earnings = "https://www.mubasher.info/markets/TDWL/stocks/{stock_id}/earnings"

    

    # Iterate over each stock to fetch additional data
    for stock_data in all_stocks_data:
        stock_id = stock_data["symbol"]
        
        # Fetch main stock data page
        response_data = requests.get(base_url_data.format(stock_id=stock_id))
        response_earnings = requests.get(base_url_earnings.format(stock_id=stock_id))
        
        # Parse main data page
        if response_data.status_code == 200:
            soup_data = BeautifulSoup(response_data.text, "html.parser")
            # Extract values such as Nominal Value, Market Value, Book Value, Profit Multiplier, etc.
            stock_data["Nominal Value"] = soup_data.find("td", text="Nominal value").find_next_sibling("td").text.strip()
            stock_data["Market Value"] = soup_data.find("td", text="Market value").find_next_sibling("td").text.strip()
            stock_data["Book Value"] = soup_data.find("td", text="Book value").find_next_sibling("td").text.strip()
            stock_data["Earnings per Share"] = soup_data.find("td", text="Earnings per share").find_next_sibling("td").text.strip()
            stock_data["Profit Multiplier"] = soup_data.find("td", text="Profit multiplier").find_next_sibling("td").text.strip()

        # Parse earnings page for quarterly and yearly profit data
        if response_earnings.status_code == 200:
            soup_earnings = BeautifulSoup(response_earnings.text, "html.parser")
            # Extract last quarter and yearly profit data
            stock_data["Last Quarter Profit (SAR)"] = soup_earnings.find("td", text="Last quarter profit amount in SAR").find_next_sibling("td").text.strip()
            stock_data["Last Quarter Announce Date"] = soup_earnings.find("td", text="Last quarter profit announce date").find_next_sibling("td").text.strip()
            stock_data["Last Quarter Change"] = soup_earnings.find("td", text="Last quarter profit change").find_next_sibling("td").text.strip()
            stock_data["Last Yearly Profit (SAR)"] = soup_earnings.find("td", text="Last yearly profit amount in SAR").find_next_sibling("td").text.strip()
            stock_data["Last Yearly Announce Date"] = soup_earnings.find("td", text="Last yearly profit announce date").find_next_sibling("td").text.strip()
            stock_data["Last Yearly Change"] = soup_earnings.find("td", text="Last yearly profit change").find_next_sibling("td").text.strip()

        # To avoid overwhelming the server, add a delay between requests
        time.sleep(1)



    return stock_data

def dataToCsv (all_stocks_data):
    # Save data to a CSV file
    with open("saudi_stocks_data.csv", mode="w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=all_stocks_data[0].keys())
        writer.writeheader()
        writer.writerows(all_stocks_data)

    print("Data saved to saudi_stocks_data.csv successfully.")


if __name__ == "__main__":
    dd = fetch_saudi_stocks_to_csv()
    print(dd)
    dataToCsv(dd)
