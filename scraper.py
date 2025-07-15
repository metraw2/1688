import requests
import re
import time
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import pandas as pd


class AlibabaScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        })
        self.driver = None
        
    def setup_selenium(self):
        """Setup Selenium WebDriver for dynamic content"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument(f'--user-agent={self.ua.random}')
        chrome_options.add_argument('--accept-lang=zh-CN,zh;q=0.9,en;q=0.8')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        return self.driver

    def extract_numbers_from_text(self, text):
        """Extract numeric values from Chinese/English text"""
        if not text:
            return None
        
        # Remove common Chinese characters and extract numbers
        text = str(text).lower()
        
        # Look for patterns like "重量: 5kg", "weight: 5kg", "5公斤", etc.
        weight_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:kg|公斤|千克)',
            r'重量[：:]\s*(\d+(?:\.\d+)?)',
            r'weight[：:]\s*(\d+(?:\.\d+)?)',
        ]
        
        volume_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:m³|立方米|cbm)',
            r'体积[：:]\s*(\d+(?:\.\d+)?)',
            r'volume[：:]\s*(\d+(?:\.\d+)?)',
        ]
        
        # Extract weight
        weight = None
        for pattern in weight_patterns:
            match = re.search(pattern, text)
            if match:
                weight = float(match.group(1))
                break
                
        # Extract volume
        volume = None
        for pattern in volume_patterns:
            match = re.search(pattern, text)
            if match:
                volume = float(match.group(1))
                break
                
        return weight, volume

    def extract_price_from_text(self, text):
        """Extract price information from text"""
        if not text:
            return None
            
        text = str(text).lower()
        
        # Price patterns for RMB/CNY
        price_patterns = [
            r'¥\s*(\d+(?:\.\d+)?)',
            r'rmb\s*(\d+(?:\.\d+)?)',
            r'cny\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*元',
            r'价格[：:]\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)',  # Price range
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, text)
            if matches:
                if isinstance(matches[0], tuple):
                    # Price range - take the lower value
                    return float(matches[0][0])
                return float(matches[0])
        
        return None

    def scrape_product_page(self, url):
        """Scrape individual product page for detailed information"""
        try:
            if not self.driver:
                self.setup_selenium()
                
            self.driver.get(url)
            time.sleep(3)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            product_data = {
                'url': url,
                'title': '',
                'price': None,
                'weight': None,
                'volume': None,
                'shipping_weight': None,
                'package_size': '',
                'supplier': '',
                'moq': None,  # Minimum order quantity
                'raw_specs': ''
            }
            
            # Extract title
            title_selectors = [
                'h1.product-title',
                '.d-title',
                '.subject',
                'h1',
                '.title'
            ]
            
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    product_data['title'] = title_elem.get_text(strip=True)
                    break
            
            # Extract price
            price_selectors = [
                '.price',
                '.unitPrice',
                '.priceRange',
                '[class*="price"]',
                '[class*="Price"]'
            ]
            
            price_text = ''
            for selector in price_selectors:
                price_elems = soup.select(selector)
                for elem in price_elems:
                    price_text += elem.get_text() + ' '
            
            if price_text:
                product_data['price'] = self.extract_price_from_text(price_text)
            
            # Extract specifications and measurements
            spec_selectors = [
                '.property',
                '.attrs',
                '.specifications',
                '.product-params',
                '[class*="spec"]',
                '[class*="attr"]',
                '.table',
                'table'
            ]
            
            specs_text = ''
            for selector in spec_selectors:
                spec_elems = soup.select(selector)
                for elem in spec_elems:
                    specs_text += elem.get_text() + ' '
            
            product_data['raw_specs'] = specs_text[:1000]  # Limit length
            
            # Extract weight and volume from specs
            if specs_text:
                weight, volume = self.extract_numbers_from_text(specs_text)
                product_data['weight'] = weight
                product_data['volume'] = volume
            
            # Extract supplier info
            supplier_selectors = [
                '.shop-name',
                '.supplier-name',
                '.company-name',
                '[class*="shop"]',
                '[class*="supplier"]'
            ]
            
            for selector in supplier_selectors:
                supplier_elem = soup.select_one(selector)
                if supplier_elem:
                    product_data['supplier'] = supplier_elem.get_text(strip=True)
                    break
            
            # Extract MOQ
            moq_text = soup.get_text().lower()
            moq_patterns = [
                r'起订量[：:]\s*(\d+)',
                r'最小订购量[：:]\s*(\d+)',
                r'moq[：:]\s*(\d+)',
                r'minimum[：:]\s*(\d+)',
            ]
            
            for pattern in moq_patterns:
                match = re.search(pattern, moq_text)
                if match:
                    product_data['moq'] = int(match.group(1))
                    break
            
            return product_data
            
        except Exception as e:
            print(f"Error scraping product page {url}: {str(e)}")
            return None

    def search_products(self, query, max_pages=3):
        """Search for products on 1688.com"""
        try:
            if not self.driver:
                self.setup_selenium()
            
            search_url = f"https://s.1688.com/selloffer/offer_search.htm?keywords={query}"
            self.driver.get(search_url)
            time.sleep(3)
            
            products = []
            
            for page in range(max_pages):
                if page > 0:
                    # Navigate to next page
                    try:
                        next_button = self.driver.find_element(By.CSS_SELECTOR, '.next')
                        if next_button and next_button.is_enabled():
                            next_button.click()
                            time.sleep(3)
                        else:
                            break
                    except:
                        break
                
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                
                # Find product links
                product_links = []
                link_selectors = [
                    'a[href*="detail.1688.com"]',
                    'a[href*="offer.1688.com"]',
                    '.offer-item a',
                    '.item a'
                ]
                
                for selector in link_selectors:
                    links = soup.select(selector)
                    for link in links:
                        href = link.get('href')
                        if href and ('detail.1688.com' in href or 'offer.1688.com' in href):
                            if not href.startswith('http'):
                                href = 'https:' + href if href.startswith('//') else 'https://www.1688.com' + href
                            product_links.append(href)
                
                # Remove duplicates
                product_links = list(set(product_links))
                
                print(f"Found {len(product_links)} products on page {page + 1}")
                
                # Scrape each product (limit to first 10 per page to avoid overwhelming)
                for link in product_links[:10]:
                    product_data = self.scrape_product_page(link)
                    if product_data:
                        products.append(product_data)
                    time.sleep(1)  # Be respectful
                
            return products
            
        except Exception as e:
            print(f"Error searching products: {str(e)}")
            return []

    def close(self):
        """Close the webdriver"""
        if self.driver:
            self.driver.quit()

    def __del__(self):
        self.close()


def demo_usage():
    """Demo function to show how to use the scraper"""
    scraper = AlibabaScraper()
    
    try:
        # Search for products
        products = scraper.search_products("电子产品", max_pages=1)
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(products)
        print(f"Scraped {len(df)} products")
        print(df[['title', 'price', 'weight', 'volume']].head())
        
        return df
        
    finally:
        scraper.close()


if __name__ == "__main__":
    demo_usage()