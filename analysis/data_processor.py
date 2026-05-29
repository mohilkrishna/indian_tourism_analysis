"""
Data Processing Module
Handles data cleaning, transformation, and preparation
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any
import warnings
warnings.filterwarnings('ignore')

class DataProcessor:
    def __init__(self):
        self.cleaning_stats = {}
        
    def clean_hotel_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess hotel dataset"""
        df = df.copy()
        cleaning_log = {}
        
        # Handle missing values
        initial_rows = len(df)
        
        # Numeric columns to clean
        numeric_cols = ['Price_Per_Night', 'Rating', 'Reviews_Count', 
                       'Distance_From_Center (km)', 'Amenities_Score']
        
        for col in numeric_cols:
            if col in df.columns:
                # Convert to numeric
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # Fill missing with median
                missing_count = df[col].isna().sum()
                if missing_count > 0:
                    median_val = df[col].median() if df[col].dtype in ['float64', 'int64'] else 0
                    df[col].fillna(median_val, inplace=True)
                    cleaning_log[f'{col}_missing_filled'] = missing_count
        
        # Handle missing text fields
        text_cols = ['Hotel_Type', 'Amenities', 'Place', 'State']
        for col in text_cols:
            if col in df.columns:
                missing_count = df[col].isna().sum()
                if missing_count > 0:
                    df[col].fillna('Not Specified', inplace=True)
                    cleaning_log[f'{col}_missing_filled'] = missing_count
        
        # Remove duplicate rows
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            df = df.drop_duplicates()
            cleaning_log['duplicates_removed'] = duplicates
        
        # Create derived columns
        if 'Price_Per_Night' in df.columns and 'Rating' in df.columns:
            df['Value_Score'] = df['Rating'] / (df['Price_Per_Night'] / 1000)
            df['Value_Category'] = pd.qcut(df['Value_Score'], q=4, 
                                           labels=['Low Value', 'Medium Value', 'Good Value', 'Excellent Value'])
        
        # Add price category
        if 'Price_Per_Night' in df.columns:
            df['Price_Category'] = pd.cut(df['Price_Per_Night'], 
                                         bins=[0, 1000, 3000, 5000, 10000, float('inf')],
                                         labels=['Budget', 'Economy', 'Mid-Range', 'Premium', 'Luxury'])
        
        self.cleaning_stats['hotel'] = cleaning_log
        print(f"✓ Hotels: Cleaned {initial_rows} → {len(df)} rows")
        
        return df
    
    def clean_place_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess places dataset"""
        df = df.copy()
        cleaning_log = {}
        
        # Numeric columns to clean
        numeric_cols = ['Cost_Per_Day', 'Rating', 'Duration_Days', 
                       'Visitors_Per_Year', 'Best_Month_Start', 'Best_Month_End']
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
                missing_count = df[col].isna().sum()
                if missing_count > 0:
                    median_val = df[col].median() if df[col].dtype in ['float64', 'int64'] else 0
                    df[col].fillna(median_val, inplace=True)
                    cleaning_log[f'{col}_missing_filled'] = missing_count
        
        # Handle text columns
        text_cols = ['Place', 'State', 'Type', 'Season', 'Budget_Type', 'Best_Time_To_Visit']
        for col in text_cols:
            if col in df.columns:
                missing_count = df[col].isna().sum()
                if missing_count > 0:
                    df[col].fillna('Unknown', inplace=True)
                    cleaning_log[f'{col}_missing_filled'] = missing_count
        
        # Remove duplicates
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            df = df.drop_duplicates()
            cleaning_log['duplicates_removed'] = duplicates
        
        # Create derived columns
        if 'Cost_Per_Day' in df.columns and 'Rating' in df.columns:
            df['Value_For_Money'] = df['Rating'] / (df['Cost_Per_Day'] / 500)
        
        # Add popularity category
        if 'Visitors_Per_Year' in df.columns:
            df['Popularity'] = pd.qcut(df['Visitors_Per_Year'], q=4, 
                                      labels=['Low Traffic', 'Moderate', 'Popular', 'Very Popular'])
        
        self.cleaning_stats['places'] = cleaning_log
        print(f"✓ Places: Cleaned {initial_rows if 'initial_rows' in dir() else len(df)} → {len(df)} rows")
        
        return df
    
    def merge_data(self, hotels_df: pd.DataFrame, places_df: pd.DataFrame) -> pd.DataFrame:
        """Merge hotel and place data for comprehensive analysis"""
        merged_df = pd.merge(places_df, hotels_df, on='Place', how='left', suffixes=('_place', '_hotel'))
        
        # Create combined metrics
        if 'Cost_Per_Day' in merged_df.columns and 'Price_Per_Night' in merged_df.columns:
            merged_df['Total_Daily_Cost'] = merged_df['Cost_Per_Day'] + merged_df['Price_Per_Night']
            
        return merged_df
    
    def get_data_summary(self, hotels_df: pd.DataFrame, places_df: pd.DataFrame) -> Dict[str, Any]:
        """Get summary statistics of the datasets"""
        summary = {
            'hotels': {
                'total_rows': len(hotels_df),
                'total_columns': len(hotels_df.columns),
                'missing_values': hotels_df.isna().sum().sum(),
                'memory_usage': hotels_df.memory_usage(deep=True).sum() / 1024 / 1024,  # MB
                'numeric_columns': hotels_df.select_dtypes(include=[np.number]).columns.tolist(),
                'categorical_columns': hotels_df.select_dtypes(include=['object']).columns.tolist()
            },
            'places': {
                'total_rows': len(places_df),
                'total_columns': len(places_df.columns),
                'missing_values': places_df.isna().sum().sum(),
                'memory_usage': places_df.memory_usage(deep=True).sum() / 1024 / 1024,
                'numeric_columns': places_df.select_dtypes(include=[np.number]).columns.tolist(),
                'categorical_columns': places_df.select_dtypes(include=['object']).columns.tolist()
            }
        }
        
        return summary
    
    def create_feature_engineering(self, df: pd.DataFrame, dataset_type: str) -> pd.DataFrame:
        """Create additional features for analysis"""
        df = df.copy()
        
        if dataset_type == 'hotels':
            if 'Reviews_Count' in df.columns and 'Rating' in df.columns:
                df['Review_Score_Weighted'] = df['Rating'] * np.log1p(df['Reviews_Count'])
            
            if 'Distance_From_Center (km)' in df.columns:
                df['Location_Score'] = 10 / (1 + df['Distance_From_Center (km)'])
                
        elif dataset_type == 'places':
            if 'Duration_Days' in df.columns and 'Cost_Per_Day' in df.columns:
                df['Total_Experience_Cost'] = df['Duration_Days'] * df['Cost_Per_Day']
        
        return df