"""
ENHANCED Dual Verifier
Better analysis and matching between text and images
"""

from PIL import Image
import numpy as np
from typing import List, Dict
import re
from datetime import datetime

class DualVerifierEnhanced:
    """
    Enhanced Dual Verifier with:
    1. Better text-image matching
    2. Keyword extraction and matching
    3. Context analysis
    4. Proper confidence scoring
    """
    
    def __init__(self):
        """Initialize verifier"""
        print("✓ Enhanced Dual Verifier initialized")
        
        # Confidence thresholds
        self.high_confidence_threshold = 70
        self.medium_confidence_threshold = 50
        
        # Common event keywords
        self.event_keywords = {
            'fire': ['fire', 'burning', 'smoke', 'flames', 'blaze'],
            'flood': ['flood', 'water', 'submerged', 'rain', 'deluge'],
            'accident': ['accident', 'crash', 'collision'],
            'disaster': ['disaster', 'emergency', 'crisis'],
            'protest': ['protest', 'rally', 'demonstration'],
            'violence': ['violence', 'attack', 'shooting']
        }
    
    def verify_text_and_image(
        self, 
        text: str, 
        user_image: Image.Image,
        text_based_images: List[Dict],
        image_based_images: List[Dict]
    ) -> Dict:
        """
        Enhanced verification with better analysis
        """
        try:
            # Extract keywords from text
            text_keywords = self._extract_keywords(text)
            
            # Verify text with BETTER analysis
            text_result = self._verify_text_with_images_enhanced(
                text, 
                text_keywords,
                text_based_images
            )
            
            # Verify image
            image_result = self._verify_image_with_images(
                user_image, 
                image_based_images
            )
            
            # Check consistency with keyword matching
            consistency_score = self._check_consistency_enhanced(
                text,
                text_keywords,
                text_result,
                image_result,
                text_based_images
            )
            
            # Determine final verdict
            verdict = self._determine_verdict_enhanced(
                text_result,
                image_result,
                consistency_score,
                len(text_based_images),
                len(image_based_images)
            )
            
            return {
                'verdict': verdict['type'],
                'main_message': verdict['message'],
                'confidence': verdict['confidence'],
                'explanation': verdict['explanation'],
                'text_verification': text_result,
                'image_verification': image_result,
                'consistency_score': consistency_score,
                'keywords_found': text_keywords
            }
        
        except Exception as e:
            print(f"Verification error: {e}")
            return self._get_error_result()
    
    def verify_text_only(self, text: str, retrieved_images: List[Dict]) -> Dict:
        """Enhanced text-only verification"""
        try:
            text_keywords = self._extract_keywords(text)
            result = self._verify_text_with_images_enhanced(text, text_keywords, retrieved_images)
            
            return {
                'is_real': result['is_real'],
                'authenticity': result['authenticity'],
                'confidence': result['confidence'],
                'explanation': result['explanation'],
                'evidence_count': len(retrieved_images),
                'keywords_matched': result.get('keywords_matched', [])
            }
        
        except Exception as e:
            print(f"Text verification error: {e}")
            return {
                'is_real': False,
                'authenticity': 'ERROR',
                'confidence': 0,
                'explanation': 'Verification failed',
                'evidence_count': 0
            }
    
    def verify_image_only(self, user_image: Image.Image, retrieved_images: List[Dict]) -> Dict:
        """Image-only verification"""
        try:
            result = self._verify_image_with_images(user_image, retrieved_images)
            
            return {
                'is_real': result['is_real'],
                'authenticity': result['authenticity'],
                'confidence': result['confidence'],
                'explanation': result['explanation'],
                'similar_count': len(retrieved_images)
            }
        
        except Exception as e:
            return {
                'is_real': False,
                'authenticity': 'ERROR',
                'confidence': 0,
                'explanation': 'Verification failed',
                'similar_count': 0
            }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract important keywords from text
        """
        text_lower = text.lower()
        keywords = []
        
        # Extract event types
        for event_type, words in self.event_keywords.items():
            if any(word in text_lower for word in words):
                keywords.append(event_type)
                keywords.extend([w for w in words if w in text_lower])
        
        # Extract locations (capitalized words)
        words = text.split()
        for word in words:
            clean = re.sub(r'[^\w]', '', word)
            if clean and len(clean) > 2 and clean[0].isupper() and clean not in keywords:
                keywords.append(clean.lower())
        
        # Extract dates
        date_patterns = [
            r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b',
            r'\b(20\d{2})\b',  # Years
            r'\b(today|yesterday|recent)\b'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text_lower)
            keywords.extend(matches)
        
        return list(set(keywords))  # Remove duplicates
    
    def _verify_text_with_images_enhanced(
        self, 
        text: str, 
        keywords: List[str],
        images: List[Dict]
    ) -> Dict:
        """
        ENHANCED text verification with keyword matching
        """
        if not images or len(images) == 0:
            return {
                'is_real': False,
                'authenticity': 'INSUFFICIENT EVIDENCE',
                'confidence': 20,
                'explanation': 'No supporting images found online. Cannot verify.',
                'evidence_score': 0,
                'keywords_matched': []
            }
        
        # Base score from image count
        image_count_score = min(len(images) * 8, 60)
        
        # Keyword matching score
        keywords_matched = []
        keyword_score = 0
        
        for img in images:
            img_source = img.get('source', '').lower()
            img_name = img.get('name', '').lower()
            img_text = f"{img_source} {img_name}"
            
            for keyword in keywords:
                if keyword in img_text:
                    keywords_matched.append(keyword)
                    keyword_score += 5
        
        keywords_matched = list(set(keywords_matched))
        keyword_match_ratio = len(keywords_matched) / max(len(keywords), 1)
        
        # Credibility boost
        credible_sources = ['news', 'reuters', 'bbc', 'cnn', 'hindu', 'ndtv']
        credible_count = sum(
            1 for img in images 
            if any(source in img.get('source', '').lower() for source in credible_sources)
        )
        credibility_score = min(credible_count * 8, 30)
        
        # Calculate final confidence
        confidence = min(
            image_count_score + min(keyword_score, 30) + credibility_score,
            95
        )
        
        # Determine authenticity
        if confidence >= 70:
            is_real = True
            authenticity = 'REAL'
            explanation = (
                f'Found {len(images)} supporting images online. '
                f'{len(keywords_matched)} keywords matched in sources. '
                f'High confidence this incident is authentic.'
            )
        elif confidence >= 50:
            is_real = True
            authenticity = 'LIKELY REAL'
            explanation = (
                f'Found {len(images)} images online. '
                f'{len(keywords_matched)}/{len(keywords)} keywords matched. '
                f'Moderate confidence this incident occurred.'
            )
        else:
            is_real = False
            authenticity = 'UNCERTAIN'
            explanation = (
                f'Limited evidence: {len(images)} images found. '
                f'Only {len(keywords_matched)} keywords matched. '
                f'Cannot confirm authenticity with high confidence.'
            )
        
        return {
            'is_real': is_real,
            'authenticity': authenticity,
            'confidence': confidence,
            'explanation': explanation,
            'evidence_score': image_count_score,
            'keywords_matched': keywords_matched,
            'keyword_match_ratio': keyword_match_ratio
        }
    
    def _verify_image_with_images(self, user_image: Image.Image, similar_images: List[Dict]) -> Dict:
        """Verify user image against similar images"""
        if not similar_images or len(similar_images) == 0:
            return {
                'is_real': False,
                'authenticity': 'INSUFFICIENT EVIDENCE',
                'confidence': 20,
                'explanation': 'No similar images found online. Cannot verify.',
                'similarity_score': 0
            }
        
        # Calculate similarity scores
        similarity_scores = []
        for img_data in similar_images:
            try:
                similarity = self._calculate_image_similarity(
                    user_image, 
                    img_data['image']
                )
                similarity_scores.append(similarity)
            except:
                continue
        
        if not similarity_scores:
            avg_similarity = 0
        else:
            avg_similarity = sum(similarity_scores) / len(similarity_scores)
        
        # Confidence based on similarity and count
        confidence = min(
            int(avg_similarity * 60) + len(similar_images) * 5 + 20,
            95
        )
        
        if confidence >= 70:
            is_real = True
            authenticity = 'REAL'
            explanation = f'Found {len(similar_images)} similar images online. Image appears authentic.'
        elif confidence >= 50:
            is_real = True
            authenticity = 'LIKELY REAL'
            explanation = f'Found {len(similar_images)} similar images. Moderate confidence.'
        else:
            is_real = False
            authenticity = 'UNCERTAIN'
            explanation = f'Limited similar images found. Cannot confirm authenticity.'
        
        return {
            'is_real': is_real,
            'authenticity': authenticity,
            'confidence': confidence,
            'explanation': explanation,
            'similarity_score': avg_similarity
        }
    
    def _calculate_image_similarity(self, img1: Image.Image, img2: Image.Image) -> float:
        """Calculate similarity between two images"""
        try:
            size = (100, 100)
            img1_resized = img1.resize(size)
            img2_resized = img2.resize(size)
            
            arr1 = np.array(img1_resized).flatten()
            arr2 = np.array(img2_resized).flatten()
            
            correlation = np.corrcoef(arr1, arr2)[0, 1]
            similarity = (correlation + 1) / 2
            
            return max(0, min(1, similarity))
        
        except:
            return 0.5
    
    def _check_consistency_enhanced(
        self,
        text: str,
        keywords: List[str],
        text_result: Dict,
        image_result: Dict,
        text_images: List[Dict]
    ) -> float:
        """
        Enhanced consistency check with keyword matching
        """
        text_real = text_result['is_real']
        image_real = image_result['is_real']
        
        # Base consistency
        if text_real == image_real:
            consistency = 0.7
        else:
            consistency = 0.3
        
        # Boost if keywords matched
        keyword_ratio = text_result.get('keyword_match_ratio', 0)
        consistency += keyword_ratio * 0.2
        
        # Boost if multiple images found
        if len(text_images) >= 5:
            consistency += 0.1
        
        return min(consistency, 1.0)
    
    def _determine_verdict_enhanced(
        self,
        text_result: Dict,
        image_result: Dict,
        consistency: float,
        text_image_count: int,
        image_image_count: int
    ) -> Dict:
        """
        Enhanced verdict determination
        """
        text_real = text_result['is_real']
        image_real = image_result['is_real']
        
        text_conf = text_result['confidence']
        image_conf = image_result['confidence']
        
        avg_confidence = int((text_conf + image_conf) / 2)
        
        # If both found evidence
        if text_image_count >= 3 and text_real and image_real and consistency > 0.6:
            return {
                'type': 'MATCH_AND_REAL',
                'message': '✅ TEXT and IMAGE VERIFIED - Both Real',
                'confidence': avg_confidence,
                'explanation': (
                    f'Both text and image verified against online sources.\n\n'
                    f'Text: {text_result["authenticity"]} ({text_conf}% confidence)\n'
                    f'  - Found {text_image_count} supporting images\n'
                    f'  - Keywords matched: {len(text_result.get("keywords_matched", []))}\n\n'
                    f'Image: {image_result["authenticity"]} ({image_conf}% confidence)\n'
                    f'  - Found {image_image_count} similar images\n\n'
                    f'Incident appears authentic.'
                )
            }
        
        elif text_real and image_real:
            return {
                'type': 'LIKELY_REAL',
                'message': '✅ LIKELY REAL - Evidence Found',
                'confidence': avg_confidence,
                'explanation': (
                    f'Evidence supports authenticity.\n\n'
                    f'Text: {text_result["authenticity"]} ({text_conf}%)\n'
                    f'Image: {image_result["authenticity"]} ({image_conf}%)\n\n'
                    f'Incident likely occurred.'
                )
            }
        
        elif not text_real and not image_real:
            return {
                'type': 'INSUFFICIENT_EVIDENCE',
                'message': '⚠️ INSUFFICIENT EVIDENCE',
                'confidence': avg_confidence,
                'explanation': (
                    f'Limited evidence found to verify incident.\n\n'
                    f'Text: {text_result["explanation"]}\n\n'
                    f'Image: {image_result["explanation"]}\n\n'
                    f'Note: Lack of online evidence does not necessarily mean fake - '
                    f'incident may be recent, local, or under-reported.'
                )
            }
        
        else:
            return {
                'type': 'PARTIAL_VERIFICATION',
                'message': '⚠️ PARTIAL VERIFICATION',
                'confidence': avg_confidence,
                'explanation': (
                    f'Mixed verification results.\n\n'
                    f'Text: {text_result["authenticity"]} ({text_conf}%)\n'
                    f'Image: {image_result["authenticity"]} ({image_conf}%)\n\n'
                    f'Further investigation recommended.'
                )
            }
    
    def _get_error_result(self) -> Dict:
        """Return error result"""
        return {
            'verdict': 'ERROR',
            'main_message': '❌ Verification Error',
            'confidence': 0,
            'explanation': 'An error occurred during verification.',
            'text_verification': {'is_real': False, 'authenticity': 'ERROR', 'confidence': 0},
            'image_verification': {'is_real': False, 'authenticity': 'ERROR', 'confidence': 0},
            'consistency_score': 0
        }


# Alias for compatibility
class DualVerifier(DualVerifierEnhanced):
    """Alias for backward compatibility"""
    pass
