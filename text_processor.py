"""
PERFECT Text Processor
Advanced keyword, location, and date extraction
"""

import re
from typing import Dict, List
from datetime import datetime

class TextProcessorPerfect:
    def __init__(self):
        """Initialize enhanced text processor"""
        print("Initializing PERFECT Text Processor...")
        
        # Try spaCy if available
        self.nlp = self._load_spacy()
        
        # Event type keywords (expanded)
        self.event_types = {
            'fire': ['fire', 'burning', 'blaze', 'flames', 'smoke', 'arson'],
            'flood': ['flood', 'flooding', 'water', 'submerged', 'deluge', 'inundation', 'rain', 'storm'],
            'accident': ['accident', 'crash', 'collision', 'wreck', 'mishap'],
            'protest': ['protest', 'demonstration', 'rally', 'march', 'agitation'],
            'explosion': ['explosion', 'blast', 'detonation', 'explode', 'bomb'],
            'earthquake': ['earthquake', 'tremor', 'seismic', 'quake'],
            'cyclone': ['cyclone', 'hurricane', 'typhoon', 'storm'],
            'violence': ['shooting', 'attack', 'violence', 'stabbing', 'assault'],
            'rescue': ['rescue', 'emergency', 'relief', 'evacuation'],
        }
        
        # Indian cities and states (common ones)
        self.indian_locations = {
            'chennai', 'mumbai', 'delhi', 'bangalore', 'kolkata', 'hyderabad',
            'pune', 'ahmedabad', 'jaipur', 'lucknow', 'kanpur', 'nagpur',
            'tamil nadu', 'maharashtra', 'karnataka', 'kerala', 'gujarat',
            'rajasthan', 'uttar pradesh', 'madhya pradesh', 'west bengal'
        }
        
        # Date/time keywords
        self.temporal_keywords = {
            'today', 'yesterday', 'tonight', 'now', 'currently', 'recent',
            'latest', 'breaking', 'just', 'this morning', 'last night'
        }
        
        # Month names
        self.months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12,
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        print("✓ PERFECT Text Processor initialized!")
    
    def _load_spacy(self):
        """Try to load spaCy"""
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
            print("✓ spaCy loaded")
            return nlp
        except:
            print("ℹ️ spaCy not available, using rule-based extraction")
            return None
    
    def process_text(self, text: str) -> Dict:
        """
        MAIN FUNCTION: Extract ALL important information
        """
        try:
            print(f"\n📝 Processing text: '{text[:100]}...'")
            
            # 1. Extract entities
            entities = self.extract_entities_advanced(text)
            print(f"  ✓ Entities: {entities}")
            
            # 2. Extract keywords
            keywords = self.extract_keywords_advanced(text)
            print(f"  ✓ Keywords: {keywords}")
            
            # 3. Classify event type
            event_type = self.classify_event_type(text)
            print(f"  ✓ Event type: {event_type}")
            
            # 4. Extract dates
            dates = self.extract_all_dates(text)
            print(f"  ✓ Dates: {dates}")
            
            # 5. Build SPECIFIC search query
            search_query = self._build_specific_search_query(
                keywords, entities, event_type, dates
            )
            print(f"  ✓ Search query: '{search_query}'")
            
            # 6. Build verification keywords (for matching)
            verification_keywords = self._build_verification_keywords(
                keywords, entities, event_type
            )
            print(f"  ✓ Verification keywords: {verification_keywords}")
            
            return {
                'original_text': text,
                'keywords': keywords,
                'entities': entities,
                'event_type': event_type,
                'dates': dates,
                'search_query': search_query,
                'verification_keywords': verification_keywords,
                'location': entities['locations'][0] if entities['locations'] else 'Unknown'
            }
        
        except Exception as e:
            print(f"Text processing error: {e}")
            return self._get_fallback_result(text)
    
    def extract_entities_advanced(self, text: str) -> Dict[str, List[str]]:
        """
        ADVANCED entity extraction
        """
        entities = {
            'locations': [],
            'organizations': [],
            'persons': [],
            'dates': []
        }
        
        # If spaCy available, use it
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in ["GPE", "LOC"]:
                    entities['locations'].append(ent.text)
                elif ent.label_ == "ORG":
                    entities['organizations'].append(ent.text)
                elif ent.label_ == "PERSON":
                    entities['persons'].append(ent.text)
                elif ent.label_ in ["DATE", "TIME"]:
                    entities['dates'].append(ent.text)
        else:
            # Fallback: rule-based extraction
            entities = self._extract_entities_rule_based(text)
        
        # Also check for Indian locations specifically
        text_lower = text.lower()
        for location in self.indian_locations:
            if location in text_lower and location.title() not in entities['locations']:
                entities['locations'].append(location.title())
        
        # Remove duplicates
        for key in entities:
            entities[key] = list(dict.fromkeys(entities[key]))[:5]  # Top 5 each
        
        return entities
    
    def _extract_entities_rule_based(self, text: str) -> Dict[str, List[str]]:
        """
        Rule-based entity extraction (fallback)
        """
        entities = {
            'locations': [],
            'organizations': [],
            'persons': [],
            'dates': []
        }
        
        # Find capitalized words (likely proper nouns)
        words = text.split()
        i = 0
        while i < len(words):
            word = re.sub(r'[^\w]', '', words[i])
            
            if word and len(word) > 2 and word[0].isupper():
                # Check if next word is also capitalized (multi-word entity)
                entity = [word]
                j = i + 1
                while j < len(words) and j < i + 3:  # Max 3 words
                    next_word = re.sub(r'[^\w]', '', words[j])
                    if next_word and next_word[0].isupper():
                        entity.append(next_word)
                        j += 1
                    else:
                        break
                
                entity_text = ' '.join(entity)
                
                # Classify entity type
                if any(loc in entity_text.lower() for loc in ['city', 'state', 'district', 'area']):
                    entities['locations'].append(entity_text)
                elif len(entity) > 1:
                    entities['locations'].append(entity_text)  # Multi-word likely location
                
                i = j
            else:
                i += 1
        
        return entities
    
    def extract_keywords_advanced(self, text: str) -> List[str]:
        """
        ADVANCED keyword extraction - focuses on IMPORTANT words
        """
        keywords = []
        text_lower = text.lower()
        
        # 1. Event type keywords
        for event_type, words in self.event_types.items():
            for word in words:
                if word in text_lower and word not in keywords:
                    keywords.append(word)
        
        # 2. Important nouns (rule-based)
        # Remove common stopwords
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these',
            'those', 'it', 'its', 'they', 'them', 'their'
        }
        
        words = re.findall(r'\b\w+\b', text_lower)
        for word in words:
            if (len(word) > 3 and 
                word not in stopwords and 
                word not in keywords and
                not word.isdigit()):
                keywords.append(word)
        
        # 3. Important adjectives (damage-related)
        damage_words = ['severe', 'heavy', 'major', 'massive', 'widespread', 
                       'extensive', 'catastrophic', 'devastating']
        for word in damage_words:
            if word in text_lower and word not in keywords:
                keywords.append(word)
        
        # Keep top 15 most relevant
        return keywords[:15]
    
    def extract_all_dates(self, text: str) -> List[str]:
        """
        Extract ALL date mentions
        """
        dates = []
        text_lower = text.lower()
        
        # 1. Relative dates
        for keyword in self.temporal_keywords:
            if keyword in text_lower:
                dates.append(keyword)
        
        # 2. Month + Year
        for month_name in self.months.keys():
            pattern = rf'\b{month_name}\s+(\d{{4}})\b'
            matches = re.findall(pattern, text_lower)
            for year in matches:
                dates.append(f"{month_name} {year}")
        
        # 3. Just year
        year_pattern = r'\b(20\d{2})\b'
        years = re.findall(year_pattern, text)
        dates.extend(years)
        
        # 4. DD/MM/YYYY format
        date_pattern = r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b'
        date_matches = re.findall(date_pattern, text)
        for match in date_matches:
            dates.append(f"{match[0]}/{match[1]}/{match[2]}")
        
        return list(dict.fromkeys(dates))  # Remove duplicates
    
    def classify_event_type(self, text: str) -> str:
        """
        Classify event type with confidence
        """
        text_lower = text.lower()
        
        # Count matches for each event type
        scores = {}
        for event_type, keywords in self.event_types.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[event_type] = score
        
        if scores:
            # Return event type with highest score
            return max(scores.items(), key=lambda x: x[1])[0]
        
        return 'incident'  # Generic fallback
    
    def _build_specific_search_query(
        self,
        keywords: List[str],
        entities: Dict,
        event_type: str,
        dates: List[str]
    ) -> str:
        """
        Build SPECIFIC search query for exact matching
        
        Format: "location event_type date keywords"
        Example: "Chennai floods December 2024 heavy rain"
        """
        query_parts = []
        
        # 1. Location (most important)
        if entities['locations']:
            query_parts.append(entities['locations'][0])
        
        # 2. Event type
        query_parts.append(event_type)
        
        # 3. Date (if specific)
        if dates:
            # Prefer month+year over relative dates
            for date in dates:
                if any(month in date.lower() for month in self.months.keys()):
                    query_parts.append(date)
                    break
            else:
                # Use first date
                if not any(d in ['today', 'yesterday', 'recent'] for d in dates):
                    query_parts.append(dates[0])
        
        # 4. Top 2-3 important keywords
        important_keywords = [
            kw for kw in keywords[:5] 
            if kw in self.event_types.get(event_type, []) or len(kw) > 5
        ]
        query_parts.extend(important_keywords[:2])
        
        # Add "news" to get news results
        query_parts.append('news')
        
        return ' '.join(query_parts)
    
    def _build_verification_keywords(
        self,
        keywords: List[str],
        entities: Dict,
        event_type: str
    ) -> List[str]:
        """
        Build list of keywords for verification matching
        These will be matched against retrieved images
        """
        verification_kw = []
        
        # Add location
        verification_kw.extend(entities['locations'])
        
        # Add event type
        verification_kw.append(event_type)
        
        # Add event-specific keywords
        if event_type in self.event_types:
            verification_kw.extend(self.event_types[event_type][:3])
        
        # Add top keywords
        verification_kw.extend(keywords[:5])
        
        # Convert to lowercase and remove duplicates
        return list(dict.fromkeys([kw.lower() for kw in verification_kw]))
    
    def _get_fallback_result(self, text: str) -> Dict:
        """Fallback if processing fails"""
        words = text.split()[:10]
        return {
            'original_text': text,
            'keywords': words,
            'entities': {'locations': [], 'organizations': [], 'persons': [], 'dates': []},
            'event_type': 'incident',
            'dates': [],
            'search_query': ' '.join(words[:5]) + ' news',
            'verification_keywords': words[:5],
            'location': 'Unknown'
        }
