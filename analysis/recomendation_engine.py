"""
Recommendation Engine Module
Provides intelligent recommendations for destinations based on user preferences
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from sklearn.preprocessing import MinMaxScaler
import warnings
warnings.filterwarnings('ignore')

class RecommendationEngine:
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.recommendation_weights = {
            'rating': 0.3,
            'value': 0.2,
            'popularity': 0.2,
            'cost': 0.15,
            'season': 0.15
        }
    
    def search_places(self, places_df: pd.DataFrame, hotels_df: pd.DataFrame, 
                     filters: Dict[str, Any]) -> Dict[str, Any]:
        """Search and filter places based on user criteria"""
        results_df = places_df.copy()
        
        # Apply filters
        if filters.get('state') and filters['state'] != '':
            results_df = results_df[results_df['State'] == filters['state']]
        
        if filters.get('type') and filters['type'] != '':
            results_df = results_df[results_df['Type'] == filters['type']]
        
        if filters.get('budget') and filters['budget'] != '':
            results_df = results_df[results_df['Budget_Type'] == filters['budget']]
        
        if filters.get('season') and filters['season'] != '':
            results_df = results_df[results_df['Season'] == filters['season']]
        
        if filters.get('min_rating') and filters['min_rating'] != '':
            results_df = results_df[results_df['Rating'] >= float(filters['min_rating'])]
        
        if filters.get('max_cost') and filters['max_cost'] != '':
            results_df = results_df[results_df['Cost_Per_Day'] <= float(filters['max_cost'])]
        
        # Enhance results with hotel information
        results = []
        for _, place in results_df.iterrows():
            place_dict = place.to_dict()
            
            # Find matching hotels
            matching_hotels = hotels_df[hotels_df['Place'] == place['Place']]
            place_dict['hotels_count'] = len(matching_hotels)
            place_dict['avg_hotel_price'] = round(matching_hotels['Price_Per_Night'].mean(), 2) if len(matching_hotels) > 0 else 0
            place_dict['hotel_rating'] = round(matching_hotels['Rating'].mean(), 1) if len(matching_hotels) > 0 else 0
            
            # Calculate recommendation score
            place_dict['recommendation_score'] = self._calculate_score(place_dict)
            
            results.append(place_dict)
        
        # Sort by recommendation score
        results.sort(key=lambda x: x.get('recommendation_score', 0), reverse=True)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(results[:10])
        
        # Analytics
        analytics = self._generate_search_analytics(results, filters)
        
        return {
            'results': results[:20],
            'recommendations': recommendations,
            'analytics': analytics,
            'total_results': len(results)
        }
    
    def _calculate_score(self, place: Dict[str, Any]) -> float:
        """Calculate recommendation score for a place"""
        score = 0
        
        # Rating score
        if 'Rating' in place:
            rating_score = (place['Rating'] / 5) * self.recommendation_weights['rating']
            score += rating_score
        
        # Value score (rating per cost)
        if 'Rating' in place and 'Cost_Per_Day' in place and place['Cost_Per_Day'] > 0:
            value_score = (place['Rating'] / (place['Cost_Per_Day'] / 500)) * self.recommendation_weights['value']
            score += min(value_score, self.recommendation_weights['value'])
        
        # Popularity score
        if 'Visitors_Per_Year' in place:
            popularity_score = (place['Visitors_Per_Year'] / 1000000) * self.recommendation_weights['popularity']
            score += min(popularity_score, self.recommendation_weights['popularity'])
        
        # Cost score (lower cost = higher score)
        if 'Cost_Per_Day' in place and place['Cost_Per_Day'] > 0:
            cost_score = (5000 / place['Cost_Per_Day']) * self.recommendation_weights['cost']
            score += min(cost_score, self.recommendation_weights['cost'])
        
        return round(score * 100, 2)
    
    def _generate_recommendations(self, top_places: List[Dict]) -> List[Dict]:
        """Generate personalized recommendations"""
        recommendations = []
        
        if not top_places:
            return recommendations
        
        # Top pick
        recommendations.append({
            'type': 'top_pick',
            'title': '🌟 Top Recommendation',
            'place': top_places[0].get('Place', 'Unknown'),
            'reason': 'Highest overall score based on quality, value, and popularity'
        })
        
        # Best value
        best_value = min(top_places[:10], key=lambda x: x.get('Cost_Per_Day', 9999))
        recommendations.append({
            'type': 'best_value',
            'title': '💰 Best Value',
            'place': best_value.get('Place', 'Unknown'),
            'reason': f"Excellent experience at just ₹{best_value.get('Cost_Per_Day', 0)} per day"
        })
        
        # Most popular
        most_popular = max(top_places[:10], key=lambda x: x.get('Visitors_Per_Year', 0))
        recommendations.append({
            'type': 'most_popular',
            'title': '🔥 Most Popular',
            'place': most_popular.get('Place', 'Unknown'),
            'reason': f"Visited by {int(most_popular.get('Visitors_Per_Year', 0)/1000000)}M+ travelers annually"
        })
        
        # Hidden gem (high rating but lower popularity)
        hidden_gems = [p for p in top_places if p.get('Visitors_Per_Year', 0) < 500000]
        if hidden_gems:
            hidden_gem = max(hidden_gems, key=lambda x: x.get('Rating', 0))
            recommendations.append({
                'type': 'hidden_gem',
                'title': '💎 Hidden Gem',
                'place': hidden_gem.get('Place', 'Unknown'),
                'reason': f"Undiscovered paradise with {hidden_gem.get('Rating', 0)}/5 rating"
            })
        
        # Budget friendly
        budget_options = [p for p in top_places if p.get('Budget_Type', '') in ['Budget', 'Low']]
        if budget_options:
            budget_pick = budget_options[0]
            recommendations.append({
                'type': 'budget_friendly',
                'title': '🎯 Budget Friendly',
                'place': budget_pick.get('Place', 'Unknown'),
                'reason': f"Perfect for budget travelers at ₹{budget_pick.get('Cost_Per_Day', 0)}/day"
            })
        
        return recommendations
    
    def _generate_search_analytics(self, results: List[Dict], filters: Dict) -> Dict:
        """Generate analytics based on search results"""
        analytics = {
            'total_destinations': len(results),
            'avg_rating': 0,
            'avg_cost': 0,
            'price_range': {'min': 0, 'max': 0},
            'popular_seasons': [],
            'budget_breakdown': {}
        }
        
        if results:
            ratings = [r.get('Rating', 0) for r in results]
            analytics['avg_rating'] = round(np.mean(ratings), 1)
            
            costs = [r.get('Cost_Per_Day', 0) for r in results]
            analytics['avg_cost'] = round(np.mean(costs), 2)
            analytics['price_range'] = {'min': min(costs), 'max': max(costs)}
            
            # Season distribution
            seasons = [r.get('Season', 'Unknown') for r in results]
            season_counts = pd.Series(seasons).value_counts().to_dict()
            analytics['popular_seasons'] = list(season_counts.keys())[:3]
            
            # Budget breakdown
            budgets = [r.get('Budget_Type', 'Unknown') for r in results]
            analytics['budget_breakdown'] = pd.Series(budgets).value_counts().to_dict()
        
        return analytics
    
    def get_similar_places(self, places_df: pd.DataFrame, place_name: str, 
                          num_recommendations: int = 5) -> List[Dict]:
        """Find similar places based on features"""
        if place_name not in places_df['Place'].values:
            return []
        
        place = places_df[places_df['Place'] == place_name].iloc[0]
        
        # Calculate similarity scores
        similarities = []
        for _, other in places_df.iterrows():
            if other['Place'] == place_name:
                continue
            
            score = 0
            if place['Type'] == other['Type']:
                score += 0.3
            if place['Budget_Type'] == other['Budget_Type']:
                score += 0.2
            if place['Season'] == other['Season']:
                score += 0.2
            
            # Rating similarity
            rating_diff = abs(place['Rating'] - other['Rating'])
            score += (1 - rating_diff/5) * 0.3
            
            similarities.append({
                'place': other['Place'],
                'similarity_score': round(score * 100, 2),
                'type': other['Type'],
                'rating': other['Rating'],
                'cost': other['Cost_Per_Day']
            })
        
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similarities[:num_recommendations]