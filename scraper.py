import requests
from bs4 import BeautifulSoup
import csv
import time
import sys

def scrape_goodreads_shelf(user_url, shelf_name="to-get", output_file="goodreads_to_get.csv"):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # Ensure the URL points to the correct shelf
    if "shelf=" not in user_url:
        if "?" in user_url:
            user_url += f"&shelf={shelf_name}"
        else:
            user_url += f"?shelf={shelf_name}"
    
    all_books = []
    page = 1
    
    print(f"Starting scrape for shelf: {shelf_name}")
    
    while True:
        current_url = f"{user_url}&page={page}"
        print(f"Fetching page {page}...")
        
        try:
            response = requests.get(current_url, headers=headers)
            if response.status_code != 200:
                print(f"Error fetching page {page}: Status {response.status_code}")
                break
            
            soup = BeautifulSoup(response.content, "html.parser")
            table = soup.find("table", id="books")
            
            if not table:
                print("No books table found. Shelf might be private or empty.")
                break
                
            rows = table.find_all("tr", class_="bookload")
            if not rows:
                break
                
            for row in rows:
                try:
                    title_elem = row.find("td", class_="field title").find("a")
                    title = title_elem.get_text(strip=True)
                    link = "https://www.goodreads.com" + title_elem["href"]
                    
                    author = row.find("td", class_="field author").find("a").get_text(strip=True)
                    
                    # Clean up author name (Goodreads often adds extra whitespace or '*' for verified)
                    author = author.replace("*", "").strip()
                    
                    all_books.append({
                        "Title": title,
                        "Author": author,
                        "URL": link
                    })
                except AttributeError:
                    continue
            
            # Check if there's a next page
            next_page = soup.find("a", class_="next_page")
            if not next_page:
                break
                
            page += 1
            time.sleep(2)  # Respectful delay
            
        except Exception as e:
            print(f"An error occurred: {e}")
            break

    if all_books:
        keys = all_books[0].keys()
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(all_books)
        print(f"Successfully scraped {len(all_books)} books to {output_file}")
    else:
        print("No books found to save.")

if __name__ == "__main__":
    target_url = "https://www.goodreads.com/review/list/25519145-thomas-reich?shelf=to-get"
    scrape_goodreads_shelf(target_url)
