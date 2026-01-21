"""
WORKING Image Retriever with API Support
Uses APIs instead of web scraping for Streamlit Cloud
"""

import requests
from PIL import Image
from io import BytesIO
import os
from typing import List, Dict

class ImageRetrieverAPI:
    """
    Image Retriever using APIs (works on Streamlit Cloud)
    
    Uses:
    1. Unsplash API (free, no auth for basic)
    2. Pexels API (free with key)
    3. Pixabay API (free with key)
    4. Fallback to placeholder images
    """
    
    def __init__(self):
        """Initialize with API keys from environment"""
        # Get API keys from Streamlit secrets
        self.pexels_key = os.getenv('PEXELS_API_KEY', '')
        self.pixabay_key = os.getenv('PIXABAY_API_KEY', '')
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print("✓ API-based Image Retriever initialized")
    
    def retrieve_images_for_text(
        self,
        query: str,
        max_images: int = 10,
        location: str = None,
        event_type: str = None,
        keywords: List[str] = None
    ) -> List[Dict]:
        """
        Retrieve images using APIs (works on Streamlit Cloud)
        """
        try:
            print(f"\n📸 Retrieving images via API: '{query}'")
            
            all_images = []
            
            # Method 1: Pexels API (if key available)
            if self.pexels_key:
                pexels_images = self._search_pexels(query, max_images // 2)
                all_images.extend(pexels_images)
                print(f"  ✓ Pexels: {len(pexels_images)} images")
            
            # Method 2: Pixabay API (if key available)
            if self.pixabay_key:
                pixabay_images = self._search_pixabay(query, max_images // 2)
                all_images.extend(pixabay_images)
                print(f"  ✓ Pixabay: {len(pixabay_images)} images")
            
            # Method 3: Unsplash (no key needed for basic)
            unsplash_images = self._search_unsplash(query, max_images // 2)
            all_images.extend(unsplash_images)
            print(f"  ✓ Unsplash: {len(unsplash_images)} images")
            
            # If no images found, create placeholders
            if not all_images:
                print("  ⚠️ No API images found, creating placeholders...")
                all_images = self._create_placeholder_images(query, max_images)
            
            print(f"  ✅ Total: {len(all_images)} images")
            
            return all_images[:max_images]
        
        except Exception as e:
            print(f"  ❌ Error: {e}")
            # Return placeholder images on error
            return self._create_placeholder_images(query, max_images)
    
    def reverse_image_search(self, image: Image.Image, max_results: int = 20) -> Dict:
        """
        Placeholder for reverse image search
        (Requires paid APIs like Google Cloud Vision)
        """
        return {
            'original_source': None,
            'all_occurrences': [],
            'first_published': None,
            'contexts': [],
            'is_original': True,
            'reuse_detected': False,
            'note': 'Reverse image search requires API keys'
        }
    
    def _search_pexels(self, query: str, max_images: int) -> List[Dict]:
        """Search Pexels API"""
        try:
            url = "https://api.pexels.com/v1/search"
            headers = {
                'Authorization': self.pexels_key
            }
            params = {
                'query': query,
                'per_page': max_images
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            images = []
            
            for photo in data.get('photos', [])[:max_images]:
                img_url = photo.get('src', {}).get('medium', '')
                
                if img_url:
                    img_data = self._download_image(img_url)
                    
                    if img_data:
                        images.append({
                            'image': img_data,
                            'source': 'Pexels',
                            'name': photo.get('alt', query),
                            'url': img_url,
                            'credibility': 'TIER2_STOCK',
                            'type': 'stock',
                            'platform': 'Pexels'
                        })
            
            return images
        
        except Exception as e:
            print(f"    Pexels error: {e}")
            return []
    
    def _search_pixabay(self, query: str, max_images: int) -> List[Dict]:
        """Search Pixabay API"""
        try:
            url = "https://pixabay.com/api/"
            params = {
                'key': self.pixabay_key,
                'q': query,
                'per_page': max_images,
                'image_type': 'photo'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            images = []
            
            for hit in data.get('hits', [])[:max_images]:
                img_url = hit.get('webformatURL', '')
                
                if img_url:
                    img_data = self._download_image(img_url)
                    
                    if img_data:
                        images.append({
                            'image': img_data,
                            'source': 'Pixabay',
                            'name': hit.get('tags', query),
                            'url': img_url,
                            'credibility': 'TIER2_STOCK',
                            'type': 'stock',
                            'platform': 'Pixabay'
                        })
            
            return images
        
        except Exception as e:
            print(f"    Pixabay error: {e}")
            return []
    
    def _search_unsplash(self, query: str, max_images: int) -> List[Dict]:
        """Search Unsplash (no key needed for basic)"""
        try:
            # Note: This uses Unsplash Source API (deprecated but still works)
            # For production, get Unsplash API key
            
            images = []
            
            # Create random seed from query
            import hashlib
            seed = int(hashlib.md5(query.encode()).hexdigest()[:8], 16)
            
            for i in range(min(max_images, 3)):  # Limit to 3 to avoid rate limits
                # Unsplash Source URL
                img_url = f"https://source.unsplash.com/800x600/?{query}&sig={seed + i}"
                
                img_data = self._download_image(img_url)
                
                if img_data:
                    images.append({
                        'image': img_data,
                        'source': 'Unsplash',
                        'name': query,
                        'url': img_url,
                        'credibility': 'TIER2_STOCK',
                        'type': 'stock',
                        'platform': 'Unsplash'
                    })
            
            return images
        
        except Exception as e:
            print(f"    Unsplash error: {e}")
            return []
    
    def _create_placeholder_images(self, query: str, count: int) -> List[Dict]:
        """
        Create placeholder images when no real images available
        """
        images = []
        
        colors = [
            (100, 150, 200),  # Blue
            (150, 100, 200),  # Purple
            (200, 150, 100),  # Orange
            (100, 200, 150),  # Green
            (200, 100, 150),  # Pink
        ]
        
        for i in range(min(count, 5)):
            # Create colored placeholder
            img = Image.new('RGB', (400, 300), color=colors[i % len(colors)])
            
            images.append({
                'image': img,
                'source': 'Placeholder',
                'name': f'{query} - Sample {i+1}',
                'url': 'N/A',
                'credibility': 'PLACEHOLDER',
                'type': 'placeholder',
                'platform': 'System'
            })
        
        return images
    
    def _download_image(self, url: str) -> Image.Image:
        """Download and validate image"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return None
            
            img = Image.open(BytesIO(response.content))
            
            if img.size[0] < 50 or img.size[1] < 50:
                return None
            
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            return img
        
        except Exception as e:
            return None


# For backward compatibility
class ImageRetrieverComplete(ImageRetrieverAPI):
    """Alias for compatibility"""
    pass
