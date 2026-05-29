"""
Visualization Engine Module
Creates interactive charts and graphs for data visualization
"""

import pandas as pd
import numpy as np
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from typing import Dict, List, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

class VisualizationEngine:
    def __init__(self):
        self.chart_count = 0
        self.colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', 
                      '#4facfe', '#11998e', '#38ef7d', '#fa709a', 
                      '#fee140', '#30cfd0', '#330867', '#a8edea']
        self.default_height = 450
        self.default_width = None
        
    def _create_figure(self, fig):
        """Helper to convert figure to JSON"""
        self.chart_count += 1
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_hotel_type_chart(self, df: pd.DataFrame) -> str:
        """Create pie chart showing hotel type distribution"""
        if 'Hotel_Type' in df.columns and not df.empty:
            data = df['Hotel_Type'].value_counts()
            
            if not data.empty:
                fig = go.Figure(data=[go.Pie(
                    labels=data.index.tolist(),
                    values=data.values.tolist(),
                    hole=0.4,
                    marker=dict(colors=self.colors[:len(data)]),
                    textinfo='label+percent',
                    textposition='auto'
                )])
                fig.update_layout(
                    title=dict(
                        text='Hotel Type Distribution',
                        font=dict(size=20, color='#2c3e50'),
                        x=0.5
                    ),
                    height=self.default_height,
                    showlegend=True,
                    legend=dict(orientation='v', yanchor='top', y=1, xanchor='left', x=0),
                    template='plotly_white',
                    annotations=[dict(text=f'Total: {len(df)} hotels', x=0.5, y=-0.1, showarrow=False, font=dict(size=12))]
                )
                return self._create_figure(fig)
        
        # Return empty figure with message
        fig = go.Figure()
        fig.update_layout(
            title='No Hotel Type Data Available',
            height=self.default_height,
            annotations=[dict(text='Add hotel data with "Hotel_Type" column', x=0.5, y=0.5, showarrow=False, font=dict(size=14))]
        )
        return self._create_figure(fig)
    
    def create_place_type_chart(self, df: pd.DataFrame) -> str:
        """Create bar chart showing place type distribution"""
        if 'Type' in df.columns and not df.empty:
            data = df['Type'].value_counts().head(10)
            
            if not data.empty:
                fig = go.Figure(data=[go.Bar(
                    x=data.values.tolist(),
                    y=data.index.tolist(),
                    orientation='h',
                    marker_color=self.colors[:len(data)],
                    text=data.values.tolist(),
                    textposition='auto',
                    textfont=dict(size=12)
                )])
                fig.update_layout(
                    title=dict(
                        text='Top 10 Place Types',
                        font=dict(size=20, color='#2c3e50'),
                        x=0.5
                    ),
                    xaxis_title='Number of Destinations',
                    yaxis_title='Place Type',
                    height=self.default_height,
                    template='plotly_white',
                    yaxis=dict(categoryorder='total ascending')
                )
                return self._create_figure(fig)
        
        fig = go.Figure()
        fig.update_layout(
            title='No Place Type Data Available',
            height=self.default_height,
            annotations=[dict(text='Add place data with "Type" column', x=0.5, y=0.5, showarrow=False, font=dict(size=14))]
        )
        return self._create_figure(fig)
    
    def create_price_distribution(self, df: pd.DataFrame) -> str:
        """Create histogram showing price distribution"""
        if 'Price_Per_Night' in df.columns and not df.empty:
            prices = df['Price_Per_Night'].dropna()
            
            if not prices.empty:
                fig = go.Figure(data=[go.Histogram(
                    x=prices,
                    nbinsx=30,
                    marker_color=self.colors[0],
                    opacity=0.7,
                    histnorm='count',
                    name='Hotels'
                )])
                
                # Add mean and median lines
                mean_val = prices.mean()
                median_val = prices.median()
                
                fig.add_vline(x=mean_val, line_dash="dash", line_color="red", 
                             annotation_text=f"Mean: ₹{mean_val:,.0f}", 
                             annotation_position="top")
                fig.add_vline(x=median_val, line_dash="dot", line_color="green", 
                             annotation_text=f"Median: ₹{median_val:,.0f}", 
                             annotation_position="bottom")
                
                fig.update_layout(
                    title=dict(
                        text='Hotel Price Distribution',
                        font=dict(size=20, color='#2c3e50'),
                        x=0.5
                    ),
                    xaxis_title='Price per Night (₹)',
                    yaxis_title='Number of Hotels',
                    height=self.default_height,
                    template='plotly_white',
                    bargap=0.05
                )
                return self._create_figure(fig)
        
        fig = go.Figure()
        fig.update_layout(
            title='No Price Data Available',
            height=self.default_height,
            annotations=[dict(text='Add hotel data with "Price_Per_Night" column', x=0.5, y=0.5, showarrow=False, font=dict(size=14))]
        )
        return self._create_figure(fig)
    
    def create_rating_analysis(self, hotels_df: pd.DataFrame, places_df: pd.DataFrame) -> str:
        """Create subplot comparing hotel and place ratings"""
        fig = make_subplots(rows=1, cols=2, 
                           subplot_titles=('Hotel Ratings Distribution', 'Place Ratings Distribution'),
                           x_title='Rating',
                           y_title='Frequency')
        
        has_data = False
        
        if 'Rating' in hotels_df.columns and not hotels_df.empty:
            hotel_ratings = hotels_df['Rating'].dropna()
            if not hotel_ratings.empty:
                fig.add_trace(go.Histogram(
                    x=hotel_ratings,
                    name='Hotels',
                    marker_color=self.colors[0],
                    opacity=0.7,
                    nbinsx=20,
                    showlegend=False
                ), row=1, col=1)
                has_data = True
        
        if 'Rating' in places_df.columns and not places_df.empty:
            place_ratings = places_df['Rating'].dropna()
            if not place_ratings.empty:
                fig.add_trace(go.Histogram(
                    x=place_ratings,
                    name='Places',
                    marker_color=self.colors[1],
                    opacity=0.7,
                    nbinsx=20,
                    showlegend=False
                ), row=1, col=2)
                has_data = True
        
        if has_data:
            fig.update_layout(
                title=dict(
                    text='Rating Distribution Analysis',
                    font=dict(size=20, color='#2c3e50'),
                    x=0.5
                ),
                height=self.default_height,
                template='plotly_white',
                showlegend=False
            )
            
            # Update x-axes to range 0-5
            fig.update_xaxes(range=[0, 5.5], row=1, col=1)
            fig.update_xaxes(range=[0, 5.5], row=1, col=2)
            
            return self._create_figure(fig)
        
        fig = go.Figure()
        fig.update_layout(
            title='No Rating Data Available',
            height=self.default_height,
            annotations=[dict(text='Add rating data to hotels or places datasets', x=0.5, y=0.5, showarrow=False, font=dict(size=14))]
        )
        return self._create_figure(fig)
    
    def create_seasonal_analysis(self, df: pd.DataFrame) -> str:
        """Create visualization for seasonal patterns"""
        if 'Season' in df.columns and not df.empty:
            data = df['Season'].value_counts()
            
            if not data.empty:
                fig = go.Figure(data=[go.Pie(
                    labels=data.index.tolist(),
                    values=data.values.tolist(),
                    hole=0.3,
                    marker=dict(colors=self.colors[:len(data)]),
                    textinfo='label+percent',
                    textposition='auto'
                )])
                fig.update_layout(
                    title=dict(
                        text='Best Time to Visit Distribution',
                        font=dict(size=20, color='#2c3e50'),
                        x=0.5
                    ),
                    height=self.default_height,
                    template='plotly_white'
                )
                return self._create_figure(fig)
        
        fig = go.Figure()
        fig.update_layout(
            title='No Seasonal Data Available',
            height=self.default_height,
            annotations=[dict(text='Add place data with "Season" column', x=0.5, y=0.5, showarrow=False, font=dict(size=14))]
        )
        return self._create_figure(fig)
    
    def create_budget_analysis(self, df: pd.DataFrame) -> str:
        """Create budget category analysis"""
        if 'Budget_Type' in df.columns and 'Cost_Per_Day' in df.columns and not df.empty:
            budget_avg = df.groupby('Budget_Type')['Cost_Per_Day'].mean().sort_values()
            
            if not budget_avg.empty:
                fig = go.Figure(data=[go.Bar(
                    x=budget_avg.values,
                    y=budget_avg.index,
                    orientation='h',
                    marker_color=self.colors[:len(budget_avg)],
                    text=[f'₹{val:,.0f}' for val in budget_avg.values],
                    textposition='auto',
                    textfont=dict(size=12)
                )])
                fig.update_layout(
                    title=dict(
                        text='Average Daily Cost by Budget Category',
                        font=dict(size=20, color='#2c3e50'),
                        x=0.5
                    ),
                    xaxis_title='Average Cost per Day (₹)',
                    yaxis_title='Budget Category',
                    height=self.default_height,
                    template='plotly_white'
                )
                return self._create_figure(fig)
        
        fig = go.Figure()
        fig.update_layout(
            title='No Budget Data Available',
            height=self.default_height,
            annotations=[dict(text='Add place data with "Budget_Type" and "Cost_Per_Day" columns', x=0.5, y=0.5, showarrow=False, font=dict(size=14))]
        )
        return self._create_figure(fig)
    
    def create_geographic_distribution(self, df: pd.DataFrame) -> str:
        """Create geographic distribution chart"""
        if 'State' in df.columns and not df.empty:
            state_counts = df['State'].value_counts().head(15)
            
            if not state_counts.empty:
                fig = go.Figure(data=[go.Bar(
                    x=state_counts.values,
                    y=state_counts.index,
                    orientation='h',
                    marker_color=self.colors[0],
                    text=state_counts.values,
                    textposition='auto',
                    textfont=dict(size=11)
                )])
                fig.update_layout(
                    title=dict(
                        text='Top 15 States by Number of Destinations',
                        font=dict(size=20, color='#2c3e50'),
                        x=0.5
                    ),
                    xaxis_title='Number of Destinations',
                    yaxis_title='State',
                    height=500,
                    template='plotly_white',
                    yaxis=dict(categoryorder='total ascending')
                )
                return self._create_figure(fig)
        
        fig = go.Figure()
        fig.update_layout(
            title='No Geographic Data Available',
            height=self.default_height,
            annotations=[dict(text='Add place data with "State" column', x=0.5, y=0.5, showarrow=False, font=dict(size=14))]
        )
        return self._create_figure(fig)
    
    def create_value_matrix(self, df: pd.DataFrame) -> str:
        """Create scatter plot for value analysis (price vs rating)"""
        if 'Price_Per_Night' in df.columns and 'Rating' in df.columns and not df.empty:
            # Remove NaN values
            plot_df = df[['Price_Per_Night', 'Rating']].dropna()
            
            if not plot_df.empty:
                # Calculate size based on reviews if available
                if 'Reviews_Count' in df.columns:
                    sizes = df.loc[plot_df.index, 'Reviews_Count'].fillna(100).clip(10, 100)
                else:
                    sizes = [20] * len(plot_df)
                
                fig = go.Figure(data=[go.Scatter(
                    x=plot_df['Price_Per_Night'],
                    y=plot_df['Rating'],
                    mode='markers',
                    marker=dict(
                        size=sizes,
                        color=plot_df['Rating'],
                        colorscale='Viridis',
                        showscale=True,
                        colorbar=dict(title="Rating", x=1.02),
                        sizemode='area',
                        sizeref=2.*max(sizes)/(40.**2),
                        sizemin=4
                    ),
                    text=df.loc[plot_df.index, 'Place'] if 'Place' in df.columns else None,
                    hovertemplate='<b>%{text}</b><br>Price: ₹%{x:,.0f}<br>Rating: %{y:.1f} ★<extra></extra>'
                )])
                
                # Add trend line
                z = np.polyfit(plot_df['Price_Per_Night'], plot_df['Rating'], 1)
                p = np.poly1d(z)
                x_trend = np.linspace(plot_df['Price_Per_Night'].min(), plot_df['Price_Per_Night'].max(), 100)
                fig.add_trace(go.Scatter(
                    x=x_trend,
                    y=p(x_trend),
                    mode='lines',
                    name=f'Trend: Rating = {z[0]:.4f}×Price + {z[1]:.2f}',
                    line=dict(color='red', dash='dash', width=2)
                ))
                
                fig.update_layout(
                    title=dict(
                        text='Price vs Rating Analysis',
                        font=dict(size=20, color='#2c3e50'),
                        x=0.5
                    ),
                    xaxis_title='Price per Night (₹)',
                    yaxis_title='Rating (1-5)',
                    height=self.default_height,
                    template='plotly_white',
                    hovermode='closest'
                )
                
                # Add quadrant annotations
                fig.add_annotation(x=plot_df['Price_Per_Night'].quantile(0.5), y=4.5, 
                                  text="High Value Area", showarrow=False,
                                  font=dict(size=10, color="green"), bgcolor="rgba(0,255,0,0.1)")
                
                return self._create_figure(fig)
        
        fig = go.Figure()
        fig.update_layout(
            title='No Price/Rating Data Available',
            height=self.default_height,
            annotations=[dict(text='Add hotel data with "Price_Per_Night" and "Rating" columns', x=0.5, y=0.5, showarrow=False, font=dict(size=14))]
        )
        return self._create_figure(fig)
    
    def create_correlation_heatmap(self, hotels_df: pd.DataFrame, places_df: pd.DataFrame) -> str:
        """Create correlation heatmap for numeric features"""
        fig = go.Figure()
        fig.update_layout(
            title='Correlation Analysis',
            height=self.default_height,
            annotations=[dict(text='Correlation heatmap would appear here with more data', x=0.5, y=0.5, showarrow=False, font=dict(size=14))]
        )
        return self._create_figure(fig)
    
    def create_amenity_correlation(self, df: pd.DataFrame) -> str:
        """Create amenity correlation analysis"""
        fig = go.Figure()
        fig.update_layout(
            title='Amenity Impact Analysis',
            height=self.default_height,
            annotations=[dict(text='Amenity analysis available with additional data', x=0.5, y=0.5, showarrow=False, font=dict(size=14))]
        )
        return self._create_figure(fig)
    
    def create_cost_breakdown(self, df: pd.DataFrame) -> str:
        """Create cost breakdown visualization"""
        if 'Budget_Type' in df.columns and 'Cost_Per_Day' in df.columns and not df.empty:
            # Create box plot for cost distribution by budget type
            fig = go.Figure()
            
            budget_types = df['Budget_Type'].unique()
            for i, budget_type in enumerate(budget_types):
                costs = df[df['Budget_Type'] == budget_type]['Cost_Per_Day'].dropna()
                if len(costs) > 0:
                    fig.add_trace(go.Box(
                        y=costs,
                        name=budget_type,
                        marker_color=self.colors[i % len(self.colors)],
                        boxmean='sd',
                        boxpoints='outliers'
                    ))
            
            if fig.data:
                fig.update_layout(
                    title='Cost Distribution by Budget Category',
                    yaxis_title='Cost per Day (₹)',
                    xaxis_title='Budget Category',
                    height=self.default_height,
                    template='plotly_white',
                    showlegend=False
                )
                return self._create_figure(fig)
        
        fig = go.Figure()
        fig.update_layout(
            title='No Cost Breakdown Data Available',
            height=self.default_height,
            annotations=[dict(text='Add place data with budget categories', x=0.5, y=0.5, showarrow=False, font=dict(size=14))]
        )
        return self._create_figure(fig)
    
    def get_chart_count(self) -> int:
        """Return total number of charts created"""
        return self.chart_count