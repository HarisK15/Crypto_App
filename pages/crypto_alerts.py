import requests
import streamlit as st
from dotenv import load_dotenv
import os
load_dotenv()
key = os.getenv("NEWS_FEED")



def main():


    st.title("Latest Crypto Alerts")
    unselected = st.text_input("Enter a coin name", value="Solana")


    # if selected:
    #     url = f"https://gnews.io/api/v4/search?q={selected.lower()}&lang=en&token=fdeeca1b2fc96d1114267107fd7dfd37"
    #     response = requests.get(url)
    #     data = response.json()
    if unselected:
        url = f"https://gnews.io/api/v4/search?q={unselected.lower()}&lang=en&token=fdeeca1b2fc96d1114267107fd7dfd37"
        response = requests.get(url)
        data = response.json()

    for article in data.get("articles", []):
        st.markdown("----")

        st.subheader(article.get("title", "No title"))

        if article.get("image"):
            st.image(article["image"])

        st.write(article.get("description", "No description available."))

        st.markdown(f"[Read More]({article.get('url', '#')})")

        source_name = article.get("source", {}).get("name", "Unknown Source")
        published_at = article.get("publishedAt", "Unknown Date")
        st.caption(f"Published by {source_name} on {published_at}")



if __name__ == "__main__":
    main()