from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
import sys
import warnings
warnings.filterwarnings('ignore')

# ============================================
# INITIALIZE FLASK APP
# ============================================
app = Flask(__name__)
app.secret_key = 'tourism_analysis_2024'

# ============================================
# CREATE FOLDERS
# ============================================
os.makedirs('reports', exist_ok=True)
os.makedirs('logs', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)

# ============================================
# LOAD DATA
# ============================================
print("\n" + "="*60)
print("TOURISM INDIA - Data Analysis Project")
print("="*60)
print("\nLoading datasets...")

hotel_file = 'data/hotel.csv'
place_file = 'data/places.csv'

if not os.path.exists(hotel_file):
    print(f"\n ERROR: Hotel data file not found at '{hotel_file}'")
    print("\nPlease ensure your data files are in the 'data' folder")
    sys.exit(1)

if not os.path.exists(place_file):
    print(f"\n ERROR: Places data file not found at '{place_file}'")
    sys.exit(1)

try:
    hotels_df = pd.read_csv(hotel_file)
    print(f" Loaded {len(hotels_df)} hotels")
    print(f" Columns: {list(hotels_df.columns)}")
except Exception as e:
    print(f" ERROR loading hotel CSV: {e}")
    sys.exit(1)

try:
    places_df = pd.read_csv(place_file)
    print(f" Loaded {len(places_df)} places")
    print(f" Columns: {list(places_df.columns)}")
except Exception as e:
    print(f" ERROR loading places CSV: {e}")
    sys.exit(1)

# Ensure required columns exist with proper names
if 'Place' not in places_df.columns:
    # Try to find a column that might contain place names
    for col in places_df.columns:
        if col.lower() in ['place', 'city', 'destination', 'location', 'name']:
            places_df = places_df.rename(columns={col: 'Place'})
            break

if 'State' not in places_df.columns:
    for col in places_df.columns:
        if col.lower() in ['state', 'region', 'province']:
            places_df = places_df.rename(columns={col: 'State'})
            break
    else:
        places_df['State'] = 'India'

if 'Rating' not in places_df.columns:
    for col in places_df.columns:
        if col.lower() in ['rating', 'ratings', 'score']:
            places_df = places_df.rename(columns={col: 'Rating'})
            break
    else:
        places_df['Rating'] = 4.0

if 'Place' not in hotels_df.columns:
    for col in hotels_df.columns:
        if col.lower() in ['place', 'city', 'location', 'hotel']:
            hotels_df = hotels_df.rename(columns={col: 'Place'})
            break

if 'Price_Per_Night' not in hotels_df.columns:
    for col in hotels_df.columns:
        if col.lower() in ['price', 'rate', 'tariff', 'cost']:
            hotels_df = hotels_df.rename(columns={col: 'Price_Per_Night'})
            break
    else:
        hotels_df['Price_Per_Night'] = 3000

# Clean data
places_df['Rating'] = pd.to_numeric(places_df['Rating'], errors='coerce').fillna(4.0)

print("\n" + "="*60)
print(f" Total Places: {len(places_df)}")
print(f" Total Hotels: {len(hotels_df)}")
print("="*60)

# ============================================
# TEMPLATE FILTERS
# ============================================

@app.template_filter('format_number')
def format_number(value):
    try:
        if value >= 10000000:
            return f"{value/10000000:.1f}Cr"
        elif value >= 100000:
            return f"{value/100000:.1f}L"
        elif value >= 1000:
            return f"{value/1000:.1f}K"
        return str(int(value))
    except:
        return str(value)

# ============================================
# ROUTES
# ============================================

@app.route('/')
def index():
    metrics = {
        'total_destinations': len(places_df),
        'total_hotels': len(hotels_df),
        'states_covered': places_df['State'].nunique() if 'State' in places_df.columns else 0,
        'avg_rating': round(places_df['Rating'].mean(), 1),
        'avg_hotel_price': round(hotels_df['Price_Per_Night'].mean(), 0) if 'Price_Per_Night' in hotels_df.columns else 0,
    }
    
    insights = [
        {'id': 1, 'title': 'Data Loaded', 'description': f'Successfully loaded {len(places_df)} destinations', 'importance': 'High', 'category': 'System'},
        {'id': 2, 'title': 'Search Available', 'description': 'Use the search bar to find destinations', 'importance': 'High', 'category': 'Feature'},
    ]
    
    return render_template('index.html', metrics=metrics, insights=insights)

