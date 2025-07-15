import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import os
from scraper import AlibabaScraper
from analyzer import CostAnalyzer


# Configure Streamlit page
st.set_page_config(
    page_title="1688.com Cost Analyzer for Russia",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stDataFrame {
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600)  # Cache for 1 hour
def scrape_products_cached(query, max_pages):
    """Cached function to scrape products"""
    scraper = AlibabaScraper()
    try:
        products = scraper.search_products(query, max_pages)
        return products
    finally:
        scraper.close()


@st.cache_data
def analyze_products_cached(products_data, shipping_rate, exchange_rate):
    """Cached function to analyze products"""
    if not products_data:
        return pd.DataFrame(), {}
    
    df = pd.DataFrame(products_data)
    analyzer = CostAnalyzer(shipping_rate_per_kg=shipping_rate, cny_to_usd_rate=exchange_rate)
    analyzed_df = analyzer.analyze_products_dataframe(df)
    summary_report = analyzer.generate_summary_report(analyzed_df)
    
    return analyzed_df, summary_report


def create_cost_breakdown_chart(df):
    """Create a cost breakdown chart"""
    if df.empty or 'cost_per_unit_usd' not in df.columns:
        return None
    
    valid_df = df[df['cost_per_unit_usd'].notna() & (df['cost_per_unit_usd'] > 0)].head(10)
    
    if valid_df.empty:
        return None
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Cost Breakdown by Product', 'Shipping vs Product Cost'),
        specs=[[{"type": "bar"}, {"type": "scatter"}]]
    )
    
    # Cost breakdown bar chart
    fig.add_trace(
        go.Bar(
            name='Product Cost',
            x=valid_df['title'].str[:30] + '...',
            y=valid_df['original_price_usd'],
            marker_color='lightblue'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            name='Shipping Cost',
            x=valid_df['title'].str[:30] + '...',
            y=valid_df['shipping_cost_usd'],
            marker_color='orange'
        ),
        row=1, col=1
    )
    
    # Scatter plot of shipping vs product cost
    fig.add_trace(
        go.Scatter(
            x=valid_df['original_price_usd'],
            y=valid_df['shipping_cost_usd'],
            mode='markers',
            marker=dict(
                size=valid_df['cost_per_unit_usd'] * 10,
                color=valid_df['shipping_percentage'],
                colorscale='RdYlBu_r',
                showscale=True,
                colorbar=dict(title="Shipping %")
            ),
            text=valid_df['title'].str[:30] + '...',
            hovertemplate='<b>%{text}</b><br>Product Cost: $%{x:.2f}<br>Shipping Cost: $%{y:.2f}<extra></extra>',
            showlegend=False
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        height=500,
        title_text="Product Cost Analysis",
        barmode='stack'
    )
    
    fig.update_xaxes(title_text="Products", row=1, col=1)
    fig.update_yaxes(title_text="Cost (USD)", row=1, col=1)
    fig.update_xaxes(title_text="Product Cost (USD)", row=1, col=2)
    fig.update_yaxes(title_text="Shipping Cost (USD)", row=1, col=2)
    
    return fig


def create_metrics_dashboard(summary_report):
    """Create metrics dashboard"""
    if not summary_report or 'error' in summary_report:
        st.warning("No valid data for metrics dashboard")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Products Analyzed",
            summary_report.get('total_products_analyzed', 0),
            delta=f"{summary_report.get('products_with_cost_data', 0)} with cost data"
        )
    
    with col2:
        avg_cost = summary_report.get('average_cost_per_unit_usd', 0)
        st.metric(
            "Avg Cost/Unit",
            f"${avg_cost:.2f}" if avg_cost else "N/A",
            delta=f"${summary_report.get('cheapest_unit_cost_usd', 0):.2f} cheapest"
        )
    
    with col3:
        avg_shipping = summary_report.get('average_shipping_cost_usd', 0)
        st.metric(
            "Avg Shipping Cost",
            f"${avg_shipping:.2f}" if avg_shipping else "N/A",
            delta=f"{summary_report.get('average_shipping_percentage', 0):.1f}% of total"
        )
    
    with col4:
        products_with_weight = summary_report.get('products_with_weight_data', 0)
        total_products = summary_report.get('total_products_analyzed', 1)
        weight_percentage = (products_with_weight / total_products * 100) if total_products > 0 else 0
        st.metric(
            "Data Quality",
            f"{weight_percentage:.1f}%",
            delta=f"{products_with_weight} products with weight data"
        )


