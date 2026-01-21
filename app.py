"""
Streamlit Application - FIXED VERSION
Enhanced Dual-Input Incident Verification System
Version: 2.1 FIXED

CHANGES:
- Uses image_retriever_COMPLETE.py
- Uses temporal_verifier_FIXED.py
- All imports corrected
"""

import streamlit as st
from PIL import Image
import sys
import os

# Import custom modules - FIXED IMPORTS
from text_processor import TextProcessorPerfect
from image_retriever_COMPLETE import ImageRetrieverComplete as ImageRetriever  # ✅ FIXED!
from dual_verifier import DualVerifier
from explanation_generator import ExplanationGenerator

# Page configuration
st.set_page_config(
    page_title="Dual Input Incident Verification",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-box {
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #ddd;
        margin: 1rem 0;
    }
    .real {
        background-color: #d4edda;
        border-color: #28a745;
    }
    .fake {
        background-color: #f8d7da;
        border-color: #dc3545;
    }
    .mismatch {
        background-color: #fff3cd;
        border-color: #ffc107;
    }
    .uncertain {
        background-color: #e7f3ff;
        border-color: #0066cc;
    }
    .credibility-badge {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        border-radius: 5px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    .tier1 {
        background-color: #28a745;
        color: white;
    }
    .tier2 {
        background-color: #ffc107;
        color: black;
    }
    .tier3 {
        background-color: #17a2b8;
        color: white;
    }
    .regional {
        background-color: #6f42c1;
        color: white;
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
    """Load models with caching"""
    try:
        with st.spinner("Loading AI models... This may take a few minutes on first run."):
            text_processor = TextProcessor()
            verifier = DualVerifier()
            explanation_gen = ExplanationGenerator()
        return text_processor, verifier, explanation_gen
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return None, None, None

def main():
    # Header
    st.markdown('<p class="main-header">🔍 Dual-Input Incident Verification System</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Verify incidents using Text + Image together or separately</p>', unsafe_allow_html=True)
    
    # Load models
    if not st.session_state.initialized:
        text_processor, verifier, explanation_gen = load_models()
        
        if text_processor and verifier and explanation_gen:
            st.session_state.text_processor = text_processor
            st.session_state.verifier = verifier
            st.session_state.explanation_gen = explanation_gen
            st.session_state.initialized = True
            st.success("✓ Models loaded successfully!")
        else:
            st.error("Failed to load models. Please restart the application.")
            return
    
    # Sidebar configuration
    st.sidebar.title("⚙️ Configuration")
    
    max_images = st.sidebar.slider(
        "Max Images to Retrieve",
        min_value=5,
        max_value=20,
        value=10,
        help="Number of images to retrieve for verification from web"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info(
        "**💡 How it works:**\n\n"
        "**Text + Image Together:**\n"
        "• Checks if both describe same incident\n"
        "• Verifies both against web sources\n"
        "• Detects mismatches\n"
        "• Shows proof images\n\n"
        "**Text Only:**\n"
        "• Retrieves images from web\n"
        "• Verifies incident authenticity\n\n"
        "**Image Only:**\n"
        "• Reverse image search\n"
        "• Finds similar images online\n"
        "• Verifies authenticity"
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
            placeholder="Example: Chennai floods December 2024 caused severe damage to infrastructure...",
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
        verify_button = st.button("🔍 Verify Incident", type="primary", use_container_width=True)
    
    if verify_button:
        # Check what inputs are provided
        has_text = bool(text_input and text_input.strip())
        has_image = uploaded_file is not None
        
        if not has_text and not has_image:
            st.error("❌ Please provide at least TEXT or IMAGE or both")
            return
        
        try:
            # CASE 1: Both Text and Image provided
            if has_text and has_image:
                st.info("🔄 Mode: TEXT + IMAGE Verification")
                
                # Process text
                with st.spinner("Processing text..."):
                    text_info = st.session_state.text_processor.process_text(text_input)
                st.success("✓ Text processed")
                
                # Initialize retriever - FIXED
                retriever = ImageRetriever()  # ✅ Now uses ImageRetrieverComplete
                
                # Retrieve images based on text
                with st.spinner("Retrieving images based on TEXT..."):
                    text_based_images = retriever.retrieve_images_for_text(  # ✅ FIXED method name
                        query=text_info['search_query'],
                        max_images=max_images,
                        location=text_info.get('location'),
                        event_type=text_info.get('event_type'),
                        keywords=text_info.get('keywords')
                    )
                
                if text_based_images:
                    st.success(f"✓ Retrieved {len(text_based_images)} images for text")
                else:
                    st.warning("⚠️ Could not retrieve images for text")
                
                # Reverse image search - NEW FEATURE!
                with st.spinner("Performing reverse image search (finding original source)..."):
                    reverse_result = retriever.reverse_image_search(
                        image=user_image,
                        max_results=20
                    )
                
                if reverse_result.get('all_occurrences'):
                    st.success(f"✓ Found {len(reverse_result['all_occurrences'])} occurrences of uploaded image")
                    
                    # Show original source
                    if reverse_result.get('original_source'):
                        orig = reverse_result['original_source']
                        st.info(f"🎯 Original source: **{orig.get('domain', 'Unknown')}**")
                else:
                    st.warning("⚠️ No reverse search results (image may be new/original)")
                
                # Retrieve similar images (backward compatibility)
                with st.spinner("Searching for similar images..."):
                    caption = f"{text_info['event_type']} incident"
                    image_based_images = retriever.retrieve_images_for_text(
                        query=caption,
                        max_images=max_images // 2
                    )
                
                # Perform dual verification
                with st.spinner("Cross-verifying text and image..."):
                    result = st.session_state.verifier.verify_text_and_image(
                        text_input,
                        user_image,
                        text_based_images,
                        image_based_images
                    )
                
                st.success("✓ Verification complete")
                
                # Display results
                display_dual_verification_results(
                    result,
                    text_based_images,
                    image_based_images,
                    user_image,
                    reverse_result
                )
            
            # CASE 2: Only Text provided
            elif has_text and not has_image:
                st.info("🔄 Mode: TEXT Only Verification")
                
                # Process text
                with st.spinner("Processing text..."):
                    text_info = st.session_state.text_processor.process_text(text_input)
                st.success("✓ Text processed")
                
                # Initialize retriever
                retriever = ImageRetriever()  # ✅ FIXED
                
                # Retrieve images
                with st.spinner("Retrieving images from web..."):
                    retrieved_images = retriever.retrieve_images_for_text(  # ✅ FIXED
                        query=text_info['search_query'],
                        max_images=max_images,
                        location=text_info.get('location'),
                        event_type=text_info.get('event_type'),
                        keywords=text_info.get('keywords')
                    )
                
                if retrieved_images:
                    st.success(f"✓ Retrieved {len(retrieved_images)} images")
                    
                    # Verify
                    with st.spinner("Verifying incident..."):
                        result = st.session_state.verifier.verify_text_only(
                            text_input,
                            retrieved_images
                        )
                    
                    st.success("✓ Verification complete")
                    display_text_only_results(result, retrieved_images)
                else:
                    st.error("❌ No images found. Cannot verify.")
            
            # CASE 3: Only Image provided
            elif not has_text and has_image:
                st.info("🔄 Mode: IMAGE Only Verification")
                
                # Initialize retriever
                retriever = ImageRetriever()  # ✅ FIXED
                
                # Reverse image search - MAIN FEATURE FOR IMAGE-ONLY!
                with st.spinner("Performing reverse image search..."):
                    reverse_result = retriever.reverse_image_search(
                        image=user_image,
                        max_results=20
                    )
                
                if reverse_result.get('all_occurrences'):
                    st.success(f"✓ Found {len(reverse_result['all_occurrences'])} occurrences")
                    
                    # Extract images from reverse search
                    retrieved_images = []
                    for occ in reverse_result['all_occurrences'][:10]:
                        # Create image dict format
                        retrieved_images.append({
                            'image': user_image,  # Placeholder (could download from URL)
                            'source': occ.get('domain', 'Unknown'),
                            'name': occ.get('title', 'Unknown'),
                            'url': occ.get('url', ''),
                            'credibility': occ.get('credibility', 'UNKNOWN')
                        })
                    
                    # Verify
                    with st.spinner("Verifying image..."):
                        result = st.session_state.verifier.verify_image_only(
                            user_image,
                            retrieved_images
                        )
                    
                    st.success("✓ Verification complete")
                    display_image_only_results(result, retrieved_images, user_image, reverse_result)
                else:
                    st.warning("⚠️ No similar images found. Cannot verify.")
        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.exception(e)


def display_dual_verification_results(result, text_images, image_images, user_image, reverse_result):
    """Display results for Text + Image verification with retrieved images"""
    st.markdown("---")
    st.header("📋 Verification Results")
    
    # Main verdict box
    verdict = result['verdict']
    
    if verdict == 'MATCH_AND_REAL':
        css_class = 'real'
    elif verdict == 'BOTH_REAL_DIFFERENT_INCIDENTS':
        css_class = 'mismatch'
    elif verdict == 'PARTIAL_FAKE':
        css_class = 'fake'
    else:
        css_class = 'uncertain'
    
    st.markdown(
        f'<div class="result-box {css_class}">'
        f'<h2>{result["main_message"]}</h2>'
        f'<h3>Confidence: {result["confidence"]}%</h3>'
        f'<p style="white-space: pre-line;">{result["explanation"]}</p>'
        f'</div>',
        unsafe_allow_html=True
    )
    
    # NEW: Show reverse image search results
    if reverse_result and reverse_result.get('all_occurrences'):
        st.markdown("---")
        st.header("🔍 Reverse Image Search Results")
        
        if reverse_result.get('original_source'):
            orig = reverse_result['original_source']
            st.success(
                f"🎯 **Original Source Found:** {orig.get('domain', 'Unknown')}\n\n"
                f"**Title:** {orig.get('title', 'N/A')}\n\n"
                f"**Credibility:** {orig.get('credibility', 'UNKNOWN')}"
            )
        
        if reverse_result.get('reuse_detected'):
            st.warning(
                f"⚠️ **Image Reuse Detected:** This image appears on "
                f"{len(reverse_result['all_occurrences'])} different websites"
            )
        
        # Show all occurrences
        with st.expander("📍 All websites where this image was found", expanded=False):
            for i, occ in enumerate(reverse_result['all_occurrences'][:10]):
                st.write(f"{i+1}. **{occ.get('domain', 'Unknown')}** - {occ.get('credibility', 'UNKNOWN')}")
                st.caption(occ.get('snippet', occ.get('title', 'No description'))[:100])
    
    # Show detailed analysis
    st.markdown("---")
    st.subheader("📊 Detailed Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📝 Text Verification")
        st.write(f"**Status:** {result['text_verification']['authenticity']}")
        st.write(f"**Confidence:** {result['text_verification']['confidence']}%")
    
    with col2:
        st.markdown("### 🖼️ Image Verification")
        st.write(f"**Status:** {result['image_verification']['authenticity']}")
        st.write(f"**Confidence:** {result['image_verification']['confidence']}%")
    
    # Show original images from internet
    st.markdown("---")
    
    text_is_real = result['text_verification']['is_real']
    image_is_real = result['image_verification']['is_real']
    
    if text_is_real or image_is_real:
        st.header("🌐 Original Images from Internet (Proof)")
        st.info("📸 Below are real images retrieved from news sources to verify this incident")
        
        # Show text-based images if text is real
        if text_is_real and text_images:
            st.subheader("📝 Images Retrieved Based on Text Description")
            st.caption("These images were found online matching your text description")
            
            cols = st.columns(4)
            for i, img_data in enumerate(text_images[:8]):
                with cols[i % 4]:
                    st.image(img_data['image'], use_column_width=True)
                    
                    # Show credibility badge
                    credibility = img_data.get('credibility', 'UNKNOWN')
                    badge_class = {
                        'TIER1_GLOBAL': 'tier1',
                        'TIER2_INDIA': 'tier2',
                        'TIER3_REGIONAL': 'tier3',
                        'SOCIAL_MEDIA': 'regional'
                    }.get(credibility, 'tier3')
                    
                    st.markdown(
                        f"**{img_data.get('source', 'Unknown')[:30]}** "
                        f'<span class="credibility-badge {badge_class}">{credibility}</span>',
                        unsafe_allow_html=True
                    )
                    st.caption(f"{img_data.get('name', '')[:40]}...")
        
        # Show image-based images if image is real
        if image_is_real and image_images:
            st.markdown("---")
            st.subheader("🖼️ Similar Images Found Online")
            st.caption("These similar images were found matching your uploaded image")
            
            cols = st.columns(4)
            for i, img_data in enumerate(image_images[:8]):
                with cols[i % 4]:
                    st.image(img_data['image'], use_column_width=True)
                    
                    # Show credibility
                    credibility = img_data.get('credibility', 'UNKNOWN')
                    badge_class = {
                        'TIER1_GLOBAL': 'tier1',
                        'TIER2_INDIA': 'tier2',
                        'TIER3_REGIONAL': 'tier3'
                    }.get(credibility, 'tier3')
                    
                    st.markdown(
                        f"**{img_data.get('source', 'Unknown')[:30]}** "
                        f'<span class="credibility-badge {badge_class}">{credibility}</span>',
                        unsafe_allow_html=True
                    )
        
        st.success("✅ Above images from news sources verify the incident authenticity")
    else:
        st.warning("⚠️ No original images retrieved - both text and image appear to be fabricated")


def display_text_only_results(result, retrieved_images):
    """Display results for text-only verification"""
    st.markdown("---")
    st.header("📋 Verification Results (Text Only)")
    
    css_class = 'real' if result['is_real'] else 'fake'
    
    st.markdown(
        f'<div class="result-box {css_class}">'
        f'<h2>Authenticity: {result["authenticity"]}</h2>'
        f'<h3>Confidence: {result["confidence"]}%</h3>'
        f'<p>{result["explanation"]}</p>'
        f'</div>',
        unsafe_allow_html=True
    )
    
    if result['is_real'] and retrieved_images:
        st.subheader("🖼️ Retrieved Images from Web")
        cols = st.columns(4)
        for i, img_data in enumerate(retrieved_images[:8]):
            with cols[i % 4]:
                st.image(img_data['image'], use_column_width=True)
                
                # Show credibility
                credibility = img_data.get('credibility', 'UNKNOWN')
                st.caption(f"**{img_data.get('source', 'Unknown')[:30]}** ({credibility})")


def display_image_only_results(result, retrieved_images, user_image, reverse_result):
    """Display results for image-only verification"""
    st.markdown("---")
    st.header("📋 Verification Results (Image Only)")
    
    css_class = 'real' if result['is_real'] else 'fake'
    
    st.markdown(
        f'<div class="result-box {css_class}">'
        f'<h2>Authenticity: {result["authenticity"]}</h2>'
        f'<h3>Confidence: {result["confidence"]}%</h3>'
        f'<p>{result["explanation"]}</p>'
        f'</div>',
        unsafe_allow_html=True
    )
    
    # Show reverse search details
    if reverse_result and reverse_result.get('original_source'):
        st.subheader("🎯 Original Source")
        orig = reverse_result['original_source']
        st.info(
            f"**Domain:** {orig.get('domain', 'Unknown')}\n\n"
            f"**Credibility:** {orig.get('credibility', 'UNKNOWN')}\n\n"
            f"**Context:** {orig.get('snippet', 'N/A')[:200]}"
        )
    
    if result['is_real'] and retrieved_images:
        st.subheader("🔍 Similar Images Found Online")
        cols = st.columns(4)
        for i, img_data in enumerate(retrieved_images[:8]):
            with cols[i % 4]:
                st.write(f"**{img_data.get('source', 'Unknown')[:30]}**")
                st.caption(f"Credibility: {img_data.get('credibility', 'UNKNOWN')}")


if __name__ == "__main__":
    main()
