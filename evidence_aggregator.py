"""
Multi-Source Evidence Aggregator
Novel Enhancement: Dynamic real-time evidence from multiple sources
Addresses DEETSA limitation: Reliance on pre-built static knowledge base

This module aggregates evidence from:
1. Google News (real-time news)
2. Fact-checking APIs (Google Fact Check Tools)
3. Wikipedia/Wikidata (structured knowledge)
4. Web scraping (existing functionality enhanced)
5. Social media trends (optional)
"""

import requests
from bs4 import BeautifulSoup
import json
from typing import Dict, List, Optional
import time
from urllib.parse import quote_plus

class EvidenceAggregator:
    """
    Multi-Source Evidence Aggregation
    
    Base Paper Limitation:
    - DEETSA uses pre-built knowledge base (static, needs manual updates)
    - Cannot handle NEW events immediately
    - Limited to training data period
    
    Our Enhancement:
    - Real-time evidence from multiple sources
    - No pre-processing needed
    - Always up-to-date
    - Broader coverage than static KB
    """
    
    def __init__(self):
        """Initialize evidence aggregator"""
        print("✓ Multi-Source Evidence Aggregator initialized")
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Source credibility weights
        self.source_weights = {
            'factcheck_api': 0.95,  # Highest credibility
            'news_api': 0.85,       # High credibility
            'wikipedia': 0.80,      # Good credibility
            'web_scraping': 0.60,   # Moderate credibility
            'social_media': 0.40    # Lower credibility
        }
    
    def aggregate_all_evidence(
        self, 
        text: str, 
        keywords: List[str],
        location: Optional[str] = None
    ) -> Dict:
        """
        Aggregate evidence from ALL sources
        
        Returns comprehensive evidence dictionary:
        {
            'news': [...],
            'factcheck': [...],
            'wikipedia': {...},
            'web_general': [...],
            'summary': {...}
        }
        """
        try:
            print(f"🔍 Aggregating evidence from multiple sources...")
            
            evidence = {}
            
            # 1. Get news evidence
            print("  📰 Fetching news articles...")
            evidence['news'] = self.get_news_evidence(text, keywords, location)
            
            # 2. Get fact-check evidence
            print("  ✅ Querying fact-check APIs...")
            evidence['factcheck'] = self.get_factcheck_evidence(text)
            
            # 3. Get Wikipedia data
            print("  📚 Searching Wikipedia...")
            evidence['wikipedia'] = self.get_wikipedia_evidence(keywords, location)
            
            # 4. Get general web evidence (existing scraping enhanced)
            print("  🌐 Web scraping for additional evidence...")
            evidence['web_general'] = self.get_web_evidence(text, keywords)
            
            # 5. Compute aggregated summary
            evidence['summary'] = self._compute_evidence_summary(evidence)
            
            print(f"✓ Evidence aggregation complete")
            return evidence
        
        except Exception as e:
            print(f"Evidence aggregation error: {e}")
            return self._get_empty_evidence()
    
    def get_news_evidence(
        self, 
        text: str, 
        keywords: List[str],
        location: Optional[str]
    ) -> List[Dict]:
        """
        Get evidence from news sources
        
        Uses:
        1. Google News scraping (free, no API)
        2. NewsAPI (optional if key available)
        """
        try:
            news_articles = []
            
            # Build search query
            query_parts = keywords[:3].copy()
            if location and location != 'Unknown':
                query_parts.append(location)
            
            search_query = ' '.join(query_parts)
            
            # Method 1: Google News scraping
            google_news = self._scrape_google_news(search_query)
            news_articles.extend(google_news)
            
            # Method 2: NewsAPI (if available)
            # Uncomment if you have NewsAPI key
            # newsapi_results = self._query_newsapi(search_query)
            # news_articles.extend(newsapi_results)
            
            return news_articles[:10]  # Top 10 articles
        
        except Exception as e:
            print(f"News evidence error: {e}")
            return []
    
    def get_factcheck_evidence(self, text: str) -> List[Dict]:
        """
        Get evidence from fact-checking APIs
        
        Uses Google Fact Check Tools API (FREE, no key needed)
        """
        try:
            # Extract main claim (first sentence or up to 100 chars)
            claim = text[:100] if len(text) > 100 else text
            claim = claim.split('.')[0]  # First sentence
            
            # Google Fact Check Tools API
            api_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
            
            params = {
                'query': claim,
                'languageCode': 'en'
            }
            
            response = requests.get(
                api_url, 
                params=params, 
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                claims = data.get('claims', [])
                
                # Parse fact-check results
                factchecks = []
                for claim_obj in claims[:5]:  # Top 5
                    claim_review = claim_obj.get('claimReview', [{}])[0]
                    
                    factchecks.append({
                        'claim': claim_obj.get('text', ''),
                        'rating': claim_review.get('textualRating', 'Unknown'),
                        'publisher': claim_review.get('publisher', {}).get('name', 'Unknown'),
                        'url': claim_review.get('url', ''),
                        'credibility': 'HIGH'
                    })
                
                return factchecks
            
            return []
        
        except Exception as e:
            print(f"Fact-check API error: {e}")
            return []
    
    def get_wikipedia_evidence(
        self, 
        keywords: List[str],
        location: Optional[str]
    ) -> Dict:
        """
        Get structured knowledge from Wikipedia
        
        Uses Wikipedia REST API (free, no key)
        """
        try:
            # Try to find main entity
            entity = None
            
            # First try location
            if location and location != 'Unknown':
                entity = location
            # Then try capitalized keywords (likely entities)
            else:
                for keyword in keywords:
                    if keyword[0].isupper():
                        entity = keyword
                        break
            
            if not entity:
                return {}
            
            # Wikipedia API
            api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote_plus(entity)}"
            
            response = requests.get(api_url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    'title': data.get('title', ''),
                    'extract': data.get('extract', ''),
                    'description': data.get('description', ''),
                    'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                    'found': True
                }
            
            return {'found': False}
        
        except Exception as e:
            print(f"Wikipedia error: {e}")
            return {'found': False}
    
    def get_web_evidence(self, text: str, keywords: List[str]) -> List[Dict]:
        """
        Enhanced web scraping for general evidence
        """
        try:
            search_query = ' '.join(keywords[:5])
            
            # Google search
            results = self._scrape_google_search(search_query)
            
            return results[:10]
        
        except Exception as e:
            print(f"Web scraping error: {e}")
            return []
    
    def _scrape_google_news(self, query: str) -> List[Dict]:
        """Scrape Google News results"""
        try:
            url = f"https://news.google.com/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = []
            
            # Find article elements
            article_elements = soup.find_all('article', limit=10)
            
            for article in article_elements:
                try:
                    # Extract title
                    title_elem = article.find('a')
                    title = title_elem.text if title_elem else 'Unknown'
                    
                    # Extract source
                    source_elem = article.find('a', {'data-n-tid': True})
                    source = source_elem.text if source_elem else 'Unknown Source'
                    
                    # Extract time
                    time_elem = article.find('time')
                    pub_time = time_elem.text if time_elem else 'Unknown'
                    
                    articles.append({
                        'title': title,
                        'source': source,
                        'published': pub_time,
                        'type': 'news',
                        'credibility': 'HIGH' if any(
                            trusted in source.lower() 
                            for trusted in ['reuters', 'bbc', 'cnn', 'nyt', 'guardian']
                        ) else 'MEDIUM'
                    })
                except:
                    continue
            
            return articles
        
        except Exception as e:
            print(f"Google News scraping error: {e}")
            return []
    
    def _scrape_google_search(self, query: str) -> List[Dict]:
        """Scrape general Google search results"""
        try:
            url = f"https://www.google.com/search?q={quote_plus(query)}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            
            # Find search result divs
            result_divs = soup.find_all('div', class_='g', limit=10)
            
            for div in result_divs:
                try:
                    # Extract title
                    title_elem = div.find('h3')
                    title = title_elem.text if title_elem else ''
                    
                    # Extract snippet
                    snippet_elem = div.find('div', class_=['VwiC3b', 'yXK7lf'])
                    snippet = snippet_elem.text if snippet_elem else ''
                    
                    # Extract URL
                    link_elem = div.find('a')
                    url = link_elem.get('href', '') if link_elem else ''
                    
                    if title and snippet:
                        results.append({
                            'title': title,
                            'snippet': snippet,
                            'url': url,
                            'type': 'web',
                            'credibility': 'MEDIUM'
                        })
                except:
                    continue
            
            return results
        
        except Exception as e:
            print(f"Google search scraping error: {e}")
            return []
    
    def _compute_evidence_summary(self, evidence: Dict) -> Dict:
        """
        Compute aggregated summary from all evidence sources
        
        Returns:
        {
            'total_sources': int,
            'credible_sources': int,
            'evidence_score': float (0-100),
            'verdict': str,
            'key_findings': List[str]
        }
        """
        try:
            total_sources = 0
            credible_sources = 0
            weighted_score = 0
            key_findings = []
            
            # Count news articles
            news = evidence.get('news', [])
            if news:
                total_sources += len(news)
                credible_news = [n for n in news if n.get('credibility') == 'HIGH']
                credible_sources += len(credible_news)
                
                # Add to weighted score
                news_weight = self.source_weights['news_api']
                weighted_score += len(credible_news) * news_weight * 10
                
                if credible_news:
                    key_findings.append(f"Found {len(credible_news)} credible news sources")
            
            # Count fact-checks
            factchecks = evidence.get('factcheck', [])
            if factchecks:
                total_sources += len(factchecks)
                credible_sources += len(factchecks)  # All fact-checks are credible
                
                # Add to weighted score
                factcheck_weight = self.source_weights['factcheck_api']
                weighted_score += len(factchecks) * factcheck_weight * 15
                
                # Add ratings to findings
                for fc in factchecks[:3]:
                    rating = fc.get('rating', 'Unknown')
                    if rating.lower() in ['false', 'fake', 'misleading']:
                        key_findings.append(f"⚠️ Fact-check: Rated as '{rating}'")
                    else:
                        key_findings.append(f"✓ Fact-check: {rating}")
            
            # Check Wikipedia
            wiki = evidence.get('wikipedia', {})
            if wiki.get('found'):
                total_sources += 1
                credible_sources += 1
                weighted_score += self.source_weights['wikipedia'] * 10
                key_findings.append(f"Wikipedia entry found: {wiki.get('title', '')}")
            
            # Count web results
            web = evidence.get('web_general', [])
            if web:
                total_sources += len(web)
                weighted_score += len(web) * self.source_weights['web_scraping'] * 5
            
            # Normalize score
            evidence_score = min(weighted_score, 100)
            
            # Determine verdict
            if evidence_score >= 70:
                verdict = 'STRONG_EVIDENCE_FOUND'
            elif evidence_score >= 50:
                verdict = 'MODERATE_EVIDENCE_FOUND'
            elif evidence_score >= 30:
                verdict = 'LIMITED_EVIDENCE_FOUND'
            else:
                verdict = 'NO_EVIDENCE_FOUND'
            
            return {
                'total_sources': total_sources,
                'credible_sources': credible_sources,
                'evidence_score': round(evidence_score, 2),
                'verdict': verdict,
                'key_findings': key_findings[:5]  # Top 5 findings
            }
        
        except Exception as e:
            print(f"Summary computation error: {e}")
            return {
                'total_sources': 0,
                'credible_sources': 0,
                'evidence_score': 0,
                'verdict': 'ERROR',
                'key_findings': []
            }
    
    def _get_empty_evidence(self) -> Dict:
        """Return empty evidence structure"""
        return {
            'news': [],
            'factcheck': [],
            'wikipedia': {'found': False},
            'web_general': [],
            'summary': {
                'total_sources': 0,
                'credible_sources': 0,
                'evidence_score': 0,
                'verdict': 'NO_EVIDENCE_FOUND',
                'key_findings': []
            }
        }
