#!/usr/bin/env python3
"""
Demo script for testing the 1688.com Cost Analyzer components
Can be run independently of the Streamlit interface for testing
"""

import sys
import argparse
import pandas as pd
from scraper import AlibabaScraper
from analyzer import CostAnalyzer


def test_scraper(query="电子产品", max_pages=1):
    """Test the scraper functionality"""
    print(f"🔍 Testing scraper with query: '{query}'")
    print(f"📄 Max pages: {max_pages}")
    print("-" * 50)
    
    scraper = AlibabaScraper()
    try:
        products = scraper.search_products(query, max_pages)
        
        if not products:
            print("❌ No products found")
            return None
        
        print(f"✅ Found {len(products)} products")
        
        # Display first few products
        for i, product in enumerate(products[:3]):
            print(f"\nProduct {i+1}:")
            print(f"  Title: {product.get('title', 'N/A')[:60]}...")
            print(f"  Price: {product.get('price', 'N/A')} CNY")
            print(f"  Weight: {product.get('weight', 'N/A')} kg")
            print(f"  Volume: {product.get('volume', 'N/A')} m³")
            print(f"  MOQ: {product.get('moq', 'N/A')}")
            print(f"  Supplier: {product.get('supplier', 'N/A')}")
        
        return products
        
    except Exception as e:
        print(f"❌ Error during scraping: {str(e)}")
        return None
    finally:
        scraper.close()


def test_analyzer(products_data, shipping_rate=2.5, exchange_rate=0.14):
    """Test the analyzer functionality"""
    print(f"\n💰 Testing analyzer")
    print(f"📦 Shipping rate: ${shipping_rate}/kg to Russia")
    print(f"💱 Exchange rate: {exchange_rate} CNY/USD")
    print("-" * 50)
    
    if not products_data:
        print("❌ No products data to analyze")
        return None, None
    
    try:
        df = pd.DataFrame(products_data)
        analyzer = CostAnalyzer(
            shipping_rate_per_kg=shipping_rate,
            cny_to_usd_rate=exchange_rate
        )
        
        # Analyze products
        analyzed_df = analyzer.analyze_products_dataframe(df)
        summary_report = analyzer.generate_summary_report(analyzed_df)
        
        print(f"✅ Analyzed {len(analyzed_df)} products")
        
        # Display summary
        print("\n📊 Summary Report:")
        for key, value in summary_report.items():
            if not key.startswith('error'):
                print(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Display best deals
        best_deals = analyzer.get_best_deals(analyzed_df, top_n=3)
        if not best_deals.empty:
            print("\n🏆 Top 3 Best Deals:")
            for i, (_, deal) in enumerate(best_deals.iterrows()):
                print(f"\n  Deal {i+1}:")
                print(f"    Product: {deal.get('title', 'N/A')[:40]}...")
                print(f"    Product Cost: ${deal.get('original_price_usd', 0):.2f}")
                print(f"    Shipping Cost: ${deal.get('shipping_cost_usd', 0):.2f}")
                print(f"    Total Cost: ${deal.get('total_cost_usd', 0):.2f}")
                print(f"    Cost per Unit: ${deal.get('cost_per_unit_usd', 0):.2f}")
                print(f"    MOQ: {deal.get('moq', 'N/A')}")
                print(f"    Shipping %: {deal.get('shipping_percentage', 0):.1f}%")
        
        return analyzed_df, summary_report
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        return None, None


def test_sample_data():
    """Test analyzer with sample data"""
    print("🧪 Testing with sample data")
    print("-" * 50)
    
    sample_products = [
        {
            'title': 'USB充电器 5V 2A 快充适配器',
            'price': 12.50,  # CNY
            'weight': 0.15,  # kg
            'volume': None,
            'moq': 100,
            'supplier': '深圳电子厂',
            'raw_specs': '重量: 150g, 尺寸: 8x5x3cm, 输出: 5V/2A'
        },
        {
            'title': '蓝牙无线耳机 TWS 立体声',
            'price': 35.80,  # CNY
            'weight': None,
            'volume': 0.0001,  # m³
            'moq': 50,
            'supplier': '广州音响公司',
            'raw_specs': '包装尺寸: 12x8x6cm, 电池容量: 400mAh'
        },
        {
            'title': '手机支架 桌面旋转 铝合金',
            'price': 18.90,  # CNY
            'weight': None,
            'volume': None,
            'moq': 200,
            'supplier': '义乌配件厂',
            'raw_specs': '材质: 铝合金, 尺寸: 15x10x8cm, 重量约200g'
        }
    ]
    
    analyzed_df, summary_report = test_analyzer(sample_products)
    return analyzed_df, summary_report


def save_results(analyzed_df, summary_report, filename_prefix="demo_results"):
    """Save analysis results to files"""
    if analyzed_df is not None and not analyzed_df.empty:
        csv_filename = f"{filename_prefix}.csv"
        analyzed_df.to_csv(csv_filename, index=False)
        print(f"💾 Results saved to {csv_filename}")
        
        if summary_report:
            import json
            json_filename = f"{filename_prefix}_summary.json"
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(summary_report, f, indent=2, ensure_ascii=False)
            print(f"📊 Summary saved to {json_filename}")


def main():
    parser = argparse.ArgumentParser(description='Demo script for 1688.com Cost Analyzer')
    parser.add_argument('--query', '-q', default='电子产品', 
                       help='Search query for 1688.com (default: 电子产品)')
    parser.add_argument('--pages', '-p', type=int, default=1,
                       help='Maximum pages to scrape (default: 1)')
    parser.add_argument('--shipping', '-s', type=float, default=2.5,
                       help='Shipping rate in USD/kg (default: 2.5)')
    parser.add_argument('--exchange', '-e', type=float, default=0.14,
                       help='CNY to USD exchange rate (default: 0.14)')
    parser.add_argument('--sample', action='store_true',
                       help='Test with sample data instead of scraping')
    parser.add_argument('--save', action='store_true',
                       help='Save results to CSV and JSON files')
    parser.add_argument('--scrape-only', action='store_true',
                       help='Only test scraping, skip analysis')
    
    args = parser.parse_args()
    
    print("🚀 1688.com Cost Analyzer Demo")
    print("=" * 50)
    
    if args.sample:
        # Test with sample data
        analyzed_df, summary_report = test_sample_data()
        products_data = None
    else:
        # Test scraping
        products_data = test_scraper(args.query, args.pages)
        
        if args.scrape_only:
            print("\n✅ Scraping test completed")
            return
        
        # Test analysis
        analyzed_df, summary_report = test_analyzer(
            products_data, args.shipping, args.exchange
        )
    
    # Save results if requested
    if args.save and analyzed_df is not None:
        save_results(analyzed_df, summary_report)
    
    print(f"\n✅ Demo completed successfully!")
    
    # Provide next steps
    print("\n🔗 Next steps:")
    print("  1. Run the full Streamlit app: streamlit run app.py")
    print("  2. Try different search queries with --query")
    print("  3. Adjust shipping rates with --shipping")
    print("  4. Save results with --save")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)