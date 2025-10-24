"""
Chart Generator
Creates charts for reports and dashboard
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.utils.logger import get_logger

logger = get_logger()


class ChartGenerator:
    """
    Generate charts for visualization
    
    Features:
    - Candlestick charts with indicators
    - Performance charts
    - Indicator charts
    - Sentiment distribution charts
    """
    
    def __init__(self):
        """Initialize chart generator"""
        self.logger = logger
        
        # Color scheme
        self.colors = {
            'bullish': '#10B981',
            'bearish': '#EF4444',
            'neutral': '#F59E0B',
            'background': '#0F172A',
            'text': '#F8FAFC',
            'grid': '#334155'
        }
    
    def create_candlestick_chart(
        self,
        df: pd.DataFrame,
        symbol: str = "SYMBOL",
        indicators: Optional[Dict[str, pd.Series]] = None,
        title: Optional[str] = None
    ) -> go.Figure:
        """
        Create candlestick chart with optional indicators
        
        Args:
            df: DataFrame with OHLCV data
            symbol: Symbol name
            indicators: Dict of indicator name to Series
            title: Chart title
            
        Returns:
            Plotly figure
        """
        fig = go.Figure()
        
        # Candlestick
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name=symbol,
            increasing_line_color=self.colors['bullish'],
            decreasing_line_color=self.colors['bearish']
        ))
        
        # Add indicators if provided
        if indicators:
            for name, series in indicators.items():
                fig.add_trace(go.Scatter(
                    x=series.index,
                    y=series,
                    name=name,
                    line=dict(width=2)
                ))
        
        # Layout
        fig.update_layout(
            title=title or f"{symbol} Price Chart",
            xaxis_title="Time",
            yaxis_title="Price",
            template="plotly_dark",
            height=500,
            xaxis_rangeslider_visible=False
        )
        
        return fig
    
    def create_indicator_chart(
        self,
        indicators: Dict[str, float],
        title: str = "Technical Indicators"
    ) -> go.Figure:
        """
        Create bar chart of indicator values
        
        Args:
            indicators: Dict of indicator name to value
            title: Chart title
            
        Returns:
            Plotly figure
        """
        names = list(indicators.keys())
        values = list(indicators.values())
        
        # Color bars based on signal
        colors = []
        for name in names:
            if 'bullish' in name.lower():
                colors.append(self.colors['bullish'])
            elif 'bearish' in name.lower():
                colors.append(self.colors['bearish'])
            else:
                colors.append(self.colors['neutral'])
        
        fig = go.Figure(data=[
            go.Bar(
                x=names,
                y=values,
                marker_color=colors,
                text=[f"{v:.2f}" for v in values],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title=title,
            xaxis_title="Indicator",
            yaxis_title="Value",
            template="plotly_dark",
            height=400
        )
        
        return fig
    
    def create_sentiment_distribution(
        self,
        sentiments: List[str],
        title: str = "Sentiment Distribution"
    ) -> go.Figure:
        """
        Create pie chart of sentiment distribution
        
        Args:
            sentiments: List of sentiment strings
            title: Chart title
            
        Returns:
            Plotly figure
        """
        from collections import Counter
        counts = Counter(sentiments)
        
        fig = go.Figure(data=[
            go.Pie(
                labels=list(counts.keys()),
                values=list(counts.values()),
                marker=dict(colors=[
                    self.colors['bullish'] if k == 'BULLISH' 
                    else self.colors['bearish'] if k == 'BEARISH'
                    else self.colors['neutral']
                    for k in counts.keys()
                ])
            )
        ])
        
        fig.update_layout(
            title=title,
            template="plotly_dark",
            height=400
        )
        
        return fig
    
    def create_accuracy_chart(
        self,
        dates: List[datetime],
        accuracies: List[float],
        title: str = "Prediction Accuracy Over Time"
    ) -> go.Figure:
        """
        Create line chart of accuracy over time
        
        Args:
            dates: List of dates
            accuracies: List of accuracy values
            title: Chart title
            
        Returns:
            Plotly figure
        """
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=accuracies,
            mode='lines+markers',
            name='Accuracy',
            line=dict(color=self.colors['bullish'], width=3),
            fill='tozeroy',
            fillcolor='rgba(16, 185, 129, 0.2)'
        ))
        
        # Add target line
        fig.add_hline(
            y=0.70,
            line_dash="dash",
            line_color=self.colors['neutral'],
            annotation_text="Target: 70%"
        )
        
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Accuracy (%)",
            template="plotly_dark",
            height=400,
            yaxis=dict(tickformat='.0%', range=[0, 1])
        )
        
        return fig
    
    def create_multi_timeframe_chart(
        self,
        mtf_results: Dict[str, Dict[str, Any]],
        title: str = "Multi-Timeframe Analysis"
    ) -> go.Figure:
        """
        Create chart showing sentiment across timeframes
        
        Args:
            mtf_results: Multi-timeframe results
            title: Chart title
            
        Returns:
            Plotly figure
        """
        timeframes = list(mtf_results.keys())
        sentiments = [r.get('sentiment', 'NEUTRAL') for r in mtf_results.values()]
        confidences = [r.get('confidence', 0.0) for r in mtf_results.values()]
        
        # Map sentiments to numeric values
        sentiment_map = {'BULLISH': 1, 'NEUTRAL': 0, 'BEARISH': -1}
        sentiment_values = [sentiment_map.get(s, 0) for s in sentiments]
        
        fig = go.Figure()
        
        # Sentiment bars
        colors_list = [
            self.colors['bullish'] if s == 'BULLISH'
            else self.colors['bearish'] if s == 'BEARISH'
            else self.colors['neutral']
            for s in sentiments
        ]
        
        fig.add_trace(go.Bar(
            x=timeframes,
            y=sentiment_values,
            name='Sentiment',
            marker_color=colors_list,
            text=sentiments,
            textposition='auto',
        ))
        
        # Confidence line
        fig.add_trace(go.Scatter(
            x=timeframes,
            y=confidences,
            name='Confidence',
            yaxis='y2',
            line=dict(color=self.colors['neutral'], width=3),
            mode='lines+markers'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Timeframe",
            yaxis_title="Sentiment",
            yaxis2=dict(
                title="Confidence",
                overlaying='y',
                side='right',
                tickformat='.0%'
            ),
            template="plotly_dark",
            height=400,
            yaxis=dict(
                tickvals=[-1, 0, 1],
                ticktext=['BEARISH', 'NEUTRAL', 'BULLISH']
            )
        )
        
        return fig
    
    def create_performance_summary(
        self,
        stats: Dict[str, Any],
        title: str = "Performance Summary"
    ) -> go.Figure:
        """
        Create performance summary chart
        
        Args:
            stats: Performance statistics
            title: Chart title
            
        Returns:
            Plotly figure
        """
        metrics = ['Total', 'Correct', 'Incorrect', 'Accuracy']
        values = [
            stats.get('total', 0),
            stats.get('correct', 0),
            stats.get('incorrect', 0),
            stats.get('accuracy', 0) * 100 if 'accuracy' in stats else 0
        ]
        
        fig = go.Figure(data=[
            go.Bar(
                x=metrics,
                y=values,
                marker_color=[
                    self.colors['neutral'],
                    self.colors['bullish'],
                    self.colors['bearish'],
                    self.colors['bullish']
                ],
                text=[f"{v:.0f}" if i < 3 else f"{v:.1f}%" for i, v in enumerate(values)],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title=title,
            xaxis_title="Metric",
            yaxis_title="Value",
            template="plotly_dark",
            height=400
        )
        
        return fig


if __name__ == "__main__":
    # Test chart generator
    print("📊 Testing Chart Generator...")
    
    chart_gen = ChartGenerator()
    
    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1H')
    data = {
        'Open': np.random.uniform(1.08, 1.09, 100),
        'High': np.random.uniform(1.09, 1.10, 100),
        'Low': np.random.uniform(1.07, 1.08, 100),
        'Close': np.random.uniform(1.08, 1.09, 100),
        'Volume': np.random.randint(1000, 10000, 100),
    }
    df = pd.DataFrame(data, index=dates)
    
    # Test candlestick chart
    fig1 = chart_gen.create_candlestick_chart(df, "EURUSD")
    print("✓ Created candlestick chart")
    
    # Test indicator chart
    indicators = {'RSI': 67.3, 'MACD': 0.0023, 'ADX': 28.5}
    fig2 = chart_gen.create_indicator_chart(indicators)
    print("✓ Created indicator chart")
    
    # Test sentiment distribution
    sentiments = ['BULLISH'] * 60 + ['BEARISH'] * 30 + ['NEUTRAL'] * 10
    fig3 = chart_gen.create_sentiment_distribution(sentiments)
    print("✓ Created sentiment distribution chart")
    
    # Test accuracy chart
    acc_dates = pd.date_range(start='2024-01-01', periods=30, freq='1D')
    accuracies = np.random.uniform(0.65, 0.80, 30)
    fig4 = chart_gen.create_accuracy_chart(acc_dates, accuracies)
    print("✓ Created accuracy chart")
    
    print("\n✓ Chart generator test completed")
