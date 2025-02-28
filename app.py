import os
from dotenv import load_dotenv
import streamlit as st
from langchain.llms import Ollama
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from datetime import datetime
import requests
from collections import Counter
import re

# Load environment variables from .env file
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="AI & Data Analytics Newsletter Generator",
    page_icon="📰",
    layout="wide"
)

# Initialize session state variables if they don't exist
if 'newsletter_content' not in st.session_state:
    st.session_state.newsletter_content = ""
if 'memory' not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

# Updated prompt templates to include instruction about think tags
NEWSLETTER_TEMPLATE = """
Write a professional AI and Data Analytics newsletter with the following topic:
{user_input}

Format it with:
1. Headline
2. Introduction
3. Main content with subsections
4. Key takeaways

Write in a clear, professional style. Provide the newsletter content directly without any meta-commentary.
If you need to think through your process, wrap that text in <think> tags.
"""

REFINEMENT_TEMPLATE = """
Here is a newsletter section:
{current_content}

Revise it according to these instructions:
{refinement_instructions}

Provide only the revised content without any explanations.
If you need to think through your process, wrap that text in <think> tags.
"""

# New prompt template for making content entertaining
ENTERTAINMENT_TEMPLATE = """
Here is a newsletter section:
{current_content}

Revise it to make it more entertaining and engaging for readers interested in AI and Data Analytics. Use a lively tone and add interesting anecdotes or examples where appropriate.

Provide only the revised content without any explanations.
If you need to think through your process, wrap that text in <think> tags.
"""

# Fetch the News API key from environment variables
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

def initialize_llm():
    """Initialize the Ollama language model."""
    try:
        return Ollama(
            model="INSERT_MODEL",  # or any other model you have in Ollama
            base_url="http://localhost:11434",  # default Ollama API URL
            temperature=0.7
        )
    except Exception as e:
        st.error(f"Error connecting to Ollama: {str(e)}")
        st.error("Please make sure Ollama is running locally (http://localhost:11434)")
        st.stop()

def generate_newsletter(user_input: str, llm) -> str:
    """Generate initial newsletter draft based on user input."""
    prompt = ChatPromptTemplate.from_template(NEWSLETTER_TEMPLATE)
    chain = LLMChain(llm=llm, prompt=prompt)
    
    try:
        result = chain.run(user_input=user_input)
        return result
    except Exception as e:
        st.error(f"Error generating newsletter: {str(e)}")
        return ""

def refine_newsletter(current_content: str, refinement_instructions: str, llm) -> str:
    """Refine specific sections of the newsletter based on user feedback."""
    prompt = ChatPromptTemplate.from_template(REFINEMENT_TEMPLATE)
    chain = LLMChain(llm=llm, prompt=prompt)
    
    try:
        result = chain.run(
            current_content=current_content,
            refinement_instructions=refinement_instructions
        )
        return result
    except Exception as e:
        st.error(f"Error refining newsletter: {str(e)}")
        return current_content

def enhance_newsletter(current_content: str, llm) -> str:
    """Enhance the newsletter content to make it more entertaining."""
    prompt = ChatPromptTemplate.from_template(ENTERTAINMENT_TEMPLATE)
    chain = LLMChain(llm=llm, prompt=prompt)
    
    try:
        result = chain.run(current_content=current_content)
        return result
    except Exception as e:
        st.error(f"Error enhancing newsletter: {str(e)}")
        return current_content

