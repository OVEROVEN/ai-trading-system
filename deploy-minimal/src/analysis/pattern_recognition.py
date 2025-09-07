import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
from scipy.signal import find_peaks, argrelextrema
from sklearn.linear_model import LinearRegression

logger = logging.getLogger(__name__)

@dataclass
class PatternResult:
    pattern_type: str
    start_date: datetime
    end_date: datetime
    confidence: float
    key_points: List[Tuple[datetime, float]]
    description: str
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None

@dataclass
class SupportResistanceLevel:
    level: float
    strength: int
    first_touch: datetime
    last_touch: datetime
    touches: List[Tuple[datetime, float]]
    level_type: str  # 'support' or 'resistance'

class PatternRecognition:
    """
    Advanced pattern recognition for stock charts.
    """
    
    def __init__(self, min_pattern_length: int = 10, max_pattern_length: int = 50):
        self.min_pattern_length = min_pattern_length
        self.max_pattern_length = max_pattern_length
    
    def find_support_resistance_levels(
        self, 
        data: pd.DataFrame, 
        window: int = 20,
        min_touches: int = 3,
        tolerance: float = 0.02
    ) -> List[SupportResistanceLevel]:
        """
        Find support and resistance levels using local minima and maxima.
        
        Args:
            data: OHLCV DataFrame
            window: Window size for finding local extrema
            min_touches: Minimum number of touches to confirm level
            tolerance: Price tolerance as percentage (0.02 = 2%)
            
        Returns:
            List of SupportResistanceLevel objects
        """
        levels = []
        
        if len(data) < window * 2:
            return levels
        
        try:
            # Find local minima (potential support)
            low_indices = argrelextrema(data['low'].values, np.less, order=window)[0]
            support_points = [(data.index[i], data['low'].iloc[i]) for i in low_indices]
            
            # Find local maxima (potential resistance)
            high_indices = argrelextrema(data['high'].values, np.greater, order=window)[0]
            resistance_points = [(data.index[i], data['high'].iloc[i]) for i in high_indices]
            
            # Group similar price levels for support
            support_levels = self._group_price_levels(support_points, tolerance, min_touches, 'support')
            levels.extend(support_levels)
            
            # Group similar price levels for resistance
            resistance_levels = self._group_price_levels(resistance_points, tolerance, min_touches, 'resistance')
            levels.extend(resistance_levels)
            
        except Exception as e:
            logger.error(f"Error finding support/resistance levels: {str(e)}")
        
        return levels
    
    def _group_price_levels(
        self, 
        points: List[Tuple], 
        tolerance: float, 
        min_touches: int,
        level_type: str
    ) -> List[SupportResistanceLevel]:
        """Group similar price levels together."""
        if not points:
            return []
        
        levels = []
        used_points = set()
        
        for i, (date1, price1) in enumerate(points):
            if i in used_points:
                continue
            
            # Find all points within tolerance
            similar_points = [(date1, price1)]
            used_points.add(i)
            
            for j, (date2, price2) in enumerate(points[i+1:], i+1):
                if j in used_points:
                    continue
                
                if abs(price2 - price1) / price1 <= tolerance:
                    similar_points.append((date2, price2))
                    used_points.add(j)
            
            # Create level if enough touches
            if len(similar_points) >= min_touches:
                avg_price = np.mean([p[1] for p in similar_points])
                dates = [p[0] for p in similar_points]
                
                levels.append(SupportResistanceLevel(
                    level=avg_price,
                    strength=len(similar_points),
                    first_touch=min(dates),
                    last_touch=max(dates),
                    touches=similar_points,
                    level_type=level_type
                ))
        
        return levels
    
    def detect_breakout(
        self, 
        data: pd.DataFrame, 
        support_resistance_levels: List[SupportResistanceLevel],
        volume_multiplier: float = 1.5
    ) -> List[PatternResult]:
        """
        Detect breakout patterns above resistance or below support.
        
        Args:
            data: OHLCV DataFrame
            support_resistance_levels: List of S/R levels
            volume_multiplier: Volume should be this times average
            
        Returns:
            List of breakout patterns
        """
        breakouts = []
        
        if len(data) < 2:
            return breakouts
        
        try:
            # Calculate volume average
            avg_volume = data['volume'].rolling(20).mean()
            
            for level in support_resistance_levels:
                # Check recent price action around this level
                recent_data = data.tail(10)  # Last 10 periods
                
                for idx, row in recent_data.iterrows():
                    # Resistance breakout (price breaks above with volume)
                    if (level.level_type == 'resistance' and 
                        row['close'] > level.level and
                        row['volume'] > avg_volume.loc[idx] * volume_multiplier):
                        
                        breakouts.append(PatternResult(
                            pattern_type='resistance_breakout',
                            start_date=level.last_touch,
                            end_date=row.name if hasattr(row, 'name') else datetime.now(),
                            confidence=min(0.9, level.strength * 0.1 + 0.3),
                            key_points=[(level.last_touch, level.level), (row.name, row['close'])],
                            description=f"Price broke above resistance at {level.level:.2f}",
                            target_price=level.level * 1.1,  # 10% above breakout
                            stop_loss=level.level * 0.98     # 2% below breakout level
                        ))
                    
                    # Support breakdown (price breaks below with volume)
                    elif (level.level_type == 'support' and 
                          row['close'] < level.level and
                          row['volume'] > avg_volume.loc[idx] * volume_multiplier):
                        
                        breakouts.append(PatternResult(
                            pattern_type='support_breakdown',
                            start_date=level.last_touch,
                            end_date=row.name if hasattr(row, 'name') else datetime.now(),
                            confidence=min(0.9, level.strength * 0.1 + 0.3),
                            key_points=[(level.last_touch, level.level), (row.name, row['close'])],
                            description=f"Price broke below support at {level.level:.2f}",
                            target_price=level.level * 0.9,  # 10% below breakdown
                            stop_loss=level.level * 1.02     # 2% above breakdown level
                        ))
            
        except Exception as e:
            logger.error(f"Error detecting breakouts: {str(e)}")
        
        return breakouts
    
    def detect_head_and_shoulders(self, data: pd.DataFrame) -> List[PatternResult]:
        """
        Detect Head and Shoulders pattern.
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            List of Head and Shoulders patterns
        """
        patterns = []
        
        if len(data) < self.min_pattern_length:
            return patterns
        
        try:
            # Find peaks (potential shoulders and head)
            peaks, _ = find_peaks(data['high'].values, distance=5, prominence=data['high'].std())
            
            if len(peaks) < 3:
                return patterns
            
            # Check each set of 3 consecutive peaks
            for i in range(len(peaks) - 2):
                left_shoulder_idx = peaks[i]
                head_idx = peaks[i + 1]
                right_shoulder_idx = peaks[i + 2]
                
                left_shoulder = data['high'].iloc[left_shoulder_idx]
                head = data['high'].iloc[head_idx]
                right_shoulder = data['high'].iloc[right_shoulder_idx]
                
                # Head should be higher than both shoulders
                # Shoulders should be approximately equal (within 5%)
                if (head > left_shoulder and head > right_shoulder and
                    abs(left_shoulder - right_shoulder) / max(left_shoulder, right_shoulder) < 0.05):
                    
                    # Find the neckline (support level between shoulders)
                    start_idx = left_shoulder_idx
                    end_idx = right_shoulder_idx
                    section = data.iloc[start_idx:end_idx+1]
                    
                    # Neckline is approximate low point between shoulders
                    neckline_idx = section['low'].idxmin()
                    neckline_price = section['low'].min()
                    
                    # Calculate confidence based on pattern quality
                    shoulder_symmetry = 1 - abs(left_shoulder - right_shoulder) / max(left_shoulder, right_shoulder)
                    head_prominence = min((head - left_shoulder) / left_shoulder, 
                                        (head - right_shoulder) / right_shoulder)
                    confidence = min(0.9, (shoulder_symmetry * 0.5 + head_prominence * 0.5))
                    
                    if confidence > 0.4:  # Minimum confidence threshold
                        patterns.append(PatternResult(
                            pattern_type='head_and_shoulders',
                            start_date=data.index[left_shoulder_idx],
                            end_date=data.index[right_shoulder_idx],
                            confidence=confidence,
                            key_points=[
                                (data.index[left_shoulder_idx], left_shoulder),
                                (data.index[head_idx], head),
                                (data.index[right_shoulder_idx], right_shoulder),
                                (neckline_idx, neckline_price)
                            ],
                            description="Head and Shoulders bearish reversal pattern",
                            target_price=neckline_price - (head - neckline_price),  # Pattern target
                            stop_loss=head * 1.02  # Above head
                        ))
            
        except Exception as e:
            logger.error(f"Error detecting head and shoulders: {str(e)}")
        
        return patterns
    
    def detect_double_top_bottom(self, data: pd.DataFrame) -> List[PatternResult]:
        """
        Detect Double Top and Double Bottom patterns.
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            List of double top/bottom patterns
        """
        patterns = []
        
        if len(data) < self.min_pattern_length:
            return patterns
        
        try:
            # Find peaks for double top
            peaks, _ = find_peaks(data['high'].values, distance=10, prominence=data['high'].std())
            
            for i in range(len(peaks) - 1):
                peak1_idx = peaks[i]
                peak2_idx = peaks[i + 1]
                
                peak1 = data['high'].iloc[peak1_idx]
                peak2 = data['high'].iloc[peak2_idx]
                
                # Peaks should be similar (within 3%)
                if abs(peak1 - peak2) / max(peak1, peak2) < 0.03:
                    # Find valley between peaks
                    valley_section = data.iloc[peak1_idx:peak2_idx+1]
                    valley_idx = valley_section['low'].idxmin()
                    valley_price = valley_section['low'].min()
                    
                    confidence = 1 - abs(peak1 - peak2) / max(peak1, peak2)
                    
                    patterns.append(PatternResult(
                        pattern_type='double_top',
                        start_date=data.index[peak1_idx],
                        end_date=data.index[peak2_idx],
                        confidence=confidence,
                        key_points=[
                            (data.index[peak1_idx], peak1),
                            (valley_idx, valley_price),
                            (data.index[peak2_idx], peak2)
                        ],
                        description="Double Top bearish reversal pattern",
                        target_price=valley_price - (peak1 - valley_price),
                        stop_loss=max(peak1, peak2) * 1.02
                    ))
            
            # Find troughs for double bottom
            troughs, _ = find_peaks(-data['low'].values, distance=10, prominence=data['low'].std())
            
            for i in range(len(troughs) - 1):
                trough1_idx = troughs[i]
                trough2_idx = troughs[i + 1]
                
                trough1 = data['low'].iloc[trough1_idx]
                trough2 = data['low'].iloc[trough2_idx]
                
                # Troughs should be similar (within 3%)
                if abs(trough1 - trough2) / max(trough1, trough2) < 0.03:
                    # Find peak between troughs
                    peak_section = data.iloc[trough1_idx:trough2_idx+1]
                    peak_idx = peak_section['high'].idxmax()
                    peak_price = peak_section['high'].max()
                    
                    confidence = 1 - abs(trough1 - trough2) / max(trough1, trough2)
                    
                    patterns.append(PatternResult(
                        pattern_type='double_bottom',
                        start_date=data.index[trough1_idx],
                        end_date=data.index[trough2_idx],
                        confidence=confidence,
                        key_points=[
                            (data.index[trough1_idx], trough1),
                            (peak_idx, peak_price),
                            (data.index[trough2_idx], trough2)
                        ],
                        description="Double Bottom bullish reversal pattern",
                        target_price=peak_price + (peak_price - trough1),
                        stop_loss=min(trough1, trough2) * 0.98
                    ))
            
        except Exception as e:
            logger.error(f"Error detecting double top/bottom: {str(e)}")
        
        return patterns
    
    def detect_triangles(self, data: pd.DataFrame) -> List[PatternResult]:
        """
        Detect triangle patterns (ascending, descending, symmetrical).
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            List of triangle patterns
        """
        patterns = []
        
        if len(data) < self.min_pattern_length:
            return patterns
        
        try:
            # Need at least 4 points to form triangle (2 highs, 2 lows)
            window = min(len(data), self.max_pattern_length)
            
            for start_idx in range(len(data) - window):
                section = data.iloc[start_idx:start_idx + window]
                
                if len(section) < self.min_pattern_length:
                    continue
                
                # Find highs and lows
                highs = section['high'].values
                lows = section['low'].values
                
                # Find trend lines
                high_peaks, _ = find_peaks(highs, distance=3)
                low_peaks, _ = find_peaks(-lows, distance=3)
                
                if len(high_peaks) >= 2 and len(low_peaks) >= 2:
                    # Get the x-coordinates (time indices) and y-coordinates (prices)
                    high_x = high_peaks
                    high_y = highs[high_peaks]
                    low_x = low_peaks
                    low_y = lows[low_peaks]
                    
                    # Fit trend lines
                    if len(high_x) >= 2 and len(low_x) >= 2:
                        high_slope = self._calculate_slope(high_x, high_y)
                        low_slope = self._calculate_slope(low_x, low_y)
                        
                        # Classify triangle type
                        triangle_type = self._classify_triangle(high_slope, low_slope)
                        
                        if triangle_type:
                            # Calculate convergence point
                            convergence_idx = self._find_convergence_point(
                                high_x, high_y, high_slope,
                                low_x, low_y, low_slope
                            )
                            
                            if convergence_idx is not None and convergence_idx > len(section) * 0.7:
                                patterns.append(PatternResult(
                                    pattern_type=triangle_type,
                                    start_date=section.index[0],
                                    end_date=section.index[-1],
                                    confidence=0.6,  # Base confidence for triangles
                                    key_points=[
                                        (section.index[high_x[0]], high_y[0]),
                                        (section.index[high_x[-1]], high_y[-1]),
                                        (section.index[low_x[0]], low_y[0]),
                                        (section.index[low_x[-1]], low_y[-1])
                                    ],
                                    description=f"{triangle_type.replace('_', ' ').title()} pattern",
                                    target_price=None,  # Will be calculated based on breakout direction
                                    stop_loss=None
                                ))
            
        except Exception as e:
            logger.error(f"Error detecting triangles: {str(e)}")
        
        return patterns
    
    def _calculate_slope(self, x_coords: np.ndarray, y_coords: np.ndarray) -> float:
        """Calculate slope of trend line."""
        if len(x_coords) < 2:
            return 0
        
        # Use linear regression for better trend line
        x_coords = x_coords.reshape(-1, 1)
        reg = LinearRegression().fit(x_coords, y_coords)
        return reg.coef_[0]
    
    def _classify_triangle(self, high_slope: float, low_slope: float) -> Optional[str]:
        """Classify triangle type based on slopes."""
        slope_threshold = 0.01  # Threshold for considering slope as flat
        
        # Ascending triangle: resistance flat, support rising
        if abs(high_slope) < slope_threshold and low_slope > slope_threshold:
            return "ascending_triangle"
        
        # Descending triangle: support flat, resistance falling
        elif abs(low_slope) < slope_threshold and high_slope < -slope_threshold:
            return "descending_triangle"
        
        # Symmetrical triangle: resistance falling, support rising
        elif high_slope < -slope_threshold and low_slope > slope_threshold:
            return "symmetrical_triangle"
        
        return None
    
    def _find_convergence_point(self, high_x, high_y, high_slope, low_x, low_y, low_slope):
        """Find where trend lines converge."""
        try:
            # Use first points of each trend line
            h_x1, h_y1 = high_x[0], high_y[0]
            l_x1, l_y1 = low_x[0], low_y[0]
            
            # Calculate intersection point
            if abs(high_slope - low_slope) < 1e-10:  # Lines are parallel
                return None
            
            # Intersection x coordinate
            x_intersect = (l_y1 - h_y1 + high_slope * h_x1 - low_slope * l_x1) / (high_slope - low_slope)
            
            return x_intersect
            
        except Exception:
            return None
    
    def detect_flags_pennants(self, data: pd.DataFrame) -> List[PatternResult]:
        """
        Detect Flag and Pennant continuation patterns.
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            List of flag/pennant patterns
        """
        patterns = []
        
        if len(data) < self.min_pattern_length:
            return patterns
        
        try:
            # Look for strong moves followed by consolidation
            price_changes = data['close'].pct_change()
            volume_sma = data['volume'].rolling(20).mean()
            
            # Find strong moves (>3% in one day with high volume)
            strong_moves = (
                (abs(price_changes) > 0.03) & 
                (data['volume'] > volume_sma * 1.5)
            )
            
            move_indices = data[strong_moves].index
            
            for move_idx in move_indices:
                move_pos = data.index.get_loc(move_idx)
                
                # Look for consolidation in next 5-15 periods
                if move_pos + 15 < len(data):
                    consolidation = data.iloc[move_pos+1:move_pos+16]
                    
                    # Check if price range is contracting
                    ranges = consolidation['high'] - consolidation['low']
                    avg_range = ranges.mean()
                    
                    # Flag: roughly horizontal consolidation
                    if avg_range < data['close'].iloc[move_pos] * 0.02:  # Range < 2% of price
                        patterns.append(PatternResult(
                            pattern_type='flag',
                            start_date=move_idx,
                            end_date=consolidation.index[-1],
                            confidence=0.6,
                            key_points=[
                                (move_idx, data['close'].loc[move_idx]),
                                (consolidation.index[-1], consolidation['close'].iloc[-1])
                            ],
                            description="Flag continuation pattern",
                            target_price=None,  # Depends on breakout direction
                            stop_loss=None
                        ))
            
        except Exception as e:
            logger.error(f"Error detecting flags/pennants: {str(e)}")
        
        return patterns
    
    def analyze_all_patterns(self, data: pd.DataFrame) -> Dict[str, List[PatternResult]]:
        """
        Run all pattern detection algorithms.
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            Dictionary with pattern types as keys and lists of patterns as values
        """
        all_patterns = {}
        
        try:
            # Find support/resistance first
            sr_levels = self.find_support_resistance_levels(data)
            
            # Detect all patterns
            all_patterns['support_resistance'] = sr_levels
            all_patterns['breakouts'] = self.detect_breakout(data, sr_levels)
            all_patterns['head_and_shoulders'] = self.detect_head_and_shoulders(data)
            all_patterns['double_patterns'] = self.detect_double_top_bottom(data)
            all_patterns['triangles'] = self.detect_triangles(data)
            all_patterns['flags_pennants'] = self.detect_flags_pennants(data)
            
        except Exception as e:
            logger.error(f"Error in pattern analysis: {str(e)}")
        
        return all_patterns

# Example usage
if __name__ == "__main__":
    # Create sample data
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    # Generate sample OHLCV data with some patterns
    base_price = 100
    price_trend = np.cumsum(np.random.randn(100) * 0.5)
    
    # Add some pattern-like behavior
    close_prices = base_price + price_trend
    high_prices = close_prices + np.random.rand(100) * 2
    low_prices = close_prices - np.random.rand(100) * 2
    open_prices = close_prices + (np.random.randn(100) * 0.3)
    volumes = np.random.randint(1000000, 5000000, 100)
    
    sample_data = pd.DataFrame({
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volumes
    }, index=dates)
    
    # Run pattern recognition
    recognizer = PatternRecognition()
    patterns = recognizer.analyze_all_patterns(sample_data)
    
    # Display results
    for pattern_type, pattern_list in patterns.items():
        if pattern_list:
            print(f"\n{pattern_type.upper()}:")
            for pattern in pattern_list[:3]:  # Show first 3 of each type
                if hasattr(pattern, 'pattern_type'):
                    print(f"  - {pattern.pattern_type}: {pattern.description} (confidence: {pattern.confidence:.2f})")
                else:
                    print(f"  - {pattern.level_type}: {pattern.level:.2f} (strength: {pattern.strength})")