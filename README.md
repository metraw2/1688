# 1688.com Cost Analyzer for Russia 📦

A comprehensive web application that scrapes product data from 1688.com (Alibaba's Chinese wholesale platform) and analyzes the total cost per unit including shipping to Russia at $2.5/kg.

## Features

### 🔍 Web Scraping
- **Smart Product Discovery**: Searches 1688.com with Chinese or English keywords
- **Comprehensive Data Extraction**: Extracts product titles, prices, weights, volumes, specifications
- **Robust Parsing**: Handles various product page layouts and formats
- **Rate Limiting**: Respectful scraping with appropriate delays

### 💰 Cost Analysis
- **Accurate Price Conversion**: Converts CNY to USD with configurable exchange rates
- **Weight Estimation**: Estimates product weight from volume or dimensions when not available
- **Shipping Cost Calculation**: Calculates shipping costs to Russia at $2.5/kg (configurable)
- **Volumetric Weight**: Considers both actual and volumetric weight for accurate shipping costs
- **MOQ Consideration**: Factors in minimum order quantities for per-unit cost calculation

### 📊 Data Visualization
- **Interactive Charts**: Cost breakdown charts showing product vs shipping costs
- **Metrics Dashboard**: Key statistics and data quality indicators
- **Best Deals Ranking**: Identifies most cost-effective products
- **Export Options**: Download results as CSV or JSON

### 🎯 Smart Features
- **Cost Effectiveness Scoring**: Ranks products by overall value
- **Data Quality Assessment**: Identifies products with complete vs estimated data
- **Shipping Percentage Analysis**: Shows what portion of total cost is shipping
- **Flexible Configuration**: Adjustable shipping rates, exchange rates, and assumptions

## Installation

### Prerequisites
- Python 3.8 or higher
- Chrome browser (for Selenium WebDriver)

### Setup

1. **Clone or download the application files**
```bash
git clone <repository-url>
cd 1688-cost-analyzer
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Chrome WebDriver** (automatic via webdriver-manager)
   - The application will automatically download and configure Chrome WebDriver

## Usage

### Running the Application

1. **Start the Streamlit app**
```bash
streamlit run app.py
```

2. **Open your browser** and navigate to `http://localhost:8501`

### Using the Interface

#### 1. Configuration (Sidebar)
- **Search Query**: Enter Chinese or English keywords (e.g., "电子产品", "bluetooth headphones")
- **Max Pages**: Choose how many search result pages to scrape (1-5)
- **Shipping Rate**: Adjust the shipping cost per kg to Russia (default: $2.5/kg)
- **Exchange Rate**: Set CNY to USD conversion rate (default: 0.14)

#### 2. Analysis Process
1. Enter your search terms
2. Click "Start Analysis"
3. Wait for the scraping and analysis to complete
4. Review the results in multiple sections

#### 3. Results Sections

**📊 Analysis Summary**
- Total products found and analyzed
- Average costs per unit
- Shipping cost statistics
- Data quality metrics

**📈 Cost Analysis Charts**
- Cost breakdown by product (stacked bar chart)
- Shipping vs product cost scatter plot
- Interactive visualizations with hover details

**🏆 Best Deals**
- Top 10 most cost-effective products
- Sorted by cost-effectiveness score
- Formatted table with key metrics

**📋 Detailed Data**
- Complete dataset with all calculated fields
- Customizable column selection
- Sortable and filterable table

**💾 Export Options**
- Download complete analysis as CSV
- Export summary statistics as JSON
- Timestamped filenames

## Understanding the Results

### Key Metrics Explained

- **Original Price (CNY/USD)**: Product price from 1688.com
- **Shipping Cost (USD)**: Calculated shipping cost to Russia based on weight
- **Total Cost (USD)**: Product price + shipping cost
- **Cost per Unit (USD)**: Total cost divided by minimum order quantity
- **Shipping Percentage**: What portion of total cost is shipping
- **Cost Effectiveness Score**: Lower is better (considers price, data quality, shipping ratio)

### Data Quality Indicators

- **Green metrics**: Complete data with actual weights/dimensions
- **Yellow metrics**: Estimated data based on volume or assumptions
- **Red metrics**: Missing critical data (weight, volume, dimensions)

### Weight Calculation Priority

1. **Actual Weight**: From product specifications (most accurate)
2. **Estimated from Volume**: Using assumed density (300 kg/m³ default)
3. **Estimated from Dimensions**: Extracted from product descriptions
4. **Volumetric Weight**: For shipping calculation (whichever is higher)

## Configuration Options

### Shipping Settings
- **Shipping Rate**: Adjust based on current rates to Russia
- **Volumetric Factor**: International shipping standard (5000 default)
- **Density Assumption**: For weight estimation (300 kg/m³ for electronics)

### Search Settings
- **Max Pages**: Balance between data quantity and processing time
- **Search Query**: Use specific terms for better results
- **Language**: Works with both Chinese and English queries

### Advanced Settings
- **Exchange Rate**: Update based on current CNY/USD rates
- **Density Factors**: Adjust for different product categories
- **Volumetric Calculations**: Modify for different shipping services

## Tips for Best Results

### Search Optimization
- Use specific product names rather than generic terms
- Try both Chinese and English keywords
- Include brand names or model numbers for precision
- Use category-specific terms (e.g., "手机配件" for phone accessories)

### Data Interpretation
- Products with actual weight data are most reliable
- Consider shipping percentage when comparing deals
- Factor in MOQ requirements for bulk ordering
- Verify results with supplier for large orders

### Cost Considerations
- Shipping rates may vary by season and shipping method
- Exchange rates fluctuate daily
- Consider additional costs (customs, handling, insurance)
- Factor in potential quality and warranty differences

## Limitations

### Technical Limitations
- Depends on 1688.com website structure (may break if site changes)
- Limited by anti-bot measures on 1688.com
- Chrome browser required for JavaScript-heavy pages
- Processing time increases with more pages/products

### Data Limitations
- Not all products have complete weight/dimension data
- Prices may not include all fees or bulk discounts
- Shipping estimates are based on standard rates
- MOQ information may not always be accurate

### Legal/Ethical Considerations
- Respects website robots.txt and rate limits
- For research and comparison purposes only
- Always verify data with suppliers directly
- Comply with local laws regarding web scraping

## Troubleshooting

### Common Issues

**"No products found"**
- Check internet connection
- Try different search terms
- Verify 1688.com is accessible
- Check if site structure has changed

**"Chrome WebDriver error"**
- Ensure Chrome browser is installed
- Update Chrome to latest version
- Check system permissions
- Try restarting the application

**"Analysis taking too long"**
- Reduce max pages setting
- Check system resources
- Try simpler search terms
- Restart the application

**"Inaccurate cost data"**
- Verify exchange rate settings
- Check shipping rate configuration
- Review weight estimation assumptions
- Cross-reference with supplier quotes

### Performance Optimization
- Start with 1-2 pages for testing
- Use specific search terms to reduce irrelevant results
- Close other browser tabs/applications
- Consider running during off-peak hours

## Contributing

This application is designed to be extensible and customizable:

- **Add new data sources**: Extend scraper for other Chinese platforms
- **Improve accuracy**: Enhance weight/dimension extraction algorithms
- **Add features**: Include additional cost factors (customs, insurance)
- **Optimize performance**: Implement parallel scraping or caching

## Disclaimer

This tool is for research and comparison purposes only. Users should:
- Verify all data with suppliers directly
- Comply with applicable laws and terms of service
- Use responsibly and ethically
- Consider this as estimates, not guarantees

Actual costs may vary based on many factors including shipping method, packaging, customs duties, current exchange rates, and supplier terms.

---

**Made with ❤️ for smart sourcing and cost analysis**