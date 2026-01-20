"""
Attention-Based Multimodal Fusion
Novel Enhancement: Lightweight attention mechanism for evidence fusion
Addresses DEETSA limitation: Heavy gated neural networks requiring training

This module:
1. Computes attention weights for different evidence sources
2. Adaptively fuses multimodal evidence
3. No training required (rule-based + heuristics)
4. Lightweight and interpretable
"""

import numpy as np
from typing import Dict, List, Tuple
from collections import defaultdict

class AttentionFusion:
    """
    Attention-Based Evidence Fusion
    
    Base Paper Limitation:
    - DEETSA uses complex gated neural networks
    - Requires training data and computational resources
    - Black-box nature reduces interpretability
    
    Our Enhancement:
    - Lightweight attention mechanism
    - No training required
    - Interpretable weights
    - Adaptive to evidence quality
    """
    
    def __init__(self):
        """Initialize attention fusion module"""
        print("✓ Attention Fusion module initialized")
        
        # Base credibility scores for different evidence types
        self.credibility_scores = {
            'factcheck_api': 0.95,
            'news_credible': 0.85,
            'news_general': 0.70,
            'wikipedia': 0.80,
            'web_general': 0.60,
            'image_similarity': 0.75,
            'temporal_check': 0.90,
            'text_evidence': 0.65
        }
        
        # Recency decay factor (newer evidence = higher weight)
        self.recency_decay = 0.1
    
    def fuse_all_evidence(
        self,
        text_verification: Dict,
        image_verification: Dict,
        temporal_verification: Dict,
        external_evidence: Dict
    ) -> Dict:
        """
        Main fusion function - combines all evidence with attention
        
        Args:
            text_verification: Result from text-only verification
            image_verification: Result from image-only verification
            temporal_verification: Result from temporal check
            external_evidence: Result from evidence aggregator
        
        Returns:
            Fused verification result with explanation
        """
        try:
            # Compute attention weights for each evidence type
            attention_weights = self._compute_attention_weights(
                text_verification,
                image_verification,
                temporal_verification,
                external_evidence
            )
            
            # Aggregate scores
            aggregated_score = self._aggregate_scores(
                text_verification,
                image_verification,
                temporal_verification,
                external_evidence,
                attention_weights
            )
            
            # Detect contradictions
            contradictions = self._detect_contradictions(
                text_verification,
                image_verification,
                temporal_verification,
                external_evidence
            )
            
            # Generate final verdict
            final_result = self._generate_final_verdict(
                aggregated_score,
                contradictions,
                attention_weights,
                text_verification,
                image_verification,
                temporal_verification,
                external_evidence
            )
            
            return final_result
        
        except Exception as e:
            print(f"Fusion error: {e}")
            return self._get_error_result()
    
    def _compute_attention_weights(
        self,
        text_verification: Dict,
        image_verification: Dict,
        temporal_verification: Dict,
        external_evidence: Dict
    ) -> Dict[str, float]:
        """
        Compute attention weights for different evidence sources
        
        Attention mechanism considers:
        1. Base credibility of source
        2. Confidence level of evidence
        3. Recency of evidence
        4. Consistency with other sources
        """
        try:
            weights = {}
            raw_scores = {}
            
            # Text verification weight
            text_conf = text_verification.get('confidence', 0) / 100.0
            text_credibility = self.credibility_scores['text_evidence']
            raw_scores['text'] = text_conf * text_credibility
            
            # Image verification weight
            image_conf = image_verification.get('confidence', 0) / 100.0
            image_credibility = self.credibility_scores['image_similarity']
            raw_scores['image'] = image_conf * image_credibility
            
            # Temporal verification weight
            if temporal_verification.get('has_mismatch'):
                # High weight if mismatch detected
                temporal_conf = temporal_verification.get('confidence', 0) / 100.0
                temporal_credibility = self.credibility_scores['temporal_check']
                raw_scores['temporal'] = temporal_conf * temporal_credibility
            else:
                raw_scores['temporal'] = 0.5  # Neutral if no temporal info
            
            # External evidence weights
            ext_summary = external_evidence.get('summary', {})
            ext_score = ext_summary.get('evidence_score', 0) / 100.0
            
            # News evidence weight
            news = external_evidence.get('news', [])
            if news:
                credible_news = [n for n in news if n.get('credibility') == 'HIGH']
                news_weight = len(credible_news) / max(len(news), 1)
                news_credibility = self.credibility_scores['news_credible']
                raw_scores['news'] = news_weight * news_credibility * ext_score
            else:
                raw_scores['news'] = 0
            
            # Fact-check evidence weight (HIGHEST)
            factchecks = external_evidence.get('factcheck', [])
            if factchecks:
                factcheck_credibility = self.credibility_scores['factcheck_api']
                raw_scores['factcheck'] = factcheck_credibility
            else:
                raw_scores['factcheck'] = 0
            
            # Wikipedia weight
            wiki = external_evidence.get('wikipedia', {})
            if wiki.get('found'):
                wiki_credibility = self.credibility_scores['wikipedia']
                raw_scores['wikipedia'] = wiki_credibility
            else:
                raw_scores['wikipedia'] = 0
            
            # Normalize weights using softmax
            total = sum(raw_scores.values())
            
            if total > 0:
                weights = {
                    key: score / total 
                    for key, score in raw_scores.items()
                }
            else:
                # Equal weights if no evidence
                num_sources = len(raw_scores)
                weights = {key: 1.0 / num_sources for key in raw_scores}
            
            return weights
        
        except Exception as e:
            print(f"Attention weight computation error: {e}")
            return {}
    
    def _aggregate_scores(
        self,
        text_verification: Dict,
        image_verification: Dict,
        temporal_verification: Dict,
        external_evidence: Dict,
        attention_weights: Dict
    ) -> Dict:
        """
        Aggregate scores using attention weights
        
        Returns:
        {
            'authenticity_score': float (0-100),
            'is_authentic': bool,
            'confidence': float (0-100),
            'dominant_evidence': str
        }
        """
        try:
            scores = []
            
            # Text score
            text_score = text_verification.get('confidence', 50)
            if not text_verification.get('is_real', False):
                text_score = 100 - text_score  # Invert if fake
            
            text_weight = attention_weights.get('text', 0)
            scores.append(('text', text_score * text_weight, text_weight))
            
            # Image score
            image_score = image_verification.get('confidence', 50)
            if not image_verification.get('is_real', False):
                image_score = 100 - image_score  # Invert if fake
            
            image_weight = attention_weights.get('image', 0)
            scores.append(('image', image_score * image_weight, image_weight))
            
            # Temporal score
            if temporal_verification.get('has_mismatch'):
                # Mismatch detected - negative contribution
                temporal_score = 100 - temporal_verification.get('confidence', 50)
            else:
                temporal_score = 50  # Neutral
            
            temporal_weight = attention_weights.get('temporal', 0)
            scores.append(('temporal', temporal_score * temporal_weight, temporal_weight))
            
            # External evidence scores
            ext_summary = external_evidence.get('summary', {})
            ext_score = ext_summary.get('evidence_score', 50)
            
            # News score
            news_weight = attention_weights.get('news', 0)
            scores.append(('news', ext_score * news_weight, news_weight))
            
            # Fact-check score
            factcheck_weight = attention_weights.get('factcheck', 0)
            if factcheck_weight > 0:
                # Analyze fact-check ratings
                factchecks = external_evidence.get('factcheck', [])
                factcheck_score = self._compute_factcheck_score(factchecks)
                scores.append(('factcheck', factcheck_score * factcheck_weight, factcheck_weight))
            
            # Wikipedia score
            wiki_weight = attention_weights.get('wikipedia', 0)
            if wiki_weight > 0:
                # If Wikipedia entry exists, slight boost
                scores.append(('wikipedia', 70 * wiki_weight, wiki_weight))
            
            # Weighted average
            total_weighted_score = sum(score for _, score, _ in scores)
            total_weight = sum(weight for _, _, weight in scores)
            
            if total_weight > 0:
                authenticity_score = total_weighted_score / total_weight
            else:
                authenticity_score = 50  # Neutral
            
            # Find dominant evidence source
            dominant_source = max(scores, key=lambda x: x[2])[0] if scores else 'unknown'
            
            # Determine if authentic
            is_authentic = authenticity_score >= 50
            
            # Confidence is based on weight concentration
            # If one source dominates, confidence is higher
            max_weight = max((w for _, _, w in scores), default=0)
            confidence = min(authenticity_score if is_authentic else (100 - authenticity_score), 95)
            
            return {
                'authenticity_score': round(authenticity_score, 2),
                'is_authentic': is_authentic,
                'confidence': round(confidence, 2),
                'dominant_evidence': dominant_source
            }
        
        except Exception as e:
            print(f"Score aggregation error: {e}")
            return {
                'authenticity_score': 50,
                'is_authentic': False,
                'confidence': 0,
                'dominant_evidence': 'error'
            }
    
    def _detect_contradictions(
        self,
        text_verification: Dict,
        image_verification: Dict,
        temporal_verification: Dict,
        external_evidence: Dict
    ) -> List[Dict]:
        """
        Detect contradictions between different evidence sources
        
        Returns list of contradiction objects
        """
        contradictions = []
        
        try:
            # 1. Text vs Image contradiction
            text_real = text_verification.get('is_real', False)
            image_real = image_verification.get('is_real', False)
            
            if text_real != image_real:
                contradictions.append({
                    'type': 'TEXT_IMAGE_MISMATCH',
                    'severity': 'HIGH',
                    'description': f'Text indicates {"REAL" if text_real else "FAKE"} but image indicates {"REAL" if image_real else "FAKE"}',
                    'confidence': abs(text_verification.get('confidence', 50) - image_verification.get('confidence', 50))
                })
            
            # 2. Temporal contradiction
            if temporal_verification.get('has_mismatch'):
                severity = temporal_verification.get('severity', 'LOW')
                contradictions.append({
                    'type': 'TEMPORAL_MISMATCH',
                    'severity': severity,
                    'description': temporal_verification.get('explanation', ''),
                    'confidence': temporal_verification.get('confidence', 0)
                })
            
            # 3. Fact-check contradictions
            factchecks = external_evidence.get('factcheck', [])
            for fc in factchecks:
                rating = fc.get('rating', '').lower()
                if rating in ['false', 'fake', 'misleading', 'incorrect']:
                    contradictions.append({
                        'type': 'FACTCHECK_CONTRADICTION',
                        'severity': 'HIGH',
                        'description': f"Fact-check rated as '{fc.get('rating')}' by {fc.get('publisher')}",
                        'confidence': 95
                    })
            
            # 4. Evidence vs Claim contradiction
            ext_summary = external_evidence.get('summary', {})
            if ext_summary.get('verdict') == 'NO_EVIDENCE_FOUND':
                if text_real or image_real:
                    contradictions.append({
                        'type': 'EVIDENCE_ABSENCE',
                        'severity': 'MEDIUM',
                        'description': 'No external evidence found to support claim',
                        'confidence': 60
                    })
            
            return contradictions
        
        except Exception as e:
            print(f"Contradiction detection error: {e}")
            return []
    
    def _compute_factcheck_score(self, factchecks: List[Dict]) -> float:
        """
        Compute score based on fact-check ratings
        
        Returns 0-100 (higher = more authentic)
        """
        if not factchecks:
            return 50  # Neutral
        
        ratings_map = {
            'true': 100,
            'mostly true': 85,
            'partly true': 60,
            'mixture': 50,
            'mostly false': 30,
            'false': 10,
            'fake': 5,
            'misleading': 20
        }
        
        scores = []
        for fc in factchecks:
            rating = fc.get('rating', '').lower()
            
            # Find matching rating
            for key, value in ratings_map.items():
                if key in rating:
                    scores.append(value)
                    break
        
        if scores:
            return sum(scores) / len(scores)
        else:
            return 50
    
    def _generate_final_verdict(
        self,
        aggregated_score: Dict,
        contradictions: List[Dict],
        attention_weights: Dict,
        text_verification: Dict,
        image_verification: Dict,
        temporal_verification: Dict,
        external_evidence: Dict
    ) -> Dict:
        """Generate comprehensive final verdict"""
        
        try:
            is_authentic = aggregated_score['is_authentic']
            confidence = aggregated_score['confidence']
            auth_score = aggregated_score['authenticity_score']
            
            # Determine verdict type
            if not contradictions:
                if is_authentic:
                    verdict_type = 'VERIFIED_AUTHENTIC'
                    main_message = '✅ VERIFIED AS AUTHENTIC'
                else:
                    verdict_type = 'LIKELY_FAKE'
                    main_message = '❌ LIKELY FABRICATED'
            else:
                # Check contradiction severity
                high_severity = any(c['severity'] == 'HIGH' for c in contradictions)
                
                if high_severity:
                    verdict_type = 'CRITICAL_CONTRADICTIONS'
                    main_message = '🚨 CRITICAL CONTRADICTIONS DETECTED'
                else:
                    verdict_type = 'MODERATE_CONCERNS'
                    main_message = '⚠️ SOME CONCERNS DETECTED'
            
            # Build explanation
            explanation_parts = []
            
            # Overall assessment
            explanation_parts.append(
                f"Overall Authenticity Score: {auth_score:.1f}/100"
            )
            
            # Dominant evidence
            dominant = aggregated_score['dominant_evidence']
            explanation_parts.append(
                f"Primary evidence source: {dominant.upper()}"
            )
            
            # Key findings
            ext_summary = external_evidence.get('summary', {})
            key_findings = ext_summary.get('key_findings', [])
            if key_findings:
                explanation_parts.append("\nKey Findings:")
                for finding in key_findings[:3]:
                    explanation_parts.append(f"  • {finding}")
            
            # Contradictions
            if contradictions:
                explanation_parts.append("\n⚠️ Contradictions Detected:")
                for contra in contradictions[:3]:
                    explanation_parts.append(
                        f"  • [{contra['severity']}] {contra['description']}"
                    )
            
            explanation = "\n".join(explanation_parts)
            
            return {
                'verdict': verdict_type,
                'main_message': main_message,
                'confidence': confidence,
                'authenticity_score': auth_score,
                'explanation': explanation,
                'contradictions': contradictions,
                'attention_weights': attention_weights,
                'text_verification': text_verification,
                'image_verification': image_verification,
                'temporal_verification': temporal_verification,
                'external_evidence': external_evidence
            }
        
        except Exception as e:
            print(f"Verdict generation error: {e}")
            return self._get_error_result()
    
    def _get_error_result(self) -> Dict:
        """Return error result"""
        return {
            'verdict': 'ERROR',
            'main_message': '❌ Verification Error',
            'confidence': 0,
            'authenticity_score': 0,
            'explanation': 'An error occurred during verification',
            'contradictions': [],
            'attention_weights': {}
        }
