"""
Temporal Verification Module
Novel Enhancement: Detects date/time mismatches between text and images
Addresses DEETSA limitation: No temporal consistency checking

This module extracts:
1. EXIF metadata from images (actual photo date)
2. Date entities from text (claimed date)
3. Temporal inconsistencies (old photos used for recent claims)
"""

from PIL import Image
from PIL.ExifTags import TAGS
import re
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import io

class TemporalVerifier:
    """
    Temporal Mismatch Detection Module
    
    Base Paper Limitation:
    - DEETSA focuses on semantic content but ignores temporal metadata
    - Cannot detect when old images are reused for recent claims
    
    Our Enhancement:
    - EXIF metadata extraction from images
    - Date entity extraction from text
    - Temporal consistency verification
    - Detects "image recycling" attacks
    """
    
    def __init__(self):
        """Initialize temporal verifier"""
        print("✓ Temporal Verifier initialized")
        
        # Temporal keywords for extraction
        self.temporal_keywords = {
            'today', 'yesterday', 'tomorrow', 'now', 'currently',
            'recent', 'latest', 'breaking', 'just happened', 'ongoing',
            'this morning', 'this evening', 'tonight', 'last night'
        }
        
        # Month names for extraction
        self.months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12,
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
    
    def verify_temporal_consistency(
        self, 
        text: str, 
        image: Image.Image
    ) -> Dict:
        """
        Main temporal verification function
        
        Returns:
        {
            'has_mismatch': bool,
            'confidence': float (0-100),
            'text_date': str or None,
            'image_date': str or None,
            'days_difference': int or None,
            'explanation': str,
            'severity': str ('LOW', 'MEDIUM', 'HIGH')
        }
        """
        try:
            # Extract dates
            text_date = self.extract_text_date(text)
            image_date = self.extract_image_date(image)
            
            # If no dates found, return neutral result
            if not text_date and not image_date:
                return {
                    'has_mismatch': False,
                    'confidence': 0,
                    'text_date': None,
                    'image_date': None,
                    'days_difference': None,
                    'explanation': 'No temporal information available for verification',
                    'severity': 'LOW'
                }
            
            # If only one date found
            if not text_date or not image_date:
                return {
                    'has_mismatch': False,
                    'confidence': 20,
                    'text_date': str(text_date) if text_date else None,
                    'image_date': str(image_date) if image_date else None,
                    'days_difference': None,
                    'explanation': 'Incomplete temporal information - cannot fully verify',
                    'severity': 'LOW'
                }
            
            # Compare dates
            days_diff = abs((text_date - image_date).days)
            
            # Determine mismatch severity
            result = self._evaluate_temporal_difference(
                text_date, 
                image_date, 
                days_diff,
                text
            )
            
            return result
        
        except Exception as e:
            print(f"Temporal verification error: {e}")
            return {
                'has_mismatch': False,
                'confidence': 0,
                'text_date': None,
                'image_date': None,
                'days_difference': None,
                'explanation': f'Temporal verification failed: {str(e)}',
                'severity': 'LOW'
            }
    
    def extract_image_date(self, image: Image.Image) -> Optional[datetime]:
        """
        Extract date from image EXIF metadata
        
        Novel Approach: Uses EXIF DateTimeOriginal tag
        This is when the photo was actually taken
        """
        try:
            # Get EXIF data
            exif_data = image._getexif()
            
            if not exif_data:
                return None
            
            # Look for date/time tags
            date_tags = ['DateTimeOriginal', 'DateTime', 'DateTimeDigitized']
            
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                
                if tag_name in date_tags:
                    # Parse date string (format: "YYYY:MM:DD HH:MM:SS")
                    date_str = str(value)
                    
                    # Try to parse
                    try:
                        # Replace ':' with '-' for first two occurrences (date part)
                        date_str = date_str.replace(':', '-', 2)
                        parsed_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                        return parsed_date
                    except:
                        # Try alternative format
                        try:
                            parsed_date = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                            return parsed_date
                        except:
                            continue
            
            return None
        
        except Exception as e:
            print(f"EXIF extraction error: {e}")
            return None
    
    def extract_text_date(self, text: str) -> Optional[datetime]:
        """
        Extract date from text description
        
        Approach:
        1. Look for explicit dates (DD/MM/YYYY, Month DD YYYY)
        2. Look for relative dates (today, yesterday)
        3. Extract year if mentioned
        """
        try:
            text_lower = text.lower()
            current_date = datetime.now()
            
            # Check for relative dates
            if any(keyword in text_lower for keyword in ['today', 'this morning', 'tonight', 'now']):
                return current_date
            
            if 'yesterday' in text_lower or 'last night' in text_lower:
                return current_date - timedelta(days=1)
            
            if 'tomorrow' in text_lower:
                return current_date + timedelta(days=1)
            
            # Look for explicit dates
            # Pattern 1: DD/MM/YYYY or DD-MM-YYYY
            date_pattern1 = r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b'
            matches = re.findall(date_pattern1, text)
            if matches:
                day, month, year = matches[0]
                try:
                    return datetime(int(year), int(month), int(day))
                except:
                    pass
            
            # Pattern 2: Month DD, YYYY (e.g., "December 25, 2024")
            for month_name, month_num in self.months.items():
                pattern = rf'\b{month_name}\s+(\d{{1,2}}),?\s+(\d{{4}})\b'
                matches = re.findall(pattern, text_lower)
                if matches:
                    day, year = matches[0]
                    try:
                        return datetime(int(year), month_num, int(day))
                    except:
                        continue
            
            # Pattern 3: Just year mentioned (e.g., "in 2023")
            year_pattern = r'\b(20\d{2})\b'
            years = re.findall(year_pattern, text)
            if years:
                # Use middle of that year
                year = int(years[0])
                return datetime(year, 6, 15)
            
            return None
        
        except Exception as e:
            print(f"Text date extraction error: {e}")
            return None
    
    def _evaluate_temporal_difference(
        self,
        text_date: datetime,
        image_date: datetime,
        days_diff: int,
        text: str
    ) -> Dict:
        """
        Evaluate temporal difference and determine severity
        
        Thresholds:
        - 0-7 days: Acceptable (same week)
        - 8-30 days: Minor concern (same month)
        - 31-365 days: Medium concern (same year)
        - 365+ days: HIGH CONCERN (different years - likely image reuse)
        """
        
        text_lower = text.lower()
        
        # Check if text claims "recent" or "breaking"
        claims_recent = any(
            keyword in text_lower 
            for keyword in ['today', 'yesterday', 'recent', 'breaking', 'just', 'now']
        )
        
        # Severity thresholds
        if days_diff <= 7:
            # Within a week - acceptable
            return {
                'has_mismatch': False,
                'confidence': 90,
                'text_date': str(text_date.date()),
                'image_date': str(image_date.date()),
                'days_difference': days_diff,
                'explanation': f'Dates are consistent (within {days_diff} days)',
                'severity': 'LOW'
            }
        
        elif days_diff <= 30:
            # Within a month
            if claims_recent:
                return {
                    'has_mismatch': True,
                    'confidence': 60,
                    'text_date': str(text_date.date()),
                    'image_date': str(image_date.date()),
                    'days_difference': days_diff,
                    'explanation': f'Text claims recent incident, but image is {days_diff} days old',
                    'severity': 'MEDIUM'
                }
            else:
                return {
                    'has_mismatch': False,
                    'confidence': 70,
                    'text_date': str(text_date.date()),
                    'image_date': str(image_date.date()),
                    'days_difference': days_diff,
                    'explanation': f'Dates are reasonably close ({days_diff} days difference)',
                    'severity': 'LOW'
                }
        
        elif days_diff <= 365:
            # Within a year but different months
            return {
                'has_mismatch': True,
                'confidence': 75,
                'text_date': str(text_date.date()),
                'image_date': str(image_date.date()),
                'days_difference': days_diff,
                'explanation': f'⚠️ Temporal mismatch detected: {days_diff} days difference between claimed date and image date',
                'severity': 'MEDIUM'
            }
        
        else:
            # More than a year - HIGH CONCERN
            years_diff = days_diff // 365
            return {
                'has_mismatch': True,
                'confidence': 95,
                'text_date': str(text_date.date()),
                'image_date': str(image_date.date()),
                'days_difference': days_diff,
                'explanation': f'🚨 SEVERE temporal mismatch: Image is {years_diff}+ years old but text claims recent incident. Likely image reuse!',
                'severity': 'HIGH'
            }
    
    def get_temporal_summary(self, result: Dict) -> str:
        """Generate human-readable summary"""
        if not result['has_mismatch']:
            return "✅ No temporal inconsistencies detected"
        
        severity = result['severity']
        
        if severity == 'HIGH':
            return f"🚨 CRITICAL: {result['explanation']}"
        elif severity == 'MEDIUM':
            return f"⚠️ WARNING: {result['explanation']}"
        else:
            return f"ℹ️ NOTICE: {result['explanation']}"