@app.route('/search', methods=['GET', 'POST'])
def search():
    all_results = []
    search_performed = False
    search_query = ""
    
    # Get unique values for filters
    states = sorted(places_df['State'].unique().tolist()) if 'State' in places_df.columns else []
    types = sorted(places_df['Type'].unique().tolist()) if 'Type' in places_df.columns else []
    seasons = sorted(places_df['Season'].unique().tolist()) if 'Season' in places_df.columns else []
    budgets = sorted(places_df['Budget_Type'].unique().tolist()) if 'Budget_Type' in places_df.columns else []
    
    popular_places = places_df['Place'].head(10).tolist() if not places_df.empty else []
    
    if request.method == 'POST':
        search_performed = True
        search_query = request.form.get('city_name', '').strip()
        
        print(f"\n SEARCH: '{search_query}'")
        
        if search_query:
            # Search in places
            matches = places_df[
                places_df['Place'].str.lower().str.contains(search_query.lower(), na=False) |
                places_df['State'].str.lower().str.contains(search_query.lower(), na=False)
            ]
            
            print(f" Found {len(matches)} matches")
            
            for _, place in matches.iterrows():
                # Get hotel info for this place
                hotel_match = hotels_df[hotels_df['Place'].str.lower() == place['Place'].lower()]
                
                result = {
                    'name': place.get('Place', 'Unknown'),
                    'state': place.get('State', 'Unknown'),
                    'category': place.get('Type', 'Tourist Place'),
                    'rating': float(place.get('Rating', 0)),
                    'cost_per_day': float(place.get('Cost_Per_Day', 0)) if 'Cost_Per_Day' in place else 2000,
                    'best_season': place.get('Season', 'Any'),
                    'budget_type': place.get('Budget_Type', 'Medium'),
                    'visitors': int(place.get('Visitors_Per_Year', 0)) if 'Visitors_Per_Year' in place else 100000,
                    'hotels_count': len(hotel_match),
                    'avg_hotel_price': round(hotel_match['Price_Per_Night'].mean(), 0) if len(hotel_match) > 0 else 0,
                    'avg_hotel_rating': round(hotel_match['Rating'].mean(), 1) if len(hotel_match) > 0 else 0,
                    'description': f"{place.get('Place', 'This destination')} is a wonderful place to visit in {place.get('State', 'India')}. Best time to visit: {place.get('Season', 'any season')}."
                }
                all_results.append(result)
    
    all_places = places_df.to_dict('records') if not search_performed else []
    
    return render_template('search.html',
                         states=states,
                         types=types,
                         seasons=seasons,
                         budgets=budgets,
                         all_results=all_results,
                         all_places=all_places,
                         popular_cities=popular_places,
                         search_performed=search_performed,
                         search_query=search_query,
                         results_count=len(all_results))
@app.route('/dashboard')
def dashboard():
    charts = {}
    
    print("\n" + "="*60)
    print("DASHBOARD - Creating Charts")
    print("="*60)
    
    # 1. Rating Distribution Chart
    if 'Rating' in places_df.columns:
        ratings = places_df['Rating'].dropna().tolist()
        if ratings:
            print(f" Creating Rating chart with {len(ratings)} values")
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=ratings, nbinsx=20, marker_color='#667eea', opacity=0.7))
            fig.update_layout(
                title='Rating Distribution',
                xaxis_title='Rating (out of 5)',
                yaxis_title='Number of Places',
                height=400,
                template='plotly_white'
            )
            charts['rating_chart'] = fig.to_json()
    
    # 2. Price Distribution Chart
    if 'Price_Per_Night' in hotels_df.columns:
        prices = hotels_df['Price_Per_Night'].dropna().tolist()
        if prices:
            print(f" Creating Price chart with {len(prices)} values")
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=prices, nbinsx=25, marker_color='#4facfe', opacity=0.7))
            fig.update_layout(
                title='Hotel Price Distribution',
                xaxis_title='Price per Night (₹)',
                yaxis_title='Number of Hotels',
                height=400,
                template='plotly_white'
            )
            # Add mean line
            mean_price = np.mean(prices)
            fig.add_vline(x=mean_price, line_dash="dash", line_color="red", 
                         annotation_text=f"Mean: ₹{mean_price:.0f}")
            charts['price_chart'] = fig.to_json()
    
    # 3. Place Types Chart
    if 'Type' in places_df.columns:
        types = places_df['Type'].value_counts().head(10)
        if not types.empty:
            print(f" Creating Type chart with {len(types)} categories")
            fig = go.Figure()
            fig.add_trace(go.Bar(x=types.values, y=types.index, orientation='h', marker_color='#764ba2'))
            fig.update_layout(
                title='Top Place Types',
                xaxis_title='Count',
                yaxis_title='Type',
                height=400,
                template='plotly_white'
            )
            charts['type_chart'] = fig.to_json()
    
    # 4. Seasonal Chart
    if 'Season' in places_df.columns:
        seasons = places_df['Season'].value_counts()
        if not seasons.empty:
            print(f" Creating Season chart with {len(seasons)} categories")
            fig = go.Figure()
            fig.add_trace(go.Pie(labels=seasons.index, values=seasons.values, hole=0.3))
            fig.update_layout(title='Seasonal Distribution', height=400, template='plotly_white')
            charts['season_chart'] = fig.to_json()
    
    # 5. Geographic Chart
    if 'State' in places_df.columns:
        states = places_df['State'].value_counts().head(15)
        if not states.empty:
            print(f" Creating Geographic chart with {len(states)} states")
            fig = go.Figure()
            fig.add_trace(go.Bar(x=states.values, y=states.index, orientation='h', marker_color='#11998e'))
            fig.update_layout(
                title='Destinations by State',
                xaxis_title='Number of Destinations',
                yaxis_title='State',
                height=450,
                template='plotly_white'
            )
            charts['geo_chart'] = fig.to_json()
    
    print(f" Total charts created: {len(charts)}")
    print("="*60)
    
    metrics = {
        'total_destinations': len(places_df),
        'total_hotels': len(hotels_df),
        'avg_rating': round(places_df['Rating'].mean(), 1) if 'Rating' in places_df.columns else 0,
        'avg_hotel_price': round(hotels_df['Price_Per_Night'].mean(), 0) if 'Price_Per_Night' in hotels_df.columns else 0,
        'states_count': places_df['State'].nunique() if 'State' in places_df.columns else 0,
    }
    
    top_rated = places_df.nlargest(10, 'Rating').to_dict('records') if 'Rating' in places_df.columns else []
    
    insights = [
        {'id': 1, 'title': 'Total Destinations', 'description': f'Analysis of {len(places_df)} destinations', 'importance': 'High', 'category': 'Overview'},
        {'id': 2, 'title': 'Hotel Network', 'description': f'{len(hotels_df)} hotels available', 'importance': 'High', 'category': 'Accommodation'},
    ]
    
    return render_template('dashboard.html', metrics=metrics, charts=charts, top_rated=top_rated, insights=insights)