def main():
    # Header
    st.markdown('<h1 class="main-header">📦 1688.com Cost Analyzer for Russia</h1>', unsafe_allow_html=True)
    st.markdown("**Analyze product costs including shipping to Russia at 2.5$/kg**")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # Search settings
        st.subheader("Search Settings")
        search_query = st.text_input(
            "Search Query (Chinese or English)",
            value="电子产品",
            help="Enter keywords to search for products on 1688.com"
        )
        
        max_pages = st.slider(
            "Maximum Pages to Scrape",
            min_value=1,
            max_value=5,
            value=2,
            help="More pages = more products but longer processing time"
        )
        
        # Cost calculation settings
        st.subheader("Cost Calculation")
        shipping_rate = st.number_input(
            "Shipping Rate (USD/kg) to Russia",
            min_value=0.1,
            max_value=10.0,
            value=2.5,
            step=0.1,
            help="Average shipping cost per kilogram to Russia"
        )
        
        exchange_rate = st.number_input(
            "CNY to USD Exchange Rate",
            min_value=0.10,
            max_value=0.20,
            value=0.14,
            step=0.01,
            help="Current exchange rate from Chinese Yuan to US Dollar"
        )
        
        # Advanced settings
        with st.expander("Advanced Settings"):
            density_assumption = st.number_input(
                "Assumed Density (kg/m³)",
                min_value=100,
                max_value=1000,
                value=300,
                help="Used to estimate weight from volume when weight is not available"
            )
            
            volumetric_factor = st.number_input(
                "Volumetric Factor",
                min_value=3000,
                max_value=7000,
                value=5000,
                help="Factor used to calculate volumetric weight for shipping"
            )
    
    # Main interface
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("🔍 Start Analysis", type="primary", use_container_width=True):
            st.session_state.start_analysis = True
    
    with col1:
        if st.session_state.get('start_analysis', False):
            st.info(f"Searching for '{search_query}' on 1688.com...")
    
    # Analysis execution
    if st.session_state.get('start_analysis', False):
        try:
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Scraping
            status_text.text("🔍 Scraping products from 1688.com...")
            progress_bar.progress(20)
            
            products_data = scrape_products_cached(search_query, max_pages)
            
            if not products_data:
                st.error("No products found. Try a different search query or check your internet connection.")
                st.session_state.start_analysis = False
                return
            
            progress_bar.progress(50)
            status_text.text(f"✅ Found {len(products_data)} products. Analyzing costs...")
            
            # Step 2: Analysis
            analyzed_df, summary_report = analyze_products_cached(
                products_data, shipping_rate, exchange_rate
            )
            
            progress_bar.progress(80)
            status_text.text("📊 Generating visualizations...")
            
            # Step 3: Display results
            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
            
            # Store results in session state
            st.session_state.analyzed_df = analyzed_df
            st.session_state.summary_report = summary_report
            st.session_state.start_analysis = False
            
        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
            st.session_state.start_analysis = False
            return
    
    # Display results if available
    if 'analyzed_df' in st.session_state and 'summary_report' in st.session_state:
        analyzed_df = st.session_state.analyzed_df
        summary_report = st.session_state.summary_report
        
        if not analyzed_df.empty:
            # Metrics dashboard
            st.header("📊 Analysis Summary")
            create_metrics_dashboard(summary_report)
            
            # Charts
            st.header("📈 Cost Analysis Charts")
            cost_chart = create_cost_breakdown_chart(analyzed_df)
            if cost_chart:
                st.plotly_chart(cost_chart, use_container_width=True)
            
            # Best deals
            st.header("🏆 Best Deals")
            analyzer = CostAnalyzer(shipping_rate_per_kg=shipping_rate, cny_to_usd_rate=exchange_rate)
            best_deals = analyzer.get_best_deals(analyzed_df, top_n=10)
            
            if not best_deals.empty:
                # Display best deals with custom formatting
                display_columns = [
                    'title', 'original_price_usd', 'shipping_cost_usd', 
                    'cost_per_unit_usd', 'moq', 'shipping_percentage'
                ]
                
                best_deals_display = best_deals[display_columns].copy()
                best_deals_display.columns = [
                    'Product Title', 'Product Cost (USD)', 'Shipping Cost (USD)',
                    'Cost per Unit (USD)', 'Min Order Qty', 'Shipping %'
                ]
                
                # Format currency columns
                for col in ['Product Cost (USD)', 'Shipping Cost (USD)', 'Cost per Unit (USD)']:
                    best_deals_display[col] = best_deals_display[col].apply(
                        lambda x: f"${x:.2f}" if pd.notna(x) else "N/A"
                    )
                
                best_deals_display['Shipping %'] = best_deals_display['Shipping %'].apply(
                    lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A"
                )
                
                st.dataframe(
                    best_deals_display,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.warning("No products with sufficient cost data found.")
            
            # Detailed data table
            with st.expander("📋 Detailed Analysis Data"):
                # Select columns to display
                available_columns = analyzed_df.columns.tolist()
                default_columns = [
                    'title', 'original_price_cny', 'original_price_usd', 
                    'weight_kg', 'shipping_cost_usd', 'total_cost_usd', 
                    'cost_per_unit_usd', 'moq', 'supplier'
                ]
                
                selected_columns = st.multiselect(
                    "Select columns to display:",
                    available_columns,
                    default=[col for col in default_columns if col in available_columns]
                )
                
                if selected_columns:
                    st.dataframe(
                        analyzed_df[selected_columns],
                        use_container_width=True,
                        hide_index=True
                    )
            
            # Export options
            st.header("💾 Export Data")
            col1, col2 = st.columns(2)
            
            with col1:
                # CSV export
                csv = analyzed_df.to_csv(index=False)
                st.download_button(
                    label="📄 Download CSV",
                    data=csv,
                    file_name=f"1688_analysis_{search_query}_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                # JSON export for summary
                import json
                summary_json = json.dumps(summary_report, indent=2)
                st.download_button(
                    label="📊 Download Summary JSON",
                    data=summary_json,
                    file_name=f"1688_summary_{search_query}_{time.strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
        else:
            st.warning("No data available for analysis. Try different search terms.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **ℹ️ How to use this app:**
    1. Enter your search query in Chinese or English
    2. Adjust shipping rate and exchange rate if needed
    3. Click 'Start Analysis' to scrape and analyze products
    4. Review the cost breakdown and best deals
    5. Export data for further analysis
    
    **Note:** This tool estimates shipping costs based on weight and volume. 
    Actual shipping costs may vary depending on shipping method, packaging, and current rates.
    """)


if __name__ == "__main__":
    main()