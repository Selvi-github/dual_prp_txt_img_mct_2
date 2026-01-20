"""
ENHANCED Streamlit Application
Dual-Input Incident Verification System with Novel Enhancements

Version: 3.0 (Research Publication Ready)

Novel Contributions Over Base Paper (DEETSA):
1. ✅ Temporal Verification - EXIF metadata + date extraction
2. ✅ Real-time Evidence Aggregation - No static KB needed  
3. ✅ Attention-based Fusion - Lightweight alternative to gated networks
4. ✅ Multi-source Evidence - News, fact-check, Wikipedia, web
5. ✅ Explainable AI - Clear reasoning for all decisions
"""

import streamlit as st
from PIL import Image
import sys
import os

# Import original modules
from text_processor import TextProcessor
from image_retriever import ImageRetriever
from explanation_generator import ExplanationGenerator

# Import ENHANCED modules (our novel contributions)
from enhanced_dual_verifier import EnhancedDualVerifier
from temporal_verifier import TemporalVerifier
from evidence_aggregator import EvidenceAggregator
from multimodal_fusion import AttentionFusion

# Page configuration
st.set_page_config(
    page_title="Enhanced Dual Input Verification (Research Version)",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (enhanced)
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 1rem;
    }
    .research-badge {
        font-size: 0.9rem;
        color: #28a745;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .result-box {
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #ddd;
        margin: 1rem 0;
    }
    .verified {
        background-color: #d4edda;
        border-color: #28a745;
    }
    .fake {
        background-color: #f8d7da;
        border-color: #dc3545;
    }
    .critical {
        background-color: #fff3cd;
        border-color: #ffc107;
    }
    .moderate {
        background-color: #e7f3ff;
        border-color: #0066cc;
    }
    .enhancement-badge {
        display: inline-block;
        background-color: #28a745;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 5px;
        font-size: 0.8rem;
        margin-left: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.text_processor = None
    st.session_state.verifier = None
    st.session_state.explanation_gen = None

@st.cache_resource
def load_models():
    """Load models with caching - ENHANCED VERSION"""
    try:
        with st.spinner("🔬 Loading Enhanced AI Models (Research Version)..."):
            text_processor = TextProcessor()
            verifier = EnhancedDualVerifier()  # ENHANCED!
            explanation_gen = ExplanationGenerator()
        return text_processor, verifier, explanation_gen
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return None, None, None

def main():
    # Header with research badge
    st.markdown('<p class="main-header">🔬 Enhanced Dual-Input Verification System</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Multi-Modal Rumor Detection with Temporal Verification & Evidence Fusion</p>', unsafe_allow_html=True)
    st.markdown('<p class="research-badge">✨ Research Publication Version | Novel Enhancements Over DEETSA ✨</p>', unsafe_allow_html=True)
    
    # Load models
    if not st.session_state.initialized:
        text_processor, verifier, explanation_gen = load_models()
        
        if text_processor and verifier and explanation_gen:
            st.session_state.text_processor = text_processor
            st.session_state.verifier = verifier
            st.session_state.explanation_gen = explanation_gen
            st.session_state.initialized = True
            st.success("✓ Enhanced models loaded successfully!")
        else:
            st.error("Failed to load models. Please restart the application.")
            return
    
    # Sidebar configuration - ENHANCED
    st.sidebar.title("⚙️ Enhanced Configuration")
    
    st.sidebar.info(
        "**🔬 Novel Enhancements:**\n\n"
        "✅ **Temporal Verification**\n"
        "└─ EXIF metadata extraction\n"
        "└─ Date/time mismatch detection\n\n"
        "✅ **Multi-Source Evidence**\n"
        "└─ Real-time news aggregation\n"
        "└─ Fact-check API integration\n"
        "└─ Wikipedia knowledge graph\n\n"
        "✅ **Attention Fusion**\n"
        "└─ Lightweight evidence weighting\n"
        "└─ Contradiction detection\n"
        "└─ Explainable results"
    )
    
    max_images = st.sidebar.slider(
        "Max Images to Retrieve",
        min_value=5,
        max_value=20,
        value=10,
        help="Number of images to retrieve from web"
    )
    
    # Enhanced features toggle
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔬 Research Features")
    
    enable_temporal = st.sidebar.checkbox(
        "Temporal Verification",
        value=True,
        help="Check date/time consistency between text and image"
    )
    
    enable_external = st.sidebar.checkbox(
        "External Evidence Aggregation",
        value=True,
        help="Fetch evidence from news, fact-check, Wikipedia"
    )
    
    show_attention = st.sidebar.checkbox(
        "Show Attention Weights",
        value=True,
        help="Display attention weights for different evidence sources"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info(
        "**📊 How Enhanced Verification Works:**\n\n"
        "1️⃣ Extract text/image features\n"
        "2️⃣ Retrieve similar images (web)\n"
        "3️⃣ 🆕 Check temporal consistency\n"
        "4️⃣ 🆕 Aggregate external evidence\n"
        "5️⃣ 🆕 Fuse with attention mechanism\n"
        "6️⃣ 🆕 Detect contradictions\n"
        "7️⃣ Generate explainable verdict"
    )
    
    # Main input area
    st.header("📝 Enter Incident Information")
    
    # Create two columns for text and image input
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Text Description")
        text_input = st.text_area(
            "Describe the incident:",
            height=200,
            placeholder="Example: Chennai floods December 2024 caused severe damage...",
            help="Describe the incident in detail"
        )
    
    with col2:
        st.subheader("🖼️ Incident Image")
        uploaded_file = st.file_uploader(
            "Upload incident image (optional):",
            type=['jpg', 'jpeg', 'png', 'webp'],
            help="Upload an image related to the incident"
        )
        
        if uploaded_file:
            user_image = Image.open(uploaded_file)
            st.image(user_image, caption="Uploaded Image", use_column_width=True)
    
    # Verify button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        verify_button = st.button("🔬 Verify with Enhanced AI", type="primary", use_container_width=True)
    
    if verify_button:
        # Check what inputs are provided
        has_text = bool(text_input and text_input.strip())
        has_image = uploaded_file is not None
        
        if not has_text and not has_image:
            st.error("❌ Please provide at least TEXT or IMAGE or both")
            return
        
        try:
            # CASE 1: Both Text and Image provided - ENHANCED VERSION
            if has_text and has_image:
                st.info("🔬 Mode: ENHANCED TEXT + IMAGE Verification")
                
                # Process text
                with st.spinner("Processing text..."):
                    text_info = st.session_state.text_processor.process_text(text_input)
                st.success("✓ Text processed")
                
                # Retrieve images based on text
                with st.spinner("Retrieving images based on TEXT..."):
                    retriever = ImageRetriever()
                    text_based_images = retriever.retrieve_images(
                        text_info['search_query'], 
                        max_images
                    )
                
                if text_based_images:
                    st.success(f"✓ Retrieved {len(text_based_images)} images for text")
                else:
                    st.warning("⚠️ Could not retrieve images for text")
                
                # Retrieve images for reverse search
                with st.spinner("Performing reverse image search..."):
                    caption = f"{text_info['event_type']} incident"
                    image_based_images = retriever.retrieve_images(caption, max_images)
                
                if image_based_images:
                    st.success(f"✓ Retrieved {len(image_based_images)} images for reverse search")
                
                # ENHANCED VERIFICATION with new modules
                with st.spinner("🔬 Running enhanced verification pipeline..."):
                    result = st.session_state.verifier.verify_text_and_image(
                        text_input,
                        user_image,
                        text_based_images,
                        image_based_images,
                        text_info=text_info  # Pass text info for better evidence
                    )
                
                st.success("✓ Enhanced verification complete")
                
                # Display ENHANCED results
                display_enhanced_dual_results(
                    result,
                    text_based_images,
                    image_based_images,
                    user_image,
                    enable_temporal,
                    enable_external,
                    show_attention
                )
            
            # CASE 2: Only Text - ENHANCED
            elif has_text and not has_image:
                st.info("🔬 Mode: ENHANCED TEXT Only Verification")
                
                with st.spinner("Processing text..."):
                    text_info = st.session_state.text_processor.process_text(text_input)
                
                with st.spinner("Retrieving images..."):
                    retriever = ImageRetriever()
                    retrieved_images = retriever.retrieve_images(
                        text_info['search_query'],
                        max_images
                    )
                
                if retrieved_images:
                    with st.spinner("🔬 Running enhanced verification..."):
                        result = st.session_state.verifier.verify_text_only(
                            text_input,
                            retrieved_images,
                            text_info=text_info
                        )
                    
                    display_enhanced_text_results(result, retrieved_images, enable_external)
                else:
                    st.error("❌ No images found. Cannot verify.")
            
            # CASE 3: Only Image - ENHANCED
            elif not has_text and has_image:
                st.info("🔬 Mode: ENHANCED IMAGE Only Verification")
                
                with st.spinner("Analyzing image..."):
                    caption = "incident scene"
                
                with st.spinner("Searching similar images..."):
                    retriever = ImageRetriever()
                    retrieved_images = retriever.retrieve_images(caption, max_images)
                
                if retrieved_images:
                    with st.spinner("🔬 Running enhanced verification..."):
                        result = st.session_state.verifier.verify_image_only(
                            user_image,
                            retrieved_images
                        )
                    
                    display_enhanced_image_results(result, retrieved_images, user_image, enable_temporal)
                else:
                    st.error("❌ No similar images found.")
        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.exception(e)


def display_enhanced_dual_results(
    result, 
    text_images, 
    image_images, 
    user_image,
    enable_temporal,
    enable_external,
    show_attention
):
    """Display ENHANCED results with all novel features"""
    st.markdown("---")
    st.header("📋 Enhanced Verification Results")
    
    # Main verdict box
    verdict = result['verdict']
    
    # Determine CSS class
    if verdict == 'VERIFIED_AUTHENTIC':
        css_class = 'verified'
    elif verdict in ['CRITICAL_CONTRADICTIONS', 'LIKELY_FAKE']:
        css_class = 'critical' if 'CRITICAL' in verdict else 'fake'
    else:
        css_class = 'moderate'
    
    st.markdown(
        f'<div class="result-box {css_class}">'
        f'<h2>{result["main_message"]}</h2>'
        f'<h3>Overall Confidence: {result["confidence"]}%</h3>'
        f'<h4>Authenticity Score: {result.get("authenticity_score", 0):.1f}/100</h4>'
        f'<p style="white-space: pre-line;">{result["explanation"]}</p>'
        f'</div>',
        unsafe_allow_html=True
    )
    
    # NEW: Attention Weights Visualization
    if show_attention and 'attention_weights' in result:
        st.subheader("🎯 Attention Weights (Novel Enhancement)")
        st.caption("How different evidence sources were weighted in the final decision")
        
        weights = result['attention_weights']
        if weights:
            import pandas as pd
            
            df = pd.DataFrame({
                'Evidence Source': list(weights.keys()),
                'Attention Weight': [f"{v*100:.1f}%" for v in weights.values()],
                'Raw Value': list(weights.values())
            })
            
            st.dataframe(df[['Evidence Source', 'Attention Weight']], use_container_width=True)
            
            # Bar chart
            st.bar_chart(df.set_index('Evidence Source')['Raw Value'])
    
    # NEW: Temporal Verification Results
    if enable_temporal and 'temporal_verification' in result:
        temp_result = result['temporal_verification']
        
        if temp_result.get('has_mismatch'):
            st.markdown("---")
            st.subheader("⏰ Temporal Verification (Novel Enhancement)")
            
            severity = temp_result.get('severity', 'LOW')
            severity_emoji = {'HIGH': '🚨', 'MEDIUM': '⚠️', 'LOW': 'ℹ️'}
            
            st.warning(
                f"{severity_emoji.get(severity, 'ℹ️')} **Temporal Mismatch Detected**\n\n"
                f"**Text Date:** {temp_result.get('text_date', 'Unknown')}\n\n"
                f"**Image Date (EXIF):** {temp_result.get('image_date', 'Unknown')}\n\n"
                f"**Difference:** {temp_result.get('days_difference', 0)} days\n\n"
                f"**Severity:** {severity}\n\n"
                f"**Explanation:** {temp_result.get('explanation', 'N/A')}"
            )
    
    # NEW: External Evidence Summary
    if enable_external and 'external_evidence' in result:
        ext_evidence = result['external_evidence']
        ext_summary = ext_evidence.get('summary', {})
        
        st.markdown("---")
        st.subheader("📰 External Evidence Aggregation (Novel Enhancement)")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Sources", ext_summary.get('total_sources', 0))
        
        with col2:
            st.metric("Credible Sources", ext_summary.get('credible_sources', 0))
        
        with col3:
            st.metric("Evidence Score", f"{ext_summary.get('evidence_score', 0)}/100")
        
        with col4:
            verdict_label = ext_summary.get('verdict', 'N/A').replace('_', ' ')
            st.metric("Verdict", verdict_label)
        
        # Key findings
        key_findings = ext_summary.get('key_findings', [])
        if key_findings:
            st.markdown("**Key Findings from External Sources:**")
            for finding in key_findings:
                st.markdown(f"• {finding}")
        
        # Fact-checks
        factchecks = ext_evidence.get('factcheck', [])
        if factchecks:
            st.markdown("**Fact-Check Results:**")
            for fc in factchecks[:3]:
                st.info(
                    f"**Publisher:** {fc.get('publisher', 'Unknown')}\n\n"
                    f"**Rating:** {fc.get('rating', 'Unknown')}\n\n"
                    f"**Claim:** {fc.get('claim', 'N/A')[:100]}..."
                )
    
    # Contradictions
    contradictions = result.get('contradictions', [])
    if contradictions:
        st.markdown("---")
        st.subheader("⚠️ Detected Contradictions")
        
        for contra in contradictions:
            severity = contra.get('severity', 'LOW')
            st.warning(
                f"**[{severity}] {contra.get('type', 'Unknown')}**\n\n"
                f"{contra.get('description', 'N/A')}\n\n"
                f"Confidence: {contra.get('confidence', 0)}%"
            )
    
    # Original images
    st.markdown("---")
    st.subheader("🌐 Retrieved Images from Internet")
    
    if text_images:
        st.caption("📝 Images based on text description:")
        cols = st.columns(4)
        for i, img_data in enumerate(text_images[:8]):
            with cols[i % 4]:
                st.image(img_data['image'], use_column_width=True)
                st.caption(f"{img_data['source'][:30]}")


def display_enhanced_text_results(result, retrieved_images, enable_external):
    """Display enhanced text-only results"""
    st.markdown("---")
    st.header("📋 Enhanced Text Verification Results")
    
    css_class = 'verified' if result['is_real'] else 'fake'
    
    st.markdown(
        f'<div class="result-box {css_class}">'
        f'<h2>Authenticity: {result["authenticity"]}</h2>'
        f'<h3>Confidence: {result["confidence"]}%</h3>'
        f'<p>{result["explanation"]}</p>'
        f'</div>',
        unsafe_allow_html=True
    )
    
    # External evidence if enabled
    if enable_external and 'external_evidence' in result:
        ext_summary = result['external_evidence'].get('summary', {})
        
        st.subheader("📰 External Evidence")
        st.metric("Evidence Score", f"{ext_summary.get('evidence_score', 0)}/100")
        
        for finding in ext_summary.get('key_findings', []):
            st.markdown(f"• {finding}")
    
    # Retrieved images
    if result['is_real'] and retrieved_images:
        st.subheader("🖼️ Supporting Images")
        cols = st.columns(4)
        for i, img_data in enumerate(retrieved_images[:8]):
            with cols[i % 4]:
                st.image(img_data['image'], use_column_width=True)
                st.caption(f"{img_data['source'][:30]}")


def display_enhanced_image_results(result, retrieved_images, user_image, enable_temporal):
    """Display enhanced image-only results"""
    st.markdown("---")
    st.header("📋 Enhanced Image Verification Results")
    
    css_class = 'verified' if result['is_real'] else 'fake'
    
    st.markdown(
        f'<div class="result-box {css_class}">'
        f'<h2>Authenticity: {result["authenticity"]}</h2>'
        f'<h3>Confidence: {result["confidence"]}%</h3>'
        f'<p>{result["explanation"]}</p>'
        f'</div>',
        unsafe_allow_html=True
    )
    
    # Similar images
    if result['is_real'] and retrieved_images:
        st.subheader("🔍 Similar Images Found Online")
        cols = st.columns(4)
        for i, img_data in enumerate(retrieved_images[:8]):
            with cols[i % 4]:
                st.image(img_data['image'], use_column_width=True)
                st.caption(f"{img_data['source'][:30]}")


if __name__ == "__main__":
    main()