@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    result = None
    calculation_done = False
    
    if request.method == 'POST':
        calculation_done = True
        place_name = request.form.get('place', '')
        num_people = int(request.form.get('num_people', 2))
        num_days = int(request.form.get('num_days', 3))
        
        place_data = places_df[places_df['Place'].str.lower() == place_name.lower()]
        
        if not place_data.empty:
            place = place_data.iloc[0]
            daily_cost = place.get('Cost_Per_Day', 2000) if 'Cost_Per_Day' in place else 2000
            hotel_cost = 3000 * max(1, num_people//2) * num_days
            total_cost = hotel_cost + (daily_cost * num_people * num_days) + (500 * num_people * num_days)
            
            result = {
                'place': place_name,
                'state': place.get('State', 'India'),
                'total_cost': total_cost,
                'cost_per_person': total_cost / num_people,
                'cost_per_day': total_cost / num_days,
                'breakdown': {
                    'hotel': {'amount': hotel_cost, 'percentage': round(hotel_cost/total_cost*100, 1)},
                    'activities': {'amount': daily_cost * num_people * num_days, 'percentage': round(daily_cost * num_people * num_days / total_cost * 100, 1)},
                    'food': {'amount': 500 * num_people * num_days, 'percentage': round(500 * num_people * num_days / total_cost * 100, 1)},
                }
            }
    
    places_list = places_df['Place'].tolist() if 'Place' in places_df.columns else []
    
    return render_template('calculator.html', places=places_list, result=result, calculation_done=calculation_done)

@app.route('/report')
def report():
    # Calculate all stats properly
    stats = {
        'total_destinations': len(places_df),
        'total_hotels': len(hotels_df),
        'states_covered': places_df['State'].nunique() if 'State' in places_df.columns else 0,
        'avg_rating': round(places_df['Rating'].mean(), 1) if 'Rating' in places_df.columns else 0,
        'avg_cost': round(places_df['Cost_Per_Day'].mean(), 0) if 'Cost_Per_Day' in places_df.columns else 0,
        'avg_hotel_price': round(hotels_df['Price_Per_Night'].mean(), 0) if 'Price_Per_Night' in hotels_df.columns else 0,
        'total_visitors': int(places_df['Visitors_Per_Year'].sum()) if 'Visitors_Per_Year' in places_df.columns else 0,
        'total_reviews': int(hotels_df['Reviews_Count'].sum()) if 'Reviews_Count' in hotels_df.columns else 0,
    }
    
    # Get places data with all needed fields
    places_list = []
    for _, place in places_df.iterrows():
        place_dict = {
            'Place': place.get('Place', 'Unknown'),
            'State': place.get('State', 'Unknown'),
            'Type': place.get('Type', 'Tourist Place'),
            'Rating': place.get('Rating', 0),
            'Cost_Per_Day': place.get('Cost_Per_Day', 0),
            'Season': place.get('Season', 'Any'),
            'Budget_Type': place.get('Budget_Type', 'Medium'),
        }
        places_list.append(place_dict)
    
    return render_template('report.html', stats=stats, places=places_list[:50])
# ============================================
# RUN APP
# ============================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print(" SERVER STARTED!")
    print("="*60)
    print("\n COPY this link into your browser:")
    print("    http://localhost:5000")
    print("\n" + "="*60)
    print(" Press CTRL+C to stop")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)