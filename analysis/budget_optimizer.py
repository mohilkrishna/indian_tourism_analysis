"""
Budget Optimization Module
Helps users plan their trips and optimize costs
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

class BudgetOptimizer:
    def __init__(self):
        self.cost_multipliers = {
            'budget': 0.7,
            'mid': 1.0,
            'luxury': 1.8
        }
        
        self.transport_costs = {
            'train': 1000,
            'flight': 3000,
            'bus': 500,
            'car': 2000
        }
        
        self.food_costs = {
            'budget': 300,
            'mid': 500,
            'luxury': 1200
        }
    
    def calculate_budget(self, places_df: pd.DataFrame, hotels_df: pd.DataFrame, 
                        params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate total trip budget based on parameters"""
        
        place_name = params.get('place')
        num_people = int(params.get('num_people', 2))
        num_days = int(params.get('num_days', 3))
        hotel_type = params.get('hotel_type', 'mid')
        transport = params.get('transport', 'train')
        food_preference = params.get('food_preference', 'mid')
        
        # Get place information
        place_info = places_df[places_df['Place'] == place_name]
        if place_info.empty:
            return None
        
        place_info = place_info.iloc[0]
        
        # Get hotel information
        place_hotels = hotels_df[hotels_df['Place'] == place_name]
        
        # Calculate hotel cost
        if not place_hotels.empty:
            base_hotel_price = place_hotels['Price_Per_Night'].mean()
            # Adjust based on hotel type preference
            hotel_multiplier = self.cost_multipliers.get(hotel_type, 1.0)
            hotel_price_per_night = base_hotel_price * hotel_multiplier
        else:
            hotel_price_per_night = 3000  # Default
        
        # Number of rooms needed (assuming 2 people per room)
        num_rooms = max(1, num_people // 2 + num_people % 2)
        hotel_cost = hotel_price_per_night * num_rooms * num_days
        
        # Calculate activity cost
        base_activity_cost = place_info['Cost_Per_Day']
        activity_multiplier = self.cost_multipliers.get(hotel_type, 1.0)
        activity_cost_per_person = base_activity_cost * activity_multiplier
        activity_cost = activity_cost_per_person * num_people * num_days
        
        # Calculate food cost
        food_cost_per_person = self.food_costs.get(food_preference, 500)
        food_cost = food_cost_per_person * num_people * num_days
        
        # Calculate transport cost
        transport_cost_per_person = self.transport_costs.get(transport, 1000)
        transport_cost = transport_cost_per_person * num_people * 2  # Round trip
        
        # Calculate miscellaneous costs (10% of total)
        subtotal = hotel_cost + activity_cost + food_cost + transport_cost
        misc_cost = subtotal * 0.1
        
        # Total cost
        total_cost = subtotal + misc_cost
        
        # Calculate savings opportunities
        savings_opportunities = self._find_savings_opportunities(
            place_info, hotel_price_per_night, num_people, num_days
        )
        
        # Generate tips
        tips = self._generate_budget_tips(
            total_cost, num_people, num_days, hotel_type, food_preference
        )
        
        return {
            'place': place_name,
            'state': place_info.get('State', 'Unknown'),
            'num_people': num_people,
            'num_days': num_days,
            'total_cost': round(total_cost, 2),
            'cost_per_person': round(total_cost / num_people, 2),
            'cost_per_day': round(total_cost / num_days, 2),
            'per_person_per_day': round(total_cost / (num_people * num_days), 2),
            'breakdown': {
                'hotel': {
                    'amount': round(hotel_cost, 2),
                    'percentage': round((hotel_cost / total_cost) * 100, 1),
                    'per_night': round(hotel_price_per_night, 2)
                },
                'activities': {
                    'amount': round(activity_cost, 2),
                    'percentage': round((activity_cost / total_cost) * 100, 1),
                    'per_person': round(activity_cost_per_person, 2)
                },
                'food': {
                    'amount': round(food_cost, 2),
                    'percentage': round((food_cost / total_cost) * 100, 1),
                    'per_person': round(food_cost_per_person, 2)
                },
                'transport': {
                    'amount': round(transport_cost, 2),
                    'percentage': round((transport_cost / total_cost) * 100, 1)
                },
                'misc': {
                    'amount': round(misc_cost, 2),
                    'percentage': round((misc_cost / total_cost) * 100, 1)
                }
            },
            'savings_opportunities': savings_opportunities,
            'tips': tips
        }
    
    def _find_savings_opportunities(self, place_info: pd.Series, 
                                   hotel_price: float, num_people: int, 
                                   num_days: int) -> List[Dict]:
        """Identify potential savings opportunities"""
        savings = []
        
        # Group discount opportunity
        if num_people >= 4:
            savings.append({
                'area': 'Accommodation',
                'potential_savings': f"Up to ₹{int(hotel_price * 0.15 * num_days)}",
                'tip': 'Book group rooms or serviced apartments for 4+ people'
            })
        
        # Long stay discount
        if num_days >= 7:
            savings.append({
                'area': 'Extended Stay',
                'potential_savings': '10-20%',
                'tip': 'Many hotels offer weekly rates - ask about long-stay discounts'
            })
        
        # Off-season travel
        if place_info.get('Season', '') in ['Peak', 'High']:
            savings.append({
                'area': 'Seasonal Pricing',
                'potential_savings': '30-50%',
                'tip': 'Consider traveling during shoulder season for better rates'
            })
        
        # Package deals
        savings.append({
            'area': 'Package Deals',
            'potential_savings': '15-25%',
            'tip': 'Look for bundled flight+hotel packages online'
        })
        
        # Local food
        savings.append({
            'area': 'Dining',
            'potential_savings': '₹500-2000 per day',
            'tip': 'Eat at local restaurants instead of hotel restaurants'
        })
        
        return savings
    
    def _generate_budget_tips(self, total_cost: float, num_people: int, 
                              num_days: int, hotel_type: str, 
                              food_preference: str) -> List[str]:
        """Generate budget optimization tips"""
        tips = []
        
        # General tips
        tips.append("✓ Book at least 2-3 weeks in advance for best rates")
        tips.append("✓ Compare prices across multiple booking platforms")
        
        # Specific tips based on context
        if total_cost > 100000:
            tips.append("✓ Consider a shorter duration or alternative destination for better value")
        elif total_cost < 30000:
            tips.append("✓ Great budget-friendly option! Consider extending your stay")
        
        if hotel_type == 'luxury':
            tips.append("✓ Look for luxury hotels with breakfast included to save on meals")
        
        if food_preference == 'luxury':
            tips.append("✓ Try local fine dining for lunch (cheaper than dinner)")
        
        if num_people >= 3:
            tips.append("✓ Cooking in a serviced apartment can save 40% on food costs")
        
        tips.append("✓ Use public transport or rent vehicles for better mobility")
        tips.append("✓ Book attractions online for early bird discounts")
        
        return tips[:6]  # Return top 6 tips
    
    def optimize_budget(self, places_df: pd.DataFrame, hotels_df: pd.DataFrame, 
                       params: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize budget for a given destination"""
        result = self.calculate_budget(places_df, hotels_df, params)
        
        if not result:
            return {'savings_potential': [], 'tips': [], 'optimized_budget': None}
        
        # Create optimized version
        optimized = result.copy()
        
        # Apply optimizations
        optimized['total_cost'] = round(result['total_cost'] * 0.85, 2)  # 15% potential savings
        optimized['cost_per_person'] = round(optimized['total_cost'] / params.get('num_people', 2), 2)
        
        # Update breakdown with optimized values
        for category in optimized['breakdown']:
            optimized['breakdown'][category]['amount'] = round(
                optimized['breakdown'][category]['amount'] * 0.85, 2
            )
        
        return {
            'original_budget': result,
            'optimized_budget': optimized,
            'savings_potential': result.get('savings_opportunities', []),
            'tips': result.get('tips', [])
        }
    
    def find_alternatives(self, places_df: pd.DataFrame, current_place: str, 
                         budget_type: str) -> List[Dict]:
        """Find alternative destinations with similar experience at lower cost"""
        current = places_df[places_df['Place'] == current_place]
        if current.empty:
            return []
        
        current_info = current.iloc[0]
        
        # Find alternatives
        alternatives = []
        for _, place in places_df.iterrows():
            if place['Place'] == current_place:
                continue
            
            similarity_score = 0
            if place['Type'] == current_info['Type']:
                similarity_score += 0.4
            
            if place['Budget_Type'] == budget_type:
                similarity_score += 0.3
            
            # Cost difference
            cost_ratio = place['Cost_Per_Day'] / current_info['Cost_Per_Day']
            if cost_ratio < 1:
                similarity_score += 0.3 * (1 - cost_ratio)
            
            if similarity_score > 0.3:
                alternatives.append({
                    'place': place['Place'],
                    'state': place['State'],
                    'type': place['Type'],
                    'cost_per_day': place['Cost_Per_Day'],
                    'savings_per_day': current_info['Cost_Per_Day'] - place['Cost_Per_Day'],
                    'similarity_score': round(similarity_score * 100, 1),
                    'rating': place['Rating']
                })
        
        alternatives.sort(key=lambda x: x['similarity_score'], reverse=True)
        return alternatives[:5]