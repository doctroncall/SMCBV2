"""
Data Validator
Validates and cleans MT5 market data for quality assurance
"""
import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any, Optional
from datetime import datetime, timedelta

from config.settings import DataConfig


class DataValidator:
    """
    Validates and cleans market data
    
    Features:
    - Missing data detection
    - Outlier/spike detection
    - Data consistency checks
    - Automatic data cleaning
    - Gap detection and handling
    """
    
    def __init__(self):
        """Initialize validator with configuration"""
        self.max_missing_pct = DataConfig.MAX_MISSING_PERCENTAGE
        self.max_spike_multiplier = DataConfig.MAX_SPIKE_MULTIPLIER
        
        self.stats = {
            "validations": 0,
            "issues_found": 0,
            "cleanings": 0,
        }
    
    def validate_ohlcv(
        self,
        df: pd.DataFrame,
        symbol: str = "",
        timeframe: str = ""
    ) -> Tuple[bool, List[str]]:
        """
        Validate OHLCV data
        
        Args:
            df: DataFrame with OHLCV data
            symbol: Symbol name for context
            timeframe: Timeframe for context
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_issues)
        """
        self.stats["validations"] += 1
        issues = []
        
        # Check if DataFrame is empty
        if df is None or len(df) == 0:
            issues.append("DataFrame is empty")
            return False, issues
        
        # Check required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            issues.append(f"Missing columns: {missing_cols}")
            return False, issues
        
        # Check for missing values
        missing_check = self._check_missing_values(df)
        if missing_check:
            issues.extend(missing_check)
        
        # Check OHLC consistency
        consistency_check = self._check_ohlc_consistency(df)
        if consistency_check:
            issues.extend(consistency_check)
        
        # Check for spikes/outliers
        spike_check = self._check_spikes(df)
        if spike_check:
            issues.extend(spike_check)
        
        # Check for gaps in time series
        gap_check = self._check_time_gaps(df, timeframe)
        if gap_check:
            issues.extend(gap_check)
        
        # Check for negative or zero values
        value_check = self._check_value_ranges(df)
        if value_check:
            issues.extend(value_check)
        
        # Check volume
        volume_check = self._check_volume(df)
        if volume_check:
            issues.extend(volume_check)
        
        if issues:
            self.stats["issues_found"] += len(issues)
        
        is_valid = len(issues) == 0
        return is_valid, issues
    
    def _check_missing_values(self, df: pd.DataFrame) -> List[str]:
        """Check for missing values"""
        issues = []
        
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            missing_count = df[col].isna().sum()
            if missing_count > 0:
                missing_pct = (missing_count / len(df)) * 100
                issues.append(
                    f"{col}: {missing_count} missing values ({missing_pct:.2f}%)"
                )
                
                if missing_pct > self.max_missing_pct:
                    issues.append(
                        f"{col}: Missing values exceed threshold ({missing_pct:.2f}% > {self.max_missing_pct}%)"
                    )
        
        return issues
    
    def _check_ohlc_consistency(self, df: pd.DataFrame) -> List[str]:
        """Check OHLC logical consistency"""
        issues = []
        
        # High should be >= Low
        invalid_high_low = df[df['High'] < df['Low']]
        if len(invalid_high_low) > 0:
            issues.append(f"High < Low in {len(invalid_high_low)} bars")
        
        # High should be >= Open and Close
        invalid_high_open = df[df['High'] < df['Open']]
        invalid_high_close = df[df['High'] < df['Close']]
        if len(invalid_high_open) > 0:
            issues.append(f"High < Open in {len(invalid_high_open)} bars")
        if len(invalid_high_close) > 0:
            issues.append(f"High < Close in {len(invalid_high_close)} bars")
        
        # Low should be <= Open and Close
        invalid_low_open = df[df['Low'] > df['Open']]
        invalid_low_close = df[df['Low'] > df['Close']]
        if len(invalid_low_open) > 0:
            issues.append(f"Low > Open in {len(invalid_low_open)} bars")
        if len(invalid_low_close) > 0:
            issues.append(f"Low > Close in {len(invalid_low_close)} bars")
        
        return issues
    
    def _check_spikes(self, df: pd.DataFrame) -> List[str]:
        """Check for abnormal price spikes"""
        issues = []
        
        # Calculate price changes
        df_temp = df.copy()
        df_temp['price_change'] = df_temp['Close'].pct_change().abs()
        
        # Calculate mean and std of changes (excluding first row)
        mean_change = df_temp['price_change'].iloc[1:].mean()
        std_change = df_temp['price_change'].iloc[1:].std()
        
        # Detect spikes (changes > mean + threshold * std)
        threshold = self.max_spike_multiplier
        spike_threshold = mean_change + (threshold * std_change)
        
        spikes = df_temp[df_temp['price_change'] > spike_threshold]
        if len(spikes) > 0:
            issues.append(
                f"Detected {len(spikes)} potential spikes/outliers "
                f"(threshold: {spike_threshold*100:.2f}%)"
            )
        
        return issues
    
    def _check_time_gaps(self, df: pd.DataFrame, timeframe: str) -> List[str]:
        """Check for gaps in time series"""
        issues = []
        
        if len(df) < 2:
            return issues
        
        # Expected time difference based on timeframe
        timeframe_minutes = DataConfig.TIMEFRAME_MAP.get(timeframe, 60)
        expected_delta = timedelta(minutes=timeframe_minutes)
        
        # Check gaps
        time_diffs = pd.Series(df.index).diff()
        
        # Allow some tolerance (weekends, holidays)
        max_allowed_delta = expected_delta * 3
        
        gaps = time_diffs[time_diffs > max_allowed_delta]
        if len(gaps) > 0:
            issues.append(f"Detected {len(gaps)} time gaps in data")
        
        return issues
    
    def _check_value_ranges(self, df: pd.DataFrame) -> List[str]:
        """Check for invalid value ranges"""
        issues = []
        
        # Check for negative or zero prices
        for col in ['Open', 'High', 'Low', 'Close']:
            invalid = df[df[col] <= 0]
            if len(invalid) > 0:
                issues.append(f"{col}: {len(invalid)} non-positive values")
        
        return issues
    
    def _check_volume(self, df: pd.DataFrame) -> List[str]:
        """Check volume data"""
        issues = []
        
        # Check for negative volume
        negative_vol = df[df['Volume'] < 0]
        if len(negative_vol) > 0:
            issues.append(f"Volume: {len(negative_vol)} negative values")
        
        # Check for zero volume (suspicious but not always invalid)
        zero_vol = df[df['Volume'] == 0]
        if len(zero_vol) > 0:
            zero_pct = (len(zero_vol) / len(df)) * 100
            if zero_pct > 5:  # More than 5% zero volume is suspicious
                issues.append(
                    f"Volume: {len(zero_vol)} zero values ({zero_pct:.2f}%)"
                )
        
        return issues
    
    def clean_ohlcv(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean OHLCV data by fixing common issues
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            pd.DataFrame: Cleaned data
        """
        self.stats["cleanings"] += 1
        df_clean = df.copy()
        
        # Remove duplicate timestamps
        df_clean = df_clean[~df_clean.index.duplicated(keep='first')]
        
        # Fill missing values with forward fill, then backward fill
        df_clean[['Open', 'High', 'Low', 'Close']] = df_clean[
            ['Open', 'High', 'Low', 'Close']
        ].fillna(method='ffill').fillna(method='bfill')
        
        # Fill missing volume with 0
        df_clean['Volume'] = df_clean['Volume'].fillna(0)
        
        # Fix OHLC inconsistencies
        df_clean['High'] = df_clean[['Open', 'High', 'Close']].max(axis=1)
        df_clean['Low'] = df_clean[['Open', 'Low', 'Close']].min(axis=1)
        
        # Remove rows with non-positive prices
        df_clean = df_clean[
            (df_clean['Open'] > 0) &
            (df_clean['High'] > 0) &
            (df_clean['Low'] > 0) &
            (df_clean['Close'] > 0)
        ]
        
        # Cap volume at 0 (no negative volume)
        df_clean['Volume'] = df_clean['Volume'].clip(lower=0)
        
        return df_clean
    
    def detect_gaps(
        self,
        df: pd.DataFrame,
        timeframe: str
    ) -> List[Tuple[datetime, datetime, int]]:
        """
        Detect gaps in time series
        
        Args:
            df: DataFrame with OHLCV data
            timeframe: Timeframe string
            
        Returns:
            List[Tuple]: List of (start_time, end_time, bars_missing)
        """
        if len(df) < 2:
            return []
        
        timeframe_minutes = DataConfig.TIMEFRAME_MAP.get(timeframe, 60)
        expected_delta = timedelta(minutes=timeframe_minutes)
        
        gaps = []
        times = pd.Series(df.index)
        
        for i in range(1, len(times)):
            actual_delta = times.iloc[i] - times.iloc[i-1]
            
            # If gap is more than 2x expected (accounting for weekends)
            if actual_delta > expected_delta * 2:
                bars_missing = int(actual_delta / expected_delta) - 1
                gaps.append((times.iloc[i-1], times.iloc[i], bars_missing))
        
        return gaps
    
    def interpolate_gaps(
        self,
        df: pd.DataFrame,
        method: str = "linear"
    ) -> pd.DataFrame:
        """
        Interpolate missing data in gaps
        
        Args:
            df: DataFrame with gaps
            method: Interpolation method (linear, time, etc.)
            
        Returns:
            pd.DataFrame: Data with interpolated gaps
        """
        df_filled = df.copy()
        
        # Interpolate price data
        for col in ['Open', 'High', 'Low', 'Close']:
            df_filled[col] = df_filled[col].interpolate(method=method)
        
        # For volume, use forward fill or 0
        df_filled['Volume'] = df_filled['Volume'].fillna(method='ffill').fillna(0)
        
        return df_filled
    
    def get_data_quality_score(self, df: pd.DataFrame, timeframe: str = "") -> float:
        """
        Calculate overall data quality score (0-100)
        
        Args:
            df: DataFrame to score
            timeframe: Timeframe for context
            
        Returns:
            float: Quality score (0-100)
        """
        if df is None or len(df) == 0:
            return 0.0
        
        score = 100.0
        is_valid, issues = self.validate_ohlcv(df, timeframe=timeframe)
        
        # Deduct points for each type of issue
        for issue in issues:
            if "missing values" in issue.lower():
                score -= 10
            elif "high < low" in issue.lower():
                score -= 15
            elif "spike" in issue.lower():
                score -= 5
            elif "gap" in issue.lower():
                score -= 3
            elif "negative" in issue.lower():
                score -= 10
        
        return max(0.0, min(100.0, score))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get validator statistics"""
        return self.stats.copy()
    
    def __repr__(self) -> str:
        return f"<DataValidator validations={self.stats['validations']} issues={self.stats['issues_found']}>"


if __name__ == "__main__":
    # Test validator
    print("🔍 Testing Data Validator...")
    
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
    
    validator = DataValidator()
    
    # Test validation
    is_valid, issues = validator.validate_ohlcv(df, "EURUSD", "H1")
    print(f"✓ Validation: {'Valid' if is_valid else 'Invalid'}")
    if issues:
        print(f"  Issues found: {issues}")
    
    # Test quality score
    score = validator.get_data_quality_score(df, "H1")
    print(f"✓ Quality Score: {score:.2f}/100")
    
    # Introduce some issues
    df_bad = df.copy()
    df_bad.iloc[10, df_bad.columns.get_loc('High')] = df_bad.iloc[10]['Low'] - 0.01  # Invalid High
    df_bad.iloc[20, df_bad.columns.get_loc('Volume')] = -100  # Negative volume
    df_bad.iloc[30:35] = np.nan  # Missing values
    
    is_valid, issues = validator.validate_ohlcv(df_bad, "EURUSD", "H1")
    print(f"\n✓ Bad Data Validation: {'Valid' if is_valid else 'Invalid'}")
    print(f"  Issues: {issues}")
    
    # Test cleaning
    df_cleaned = validator.clean_ohlcv(df_bad)
    is_valid, issues = validator.validate_ohlcv(df_cleaned, "EURUSD", "H1")
    print(f"\n✓ After Cleaning: {'Valid' if is_valid else 'Invalid'}")
    print(f"  Remaining issues: {issues}")
    
    # Statistics
    stats = validator.get_statistics()
    print(f"\n✓ Statistics: {stats}")
    
    print("\n✓ Validator test completed")
