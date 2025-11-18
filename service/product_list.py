from serpapi import GoogleSearch
import pandas as pd
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor
from firecrawl import Firecrawl
 
firecrawl = Firecrawl(api_key="fc-180b0d469569419f99fde0fc08367300")
 
def product_list_service(search_term):

    amazon_stats = get_amazon_price(search_term)
    flipkart_stats = get_flipkart_price(search_term)
    myntra_stats = get_myntra_price(search_term)

    return {"amazon": amazon_stats,
            "flipkart": flipkart_stats,
            "meesho": None,
            "myntra": myntra_stats}

def parse_price(value):
    """Remove currency symbols & convert to float"""
    if not value:
        return None
    value = re.sub(r"[^\d.]", "", value)
    try:
        return float(value)
    except ValueError:
        return None

def get_amazon_price(search_term):
    api_key = "f319fff191241e709c08e8e81354612899e7dae65dda9d44576bd46ace59a1a6"

    all_products = []
    max_pages = 5
    for page in range(1, max_pages + 1):
        params = {
            "engine": "amazon",
            "k": search_term,
            "amazon_domain": "amazon.in",
            "api_key": api_key,
            "page": page
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        products = results.get("organic_results", [])

        if not products:
            break

        for product in products:
            price = parse_price(product.get("price"))
            old_price = parse_price(product.get("old_price"))
            discount_percentage = ""

            if price and old_price and old_price > price:
                discount_percentage = f"{round(((old_price - price) / old_price) * 100)}%"

            cleaned = {
                "asin": product.get("asin", ""),
                "title": product.get("title", ""),
                "link": product.get("link", ""),
                "link_clean": product.get("link", "").split("?")[0] if product.get("link") else "",
                "price": product.get("price", ""),
                "old_price": product.get("old_price", ""),
                "offers": product.get("offers", ""),
                "prime": product.get("prime", ""),
                "delivery": product.get("delivery", ""),
                "location": "India",
                "discount_percentage": discount_percentage,
                "variants": product.get("variants", "")
            }

            all_products.append(cleaned)
    # Convert to DataFrame for cleaning and stats
    df = pd.DataFrame(all_products)
    df = df[df['price'] != '']

    df['price'] = df['price'].replace({'₹': '', ',': ''}, regex=True).astype(float)

    return {
        "min": int(df['price'].min()),
        "max": int(df['price'].max()),
        "avg": float(round(df['price'].mean(), 2))
    }

# Worker function (runs Firecrawl scrape)
def scrape_page(search_term, page):
    base_url = "https://www.flipkart.com/search?q={}&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&page={}"
    url = base_url.format(search_term, page)
    print(f"Scraping page {page}: {url}")
    result = firecrawl.scrape(url, formats=scrape_format)
    return result.json.get("products", [])

# Async wrapper
async def scrape_all_pages(search_term, max_pages=5):
    all_products = []
    loop = asyncio.get_event_loop()
 
    # Run tasks in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=5) as executor:
        tasks = [
            loop.run_in_executor(executor, scrape_page, search_term, page)
            for page in range(1, max_pages + 1)
        ]
        results = await asyncio.gather(*tasks)
 
    # Merge results
    for products in results:
        all_products.extend(products)
 
    return {"products": all_products}

def get_flipkart_price(search_term):
    final_result = asyncio.run(scrape_all_pages(search_term, 5))
    product = final_result.get("products", [])
    
    df=pd.DataFrame(product)
    
    
    #remove ₹ and commas
    df["original_price"] = df["original_price"].astype(str).str.replace("₹", "").str.replace(",", "")
    
    #  convert to numeric (invalid → NaN)
    df["original_price"] = pd.to_numeric(df["original_price"], errors="coerce")
    
    # Drop rows where original_price is null
    df = df.dropna(subset=["original_price"])
    
    
    min=int(df['original_price'].min())
    max=int(df['original_price'].max())
    avg=float(round(df['original_price'].mean(), 2))
    
    return {
        'min':min,
        'max':max,
        'avg':avg
    }

scrape_format = [{
    "type": "json",
    "prompt": "Extract all product details including product name, original price, discount price, ratings, reviews count, discount percentage, brand, and product URL",
    "schema": {
        "type": "object",
        "properties": {
            "products": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "original_price": {"type": "string"},
                        "discount_price": {"type": "string"},
                        "rating": {"type": "string"},
                        "reviews_count": {"type": "string"},
                        "discount_percentage": {"type": "string"},
                        "brand": {"type": "string"},
                        "product_url": {"type": "string"}
                    },
                    "required": ["name", "original_price", "discount_price", "rating"]
                }
            }
        },
        "required": ["products"]
    }
}]
 
def scrape_page_myntra(search_term, page):
    base_url = f"https://www.myntra.com/{search_term}?rawQuery={search_term}&p={page}"
    result = firecrawl.scrape(base_url, formats=scrape_format)
    return result.json.get("products", [])

async def scrape_all_pages_myntra(search_term, max_pages=5):
    all_products = []
    loop = asyncio.get_event_loop()

    with ThreadPoolExecutor(max_workers=5) as executor:
        tasks = [
            loop.run_in_executor(executor, scrape_page_myntra, search_term, page)
            for page in range(1, max_pages + 1)
        ]
        results = await asyncio.gather(*tasks)

    for products in results:
        all_products.extend(products)

    return {"products": all_products}

def get_myntra_price(search_term):
    final_result = asyncio.run(scrape_all_pages_myntra(search_term, 5))
    product = final_result.get("products", [])

    df = pd.DataFrame(product)
    df["original_price"] = df["original_price"].astype(str).str.replace("₹", "").str.replace(",", "").str.replace("Rs. ", "")
    df["original_price"] = pd.to_numeric(df["original_price"], errors="coerce")
    df = df.dropna(subset=["original_price"])

    return {
        'min': int(df['original_price'].min()),
        'max': int(df['original_price'].max()),
        'avg': float(round(df['original_price'].mean(), 2))
    }