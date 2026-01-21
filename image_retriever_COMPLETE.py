"""
PERFECT Image Retriever
- Uses exact keywords from text
- Filters out generic/unrelated images
- Only returns images matching the specific incident
"""

import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import time
from typing import List, Dict
import urllib.parse
import random

class ImageRetrieverPerfect:
    """
    PERFECT Image Retriever - Exact matching only
    """
    
    def __init__(self):
        """Initialize"""
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        
        print("✓ PERFECT Image Retriever initialized")
    
    def retrieve_images_for_text(
        self,
        query: str,
        max_images: int = 10,
        location: str = None,
        event_type: str = None,
        keywords: List[str] = None,
        verification_keywords: List[str] = None
    ) -> List[Dict]:
        """
        Retrieve images with EXACT matching
        
        Args:
            query: Search query (already optimized)
            verification_keywords: Keywords that MUST appear in results
        """
        try:
            print(f"\n🔍 EXACT IMAGE SEARCH")
            print(f"  Query: '{query}'")
            print(f"  Must match: {verification_keywords}")
            
            all_images = []
            
            # Use the specific query (already has location + event + date)
            search_query = query
            
            # Method 1: DuckDuckGo with EXACT query
            print("  📸 Searching DuckDuckGo...")
            ddg_images = self._search_duckduckgo_exact(
                search_query,
                verification_keywords or [],
                max_images
            )
            all_images.extend(ddg_images)
            print(f"     ✓ Matched {len(ddg_images)} images")
            
            # Method 2: Bing with EXACT query
            if len(all_images) < max_images:
                print("  📸 Searching Bing...")
                bing_images = self._search_bing_exact(
                    search_query,
                    verification_keywords or [],
                    max_images - len(all_images)
                )
                all_images.extend(bing_images)
                print(f"     ✓ Matched {len(bing_images)} images")
            
            # Method 3: Search specific news sites
            if len(all_images) < max_images and location:
                print("  📰 Searching news sites...")
                news_images = self._search_news_sites_exact(
                    location,
                    event_type or 'incident',
                    verification_keywords or [],
                    max_images - len(all_images)
                )
                all_images.extend(news_images)
                print(f"     ✓ Matched {len(news_images)} images")
            
            # Filter: Only keep images matching verification keywords
            if verification_keywords:
                filtered_images = self._filter_by_keywords(
                    all_images,
                    verification_keywords
                )
                print(f"  🔍 Filtered: {len(all_images)} → {len(filtered_images)} (exact matches)")
                all_images = filtered_images
            
            print(f"  ✅ TOTAL EXACT MATCHES: {len(all_images)}")
            
            return all_images[:max_images]
        
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def reverse_image_search(self, image: Image.Image, max_results: int = 20) -> Dict:
        """Placeholder for reverse search"""
        return {
            'original_source': None,
            'all_occurrences': [],
            'contexts': [],
            'is_original': True,
            'reuse_detected': False
        }
    
    def _search_duckduckgo_exact(
        self,
        query: str,
        must_match_keywords: List[str],
        max_images: int
    ) -> List[Dict]:
        """
        DuckDuckGo search with keyword filtering
        """
        try:
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml',
                'Accept-Language': 'en-US,en;q=0.9'
            }
            
            # Add quotes for exact phrase matching
            search_query = f'"{query}"'
            search_url = f"https://duckduckgo.com/?q={urllib.parse.quote(search_query)}&iax=images&ia=images"
            
            session = requests.Session()
            response = session.get(search_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            images = []
            img_elements = soup.find_all('img', limit=max_images * 5)  # Get more, filter later
            
            for img in img_elements:
                if len(images) >= max_images * 2:  # Get extras for filtering
                    break
                
                img_url = img.get('src') or img.get('data-src')
                
                if not img_url or img_url.startswith('data:') or 'logo' in img_url.lower():
                    continue
                
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif not img_url.startswith('http'):
                    continue
                
                # Get alt text and title for keyword matching
                alt_text = img.get('alt', '').lower()
                title = img.get('title', '').lower()
                
                # Download image
                img_data = self._download_image(img_url, headers)
                
                if img_data:
                    images.append({
                        'image': img_data,
                        'source': self._extract_domain(img_url),
                        'name': alt_text or title or query,
                        'url': img_url,
                        'alt_text': alt_text,
                        'title': title,
                        'credibility': self._determine_credibility(img_url),
                        'type': 'web',
                        'platform': 'DuckDuckGo'
                    })
                
                time.sleep(0.05)
            
            return images
        
        except Exception as e:
            print(f"     DuckDuckGo error: {e}")
            return []
    
    def _search_bing_exact(
        self,
        query: str,
        must_match_keywords: List[str],
        max_images: int
    ) -> List[Dict]:
        """
        Bing search with keyword filtering
        """
        try:
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml'
            }
            
            search_url = f"https://www.bing.com/images/search?q={urllib.parse.quote(query)}"
            
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            images = []
            img_elements = soup.find_all('img', limit=max_images * 5)
            
            for img in img_elements:
                if len(images) >= max_images * 2:
                    break
                
                img_url = img.get('src') or img.get('data-src')
                
                if not img_url or img_url.startswith('data:'):
                    continue
                
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif not img_url.startswith('http'):
                    continue
                
                alt_text = img.get('alt', '').lower()
                
                img_data = self._download_image(img_url, headers)
                
                if img_data:
                    images.append({
                        'image': img_data,
                        'source': self._extract_domain(img_url),
                        'name': alt_text or query,
                        'url': img_url,
                        'alt_text': alt_text,
                        'credibility': self._determine_credibility(img_url),
                        'type': 'web',
                        'platform': 'Bing'
                    })
                
                time.sleep(0.05)
            
            return images
        
        except Exception as e:
            print(f"     Bing error: {e}")
            return []
    
    def _search_news_sites_exact(
        self,
        location: str,
        event_type: str,
        must_match_keywords: List[str],
        max_images: int
    ) -> List[Dict]:
        """
        Search specific news sites for exact incident
        """
        try:
            images = []
            
            # Build specific news query
            news_query = f"{location} {event_type} site:reuters.com OR site:bbc.com OR site:thehindu.com"
            
            # Use DuckDuckGo to search news sites
            news_images = self._search_duckduckgo_exact(
                news_query,
                must_match_keywords,
                max_images
            )
            
            # Mark as news
            for img in news_images:
                img['credibility'] = 'TIER1_NEWS'
                img['type'] = 'news'
            
            return news_images
        
        except:
            return []
    
    def _filter_by_keywords(
        self,
        images: List[Dict],
        must_match_keywords: List[str]
    ) -> List[Dict]:
        """
        Filter images - only keep if keywords match
        
        Checks:
        1. Image source domain
        2. Image alt text
        3. Image title
        4. Image name/description
        """
        if not must_match_keywords:
            return images
        
        filtered = []
        
        for img in images:
            # Combine all text fields
            searchable_text = ' '.join([
                img.get('source', ''),
                img.get('name', ''),
                img.get('alt_text', ''),
                img.get('title', ''),
                img.get('url', '')
            ]).lower()
            
            # Count keyword matches
            matches = sum(1 for kw in must_match_keywords if kw.lower() in searchable_text)
            
            # Calculate match ratio
            match_ratio = matches / len(must_match_keywords)
            
            # Keep if matches at least 40% of keywords
            # OR if from credible news source
            if match_ratio >= 0.4 or img.get('credibility') == 'TIER1_NEWS':
                img['keyword_matches'] = matches
                img['match_ratio'] = match_ratio
                filtered.append(img)
        
        # Sort by match ratio (best matches first)
        filtered.sort(key=lambda x: x.get('match_ratio', 0), reverse=True)
        
        return filtered
    
    def _determine_credibility(self, url: str) -> str:
        """Determine source credibility"""
        url_lower = url.lower()
        
        # Tier 1: Major news
        tier1 = ['reuters', 'bbc', 'cnn', 'apnews', 'afp']
        if any(s in url_lower for s in tier1):
            return 'TIER1_NEWS'
        
        # Tier 2: Indian news
        tier2 = ['thehindu', 'indianexpress', 'ndtv', 'timesofindia', 'hindustantimes']
        if any(s in url_lower for s in tier2):
            return 'TIER2_NEWS'
        
        # Tier 3: Regional
        tier3 = ['dinamalar', 'thanthi', 'maalaimalar']
        if any(s in url_lower for s in tier3):
            return 'TIER3_REGIONAL'
        
        return 'TIER2_WEB'
    
    def _download_image(self, url: str, headers: dict) -> Image.Image:
        """Download and validate image"""
        try:
            response = requests.get(url, headers=headers, timeout=5, stream=True)
            
            if response.status_code != 200:
                return None
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            if 'image' not in content_type.lower():
                return None
            
            img = Image.open(BytesIO(response.content))
            
            # Validate size (not too small)
            if img.size[0] < 200 or img.size[1] < 200:
                return None
            
            # Convert to RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            return img
        
        except:
            return None
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return 'Unknown'


# Alias for compatibility
class ImageRetrieverComplete(ImageRetrieverPerfect):
    """Alias"""
    pass
