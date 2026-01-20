"""
Enhanced Dual Verification Module
Integrates ALL novel enhancements:
1. Temporal verification (EXIF + date extraction)
2. Multi-source evidence aggregation (news, fact-check, Wikipedia)
3. Attention-based fusion (lightweight, no training needed)
4. Semantic contradiction detection

This is the MAIN ENHANCEMENT over base DEETSA paper
"""

from PIL import Image
import numpy as np
from typing import List, Dict
import re

# Import our new modules
from temporal_verifier import TemporalVerifier
from evidence_aggregator import EvidenceAggregator
from multimodal_fusion import AttentionFusion

class EnhancedDualVerifier:
    """
    Enhanced Dual Verifier with Novel Contributions
    
    Enhancements over Base Paper (DEETSA):
    1. ✅ Temporal Verification - detects date/time mismatches
    2. ✅ Real-time Evidence Aggregation - no static KB needed
    3. ✅ Attention-based Fusion - lightweight alternative to gated networks
    4. ✅ Multi-source Evidence - news, fact-check, Wikipedia, web
    5. ✅ Explainable Results - clear reasoning for decisions
    """
    
    def __init__(self):
        """Initialize enhanced verifier with all modules"""
        print("Initializing Enhanced Dual Verifier...")
        
        # Initialize our novel modules
        self.temporal_verifier = TemporalVerifier()
        self.evidence_aggregator = EvidenceAggregator()
        self.attention_fusion = AttentionFusion()
        
        # Confidence thresholds
        self.high_confidence_threshold = 70
        self.medium_confidence_threshold = 50
        
        print("✓ Enhanced Dual Verifier initialized with ALL enhancements!")
    
    def verify_text_and_image(
        self, 
        text: str, 
        user_image: Image.Image,
        text_based_images: List[Dict],
        image_based_images: List[Dict],
        text_info: Dict = None
    ) -> Dict:
        """
        ENHANCED verification with temporal check and external evidence
        
        New Features:
        1. Temporal consistency verification
        2. Multi-source evidence aggregation
        3. Attention-based fusion
        4. Contradiction detection
        """
        try:
            print("\n" + "="*60)
            print("ENHANCED VERIFICATION PROCESS")
            print("="*60)
            
            # STEP 1: Basic text and image verification (existing)
            print("\n[1/5] Basic verification...")
            text_result = self._verify_text_with_images(text, text_based_images)
            image_result = self._verify_image_with_images(user_image, image_based_images)
            
            # STEP 2: NOVEL - Temporal Verification
            print("[2/5] Temporal verification (NEW)...")
            temporal_result = self.temporal_verifier.verify_temporal_consistency(
                text, 
                user_image
            )
            
            if temporal_result['has_mismatch']:
                print(f"  ⚠️ Temporal mismatch detected: {temporal_result['severity']}")
            else:
                print("  ✓ No temporal inconsistencies")
            
            # STEP 3: NOVEL - Multi-source Evidence Aggregation
            print("[3/5] Aggregating external evidence (NEW)...")
            keywords = text_info.get('keywords', []) if text_info else text.split()[:10]
            location = text_info.get('location') if text_info else None
            
            external_evidence = self.evidence_aggregator.aggregate_all_evidence(
                text,
                keywords,
                location
            )
            
            summary = external_evidence['summary']
            print(f"  ✓ Evidence aggregated: {summary['total_sources']} sources")
            print(f"  ✓ Evidence score: {summary['evidence_score']}/100")
            
            # STEP 4: NOVEL - Attention-based Fusion
            print("[4/5] Fusing evidence with attention mechanism (NEW)...")
            fused_result = self.attention_fusion.fuse_all_evidence(
                text_result,
                image_result,
                temporal_result,
                external_evidence
            )
            
            print(f"  ✓ Final authenticity score: {fused_result['authenticity_score']}/100")
            
            # STEP 5: Generate comprehensive result
            print("[5/5] Generating final verdict...")
            final_result = self._build_comprehensive_result(
                fused_result,
                text_result,
                image_result,
                temporal_result,
                external_evidence
            )
            
            print("="*60)
            print(f"VERDICT: {final_result['verdict']}")
            print(f"CONFIDENCE: {final_result['confidence']}%")
            print("="*60 + "\n")
            
            return final_result
        
        except Exception as e:
            print(f"Enhanced verification error: {e}")
            import traceback
            traceback.print_exc()
            return self._get_error_result()
    
    def verify_text_only(
        self, 
        text: str, 
        retrieved_images: List[Dict],
        text_info: Dict = None
    ) -> Dict:
        """
        ENHANCED text-only verification with external evidence
        """
        try:
            # Basic verification
            text_result = self._verify_text_with_images(text, retrieved_images)
            
            # External evidence
            keywords = text_info.get('keywords', []) if text_info else text.split()[:10]
            location = text_info.get('location') if text_info else None
            
            external_evidence = self.evidence_aggregator.aggregate_all_evidence(
                text,
                keywords,
                location
            )
            
            # Combine scores
            basic_score = text_result['confidence']
            evidence_score = external_evidence['summary']['evidence_score']
            
            # Weighted average (60% basic, 40% external)
            final_confidence = int(basic_score * 0.6 + evidence_score * 0.4)
            
            # Check fact-checks
            factchecks = external_evidence.get('factcheck', [])
            if factchecks:
                # If fact-check says false, override
                for fc in factchecks:
                    if fc.get('rating', '').lower() in ['false', 'fake', 'misleading']:
                        return {
                            'is_real': False,
                            'authenticity': 'FACT-CHECKED AS FALSE',
                            'confidence': 95,
                            'explanation': f"Fact-check by {fc.get('publisher')}: {fc.get('rating')}",
                            'evidence_count': len(retrieved_images),
                            'external_evidence': external_evidence
                        }
            
            return {
                'is_real': text_result['is_real'],
                'authenticity': text_result['authenticity'],
                'confidence': final_confidence,
                'explanation': text_result['explanation'] + f"\n\nExternal evidence: {external_evidence['summary']['verdict']}",
                'evidence_count': len(retrieved_images),
                'external_evidence': external_evidence
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
    
    def verify_image_only(
        self, 
        user_image: Image.Image, 
        retrieved_images: List[Dict]
    ) -> Dict:
        """
        ENHANCED image-only verification with temporal check
        """
        try:
            # Basic verification
            image_result = self._verify_image_with_images(user_image, retrieved_images)
            
            # Temporal check (just image metadata)
            try:
                image_date = self.temporal_verifier.extract_image_date(user_image)
                
                if image_date:
                    # Check if image is very old
                    from datetime import datetime
                    age_days = (datetime.now() - image_date).days
                    
                    if age_days > 365:
                        image_result['explanation'] += f"\n\n⚠️ Note: Image is {age_days} days old (taken {image_date.date()})"
            except:
                pass
            
            return {
                'is_real': image_result['is_real'],
                'authenticity': image_result['authenticity'],
                'confidence': image_result['confidence'],
                'explanation': image_result['explanation'],
                'similar_count': len(retrieved_images)
            }
        
        except Exception as e:
            print(f"Image verification error: {e}")
            return {
                'is_real': False,
                'authenticity': 'ERROR',
                'confidence': 0,
                'explanation': 'Verification failed',
                'similar_count': 0
            }
    
    # ============== EXISTING METHODS (kept for backward compatibility) ==============
    
    def _verify_text_with_images(self, text: str, images: List[Dict]) -> Dict:
        """Verify text description against retrieved images"""
        if not images or len(images) == 0:
            return {
                'is_real': False,
                'authenticity': 'LIKELY FAKE',
                'confidence': 30,
                'explanation': 'No supporting images found online',
                'evidence_score': 0
            }
        
        # Calculate evidence score based on number of images
        evidence_score = min(len(images) * 10, 100)
        
        # Check if images are from credible sources
        credible_sources = ['news', 'government', 'official', 'reuters', 'bbc', 'cnn']
        credible_count = sum(
            1 for img in images 
            if any(source in img.get('source', '').lower() for source in credible_sources)
        )
        
        credibility_boost = min(credible_count * 5, 20)
        
        # Final confidence
        confidence = min(evidence_score + credibility_boost, 95)
        
        if confidence >= self.high_confidence_threshold:
            is_real = True
            authenticity = 'REAL'
            explanation = f'Found {len(images)} supporting images online. High confidence this incident is authentic.'
        elif confidence >= self.medium_confidence_threshold:
            is_real = True
            authenticity = 'LIKELY REAL'
            explanation = f'Found {len(images)} images online. Moderate confidence this incident occurred.'
        else:
            is_real = False
            authenticity = 'UNCERTAIN'
            explanation = f'Limited evidence found ({len(images)} images). Cannot confirm authenticity.'
        
        return {
            'is_real': is_real,
            'authenticity': authenticity,
            'confidence': confidence,
            'explanation': explanation,
            'evidence_score': evidence_score
        }
    
    def _verify_image_with_images(self, user_image: Image.Image, similar_images: List[Dict]) -> Dict:
        """Verify user image against similar images found online"""
        if not similar_images or len(similar_images) == 0:
            return {
                'is_real': False,
                'authenticity': 'LIKELY FAKE',
                'confidence': 25,
                'explanation': 'No similar images found online. Image may be fabricated.',
                'similarity_score': 0
            }
        
        # Calculate similarity score
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
        confidence = min(int(avg_similarity * 100) + len(similar_images) * 5, 95)
        
        if confidence >= self.high_confidence_threshold:
            is_real = True
            authenticity = 'REAL'
            explanation = f'Found {len(similar_images)} similar images online with {avg_similarity:.1%} similarity. Image appears authentic.'
        elif confidence >= self.medium_confidence_threshold:
            is_real = True
            authenticity = 'LIKELY REAL'
            explanation = f'Found {len(similar_images)} similar images. Moderate confidence image is real.'
        else:
            is_real = False
            authenticity = 'UNCERTAIN'
            explanation = f'Limited similar images found. Cannot confirm image authenticity.'
        
        return {
            'is_real': is_real,
            'authenticity': authenticity,
            'confidence': confidence,
            'explanation': explanation,
            'similarity_score': avg_similarity
        }
    
    def _calculate_image_similarity(self, img1: Image.Image, img2: Image.Image) -> float:
        """Calculate basic similarity between two images"""
        try:
            # Resize to same size for comparison
            size = (100, 100)
            img1_resized = img1.resize(size)
            img2_resized = img2.resize(size)
            
            # Convert to numpy arrays
            arr1 = np.array(img1_resized).flatten()
            arr2 = np.array(img2_resized).flatten()
            
            # Calculate correlation
            correlation = np.corrcoef(arr1, arr2)[0, 1]
            
            # Convert to similarity (0 to 1)
            similarity = (correlation + 1) / 2
            
            return max(0, min(1, similarity))
        
        except Exception as e:
            return 0.5  # Default middle value
    
    def _build_comprehensive_result(
        self,
        fused_result: Dict,
        text_result: Dict,
        image_result: Dict,
        temporal_result: Dict,
        external_evidence: Dict
    ) -> Dict:
        """
        Build comprehensive result with all information
        """
        try:
            # Extract main verdict components
            verdict = fused_result['verdict']
            main_message = fused_result['main_message']
            confidence = fused_result['confidence']
            
            # Build detailed explanation
            explanation_parts = []
            
            # Overall assessment
            explanation_parts.append(fused_result['explanation'])
            
            # Temporal information
            if temporal_result.get('has_mismatch'):
                temporal_summary = self.temporal_verifier.get_temporal_summary(temporal_result)
                explanation_parts.append(f"\n{temporal_summary}")
            
            # External evidence summary
            ext_summary = external_evidence.get('summary', {})
            if ext_summary.get('key_findings'):
                explanation_parts.append("\n📰 External Evidence:")
                for finding in ext_summary['key_findings'][:3]:
                    explanation_parts.append(f"  • {finding}")
            
            explanation = "\n".join(explanation_parts)
            
            return {
                'verdict': verdict,
                'main_message': main_message,
                'confidence': confidence,
                'explanation': explanation,
                'text_verification': text_result,
                'image_verification': image_result,
                'temporal_verification': temporal_result,
                'external_evidence': external_evidence,
                'attention_weights': fused_result.get('attention_weights', {}),
                'contradictions': fused_result.get('contradictions', []),
                'authenticity_score': fused_result.get('authenticity_score', 0)
            }
        
        except Exception as e:
            print(f"Result building error: {e}")
            return self._get_error_result()
    
    def _get_error_result(self) -> Dict:
        """Return error result"""
        return {
            'verdict': 'ERROR',
            'main_message': '❌ Verification Error',
            'confidence': 0,
            'explanation': 'An error occurred during verification. Please try again.',
            'text_verification': {'is_real': False, 'authenticity': 'ERROR', 'confidence': 0, 'explanation': 'Error'},
            'image_verification': {'is_real': False, 'authenticity': 'ERROR', 'confidence': 0, 'explanation': 'Error'},
            'temporal_verification': {'has_mismatch': False, 'confidence': 0},
            'external_evidence': {},
            'authenticity_score': 0
        }
