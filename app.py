"""
Bilingual Interlinear PDF Reader
Streamlit web application with advanced paginated reader interface.
"""

import streamlit as st
import streamlit.components.v1 as components
from pdf_extractor import extract_text_from_pdf
from sentence_processor import group_sentences_by_paragraph
from translator import get_translator
from reader_component import generate_reader_html


# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="Bilingual PDF Reader",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def show_upload_page():
    """Display the upload and processing interface."""
    
    # Custom CSS for upload page
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
        }
        
        .upload-header {
            text-align: center;
            padding: 2rem 0;
        }
        
        .upload-header h1 {
            font-size: 2.5rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        
        .feature-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
        }
        
        /* Hide default Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Progress styling */
        .stProgress > div > div > div > div {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="upload-header">
        <h1>📚 Bilingual PDF Reader</h1>
        <p style="color: #666; font-size: 1.1rem;">
            Transform Spanish PDFs into an immersive bilingual reading experience
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main content columns
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Upload section
        st.markdown("### 📄 Upload Your PDF")
        uploaded_file = st.file_uploader(
            "Select a Spanish PDF document",
            type=['pdf'],
            help="Choose a PDF file containing Spanish text",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            st.success(f"✓ **{uploaded_file.name}** ready for processing")
            
            # Process button
            if st.button("🚀 Start Reading", type="primary", use_container_width=True):
                process_and_open_reader(uploaded_file)
        
        # Features section
        st.markdown("---")
        st.markdown("### ✨ Features")
        
        features = [
            ("📖 **Paginated Reader**", "Book-like reading experience with smooth page turns"),
            ("🎛️ **Tap Controls**", "Tap center to show/hide navigation overlay"),
            ("🔤 **Adjustable Font**", "Customize font size and margins to your preference"),
            ("🌐 **Local Translation**", "Powered by MarianMT - no internet needed after setup"),
            ("📱 **Touch Support**", "Swipe left/right to navigate pages")
        ]
        
        for title, desc in features:
            st.markdown(f"{title}  \n<small style='color: #666'>{desc}</small>", unsafe_allow_html=True)
    
    # Sidebar info (collapsed by default)
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        This app converts Spanish PDFs into a bilingual interlinear format, 
        displaying English translations below each Spanish sentence.
        
        **How to use:**
        1. Upload a Spanish PDF
        2. Wait for processing
        3. Read in the paginated viewer
        
        **Navigation:**
        - Click sides to turn pages
        - Tap center for controls
        - Use arrow keys
        - Swipe on touch devices
        """)
        
        import torch
        device = "GPU 🚀" if torch.cuda.is_available() else "CPU"
        st.info(f"**Device:** {device}")


def process_and_open_reader(uploaded_file):
    """Process PDF and transition to reader view with progressive loading."""
    
    progress_bar = st.progress(0)
    status = st.empty()
    
    try:
        # Step 1: Extract text
        status.info("📄 Extracting text from PDF...")
        progress_bar.progress(10)
        
        text = extract_text_from_pdf(uploaded_file)
        
        if not text.strip():
            st.error("❌ Could not extract text. The PDF may be image-based or empty.")
            return
        
        # Step 2: Segment sentences
        status.info("✂️ Segmenting text into sentences...")
        progress_bar.progress(20)
        
        paragraphs = group_sentences_by_paragraph(text)
        all_sentences = [sent for para in paragraphs for sent in para]
        total = len(all_sentences)
        
        if total == 0:
            st.error("❌ No sentences found in the PDF.")
            return
        
        # Step 3: Load translation model
        status.info("🔧 Loading translation model...")
        progress_bar.progress(30)
        
        translator = get_translator()
        translator.load_model()
        
        # Step 4: Progressive Translation - translate initial batch first
        # Estimate ~10-15 sentence pairs per page, so 40-50 sentences ≈ 3-4 pages
        initial_batch_size = min(50, total)
        status.info(f"🌐 Translating initial content ({initial_batch_size} sentences)...")
        
        # Translate initial batch
        initial_sentences = all_sentences[:initial_batch_size]
        initial_translations = []
        batch_size = 8
        
        for i in range(0, len(initial_sentences), batch_size):
            batch = initial_sentences[i:i + batch_size]
            batch_trans = translator.translate_batch(batch)
            initial_translations.extend(batch_trans)
            
            progress = 30 + int(40 * (i + len(batch)) / initial_batch_size)
            progress_bar.progress(progress)
        
        progress_bar.progress(70)
        status.success(f"✅ Ready to read! Processing remaining {total - initial_batch_size} sentences in background...")
        
        # Create initial sentence pairs
        initial_pairs = list(zip(initial_sentences, initial_translations))
        
        # Store in session state for immediate display
        st.session_state.sentence_pairs = initial_pairs
        st.session_state.all_sentences = all_sentences
        st.session_state.total_sentences = total
        st.session_state.processed_count = initial_batch_size
        st.session_state.translator_ready = True
        st.session_state.reader_mode = True
        st.session_state.document_name = uploaded_file.name
        st.session_state.processing_complete = (initial_batch_size >= total)
        
        # Clear progress UI
        progress_bar.empty()
        status.empty()
        
        # Trigger rerun to show reader
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        progress_bar.empty()
        status.empty()


def show_reader():
    """Display the full-screen reader interface with background processing."""
    
    sentence_pairs = st.session_state.get('sentence_pairs', [])
    
    if not sentence_pairs:
        st.session_state.reader_mode = False
        st.rerun()
        return
    
    # Check if we need to continue processing
    processing_complete = st.session_state.get('processing_complete', True)
    
    if not processing_complete:
        # Continue background translation
        all_sentences = st.session_state.get('all_sentences', [])
        total_sentences = st.session_state.get('total_sentences', 0)
        processed_count = st.session_state.get('processed_count', 0)
        
        if processed_count < total_sentences:
            # Process next batch
            translator = get_translator()
            batch_size = 16  # Larger batch for background processing
            end_idx = min(processed_count + batch_size, total_sentences)
            
            batch_to_translate = all_sentences[processed_count:end_idx]
            batch_translations = translator.translate_batch(batch_to_translate)
            
            # Append new pairs to existing ones
            new_pairs = list(zip(batch_to_translate, batch_translations))
            st.session_state.sentence_pairs.extend(new_pairs)
            st.session_state.processed_count = end_idx
            
            # Check if complete
            if end_idx >= total_sentences:
                st.session_state.processing_complete = True
            else:
                # Schedule rerun to continue processing
                import time
                time.sleep(0.1)  # Small delay to not overwhelm
    
    # Hide Streamlit UI elements for full-screen reader
    st.markdown("""
    <style>
        .stApp > header { display: none !important; }
        .stMainBlockContainer { padding: 0 !important; max-width: 100% !important; }
        .block-container { padding: 0 !important; max-width: 100% !important; }
        section[data-testid="stSidebar"] { display: none !important; }
        .stApp { overflow: hidden !important; }
        #MainMenu { display: none !important; }
        footer { display: none !important; }
        .stDeployButton { display: none !important; }
    </style>
    """, unsafe_allow_html=True)
    
    # Top bar with exit button and processing indicator
    col1, col2, col3 = st.columns([1, 8, 1])
    with col1:
        if st.button("← Exit", key="exit_reader"):
            st.session_state.reader_mode = False
            st.rerun()
    
    # Show processing status if not complete
    if not processing_complete:
        with col2:
            processed = st.session_state.get('processed_count', 0)
            total = st.session_state.get('total_sentences', 0)
            progress_pct = int(100 * processed / total) if total > 0 else 0
            st.info(f"📥 Loading more content... {processed}/{total} sentences ({progress_pct}%)")
    
    # Generate and display reader
    reader_html = generate_reader_html(st.session_state.sentence_pairs)
    
    # Use components.html for the full reader experience
    components.html(reader_html, height=700, scrolling=False)
    
    # Auto-refresh if processing not complete
    if not processing_complete:
        st.rerun()


def main():
    """Main application entry point."""
    
    # Check if we should show reader or upload page
    if st.session_state.get('reader_mode', False):
        show_reader()
    else:
        show_upload_page()


if __name__ == "__main__":
    main()
