from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.animation import Animation
import os
import sys
import random
import re
import requests
from bs4 import BeautifulSoup
from googlesearch import search

# Function to clean up scraped text
def clean_text(text):
    text = re.sub(r"\s+", " ", text)  # Remove extra spaces
    text = re.sub(r"\[.*?\]", "", text)  # Remove citation references
    return text.strip()

# Function to fetch code snippets
def fetch_code_snippet(query):
    search_query = f"{query} site:stackoverflow.com OR site:github.com OR site:geeksforgeeks.org OR site:w3schools.com"
    try:
        results = search(search_query, num_results=5)
        for url in results:
            try:
                response = requests.get(url, timeout=5)
                soup = BeautifulSoup(response.text, "html.parser")
                code_blocks = soup.find_all("code")
                for code in code_blocks:
                    code_text = clean_text(code.get_text())
                    if len(code_text.split()) > 5:
                        return f"Here's a possible solution from {url}:\n\n```{code_text}```"
            except Exception:
                continue
    except Exception:
        return "I couldn't find an exact code snippet, but I can help guide you!"
    return "I searched but didn't find an exact match. Try rephrasing!"

# Function to fetch Reddit responses
def fetch_reddit_response(query):
    search_query = f"{query} site:reddit.com"
    try:
        results = search(search_query, num_results=5)
        for url in results:
            try:
                response = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
                soup = BeautifulSoup(response.text, "html.parser")
                comments = soup.find_all("p")
                for comment in comments:
                    text = clean_text(comment.get_text())
                    if len(text.split()) > 10:
                        return f"Here's a Reddit response from {url}:\n\n{text}"
            except Exception:
                continue
    except Exception:
        return "I couldn't find any relevant Reddit posts."
    return "I searched Reddit but didn't find a perfect answer. Try rephrasing!"

# Function to fetch general Google responses
def fetch_google_response(query):
    try:
        results = search(query, num_results=5)
        for url in results:
            try:
                response = requests.get(url, timeout=5)
                soup = BeautifulSoup(response.text, "html.parser")
                paragraphs = soup.find_all("p")
                for p in paragraphs:
                    text = clean_text(p.get_text())
                    if len(text.split()) > 10 and "subscribe" not in text.lower():
                        return text
            except Exception:
                continue
    except Exception:
        return "I couldn't find an exact answer, but I can help figure it out!"
    return "I searched but didn't find a perfect match. Try rephrasing!"

# Function to generate chatbot response
def generate_response(user_input):
    if re.search(r"\b(hi|hello|hey)\b", user_input, re.IGNORECASE):
        return random.choice(["Hey there!", "Hello! How can I assist you today?", "Hi! Need help with something?"])
    elif re.search(r"\b(how are you)\b", user_input, re.IGNORECASE):
        return "I'm just a chatbot, but I'm here to help! How about you?"
    elif re.search(r"\b(who are you|what is your name)\b", user_input, re.IGNORECASE):
        return "I'm Google AI, your chatbot assistant!"
    elif re.search(r"\b(exit|quit|bye)\b", user_input, re.IGNORECASE):
        return "Goodbye! Have a great day!"
    
    if re.search(r"\b(code|example|script|program|how to)\b", user_input, re.IGNORECASE):
        return fetch_code_snippet(user_input)
    
    if "reddit" in user_input.lower():
        return fetch_reddit_response(user_input)
    
    return fetch_google_response(user_input)

# Kivy App Class
class ChatBotApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        
        # Chatbot Name
        chatbot_label = Label(text="Google AI Chatbot", size_hint_y=None, height=50, font_size=24, bold=True)
        layout.add_widget(chatbot_label)
        
        # Scrollable chat display
        self.chat_display = Label(text="Welcome to Google AI Chatbot!\n", size_hint_y=None, text_size=(400, None), halign="left", valign="top")
        self.scroll_view = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.scroll_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.scroll_layout.add_widget(self.chat_display)
        self.scroll_view.add_widget(self.scroll_layout)
        layout.add_widget(self.scroll_view)
        
        # Input and Send Button
        input_layout = BoxLayout(size_hint_y=None, height=50)
        self.user_input = TextInput(size_hint_x=0.8, multiline=False)
        self.send_button = Button(text="Send", size_hint_x=0.2)
        self.send_button.bind(on_press=self.send_message)
        input_layout.add_widget(self.user_input)
        input_layout.add_widget(self.send_button)
        layout.add_widget(input_layout)
        
        return layout

    def send_message(self, instance):
        user_text = self.user_input.text.strip()
        if user_text == "":
            return
        
        self.chat_display.text += f"\nYou: {user_text}"  # Display user message
        response = generate_response(user_text)
        self.chat_display.text += f"\nGoogle AI: {response}\n"  # Display bot response
        self.user_input.text = ""  # Clear input field
        
        # Adjust scroll height
        self.scroll_layout.height = self.chat_display.texture_size[1]
        self.scroll_view.scroll_y = 0
        
        # Smooth Scroll Animation
        anim = Animation(scroll_y=0, duration=0.2)
        anim.start(self.scroll_view)

# Run the Kivy app
if __name__ == "__main__":
    ChatBotApp().run()
