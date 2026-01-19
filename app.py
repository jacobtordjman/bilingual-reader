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
    """Process PDF and transition to reader view."""
    
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
        
        # Step 4: Translate
        status.info("🌐 Translating sentences...")
        translations = []
        batch_size = 8
        
        for i in range(0, total, batch_size):
            batch = all_sentences[i:i + batch_size]
            batch_trans = translator.translate_batch(batch)
            translations.extend(batch_trans)
            
            progress = 30 + int(60 * (i + len(batch)) / total)
            progress_bar.progress(progress)
            status.info(f"🌐 Translating... ({min(i + batch_size, total)}/{total})")
        
        progress_bar.progress(95)
        status.info("✨ Preparing reader...")
        
        # Create sentence pairs
        sentence_pairs = list(zip(all_sentences, translations))
        
        # Store in session state
        st.session_state.sentence_pairs = sentence_pairs
        st.session_state.reader_mode = True
        st.session_state.document_name = uploaded_file.name
        
        progress_bar.progress(100)
        status.success("✅ Ready! Loading reader...")
        
        # Trigger rerun to show reader
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        progress_bar.empty()
        status.empty()


def show_reader():
    """Display the full-screen reader interface."""
    
    sentence_pairs = st.session_state.get('sentence_pairs', [])
    
    if not sentence_pairs:
        st.session_state.reader_mode = False
        st.rerun()
        return
    
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
    
    # Exit reader button (small, top-left)
    col1, col2, col3 = st.columns([1, 8, 1])
    with col1:
        if st.button("← Exit", key="exit_reader"):
            st.session_state.reader_mode = False
            st.rerun()
    
    # Generate and display reader
    reader_html = generate_reader_html(sentence_pairs)
    
    # Use components.html for the full reader experience
    components.html(reader_html, height=700, scrolling=False)


def main():
    """Main application entry point."""
    
    # Check if we should show reader or upload page
    if st.session_state.get('reader_mode', False):
        show_reader()
    else:
        show_upload_page()


if __name__ == "__main__":
    main()
