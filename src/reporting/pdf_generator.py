"""
PDF Report Generator
Creates professional PDF reports with charts and analysis
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os
from typing import Dict, Any, List, Optional
import pandas as pd

from config.settings import REPORTS_DIR
from .charts import ChartGenerator
from src.utils.logger import get_logger

logger = get_logger()


class PDFReportGenerator:
    """
    Generate professional PDF reports
    
    Report types:
    - Daily summary
    - Weekly performance
    - Monthly analytics
    - Custom period
    """
    
    def __init__(self):
        """Initialize PDF generator"""
        self.logger = logger
        self.chart_generator = ChartGenerator()
        
        # Styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
        # Ensure reports directory exists
        REPORTS_DIR.mkdir(exist_ok=True)
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1E40AF'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1E40AF'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # Body text
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8
        ))
    
    def generate_daily_report(
        self,
        symbol: str,
        analysis_results: Dict[str, Any],
        predictions: List[Dict[str, Any]],
        stats: Dict[str, Any]
    ) -> str:
        """
        Generate daily summary report
        
        Args:
            symbol: Trading symbol
            analysis_results: Analysis results
            predictions: List of predictions
            stats: Performance statistics
            
        Returns:
            str: Path to generated PDF
        """
        try:
            # Generate filename
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = f"daily_report_{symbol}_{date_str}.pdf"
            filepath = REPORTS_DIR / filename
            
            # Create document
            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build story
            story = []
            
            # Title
            title = Paragraph(
                f"MT5 Sentiment Analysis<br/>Daily Report",
                self.styles['CustomTitle']
            )
            story.append(title)
            
            # Subtitle
            subtitle = Paragraph(
                f"{symbol} - {date_str}",
                self.styles['Heading3']
            )
            story.append(subtitle)
            story.append(Spacer(1, 0.3*inch))
            
            # Executive Summary
            story.append(Paragraph("EXECUTIVE SUMMARY", self.styles['SectionHeader']))
            
            sentiment = analysis_results.get('sentiment', 'NEUTRAL')
            confidence = analysis_results.get('confidence', 0.0)
            risk = analysis_results.get('risk_level', 'MEDIUM')
            
            summary_data = [
                ['Overall Sentiment:', sentiment],
                ['Confidence:', f"{confidence:.1%}"],
                ['Risk Level:', risk],
                ['Total Predictions:', str(stats.get('total', 0))],
                ['Correct:', str(stats.get('correct', 0))],
                ['Accuracy:', f"{stats.get('accuracy', 0):.1%}"]
            ]
            
            summary_table = Table(summary_data, colWidths=[2*inch, 3*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Key Insights
            story.append(Paragraph("KEY INSIGHTS", self.styles['SectionHeader']))
            
            insights = analysis_results.get('insights', [])
            for i, insight in enumerate(insights[:5], 1):
                story.append(Paragraph(f"{i}. {insight}", self.styles['CustomBody']))
            
            story.append(Spacer(1, 0.3*inch))
            
            # Predictions Table
            if predictions:
                story.append(Paragraph("RECENT PREDICTIONS", self.styles['SectionHeader']))
                
                pred_data = [['Time', 'Sentiment', 'Confidence', 'Result']]
                for pred in predictions[-10:]:  # Last 10 predictions
                    pred_data.append([
                        pred.get('time', 'N/A'),
                        pred.get('sentiment', 'N/A'),
                        f"{pred.get('confidence', 0):.0%}",
                        pred.get('result', 'Pending')
                    ])
                
                pred_table = Table(pred_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
                pred_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                ]))
                
                story.append(pred_table)
            
            story.append(Spacer(1, 0.3*inch))
            
            # Footer
            footer = Paragraph(
                f"Generated by MT5 Sentiment Analysis Bot on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                self.styles['Normal']
            )
            story.append(Spacer(1, 0.5*inch))
            story.append(footer)
            
            # Build PDF
            doc.build(story)
            
            self.logger.info(f"Generated daily report: {filepath}", category="reporting")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error generating daily report: {str(e)}", category="reporting")
            raise
    
    def generate_performance_report(
        self,
        symbol: str,
        period: str,
        stats: Dict[str, Any],
        predictions: List[Dict[str, Any]]
    ) -> str:
        """
        Generate performance report
        
        Args:
            symbol: Trading symbol
            period: Report period (weekly, monthly)
            stats: Performance statistics
            predictions: List of predictions
            
        Returns:
            str: Path to generated PDF
        """
        try:
            # Generate filename
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = f"{period}_report_{symbol}_{date_str}.pdf"
            filepath = REPORTS_DIR / filename
            
            # Create document
            doc = SimpleDocTemplate(str(filepath), pagesize=letter)
            story = []
            
            # Title
            title = Paragraph(
                f"MT5 Sentiment Analysis<br/>{period.capitalize()} Performance Report",
                self.styles['CustomTitle']
            )
            story.append(title)
            story.append(Spacer(1, 0.3*inch))
            
            # Performance Summary
            story.append(Paragraph("PERFORMANCE SUMMARY", self.styles['SectionHeader']))
            
            perf_data = [
                ['Metric', 'Value'],
                ['Total Predictions', str(stats.get('total', 0))],
                ['Correct Predictions', str(stats.get('correct', 0))],
                ['Incorrect Predictions', str(stats.get('incorrect', 0))],
                ['Overall Accuracy', f"{stats.get('accuracy', 0):.1%}"],
                ['Average Confidence', f"{stats.get('avg_confidence', 0):.1%}"],
                ['Best Streak', str(stats.get('best_streak', 0))],
            ]
            
            perf_table = Table(perf_data, colWidths=[3*inch, 2*inch])
            perf_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            
            story.append(perf_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Recommendations
            story.append(Paragraph("RECOMMENDATIONS", self.styles['SectionHeader']))
            
            recommendations = [
                "Continue monitoring current sentiment patterns",
                "Review and adjust indicator weights if accuracy drops below 70%",
                "Increase position sizes during high-confidence signals (>85%)",
                "Use tighter stops during high volatility periods"
            ]
            
            for i, rec in enumerate(recommendations, 1):
                story.append(Paragraph(f"{i}. {rec}", self.styles['CustomBody']))
            
            story.append(Spacer(1, 0.5*inch))
            
            # Footer
            footer = Paragraph(
                f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                self.styles['Normal']
            )
            story.append(footer)
            
            # Build PDF
            doc.build(story)
            
            self.logger.info(f"Generated performance report: {filepath}", category="reporting")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error generating performance report: {str(e)}", category="reporting")
            raise


if __name__ == "__main__":
    # Test PDF generator
    print("📄 Testing PDF Generator...")
    
    pdf_gen = PDFReportGenerator()
    
    # Test data
    analysis_results = {
        'sentiment': 'BULLISH',
        'confidence': 0.82,
        'risk_level': 'MEDIUM',
        'insights': [
            'Market structure confirms bullish bias',
            'Active bullish order block at 1.08450-1.08475',
            'Price in discount zone - favorable for longs',
            'Volume confirms price action',
            'RSI showing strength at 67.3'
        ]
    }
    
    predictions = [
        {'time': '14:00', 'sentiment': 'BULLISH', 'confidence': 0.82, 'result': 'Pending'},
        {'time': '09:15', 'sentiment': 'NEUTRAL', 'confidence': 0.68, 'result': 'Correct'},
        {'time': '04:30', 'sentiment': 'BEARISH', 'confidence': 0.71, 'result': 'Wrong'},
    ]
    
    stats = {
        'total': 18,
        'correct': 14,
        'incorrect': 4,
        'accuracy': 0.78,
        'avg_confidence': 0.74,
        'best_streak': 7
    }
    
    # Generate reports
    try:
        daily_report = pdf_gen.generate_daily_report("EURUSD", analysis_results, predictions, stats)
        print(f"✓ Generated daily report: {daily_report}")
        
        perf_report = pdf_gen.generate_performance_report("EURUSD", "weekly", stats, predictions)
        print(f"✓ Generated performance report: {perf_report}")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
    
    print("\n✓ PDF generator test completed")
