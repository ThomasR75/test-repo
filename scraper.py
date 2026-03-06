import requests
import csv
import time
import re

def scrape_goodreads_shelf_public(user_id, shelf_name="to-get", output_file="goodreads_to_get.csv"):
    # Goodreads public shelf URLs typically look like this:
    # https://www.goodreads.com/review/list_rss/25519145?shelf=to-get
    # Using the RSS feed is often more reliable for public data as it's cleaner than HTML
    
    rss_url = f"https://www.goodreads.com/review/list_rss/{user_id}?shelf={shelf_name}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print(f"Fetching RSS feed for shelf: {shelf_name}")
    
    try:
        response = requests.get(rss_url, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching RSS: Status {response.status_code}")
            return
            
        xml_content = response.text
        
        # Extract items from RSS
        items = re.findall(r'<item>(.*?)</item>', xml_content, re.DOTALL)
        
        all_books = []
        for item in items:
            title = re.search(r'<title>(.*?)</title>', item, re.DOTALL)
            author = re.search(r'<author_name>(.*?)</author_name>', item, re.DOTALL)
            link = re.search(r'<link>(.*?)</link>', item, re.DOTALL)
            
            if title:
                # Clean CDATA and whitespace
                t = title.group(1).replace('<![CDATA[', '').replace(']]>', '').strip()
                a = author.group(1).replace('<![CDATA[', '').replace(']]>', '').strip() if author else "Unknown"
                l = link.group(1).strip() if link else ""
                
                all_books.append({
                    "Title": t,
                    "Author": a,
                    "URL": l
                })
        
        if all_books:
            keys = all_books[0].keys()
            with open(output_file, "w", newline="", encoding="utf-8") as f:
                dict_writer = csv.DictWriter(f, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(all_books)
            print(f"Successfully saved {len(all_books)} books to {output_file}")
        else:
            print("No books found in the RSS feed. The shelf may be private or empty.")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Extracted ID from your URL
    user_id = "25519145"
    scrape_goodreads_shelf_public(user_id)
