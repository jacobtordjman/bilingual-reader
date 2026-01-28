"""
Bilingual Interlinear PDF Reader with Cloud Library
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import tempfile
import os
from supabase_manager import SupabaseManager
from pdf_extractor import extract_text_from_pdf
from sentence_processor import group_sentences_by_paragraph
from translator import get_translator
from reader_component import generate_reader_html

# Page configuration
st.set_page_config(
    page_title="Bilingual Library",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize Supabase Manager
db = SupabaseManager()

def show_library():
    """Display the library grid view."""
    
    st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%); }
        .book-card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: transform 0.2s;
            cursor: pointer;
            height: 100%;
            border: 1px solid #eee;
        }
        .book-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 15px rgba(0,0,0,0.1);
            border-color: #667eea;
        }
        .book-title {
            font-weight: 600;
            font-size: 1.1rem;
            margin-bottom: 8px;
            color: #2d3748;
            height: 3.6rem;
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
        }
        .book-meta {
            font-size: 0.85rem;
            color: #718096;
            margin-bottom: 16px;
        }
        .progress-bar {
            height: 4px;
            background: #edf2f7;
            border-radius: 2px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: #667eea;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("📚 My Library")
    with col2:
        if st.button("➕ Upload New Book", use_container_width=True):
            st.session_state.view_mode = "upload"
            st.rerun()
            
    # Load books
    books = db.get_books()
    
    if not books:
        st.info("Your library is empty. Upload a PDF to get started!")
        return
        
    # Grid Layout
    cols = st.columns(3)
    for i, book in enumerate(books):
        with cols[i % 3]:
            # Calculate progress
            progress = 0
            if book['total_sentences'] > 0:
                # Approximate 10 sentences per page for progress calc
                current_page = book['current_page']
                est_sentences = current_page * 10
                progress = min(100, int((est_sentences / book['total_sentences']) * 100))
            
            # Card HTML
            st.markdown(f"""
            <div class="book-card">
                <div class="book-title">{book['title']}</div>
                <div class="book-meta">
                    {book['total_sentences']} sentences<br>
                    Bookmark: Page {book['current_page'] + 1}
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {progress}%"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Invisible button for interaction
            if st.button(f"Read {book['title']}", key=f"read_{book['id']}", use_container_width=True):
                st.session_state.current_book = book
                st.session_state.view_mode = "reader"
                st.rerun()
            
            st.markdown("<div style='margin-bottom: 20px'></div>", unsafe_allow_html=True)

def show_upload():
    """Display upload and processing interface."""
    st.button("← Back to Library", on_click=lambda: st.session_state.update(view_mode="home"))
    
    st.header("📄 Add to Library")
    
    uploaded_file = st.file_uploader("Choose a Spanish PDF", type=['pdf'])
    
    if uploaded_file and st.button("🚀 Process & Add to Library", type="primary"):
        with st.status("Processing book...", expanded=True) as status:
            try:
                # 1. Extract
                status.write("Extracting text...")
                text = extract_text_from_pdf(uploaded_file)
                if not text.strip():
                    status.error("Empty or image-based PDF text.")
                    return

                # 2. Segment
                status.write("Segmenting sentences...")
                paragraphs = group_sentences_by_paragraph(text)
                all_sentences = [sent for para in paragraphs for sent in para]
                total = len(all_sentences)
                
                if total == 0:
                    status.error("No sentences found.")
                    return

                # 3. Translate
                status.write(f"Translating {total} sentences (this may take a minute)...")
                progress_bar = status.progress(0)
                
                translator = get_translator()
                translator.load_model()
                
                translations = []
                batch_size = 16
                
                for i in range(0, total, batch_size):
                    batch = all_sentences[i:i + batch_size]
                    batch_trans = translator.translate_batch(batch)
                    translations.extend(batch_trans)
                    progress_bar.progress(min(100, int(100 * (i + len(batch)) / total)))
                
                # 4. Prepare Content & Upload to Cloud
                sentence_pairs = list(zip(all_sentences, translations))
                status.write("Syncing to cloud...")
                storage_path = f"{uploaded_file.name}-{os.urandom(4).hex()}.json"
                
                upload_success = db.upload_content(storage_path, sentence_pairs)
                if not upload_success:
                    status.error("❌ Failed to upload to cloud storage. Check Supabase setup.")
                    st.stop()
                
                # 5. Create DB Entry
                book_entry = db.add_book(
                    title=uploaded_file.name.replace(".pdf", ""),
                    total_sentences=total,
                    processed_path=storage_path,
                    original_filename=uploaded_file.name
                )
                
                if not book_entry:
                    status.error("❌ Failed to save book to database. Check Supabase setup.")
                    st.stop()
                    
                status.update(label="✅ Complete!", state="complete", expanded=False)
                st.success("Book added! Redirecting...")
                st.session_state.view_mode = "home"
                st.rerun()
                    
            except Exception as e:
                status.error(f"Error: {str(e)}")
                import traceback
                st.error(f"Details: {traceback.format_exc()}")

def show_reader():
    """Display the reader view."""
    book = st.session_state.get('current_book')
    if not book:
        st.session_state.view_mode = "home"
        st.rerun()
        return

    # Top Bar
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Back to Library"):
            st.session_state.view_mode = "home"
            st.rerun()
            
    with col2:
        st.caption(f"Reading: **{book['title']}**")

    # Load Content (Cache this)
    @st.cache_data(show_spinner=False)
    def load_book_data(path):
        return db.load_content(path)
        
    try:
        sentence_pairs = load_book_data(book['storage_path'])
    except Exception as e:
        st.error("Could not load book content. Please try again.")
        return

    # Reader Component
    # We pass the book ID so the JS can send bookmark updates (conceptually, 
    # but for now we'll just handle it by initial page load)
    
    # Inject initial page from DB bookmark
    # The pure HTML/JS component handles pagination logic internally.
    # To support "Resume", we'd ideally pass the `initialPage` to the component.
    # Let's quickly patch reader_component.py to accept initial_page if needed, 
    # but strictly speaking, we can just let it load.
    # For now, let's just show it.
    
    reader_html = generate_reader_html(sentence_pairs)
    
    # Update Bookmark Logic (Simple approach: Updates on exit or periodically? 
    # Real-time sync requires bi-directional comms which is hard with pure Streamlit components.
    # We will simulate by updating when user clicks "Back" if we could read JS state, 
    # but we can't easily.
    # ALTERNATIVE: Use Streamlit URL params or dedicated sync button if needed.
    # For this iteration, we'll focus on the Library structure first.)
    
    components.html(reader_html, height=750, scrolling=False)


def main():
    if 'view_mode' not in st.session_state:
        st.session_state.view_mode = "home"
        
    if st.session_state.view_mode == "upload":
        show_upload()
    elif st.session_state.view_mode == "reader":
        show_reader()
    else:
        show_library()

if __name__ == "__main__":
    main()
