"""
Statistical Analysis Module
Performs comprehensive statistical analysis on tourism data
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

class StatisticalAnalyzer:
    def __init__(self):
        self.analysis_results = {}
        
    def calculate_all_metrics(self, hotels_df: pd.DataFrame, places_df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive metrics for both datasets"""
        metrics = {
            'hotels': {},
            'places': {},
            'combined': {}
        }
        
        # Hotel metrics
        if 'Price_Per_Night' in hotels_df.columns:
            metrics['hotels']['price_stats'] = {
                'mean': hotels_df['Price_Per_Night'].mean(),
                'median': hotels_df['Price_Per_Night'].median(),
                'std': hotels_df['Price_Per_Night'].std(),
                'min': hotels_df['Price_Per_Night'].min(),
                'max': hotels_df['Price_Per_Night'].max(),
                'q25': hotels_df['Price_Per_Night'].quantile(0.25),
                'q75': hotels_df['Price_Per_Night'].quantile(0.75)
            }
        
        if 'Rating' in hotels_df.columns:
            metrics['hotels']['rating_stats'] = {
                'mean': hotels_df['Rating'].mean(),
                'median': hotels_df['Rating'].median(),
                'std': hotels_df['Rating'].std(),
                'min': hotels_df['Rating'].min(),
                'max': hotels_df['Rating'].max()
            }
        
        # Place metrics
        if 'Cost_Per_Day' in places_df.columns:
            metrics['places']['cost_stats'] = {
                'mean': places_df['Cost_Per_Day'].mean(),
                'median': places_df['Cost_Per_Day'].median(),
                'std': places_df['Cost_Per_Day'].std(),
                'min': places_df['Cost_Per_Day'].min(),
                'max': places_df['Cost_Per_Day'].max()
            }
        
        if 'Visitors_Per_Year' in places_df.columns:
            metrics['places']['visitor_stats'] = {
                'total': places_df['Visitors_Per_Year'].sum(),
                'mean': places_df['Visitors_Per_Year'].mean(),
                'median': places_df['Visitors_Per_Year'].median(),
                'std': places_df['Visitors_Per_Year'].std()
            }
        
        if 'Rating' in places_df.columns:
            metrics['places']['rating_stats'] = {
                'mean': places_df['Rating'].mean(),
                'median': places_df['Rating'].median(),
                'std': places_df['Rating'].std()
            }
        
        # Combined metrics
        metrics['combined']['total_destinations'] = len(places_df)
        metrics['combined']['total_hotels'] = len(hotels_df)
        metrics['combined']['states_covered'] = places_df['State'].nunique() if 'State' in places_df.columns else 0
        
        return metrics
    
    def get_key_findings(self, hotels_df: pd.DataFrame, places_df: pd.DataFrame) -> Dict[str, Any]:
        """Extract key findings from the data"""
        findings = {}
        
        # Basic statistics
        findings['total_destinations'] = len(places_df)
        findings['total_hotels'] = len(hotels_df)
        
        if 'State' in places_df.columns:
            findings['states_covered'] = places_df['State'].nunique()
            findings['top_states'] = places_df['State'].value_counts().head(5).to_dict()
        
        if 'Rating' in places_df.columns:
            findings['avg_rating'] = round(places_df['Rating'].mean(), 2)
            findings['highest_rated'] = places_df.nlargest(1, 'Rating')[['Place', 'Rating']].iloc[0].to_dict()
            findings['lowest_rated'] = places_df.nsmallest(1, 'Rating')[['Place', 'Rating']].iloc[0].to_dict()
        
        if 'Price_Per_Night' in hotels_df.columns:
            findings['avg_hotel_price'] = round(hotels_df['Price_Per_Night'].mean(), 2)
            findings['cheapest_hotel'] = hotels_df.nsmallest(1, 'Price_Per_Night')[['Place', 'Price_Per_Night']].iloc[0].to_dict()
            findings['expensive_hotel'] = hotels_df.nlargest(1, 'Price_Per_Night')[['Place', 'Price_Per_Night']].iloc[0].to_dict()
        
        if 'Budget_Type' in places_df.columns:
            budget_dist = places_df['Budget_Type'].value_counts().to_dict()
            findings['budget_distribution'] = budget_dist
            findings['budget_options'] = budget_dist.get('Budget', 0) + budget_dist.get('Low', 0)
            findings['luxury_options'] = budget_dist.get('Luxury', 0) + budget_dist.get('High', 0)
        
        if 'Visitors_Per_Year' in places_df.columns:
            findings['most_visited'] = places_df.nlargest(1, 'Visitors_Per_Year')[['Place', 'Visitors_Per_Year']].iloc[0].to_dict()
            findings['annual_visitors'] = int(places_df['Visitors_Per_Year'].sum())
        
        if 'Type' in places_df.columns:
            findings['place_type_distribution'] = places_df['Type'].value_counts().to_dict()
            findings['most_common_type'] = places_df['Type'].mode().iloc[0] if not places_df['Type'].empty else 'N/A'
        
        return findings
    
    def get_statistical_summaries(self, hotels_df: pd.DataFrame, places_df: pd.DataFrame) -> Dict[str, Any]:
        """Generate detailed statistical summaries"""
        summaries = {}
        
        # Hotel summaries
        hotel_summary = {}
        numeric_hotel_cols = hotels_df.select_dtypes(include=[np.number]).columns
        for col in numeric_hotel_cols:
            hotel_summary[col] = {
                'mean': hotels_df[col].mean(),
                'median': hotels_df[col].median(),
                'std': hotels_df[col].std(),
                'skew': hotels_df[col].skew(),
                'kurtosis': hotels_df[col].kurtosis()
            }
        summaries['hotel_summary'] = hotel_summary
        
        # Place summaries
        place_summary = {}
        numeric_place_cols = places_df.select_dtypes(include=[np.number]).columns
        for col in numeric_place_cols:
            place_summary[col] = {
                'mean': places_df[col].mean(),
                'median': places_df[col].median(),
                'std': places_df[col].std(),
                'skew': places_df[col].skew(),
                'kurtosis': places_df[col].kurtosis()
            }
        summaries['place_summary'] = place_summary
        
        # Correlation analysis
        if len(numeric_hotel_cols) > 1:
            summaries['hotel_correlations'] = hotels_df[numeric_hotel_cols].corr().to_dict()
        
        if len(numeric_place_cols) > 1:
            summaries['place_correlations'] = places_df[numeric_place_cols].corr().to_dict()
        
        return summaries
    
    def generate_insights(self, hotels_df: pd.DataFrame, places_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate actionable insights from the data"""
        insights = []
        insight_id = 1
        
        # Overview insights
        insights.append({
            'id': insight_id,
            'title': 'Comprehensive Tourism Analysis',
            'description': f"Analysis of {len(places_df)} destinations and {len(hotels_df)} hotels across India",
            'importance': 'High',
            'category': 'Overview'
        })
        insight_id += 1
        
        # Rating insights
        if 'Rating' in places_df.columns:
            avg_rating = places_df['Rating'].mean()
            top_rated = places_df.nlargest(3, 'Rating')['Place'].tolist()
            insights.append({
                'id': insight_id,
                'title': 'Quality Assessment',
                'description': f"Average rating across destinations: {avg_rating:.1f}/5. Top rated: {', '.join(top_rated)}",
                'importance': 'High',
                'category': 'Quality'
            })
            insight_id += 1
        
        # Budget insights
        if 'Budget_Type' in places_df.columns:
            budget_count = len(places_df[places_df['Budget_Type'].isin(['Budget', 'Low'])])
            luxury_count = len(places_df[places_df['Budget_Type'].isin(['Luxury', 'High'])])
            insights.append({
                'id': insight_id,
                'title': 'Budget Friendly Options',
                'description': f"{budget_count} budget-friendly destinations available. {luxury_count} luxury options for premium travelers.",
                'importance': 'Medium',
                'category': 'Budget'
            })
            insight_id += 1
        
        # Geographic insights
        if 'State' in places_df.columns:
            top_state = places_df['State'].value_counts().index[0]
            insights.append({
                'id': insight_id,
                'title': 'Geographic Distribution',
                'description': f"Destinations spread across {places_df['State'].nunique()} states. {top_state} has the most destinations.",
                'importance': 'Medium',
                'category': 'Geographic'
            })
            insight_id += 1
        
        # Seasonal insights
        if 'Season' in places_df.columns:
            top_season = places_df['Season'].value_counts().index[0]
            insights.append({
                'id': insight_id,
                'title': 'Seasonal Patterns',
                'description': f"{top_season} is the most popular season for tourism.",
                'importance': 'Low',
                'category': 'Seasonal'
            })
            insight_id += 1
        
        # Price insights
        if 'Price_Per_Night' in hotels_df.columns:
            avg_price = hotels_df['Price_Per_Night'].mean()
            insights.append({
                'id': insight_id,
                'title': 'Accommodation Costs',
                'description': f"Average hotel price: ₹{avg_price:,.0f} per night. Options available for all budget ranges.",
                'importance': 'High',
                'category': 'Accommodation'
            })
            insight_id += 1
        
        # Visitor insights
        if 'Visitors_Per_Year' in places_df.columns:
            total_visitors = places_df['Visitors_Per_Year'].sum()
            most_visited = places_df.nlargest(1, 'Visitors_Per_Year')['Place'].iloc[0]
            insights.append({
                'id': insight_id,
                'title': 'Visitor Statistics',
                'description': f"Annual visitors: {total_visitors:,.0f}. Most visited: {most_visited}",
                'importance': 'Medium',
                'category': 'Popularity'
            })
            insight_id += 1
        
        return insights
    
    def perform_correlation_analysis(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Perform correlation analysis between specified columns"""
        numeric_df = df[columns].select_dtypes(include=[np.number])
        return numeric_df.corr()
    
    def detect_outliers(self, df: pd.DataFrame, column: str, method: str = 'iqr') -> pd.Series:
        """Detect outliers in a column using specified method"""
        if method == 'iqr':
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            return (df[column] < lower_bound) | (df[column] > upper_bound)
        elif method == 'zscore':
            z_scores = np.abs(stats.zscore(df[column].dropna()))
            return np.where(z_scores > 3)[0]
        return pd.Series([False] * len(df))