def fetch_news_articles(query: str, api_key: str) -> list:
    """Fetch recent news articles related to AI and Data Analytics."""
    url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&pageSize=5&apiKey={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        articles = response.json().get('articles', [])
        return articles
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching news articles: {str(e)}")
        return []

def get_top_news_orgs(articles: list) -> list:
    """Get the top news organizations from the articles."""
    sources = [article['source']['name'] for article in articles]
    source_count = Counter(sources)
    top_sources = source_count.most_common(3)  # Get top 3 news organizations
    return top_sources

def create_markdown(content: str) -> str:
    """Create a Markdown string from the newsletter content."""
    # Remove any chain-of-thought content
    cleaned_content = remove_think_content(content)
    
    markdown_content = "# AI & Data Analytics Newsletter\n\n"
    markdown_content += f"**Generated on {datetime.now().strftime('%B %d, %Y')}**\n\n"
    markdown_content += cleaned_content
    return markdown_content

def remove_think_content(text: str) -> str:
    """
    Removes all content (including the <think> and </think> tags)
    from the provided text.
    """
    # Make sure we're handling the pattern correctly
    pattern = r'<think>[\s\S]*?</think>'
    cleaned_text = re.sub(pattern, "", text)
    
    # Double-check for any remaining think tags
    if '<think>' in cleaned_text or '</think>' in cleaned_text:
        # Try a more aggressive approach if tags still exist
        cleaned_text = re.sub(r'<think>.*?</think>', "", cleaned_text, flags=re.DOTALL)
    
    return cleaned_text

def main():
    # Initialize LLM
    llm = initialize_llm()
    
    # Sidebar for LLM settings
    st.sidebar.header("LLM Settings")
    temperature = st.sidebar.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Adjust the randomness of the LLM's output. Lower values make the output more deterministic."
    )
    
    # Update LLM with new temperature
    llm.temperature = temperature

    # App header
    st.title("📰 AI & Data Analytics Newsletter Generator")
    st.markdown("""
    Create professional newsletters about AI and Data Analytics topics.
    Provide a topic or context, and the AI will generate a structured newsletter draft.
    You can then refine specific sections and export to Markdown.
    """)
    
    # News Search Section
    st.markdown("### Recent News on AI and Data Analytics")
    news_query = st.text_input("Enter a topic to search for recent news articles:", "AI and Data Analytics")
    
    if st.button("Search News"):
        with st.spinner("Fetching news articles..."):
            articles = fetch_news_articles(news_query, NEWS_API_KEY)
            if articles:
                st.markdown("#### Top News Organizations")
                top_orgs = get_top_news_orgs(articles)
                for org, count in top_orgs:
                    st.markdown(f"- **{org}**: {count} articles")
                
                st.markdown("#### Articles")
                for article in articles:
                    st.markdown(f"**{article['title']}**")
                    st.markdown(f"*{article['source']['name']} - {article['publishedAt']}*")
                    st.markdown(article['description'])
                    st.markdown(f"[Read more]({article['url']})")
                    st.markdown("---")
            else:
                st.info("No articles found for the given topic.")
    
    # User input section
    user_input = st.text_area(
        "Enter your newsletter topic or context:",
        height=100,
        placeholder="Example: Latest trends in machine learning research and real-world analytics use cases"
    )
    
    # Generate and enhance newsletter
    if st.button("Generate Newsletter"):
        with st.spinner("Generating and enhancing newsletter..."):
            # Generate the initial newsletter
            initial_content = generate_newsletter(user_input, llm)
            # Automatically enhance the content
            st.session_state.newsletter_content = enhance_newsletter(initial_content, llm)
    
    # Display and edit newsletter
    if st.session_state.newsletter_content:
        st.markdown("### Generated Newsletter")
        st.markdown(st.session_state.newsletter_content)
        
        # Export to Markdown button
        if st.button("Export to Markdown"):
            markdown_data = create_markdown(st.session_state.newsletter_content)
            file_name = f"newsletter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            st.download_button(
                label="Download Markdown",
                data=markdown_data,
                file_name=file_name,
                mime="text/markdown"
            )
        
        # Refinement section
        st.markdown("### Refine Newsletter")
        refinement_instructions = st.text_area(
            "Enter your refinement instructions:",
            height=100,
            placeholder="Example: Make the introduction more concise and add bullet points to the main topics"
        )
        
        if st.button("Refine Content"):
            with st.spinner("Refining newsletter..."):
                st.session_state.newsletter_content = refine_newsletter(
                    st.session_state.newsletter_content,
                    refinement_instructions,
                    llm
                )

if __name__ == "__main__":
    main() 
