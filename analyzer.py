import pandas as pd
import numpy as np
import re
from typing import Dict, List, Optional, Tuple


class CostAnalyzer:
    def __init__(self, shipping_rate_per_kg: float = 2.5, cny_to_usd_rate: float = 0.14):
        """
        Initialize the cost analyzer
        
        Args:
            shipping_rate_per_kg: Shipping cost in USD per kg to Russia
            cny_to_usd_rate: CNY to USD exchange rate
        """
        self.shipping_rate_per_kg = shipping_rate_per_kg
        self.cny_to_usd_rate = cny_to_usd_rate
        
    def estimate_weight_from_volume(self, volume_m3: float, density_kg_m3: float = 300) -> float:
        """
        Estimate weight from volume assuming average density
        
        Args:
            volume_m3: Volume in cubic meters
            density_kg_m3: Assumed density in kg/m³ (default 300 for electronics/general goods)
        """
        if volume_m3 and volume_m3 > 0:
            return volume_m3 * density_kg_m3
        return None
    
    def estimate_weight_from_dimensions(self, length_cm: float, width_cm: float, 
                                      height_cm: float, density_kg_m3: float = 300) -> float:
        """
        Estimate weight from dimensions
        
        Args:
            length_cm, width_cm, height_cm: Dimensions in centimeters
            density_kg_m3: Assumed density in kg/m³
        """
        if all([length_cm, width_cm, height_cm]):
            volume_m3 = (length_cm * width_cm * height_cm) / 1_000_000  # Convert cm³ to m³
            return self.estimate_weight_from_volume(volume_m3, density_kg_m3)
        return None
    
    def extract_dimensions_from_text(self, text: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """
        Extract dimensions (L x W x H) from product description text
        
        Returns:
            Tuple of (length, width, height) in cm
        """
        if not text:
            return None, None, None
            
        text = str(text).lower()
        
        # Common dimension patterns
        dimension_patterns = [
            r'(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)\s*(?:cm|厘米)',
            r'长\s*(\d+(?:\.\d+)?)\s*[x×]\s*宽\s*(\d+(?:\.\d+)?)\s*[x×]\s*高\s*(\d+(?:\.\d+)?)',
            r'尺寸[：:]\s*(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)',
            r'size[：:]\s*(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)',
        ]
        
        for pattern in dimension_patterns:
            match = re.search(pattern, text)
            if match:
                return float(match.group(1)), float(match.group(2)), float(match.group(3))
        
        return None, None, None
    
    def calculate_volumetric_weight(self, volume_m3: float, volumetric_factor: float = 5000) -> float:
        """
        Calculate volumetric weight for shipping
        
        Args:
            volume_m3: Volume in cubic meters
            volumetric_factor: Volumetric factor (default 5000 for international shipping)
        """
        if volume_m3 and volume_m3 > 0:
            # Convert m³ to cm³ and apply volumetric factor
            volume_cm3 = volume_m3 * 1_000_000
            return volume_cm3 / volumetric_factor
        return None
    
    def get_shipping_weight(self, actual_weight: Optional[float], 
                           volumetric_weight: Optional[float]) -> Optional[float]:
        """
        Get the chargeable weight (higher of actual or volumetric weight)
        """
        weights = [w for w in [actual_weight, volumetric_weight] if w is not None]
        if weights:
            return max(weights)
        return None
    
    def calculate_total_cost_per_unit(self, product_data: Dict) -> Dict:
        """
        Calculate total cost per unit including shipping to Russia
        
        Args:
            product_data: Dictionary containing product information
            
        Returns:
            Dictionary with cost breakdown
        """
        result = {
            'original_price_cny': product_data.get('price'),
            'original_price_usd': None,
            'weight_kg': product_data.get('weight'),
            'volume_m3': product_data.get('volume'),
            'estimated_weight_kg': None,
            'volumetric_weight_kg': None,
            'shipping_weight_kg': None,
            'shipping_cost_usd': None,
            'total_cost_usd': None,
            'moq': product_data.get('moq', 1),
            'cost_per_unit_usd': None,
            'cost_breakdown': {}
        }
        
        # Convert price to USD
        if result['original_price_cny']:
            result['original_price_usd'] = result['original_price_cny'] * self.cny_to_usd_rate
        
        # Try to get or estimate weight
        weight_kg = result['weight_kg']
        
        # If no weight but we have volume, estimate it
        if not weight_kg and result['volume_m3']:
            result['estimated_weight_kg'] = self.estimate_weight_from_volume(result['volume_m3'])
            weight_kg = result['estimated_weight_kg']
        
        # Try to extract dimensions from product specs and estimate weight
        if not weight_kg and product_data.get('raw_specs'):
            length, width, height = self.extract_dimensions_from_text(product_data['raw_specs'])
            if all([length, width, height]):
                result['estimated_weight_kg'] = self.estimate_weight_from_dimensions(length, width, height)
                weight_kg = result['estimated_weight_kg']
        
        # Calculate volumetric weight if we have volume
        if result['volume_m3']:
            result['volumetric_weight_kg'] = self.calculate_volumetric_weight(result['volume_m3'])
        
        # Get shipping weight (higher of actual/estimated and volumetric)
        result['shipping_weight_kg'] = self.get_shipping_weight(
            weight_kg, result['volumetric_weight_kg']
        )
        
        # Calculate shipping cost
        if result['shipping_weight_kg']:
            result['shipping_cost_usd'] = result['shipping_weight_kg'] * self.shipping_rate_per_kg
        
        # Calculate total cost
        if result['original_price_usd'] and result['shipping_cost_usd']:
            result['total_cost_usd'] = result['original_price_usd'] + result['shipping_cost_usd']
            
            # Calculate cost per unit considering MOQ
            moq = max(result['moq'], 1)
            result['cost_per_unit_usd'] = result['total_cost_usd'] / moq
        
        # Create cost breakdown
        result['cost_breakdown'] = {
            'product_cost_usd': result['original_price_usd'],
            'shipping_cost_usd': result['shipping_cost_usd'],
            'total_cost_usd': result['total_cost_usd'],
            'units_in_order': result['moq'],
            'cost_per_unit_usd': result['cost_per_unit_usd']
        }
        
        return result
    
    def analyze_products_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze a DataFrame of products and add cost calculations
        
        Args:
            df: DataFrame with product data
            
        Returns:
            Enhanced DataFrame with cost analysis
        """
        if df.empty:
            return df
            
        # Apply cost analysis to each row
        cost_analyses = []
        for _, row in df.iterrows():
            cost_analysis = self.calculate_total_cost_per_unit(row.to_dict())
            cost_analyses.append(cost_analysis)
        
        # Create new DataFrame with cost analysis
        cost_df = pd.DataFrame(cost_analyses)
        
        # Combine with original data
        result_df = pd.concat([df.reset_index(drop=True), cost_df], axis=1)
        
        # Add some useful calculated columns
        result_df['cost_effectiveness_score'] = self.calculate_cost_effectiveness_score(result_df)
        result_df['shipping_percentage'] = (result_df['shipping_cost_usd'] / result_df['total_cost_usd'] * 100).round(2)
        
        return result_df
    
    def calculate_cost_effectiveness_score(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate a cost effectiveness score (lower is better)
        Based on cost per unit and availability of data
        """
        scores = pd.Series(index=df.index, dtype=float)
        
        for idx, row in df.iterrows():
            score = 100  # Base score
            
            # Lower score for lower cost per unit
            if pd.notna(row['cost_per_unit_usd']) and row['cost_per_unit_usd'] > 0:
                score = row['cost_per_unit_usd']
            
            # Penalty for missing weight data (add 20% to score)
            if pd.isna(row['weight_kg']) and pd.isna(row['estimated_weight_kg']):
                score *= 1.2
            
            # Penalty for high shipping percentage (if > 50% of total cost)
            if pd.notna(row.get('shipping_percentage')) and row['shipping_percentage'] > 50:
                score *= 1.1
            
            scores.iloc[idx] = score
        
        return scores
    
    def get_best_deals(self, df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        """
        Get the best deals based on cost effectiveness score
        
        Args:
            df: Analyzed DataFrame
            top_n: Number of top deals to return
            
        Returns:
            DataFrame with top deals
        """
        if df.empty:
            return df
            
        # Filter out products without cost calculations
        valid_df = df[df['cost_per_unit_usd'].notna() & (df['cost_per_unit_usd'] > 0)]
        
        if valid_df.empty:
            return df.head(0)  # Return empty DataFrame with same structure
        
        # Sort by cost effectiveness score
        best_deals = valid_df.nsmallest(top_n, 'cost_effectiveness_score')
        
        return best_deals
    
    def generate_summary_report(self, df: pd.DataFrame) -> Dict:
        """
        Generate a summary report of the analysis
        
        Args:
            df: Analyzed DataFrame
            
        Returns:
            Dictionary with summary statistics
        """
        if df.empty:
            return {"error": "No data to analyze"}
        
        valid_df = df[df['cost_per_unit_usd'].notna() & (df['cost_per_unit_usd'] > 0)]
        
        if valid_df.empty:
            return {"error": "No products with valid cost data"}
        
        report = {
            'total_products_analyzed': len(df),
            'products_with_cost_data': len(valid_df),
            'average_product_price_usd': valid_df['original_price_usd'].mean(),
            'average_shipping_cost_usd': valid_df['shipping_cost_usd'].mean(),
            'average_total_cost_usd': valid_df['total_cost_usd'].mean(),
            'average_cost_per_unit_usd': valid_df['cost_per_unit_usd'].mean(),
            'cheapest_unit_cost_usd': valid_df['cost_per_unit_usd'].min(),
            'most_expensive_unit_cost_usd': valid_df['cost_per_unit_usd'].max(),
            'average_shipping_percentage': valid_df['shipping_percentage'].mean(),
            'products_with_weight_data': len(df[df['weight_kg'].notna()]),
            'products_with_volume_data': len(df[df['volume_m3'].notna()]),
            'products_with_estimated_weight': len(df[df['estimated_weight_kg'].notna()]),
        }
        
        # Round numeric values
        for key, value in report.items():
            if isinstance(value, float):
                report[key] = round(value, 2)
        
        return report


def demo_analysis():
    """Demo function showing how to use the analyzer"""
    # Sample data
    sample_products = [
        {
            'title': '电子设备 USB充电器',
            'price': 15.50,  # CNY
            'weight': 0.2,   # kg
            'volume': None,
            'moq': 100,
            'raw_specs': '重量: 200g, 尺寸: 10x5x3cm'
        },
        {
            'title': '蓝牙耳机',
            'price': 45.00,  # CNY
            'weight': None,
            'volume': 0.0001,  # m³
            'moq': 50,
            'raw_specs': '包装尺寸: 15x10x8cm, 净重约150g'
        }
    ]
    
    df = pd.DataFrame(sample_products)
    
    analyzer = CostAnalyzer()
    analyzed_df = analyzer.analyze_products_dataframe(df)
    
    print("Analysis Results:")
    print(analyzed_df[['title', 'original_price_usd', 'shipping_cost_usd', 'cost_per_unit_usd']].to_string())
    
    print("\nSummary Report:")
    report = analyzer.generate_summary_report(analyzed_df)
    for key, value in report.items():
        print(f"{key}: {value}")
    
    return analyzed_df


if __name__ == "__main__":
    demo_analysis()