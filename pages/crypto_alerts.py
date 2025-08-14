import requests
import streamlit as st
from config_loader import get_config
from datetime import datetime
import logging

# Set up logging
logger = logging.getLogger(__name__)

def fetch_crypto_news(query, api_key):
    """Gets crypto news from the GNews API."""
    try:
        url = f"https://gnews.io/api/v4/search?q={query.lower()}&lang=en&token={api_key}&max=10"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching news: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None

def main():
    st.title("📰 Latest Crypto News")
    
    # Get the API key from our config
    api_key = get_config('api.gnews.api_key')
    
    if not api_key:
        st.error("⚠️ GNews API key not configured. Please set GNEWS_API_KEY in your .env file.")
        st.info("Get a free API key from: https://gnews.io/")
        return
    
    # Search interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "Enter a cryptocurrency name", 
            value="Bitcoin",
            placeholder="e.g., Bitcoin, Ethereum, Solana",
            key="news_search_input"
        )
    
    with col2:
        if st.button("🔍 Search News", key="search_news_button"):
            st.session_state.search_triggered = True
    
    # Default search if user hasn't searched for anything specific
    if not st.session_state.get('search_triggered', False):
        search_query = "cryptocurrency"
    
    # Get and show the news
    if search_query:
        with st.spinner(f"Fetching latest news about {search_query}..."):
            news_data = fetch_crypto_news(search_query, api_key)
        
        if news_data and "articles" in news_data:
            articles = news_data["articles"]
            
            if articles:
                st.success(f"Found {len(articles)} articles about {search_query}")
                
                # Display each article
                for i, article in enumerate(articles):
                    with st.container():
                        st.markdown("---")
                        
                        # Article title
                        st.subheader(article.get("title", "No title"))
                        
                        # Article image (if it has one)
                        if article.get("image"):
                            try:
                                st.image(article["image"], use_column_width=True)
                            except Exception as e:
                                logger.warning(f"Could not display image: {e}")
                        
                        # Article description
                        description = article.get("description", "No description available.")
                        st.write(description)
                        
                        # Article metadata in columns
                        col1, col2 = st.columns([1, 1])
                        
                        with col1:
                            source_name = article.get("source", {}).get("name", "Unknown Source")
                            st.caption(f"📰 Source: {source_name}")
                        
                        with col2:
                            published_at = article.get("publishedAt", "Unknown Date")
                            if published_at != "Unknown Date":
                                try:
                                    # Parse and format the date nicely
                                    from datetime import datetime
                                    dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                                    formatted_date = dt.strftime("%B %d, %Y at %I:%M %p")
                                    st.caption(f"📅 Published: {formatted_date}")
                                except:
                                    st.caption(f"📅 Published: {published_at}")
                            else:
                                st.caption(f"📅 Published: {published_at}")
                        
                        # Link to read the full article
                        article_url = article.get("url", "#")
                        if article_url != "#":
                            st.markdown(f"[🔗 Read Full Article]({article_url})")
                        
                        # Add some spacing
                        st.write("")
            else:
                st.warning(f"No articles found for '{search_query}'. Try a different search term.")
        else:
            st.error("Failed to fetch news. Please check your API key and try again.")
    
    # Footer with last update time
    st.markdown("---")
    st.caption(f"Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    
    # Button to refresh the news
    if st.button("🔄 Refresh News", key="refresh_news_button"):
        st.rerun()

if __name__ == "__main__":
    main()