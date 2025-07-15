# Quick Start Guide 🚀

## What This App Does

This application scrapes product data from **1688.com** (Alibaba's Chinese wholesale platform) and calculates the **total cost per unit including shipping to Russia** at **$2.5/kg**.

### Key Features:
- 🔍 **Smart Product Search**: Search in Chinese or English
- 💰 **Cost Analysis**: Calculates product + shipping costs
- 📊 **Best Deals**: Ranks products by cost-effectiveness
- 📈 **Visualizations**: Interactive charts and metrics
- 💾 **Export**: Save results as CSV/JSON

## Quick Setup (2 minutes)

### Option 1: Automatic Setup (Recommended)
```bash
# Run the setup script (handles everything automatically)
./setup.sh
```

### Option 2: Manual Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Test

### 1. Test with Sample Data (No Internet Required)
```bash
# Activate environment (if not already active)
source venv/bin/activate

# Test with sample data
python demo.py --sample --save
```

### 2. Test Web Scraping (Requires Internet)
```bash
# Test scraping electronics products
python demo.py --query "电子产品" --pages 1 --save
```

### 3. Run Full Web Interface
```bash
# Start the web app
streamlit run app.py
```
Then open http://localhost:8501 in your browser.

## Usage Examples

### Web Interface
1. **Enter Search Terms**: "电子产品", "bluetooth headphones", "phone accessories"
2. **Adjust Settings**: Shipping rate ($2.5/kg default), exchange rate (0.14 CNY/USD default)
3. **Start Analysis**: Click "Start Analysis" button
4. **Review Results**: View metrics, charts, and best deals
5. **Export Data**: Download CSV or JSON results

### Command Line
```bash
# Search for USB chargers, analyze 2 pages, save results
python demo.py --query "USB充电器" --pages 2 --save

# Test with different shipping rate
python demo.py --sample --shipping 3.0 --exchange 0.15

# Just test scraping without analysis
python demo.py --query "electronics" --scrape-only
```

## Understanding Results

### Key Metrics
- **Product Cost**: Original price converted to USD
- **Shipping Cost**: Weight × $2.5/kg (configurable)
- **Total Cost**: Product + Shipping
- **Cost per Unit**: Total ÷ Minimum Order Quantity
- **Shipping %**: What portion is shipping cost

### Best Deals Table
Products are ranked by **cost-effectiveness score** (lower = better):
- Considers unit cost, data quality, and shipping ratio
- Products with actual weight data rank higher
- Lower overall cost per unit ranks higher

### Data Quality Indicators
- ✅ **Complete Data**: Has actual weight/dimensions
- ⚠️ **Estimated Data**: Weight estimated from volume/dimensions
- ❌ **Missing Data**: Key information unavailable

## Configuration

### Shipping Settings
- **Rate**: $2.5/kg default (adjustable)
- **Destination**: Russia (built-in)
- **Calculation**: Uses higher of actual or volumetric weight

### Search Settings
- **Language**: Chinese or English keywords
- **Pages**: 1-5 pages (more = slower but more data)
- **Products**: ~10 products per page

### Cost Settings
- **Exchange Rate**: 0.14 CNY/USD (adjustable)
- **Density**: 300 kg/m³ for weight estimation
- **Volumetric Factor**: 5000 for shipping calculations

## Troubleshooting

### Setup Issues
```bash
# If setup.sh fails, try manual installation
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install streamlit pandas requests beautifulsoup4 selenium plotly
```

### Scraping Issues
- **No products found**: Try different search terms
- **Chrome errors**: Install `chromium-browser` or `google-chrome`
- **Slow performance**: Reduce pages or use specific search terms
- **Connection errors**: Check internet connection and 1688.com accessibility

### Analysis Issues
- **Missing costs**: Products may lack weight/dimension data
- **Incorrect calculations**: Verify exchange rate and shipping settings
- **No best deals**: Products may have incomplete data

## Tips for Best Results

### Search Optimization
- Use specific product names: "蓝牙耳机" vs "电子产品"
- Try brand names: "iPhone case", "Samsung charger"
- Use Chinese terms for better results: "手机配件" (phone accessories)

### Cost Analysis
- Verify current CNY/USD exchange rate
- Consider seasonal shipping rate variations
- Factor in customs duties (not included in calculations)
- Confirm MOQ requirements with suppliers

### Data Interpretation
- Products with actual weight are most reliable
- Consider shipping percentage in decision making
- Cross-reference top deals with supplier reviews
- Factor in quality differences between suppliers

## File Structure

```
📁 1688-cost-analyzer/
├── 📄 app.py              # Main Streamlit web interface
├── 📄 scraper.py          # 1688.com web scraper
├── 📄 analyzer.py         # Cost analysis engine
├── 📄 demo.py             # Command-line demo/testing
├── 📄 setup.sh            # Automatic setup script
├── 📄 requirements.txt    # Python dependencies
├── 📄 README.md          # Full documentation
├── 📄 QUICKSTART.md      # This quick start guide
└── 📁 venv/              # Virtual environment (after setup)
```

## Next Steps

1. **Run Tests**: Start with `python demo.py --sample`
2. **Try Scraping**: Test with `python demo.py --query "electronics" --pages 1`
3. **Use Web Interface**: Run `streamlit run app.py` for full features
4. **Customize**: Adjust shipping rates and search terms for your needs
5. **Export Results**: Save analysis data for further processing

## Support

If you encounter issues:
1. Check the full [README.md](README.md) for detailed documentation
2. Verify all dependencies are installed correctly
3. Test with sample data first before scraping
4. Ensure internet connection for scraping functionality

---

**Happy cost analyzing! 📊💰**