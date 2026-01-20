"""
FIXED Temporal Verification Module
Critical Fixes:
1. Better text date extraction (extracts ALL dates from text)
2. Cross-verification with web search for actual event dates
3. Detects when user gives WRONG year (e.g., says 2023 but actual is 2024)
4. Shows correct date found from news sources
"""

from PIL import Image
from PIL.ExifTags import TAGS
import re
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
import requests
from bs4 import BeautifulSoup

class TemporalVerifierFixed:
    """
    FIXED Temporal Verifier
    
    New Capabilities:
    1. Extracts ALL dates from text (not just first one)
    2. Web search to find ACTUAL event date
    3. Compares claimed date vs actual date
    4. Shows correction: "You said 2023 but actually happened in 2024"
    """
    
    def __init__(self):
        """Initialize temporal verifier"""
        print("✓ FIXED Temporal Verifier initialized")
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Temporal keywords
        self.temporal_keywords = {
            'today', 'yesterday', 'tomorrow', 'now', 'currently',
            'recent', 'latest', 'breaking', 'just happened', 'ongoing',
            'this morning', 'this evening', 'tonight', 'last night',
            'last week', 'last month', 'this year', 'last year'
        }
        
        # Month names
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
        image: Image.Image,
        keywords: List[str] = None
    ) -> Dict:
        """
        FIXED: Now checks claimed date vs ACTUAL date from web
        
        Process:
        1. Extract ALL dates from text (user's claim)
        2. Search web for ACTUAL event date
        3. Extract EXIF from image
        4. Cross-verify all three
        5. Show corrections if needed
        """
        try:
            print("\n🔍 FIXED Temporal Verification Starting...")
            
            # Step 1: Extract claimed dates from text
            claimed_dates = self.extract_all_text_dates(text)
            print(f"  📝 Claimed dates from text: {claimed_dates}")
            
            # Step 2: Search web for ACTUAL event date
            actual_date = self.search_actual_event_date(text, keywords)
            print(f"  🌐 Actual date from web: {actual_date}")
            
            # Step 3: Extract image EXIF date
            image_date = self.extract_image_date(image)
            print(f"  📸 Image EXIF date: {image_date}")
            
            # Step 4: Cross-verify everything
            result = self._cross_verify_dates(
                text,
                claimed_dates,
                actual_date,
                image_date
            )
            
            print(f"  ✓ Verification complete: {result['verdict']}")
            return result
        
        except Exception as e:
            print(f"Temporal verification error: {e}")
            return self._get_neutral_result()
    
    def extract_all_text_dates(self, text: str) -> List[Dict]:
        """
        FIXED: Extract ALL dates from text, not just first one
        
        Returns list of dates with context
        """
        dates_found = []
        text_lower = text.lower()
        current_date = datetime.now()
        
        # Pattern 1: Explicit dates (DD/MM/YYYY, DD-MM-YYYY)
        pattern1 = r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b'
        matches1 = re.finditer(pattern1, text)
        for match in matches1:
            day, month, year = match.groups()
            try:
                date = datetime(int(year), int(month), int(day))
                dates_found.append({
                    'date': date,
                    'format': 'DD/MM/YYYY',
                    'text': match.group(0),
                    'confidence': 0.95
                })
            except:
                pass
        
        # Pattern 2: Month DD, YYYY (e.g., "December 25, 2024")
        for month_name, month_num in self.months.items():
            pattern = rf'\b{month_name}\s+(\d{{1,2}}),?\s+(\d{{4}})\b'
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                day, year = match.groups()
                try:
                    date = datetime(int(year), month_num, int(day))
                    dates_found.append({
                        'date': date,
                        'format': 'Month DD, YYYY',
                        'text': match.group(0),
                        'confidence': 0.95
                    })
                except:
                    pass
        
        # Pattern 3: Just Month YYYY
        for month_name, month_num in self.months.items():
            pattern = rf'\b{month_name}\s+(\d{{4}})\b'
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                year = match.groups()[0]
                try:
                    # Middle of month
                    date = datetime(int(year), month_num, 15)
                    dates_found.append({
                        'date': date,
                        'format': 'Month YYYY',
                        'text': match.group(0),
                        'confidence': 0.80
                    })
                except:
                    pass
        
        # Pattern 4: Just year (YYYY)
        year_pattern = r'\b(20\d{2})\b'
        years = re.finditer(year_pattern, text)
        for match in years:
            year = int(match.group(1))
            # Middle of year
            date = datetime(year, 6, 15)
            dates_found.append({
                'date': date,
                'format': 'YYYY',
                'text': match.group(0),
                'confidence': 0.60
            })
        
        # Pattern 5: Relative dates
        if any(keyword in text_lower for keyword in ['today', 'now', 'currently']):
            dates_found.append({
                'date': current_date,
                'format': 'relative',
                'text': 'today/now',
                'confidence': 0.90
            })
        
        if 'yesterday' in text_lower:
            dates_found.append({
                'date': current_date - timedelta(days=1),
                'format': 'relative',
                'text': 'yesterday',
                'confidence': 0.90
            })
        
        # Remove duplicates and sort by confidence
        unique_dates = []
        seen = set()
        for d in sorted(dates_found, key=lambda x: x['confidence'], reverse=True):
            date_key = d['date'].strftime('%Y-%m-%d')
            if date_key not in seen:
                seen.add(date_key)
                unique_dates.append(d)
        
        return unique_dates
    
    def search_actual_event_date(self, text: str, keywords: List[str] = None) -> Optional[Dict]:
        """
        NEW FUNCTION: Search web to find ACTUAL event date
        
        This is KEY FIX - searches news to find when event actually happened
        """
        try:
            print("  🔍 Searching web for actual event date...")
            
            # Build search query
            if keywords:
                search_query = ' '.join(keywords[:5]) + ' date'
            else:
                # Use first 50 chars of text
                search_query = text[:50] + ' date'
            
            # Search Google News
            url = f"https://www.google.com/search?q={requests.utils.quote(search_query)}&tbm=nws"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find date in news results
            dates_in_news = []
            
            # Look for date patterns in news snippets
            snippets = soup.find_all(['div', 'span'], limit=10)
            
            for snippet in snippets:
                text_content = snippet.get_text()
                
                # Extract dates from snippet
                # Pattern: Month DD, YYYY
                for month_name, month_num in self.months.items():
                    pattern = rf'{month_name}\s+(\d{{1,2}}),?\s+(\d{{4}})'
                    matches = re.finditer(pattern, text_content.lower())
                    for match in matches:
                        day, year = match.groups()
                        try:
                            date = datetime(int(year), month_num, int(day))
                            dates_in_news.append({
                                'date': date,
                                'source': 'news',
                                'text': match.group(0),
                                'confidence': 0.85
                            })
                        except:
                            pass
                
                # Pattern: YYYY
                year_pattern = r'\b(20\d{2})\b'
                years = re.finditer(year_pattern, text_content)
                for match in years:
                    year = int(match.group(1))
                    date = datetime(year, 6, 15)
                    dates_in_news.append({
                        'date': date,
                        'source': 'news',
                        'text': match.group(0),
                        'confidence': 0.70
                    })
            
            # Return most recent date found (likely the actual event date)
            if dates_in_news:
                # Sort by date (most recent first)
                dates_in_news.sort(key=lambda x: x['date'], reverse=True)
                print(f"  ✓ Found actual date from news: {dates_in_news[0]['date'].strftime('%Y-%m-%d')}")
                return dates_in_news[0]
            
            return None
        
        except Exception as e:
            print(f"  ⚠️ Web search for actual date failed: {e}")
            return None
    
    def extract_image_date(self, image: Image.Image) -> Optional[datetime]:
        """Extract date from image EXIF (unchanged)"""
        try:
            exif_data = image._getexif()
            
            if not exif_data:
                return None
            
            date_tags = ['DateTimeOriginal', 'DateTime', 'DateTimeDigitized']
            
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                
                if tag_name in date_tags:
                    date_str = str(value)
                    
                    try:
                        date_str = date_str.replace(':', '-', 2)
                        parsed_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                        return parsed_date
                    except:
                        try:
                            parsed_date = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                            return parsed_date
                        except:
                            continue
            
            return None
        
        except Exception as e:
            return None
    
    def _cross_verify_dates(
        self,
        text: str,
        claimed_dates: List[Dict],
        actual_date: Optional[Dict],
        image_date: Optional[datetime]
    ) -> Dict:
        """
        CRITICAL FIX: Cross-verify all dates and show corrections
        
        Checks:
        1. Claimed date vs Actual date (from web)
        2. Claimed date vs Image date
        3. Actual date vs Image date
        """
        
        # If no dates at all
        if not claimed_dates and not actual_date and not image_date:
            return {
                'has_mismatch': False,
                'verdict': 'NO_TEMPORAL_INFO',
                'claimed_date': None,
                'actual_date': None,
                'image_date': None,
                'correction': None,
                'explanation': 'No temporal information available',
                'confidence': 0
            }
        
        # PRIMARY CHECK: Claimed vs Actual
        if claimed_dates and actual_date:
            claimed = claimed_dates[0]['date']  # Highest confidence claimed date
            actual = actual_date['date']
            
            days_diff = abs((claimed - actual).days)
            years_diff = days_diff / 365
            
            # CRITICAL: Different years!
            if years_diff >= 1:
                return {
                    'has_mismatch': True,
                    'verdict': 'WRONG_YEAR_CLAIMED',
                    'severity': 'CRITICAL',
                    'claimed_date': claimed.strftime('%Y-%m-%d'),
                    'actual_date': actual.strftime('%Y-%m-%d'),
                    'image_date': image_date.strftime('%Y-%m-%d') if image_date else None,
                    'correction': f"❌ You said {claimed.year} but event actually happened in {actual.year}",
                    'explanation': (
                        f"User claimed date: {claimed.strftime('%B %d, %Y')}\n"
                        f"Actual date from news: {actual.strftime('%B %d, %Y')}\n"
                        f"Difference: {int(years_diff)} years!\n\n"
                        f"🚨 CRITICAL: Year mismatch detected. The event happened in {actual.year}, not {claimed.year}."
                    ),
                    'confidence': 95
                }
            
            # Different months
            elif days_diff > 60:
                return {
                    'has_mismatch': True,
                    'verdict': 'WRONG_MONTH_CLAIMED',
                    'severity': 'HIGH',
                    'claimed_date': claimed.strftime('%Y-%m-%d'),
                    'actual_date': actual.strftime('%Y-%m-%d'),
                    'image_date': image_date.strftime('%Y-%m-%d') if image_date else None,
                    'correction': f"⚠️ Event was in {actual.strftime('%B %Y')}, not {claimed.strftime('%B %Y')}",
                    'explanation': (
                        f"User claimed: {claimed.strftime('%B %Y')}\n"
                        f"Actual date: {actual.strftime('%B %Y')}\n"
                        f"Difference: {days_diff} days\n\n"
                        f"⚠️ Month mismatch detected."
                    ),
                    'confidence': 85
                }
        
        # SECONDARY CHECK: Image EXIF vs Claimed/Actual
        if image_date:
            # Check against claimed
            if claimed_dates:
                claimed = claimed_dates[0]['date']
                days_diff = abs((claimed - image_date).days)
                
                if days_diff > 365:
                    return {
                        'has_mismatch': True,
                        'verdict': 'OLD_IMAGE_REUSED',
                        'severity': 'CRITICAL',
                        'claimed_date': claimed.strftime('%Y-%m-%d'),
                        'actual_date': actual_date['date'].strftime('%Y-%m-%d') if actual_date else None,
                        'image_date': image_date.strftime('%Y-%m-%d'),
                        'correction': f"🚨 Image is from {image_date.year}, but claimed incident is from {claimed.year}",
                        'explanation': (
                            f"Image EXIF date: {image_date.strftime('%B %d, %Y')}\n"
                            f"Claimed incident date: {claimed.strftime('%B %d, %Y')}\n"
                            f"Difference: {days_diff} days ({days_diff//365} years)\n\n"
                            f"🚨 CRITICAL: Old image being reused for recent claim!"
                        ),
                        'confidence': 95
                    }
        
        # No significant mismatch
        return {
            'has_mismatch': False,
            'verdict': 'DATES_CONSISTENT',
            'claimed_date': claimed_dates[0]['date'].strftime('%Y-%m-%d') if claimed_dates else None,
            'actual_date': actual_date['date'].strftime('%Y-%m-%d') if actual_date else None,
            'image_date': image_date.strftime('%Y-%m-%d') if image_date else None,
            'correction': None,
            'explanation': 'Dates are reasonably consistent',
            'confidence': 70
        }
    
    def _get_neutral_result(self) -> Dict:
        """Return neutral result for errors"""
        return {
            'has_mismatch': False,
            'verdict': 'ERROR',
            'claimed_date': None,
            'actual_date': None,
            'image_date': None,
            'correction': None,
            'explanation': 'Could not verify temporal consistency',
            'confidence': 0
        }
