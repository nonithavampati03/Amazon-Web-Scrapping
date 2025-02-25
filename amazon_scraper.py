import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# Configure Selenium ChromeDriver with User-Agent Spoofing
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)

# Start WebDriver
driver = webdriver.Chrome(options=chrome_options)

# List to store all scraped data
scraped_data = []

# Function to get paginated URLs
def get_urls(base_url):
    pages = [base_url]  # First page
    for page in range(2, 6):  # Scrape first 5 pages (adjust as needed)
        pages.append(f"{base_url}&page={page}")
    return pages

# Function to extract product data
def get_data(item):
    try:
        # Extract Name
        atag = item.find("h2")
        req_name = atag.text.strip() if atag else "No Name"

        # Extract URL
        req_url = item.find("a", href=True)
        req_url = "https://www.amazon.com" + req_url["href"] if req_url else "No URL"

        # Extract Price
        req_price = item.find("span", class_="a-offscreen")
        req_price = req_price.text.strip() if req_price else "No Price"

        # Extract Rating
        req_rating = item.find("i", class_="a-icon-star-small")
        req_rating = req_rating.text.strip() if req_rating else "No Rating"

        # Extract Number of Reviews
        req_no_of_ratings = item.find("span", class_="a-size-base s-underline-text")
        req_no_of_ratings = req_no_of_ratings.text.strip() if req_no_of_ratings else "No Reviews"

        return {
            "Product Name": req_name,
            "Product URL": req_url,
            "Product Price": req_price,
            "Rating": req_rating,
            "Number of Reviews": req_no_of_ratings
        }
    except Exception as e:
        print(f"⚠️ Error extracting product: {e}")
        return None

# Main scraping function
def main():
    base_url = input("Enter the Amazon search URL: ").strip()  # Get URL from user input
    urls = get_urls(base_url)

    for url in urls:
        print(f"Scraping page: {url}")
        driver.get(url)
        time.sleep(5)  # Allow page to load

        soup = BeautifulSoup(driver.page_source, "html.parser")
        results = soup.find_all("div", {"data-component-type": "s-search-result"})

        print(f"Found {len(results)} products on this page")

        for item in results:
            product_data = get_data(item)
            if product_data:
                scraped_data.append(product_data)

    # Write to CSV after scraping all pages
    field_names = ["Product Name", "Product URL", "Product Price", "Rating", "Number of Reviews"]
    with open("Amazon_Scraped_Data.csv", "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(scraped_data)

    print("✅ Scraping complete. Data saved to 'Amazon_Scraped_Data.csv'.")

# Run the scraper
if __name__ == "__main__":
    main()
    driver.quit()  # Close the WebDriver

