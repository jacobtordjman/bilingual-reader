import os
import json
import streamlit as st
from supabase import create_client, Client
from datetime import datetime

class SupabaseManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseManager, cls).__new__(cls)
            cls._instance._init_client()
        return cls._instance
    
    def _init_client(self):
        """Initialize Supabase client from Streamlit secrets."""
        try:
            url = st.secrets["supabase"]["url"]
            key = st.secrets["supabase"]["key"]
            self.client: Client = create_client(url, key)
            self.user_id = "user_123"  # Simplified for this specific user request
        except Exception as e:
            st.error(f"Failed to initialize Supabase: {str(e)}")
            self.client = None

    def get_books(self):
        """Fetch all books for the current user."""
        if not self.client: return []
        
        try:
            # First check if table exists by trying to select
            response = self.client.table("user_books").select("*").execute()
            return response.data
        except Exception as e:
            st.error(f"Error fetching books: {str(e)}")
            return []

    def add_book(self, title, total_sentences, processed_path, original_filename):
        """Add a new book to the library."""
        if not self.client: return None
        
        data = {
            "title": title,
            "total_sentences": total_sentences,
            "processed_sentences": 0,
            "current_page": 0,
            "storage_path": processed_path,
            "created_at": datetime.now().isoformat(),
            "original_filename": original_filename
        }
        
        try:
            response = self.client.table("user_books").insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error adding book: {str(e)}")
            return None

    def update_bookmark(self, book_id, page_number):
        """Update the current page bookmark."""
        if not self.client: return
        
        try:
            self.client.table("user_books").update({"current_page": page_number}).eq("id", book_id).execute()
        except Exception as e:
            print(f"Error updating bookmark: {str(e)}")

    def update_progress(self, book_id, processed_count):
        """Update processed sentence count."""
        if not self.client: return
        
        try:
            self.client.table("user_books").update({"processed_sentences": processed_count}).eq("id", book_id).execute()
        except Exception as e:
            print(f"Error updating progress: {str(e)}")

    def upload_content(self, path, content_json):
        """Upload processed content to Storage."""
        if not self.client: return False
        
        try:
            # Convert to JSON string
            if isinstance(content_json, (list, dict)):
                content_str = json.dumps(content_json, ensure_ascii=False)
            else:
                content_str = content_json
                
            bucket_name = "book-content"
            
            # Check if bucket exists, if not create (might need permissions)
            # For now assuming bucket exists or we use public one
            
            self.client.storage.from_(bucket_name).upload(
                path,
                content_str.encode('utf-8'),
                {"content-type": "application/json", "upsert": "true"}
            )
            return True
        except Exception as e:
            st.error(f"Error uploading to storage: {str(e)}")
            return False

    def load_content(self, path):
        """Download content from Storage."""
        if not self.client: return []
        
        try:
            bucket_name = "book-content"
            response = self.client.storage.from_(bucket_name).download(path)
            return json.loads(response.decode('utf-8'))
        except Exception as e:
            st.error(f"Error loading content: {str(e)}")
            return []
