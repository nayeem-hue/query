from flask import Flask, render_template, request, jsonify
import wikipediaapi
from sentence_transformers import SentenceTransformer, util
import torch
import re
import requests
from bs4 import BeautifulSoup
import json
import os
from spellchecker import SpellChecker
from fuzzywuzzy import fuzz
from googlesearch import search
import time
from urllib.parse import unquote

app = Flask(__name__)

# Create a directory for storing images if it doesn't exist
os.makedirs(os.path.join('static', 'images'), exist_ok=True)

class WikiQA:
    def __init__(self):
        self.wiki = wikipediaapi.Wikipedia('WikiQA (khaja@example.com)', 'en')
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.spell = SpellChecker()
        
    def get_google_results(self, query, num_results=3):
        """Get relevant information from Google search results."""
        search_results = []
        try:
            # Search both Wikipedia and general web
            wiki_query = f"{query} site:wikipedia.org"
            web_query = f"{query} facts information"
            
            # Collect Wikipedia results
            wiki_results = list(search(wiki_query, num_results=num_results))
            
            # Collect general web results
            web_results = list(search(web_query, num_results=num_results))
            
            # Combine and process results
            all_results = wiki_results + web_results
            for url in all_results:
                if 'wikipedia.org/wiki/' in url:
                    # Extract Wikipedia title
                    title = unquote(url.split('/')[-1].replace('_', ' '))
                    page = self.wiki.page(title)
                    if page.exists():
                        search_results.append({
                            'title': title,
                            'summary': page.summary[:500],
                            'url': url,
                            'source': 'Wikipedia'
                        })
                else:
                    # For non-Wikipedia results, just store the URL
                    search_results.append({
                        'title': url.split('//')[-1].split('/')[0],
                        'url': url,
                        'source': 'Web'
                    })
            
            return search_results
        except Exception as e:
            print(f"Error in Google search: {e}")
            return []

    def get_comprehensive_answer(self, question, topic):
        """Get comprehensive answer combining Wikipedia and Google results."""
        try:
            # Get Wikipedia content
            wiki_page = self.wiki.page(topic)
            main_answer = wiki_page.summary if wiki_page.exists() else ""
            
            # Get additional sections from Wikipedia
            sections = []
            if wiki_page.exists():
                for section in wiki_page.sections:
                    if len(section.text.strip()) > 100:  # Only include substantial sections
                        sections.append({
                            'title': section.title,
                            'content': section.text[:300] + '...' if len(section.text) > 300 else section.text
                        })
            
            # Get Google results
            google_results = self.get_google_results(f"{topic} {question}")
            
            # Combine all information
            comprehensive_answer = {
                'main_answer': main_answer,
                'sections': sections[:3],  # Top 3 most relevant sections
                'additional_sources': google_results,
                'topic': topic
            }
            
            return comprehensive_answer
            
        except Exception as e:
            print(f"Error getting comprehensive answer: {e}")
            return None

    def correct_spelling(self, text):
        """Correct spelling mistakes in the text."""
        words = text.split()
        corrected_words = []
        
        for word in words:
            if not word[0].isupper():
                corrected = self.spell.correction(word)
                if corrected:
                    word = corrected
            corrected_words.append(word)
        
        return ' '.join(corrected_words)

    def extract_topic_from_question(self, question):
        """Extract topic from question with spell correction."""
        corrected_question = self.correct_spelling(question)
        words = corrected_question.split()
        potential_topics = []
        
        current_topic = []
        for word in words:
            if word[0].isupper() and word.lower() not in ['who', 'what', 'when', 'where', 'why', 'how']:
                current_topic.append(word)
            elif current_topic:
                potential_topics.append(' '.join(current_topic))
                current_topic = []
        
        if current_topic:
            potential_topics.append(' '.join(current_topic))

        # Try each potential topic
        for topic in potential_topics:
            page = self.wiki.page(topic)
            if page.exists():
                return topic

        # If no topic found, try the whole question
        search_terms = re.sub(r'^(who|what|when|where|why|how)\s+', '', corrected_question.lower())
        search_terms = re.sub(r'\?+$', '', search_terms)
        
        # Try Google search to find the most relevant topic
        google_results = self.get_google_results(search_terms, num_results=1)
        if google_results and 'wikipedia.org/wiki/' in google_results[0]['url']:
            return google_results[0]['title']
            
        return search_terms

    def get_wiki_images(self, topic):
        """Get images related to the topic from Wikipedia."""
        try:
            url = f"https://en.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "format": "json",
                "titles": topic,
                "prop": "images|pageimages",
                "imlimit": "5",
                "pithumbsize": "300"
            }
            response = requests.get(url, params=params)
            data = response.json()
            
            page_id = list(data['query']['pages'].keys())[0]
            page_data = data['query']['pages'][page_id]
            
            images = []
            if 'thumbnail' in page_data:
                images.append(page_data['thumbnail']['source'])
            
            if 'images' in page_data:
                for img in page_data['images']:
                    if img['title'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        img_params = {
                            "action": "query",
                            "format": "json",
                            "titles": img['title'],
                            "prop": "imageinfo",
                            "iiprop": "url",
                            "iiurlwidth": "300"
                        }
                        img_response = requests.get(url, params=img_params)
                        img_data = img_response.json()
                        img_page = list(img_data['query']['pages'].values())[0]
                        if 'imageinfo' in img_page:
                            img_url = img_page['imageinfo'][0]['url']
                            if not any(img_url in x for x in images):
                                images.append(img_url)
                                if len(images) >= 3:
                                    break
            
            return images[:3]
        except Exception as e:
            print(f"Error fetching images: {e}")
            return []

# Initialize WikiQA
qa_system = WikiQA()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question')
    
    if not question:
        return jsonify({
            'answer': 'Please provide a question.',
            'images': [],
            'corrected_question': None
        })
    
    # Extract topic and get comprehensive answer
    topic = qa_system.extract_topic_from_question(question)
    comprehensive_answer = qa_system.get_comprehensive_answer(question, topic)
    
    if not comprehensive_answer:
        return jsonify({
            'answer': f"Sorry, I couldn't find relevant information to answer your question. Try rephrasing it with more specific terms.",
            'images': [],
            'corrected_question': qa_system.correct_spelling(question)
        })
    
    # Get related images
    images = qa_system.get_wiki_images(topic)
    
    # Check if question was corrected
    corrected_question = qa_system.correct_spelling(question)
    show_correction = corrected_question.lower() != question.lower()
    
    return jsonify({
        'answer': comprehensive_answer,
        'images': images,
        'corrected_question': corrected_question if show_correction else None
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
