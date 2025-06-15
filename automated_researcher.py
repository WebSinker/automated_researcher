import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import ollama

class AutomatedResearcher:
    def __init__(self, model_name="tinyllama", headless=False):
        """
        Initialize the automated researcher
        
        Args:
            model_name (str): Ollama model name to use
            headless (bool): Run browser in headless mode
        """
        self.model_name = model_name
        self.headless = headless
        self.driver = None
        self.research_data = []
        
    def setup_browser(self):
        """Setup and configure the browser with better anti-detection"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # Anti-detection arguments
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")  # Faster loading
        chrome_options.add_argument("--disable-javascript")  # Sometimes helps
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Remove automation indicators
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Add random window size
        import random
        width = random.randint(1200, 1920)
        height = random.randint(800, 1080)
        chrome_options.add_argument(f"--window-size={width},{height}")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # Remove webdriver property
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Add random delays and human-like behavior
        self.driver.implicitly_wait(random.uniform(1, 3))
        
    def simulate_typing(self, element, text, typing_speed=None):
        """
        Simulate human-like typing with random delays
        
        Args:
            element: Web element to type into
            text (str): Text to type
            typing_speed (float): Base delay between keystrokes
        """
        import random
        
        if typing_speed is None:
            typing_speed = random.uniform(0.05, 0.15)  # Random typing speed
        
        element.clear()
        
        # Random initial delay
        time.sleep(random.uniform(0.5, 1.5))
        
        for i, char in enumerate(text):
            element.send_keys(char)
            
            # Variable typing speed with occasional pauses
            if i % 5 == 0:  # Pause every 5 characters
                time.sleep(random.uniform(0.1, 0.3))
            else:
                time.sleep(random.uniform(typing_speed * 0.5, typing_speed * 1.5))
        
        # Random delay before submitting
        time.sleep(random.uniform(1, 2))
    
    def search_topic(self, query, num_results=5):
        """
        Perform automated search and collect results
        
        Args:
            query (str): Search query
            num_results (int): Number of results to collect
        """
        try:
            # Navigate to Google
            print("🌐 Navigating to Google...")
            self.driver.get("https://www.google.com")
            
            # Handle cookie consent if present
            try:
                time.sleep(2)
                cookie_buttons = [
                    "button[id*='accept']",
                    "button[id*='consent']",
                    "button:contains('Accept')",
                    "#L2AGLb",  # Google's "I agree" button
                    ".QS5gu"   # Alternative Google consent button
                ]
                
                for selector in cookie_buttons:
                    try:
                        button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if button.is_displayed():
                            button.click()
                            time.sleep(1)
                            break
                    except:
                        continue
            except:
                pass
            
            # Find search box and simulate typing
            search_selectors = ["input[name='q']", "textarea[name='q']", "#APjFqb"]
            search_box = None
            
            for selector in search_selectors:
                try:
                    search_box = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if search_box:
                        break
                except:
                    continue
            
            if not search_box:
                raise Exception("Could not find Google search box")
            
            print(f"🔍 Searching for: {query}")
            self.simulate_typing(search_box, query)
            search_box.send_keys(Keys.RETURN)
            
            # Wait for results to load with multiple possible indicators
            wait_selectors = ["#search", "#rso", ".g", "[data-ved]"]
            
            for selector in wait_selectors:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            # Additional wait for dynamic content
            time.sleep(3)
            
            # Debug: Save screenshot and page source
            try:
                self.driver.save_screenshot("debug_search_results.png")
                print("📸 Screenshot saved as debug_search_results.png")
                
                # Print page title for verification
                print(f"📄 Current page title: {self.driver.title}")
                
                # Check if we're actually on a search results page
                if "search" not in self.driver.current_url.lower():
                    print(f"⚠️ Warning: Current URL doesn't look like search results: {self.driver.current_url}")
                
            except Exception as e:
                print(f"Debug info error: {e}")
            
            # Extract search results
            results = self.extract_search_results(num_results)
            
            # If no results found, try alternative approach
            if not results:
                print("🔄 Trying alternative search approach...")
                results = self.alternative_search_extraction(num_results)
            
            return results
            
        except Exception as e:
            print(f"❌ Error during search: {e}")
            return []
    
    def alternative_search_extraction(self, num_results):
        """Alternative method to extract search results"""
        results = []
        
        try:
            # Get all clickable elements that might be search results
            all_links = self.driver.find_elements(By.XPATH, "//a[@href]")
            print(f"🔍 Found {len(all_links)} total links on page")
            
            for link in all_links:
                try:
                    href = link.get_attribute("href")
                    text = link.text.strip()
                    
                    # Use our text-based URL filter
                    if (href and 
                        self.is_text_based_url(href, text) and
                        len(text) > 15 and
                        not text.lower().startswith(("images", "videos", "news", "shopping", "maps"))):
                        
                        results.append({
                            "title": text[:100],
                            "url": href,
                            "snippet": f"Found via alternative extraction: {text[:150]}"
                        })
                        
                        print(f"📄 Alternative extraction found: {text[:50]}...")
                        
                        if len(results) >= num_results:
                            break
                            
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"❌ Alternative extraction failed: {e}")
        
        return results
    
    def is_text_based_url(self, url, title=""):
        """
        Check if URL points to text-based content (not media)
        
        Args:
            url (str): URL to check
            title (str): Title/text associated with the link
        
        Returns:
            bool: True if URL likely contains text content
        """
        if not url or not url.startswith("http"):
            return False
        
        # Banned domains and patterns
        banned_domains = [
            "youtube.com", "youtu.be", "vimeo.com", "dailymotion.com",
            "instagram.com", "facebook.com", "twitter.com", "tiktok.com",
            "pinterest.com", "flickr.com", "imgur.com",
            "maps.google", "images.google", "translate.google",
            "amazon.com/dp/", "ebay.com", "aliexpress.com",
            "spotify.com", "soundcloud.com", "apple.com/music",
            "netflix.com", "hulu.com", "disney.com"
        ]
        
        # Banned file extensions
        banned_extensions = [
            ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg",
            ".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm",
            ".mp3", ".wav", ".flac", ".aac", ".ogg",
            ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx",
            ".zip", ".rar", ".tar", ".gz"
        ]
        
        # Banned URL patterns
        banned_patterns = [
            "/images/", "/img/", "/video/", "/videos/", "/audio/",
            "/download/", "/file/", "/attachment/", "/media/",
            "webcache.googleusercontent.com", "google.com/search",
            "google.com/url?q=", "shopping", "maps", "flights"
        ]
        
        # Banned title keywords
        banned_title_keywords = [
            "video", "watch", "listen", "download", "image", "photo",
            "picture", "song", "music", "movie", "film", "playlist",
            "gallery", "album", "stream", "live", "podcast"
        ]
        
        url_lower = url.lower()
        title_lower = title.lower()
        
        # Check banned domains
        for domain in banned_domains:
            if domain in url_lower:
                print(f"🚫 Blocked domain: {domain} in {url}")
                return False
        
        # Check banned extensions
        for ext in banned_extensions:
            if url_lower.endswith(ext):
                print(f"🚫 Blocked file extension: {ext} in {url}")
                return False
        
        # Check banned patterns
        for pattern in banned_patterns:
            if pattern in url_lower:
                print(f"🚫 Blocked pattern: {pattern} in {url}")
                return False
        
        # Check banned title keywords
        for keyword in banned_title_keywords:
            if keyword in title_lower:
                print(f"🚫 Blocked title keyword: {keyword} in '{title}'")
                return False
        
        # Preferred domains (news, blogs, educational sites)
        preferred_domains = [
            "wikipedia.org", "britannica.com", "edu", ".gov",
            "reuters.com", "bbc.com", "cnn.com", "npr.org",
            "medium.com", "substack.com", "wordpress.com", "blogspot.com",
            "techcrunch.com", "wired.com", "arstechnica.com",
            "nature.com", "sciencedirect.com", "arxiv.org",
            "stackoverflow.com", "github.com"
        ]
        
        # Boost score for preferred domains
        for domain in preferred_domains:
            if domain in url_lower:
                print(f"✅ Preferred domain: {domain} in {url}")
                return True
        
        # If no specific red flags, likely text-based
        return True
    
    def extract_search_results(self, num_results):
        """Extract URLs and snippets from search results"""
        results = []
        
        # Wait for search results to load
        time.sleep(3)
        
        # Try multiple CSS selectors for Google search results
        possible_selectors = [
            "div.g",
            "div[data-ved]",
            ".g",
            "[data-ved] h3",
            "div.yuRUbf"
        ]
        
        search_results = []
        for selector in possible_selectors:
            try:
                search_results = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if search_results:
                    print(f"✅ Found {len(search_results)} results using selector: {selector}")
                    break
            except:
                continue
        
        if not search_results:
            print("❌ No search results found with any selector")
            # Try alternative approach - find all links
            all_links = self.driver.find_elements(By.TAG_NAME, "a")
            print(f"Found {len(all_links)} total links on page")
            
            for link in all_links[:num_results * 5]:  # Get more links to filter
                try:
                    href = link.get_attribute("href")
                    text = link.text.strip()
                    
                    if (href and self.is_text_based_url(href, text) and len(text) > 10):
                        results.append({
                            "title": text[:100],
                            "url": href,
                            "snippet": text[:200]
                        })
                        print(f"📄 Found valid link: {text[:50]}...")
                        
                        if len(results) >= num_results:
                            break
                            
                except Exception as e:
                    continue
            
            return results
        
        # Process found search results
        for i, result in enumerate(search_results[:num_results * 2]):  # Get extra to filter
            try:
                # Multiple ways to extract title
                title = "No title"
                title_selectors = ["h3", "a h3", "[role='heading']"]
                
                for selector in title_selectors:
                    try:
                        title_element = result.find_element(By.CSS_SELECTOR, selector)
                        if title_element and title_element.text:
                            title = title_element.text
                            break
                    except:
                        continue
                
                # Multiple ways to extract URL
                url = ""
                link_selectors = ["a", "a[href]", "h3 a"]
                
                for selector in link_selectors:
                    try:
                        link_element = result.find_element(By.CSS_SELECTOR, selector)
                        if link_element:
                            url = link_element.get_attribute("href")
                            break
                    except:
                        continue
                
                # Extract snippet
                snippet = ""
                snippet_selectors = [
                    "[data-ved] span",
                    ".VwiC3b",
                    ".s3v9rd",
                    "span"
                ]
                
                for selector in snippet_selectors:
                    try:
                        snippet_elements = result.find_elements(By.CSS_SELECTOR, selector)
                        for span in snippet_elements:
                            if span.text and len(span.text) > 30:
                                snippet = span.text
                                break
                        if snippet:
                            break
                    except:
                        continue
                
                # Only add if it's a text-based URL
                if url and self.is_text_based_url(url, title):
                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet
                    })
                    print(f"📄 Added valid result: {title}")
                    
                    # Stop when we have enough valid results
                    if len(results) >= num_results:
                        break
                else:
                    print(f"🚫 Filtered out: {title} ({url})")
                    
            except Exception as e:
                print(f"⚠️ Error extracting result {i}: {e}")
                continue
                
        return results
    
    def is_content_text_rich(self, content, min_words=50):
        """
        Check if content has enough meaningful text for analysis
        
        Args:
            content (str): Content to check
            min_words (int): Minimum number of words required
        
        Returns:
            bool: True if content is text-rich
        """
        if not content or len(content) < 100:
            return False
        
        # Count actual words (not just whitespace)
        words = content.split()
        word_count = len([word for word in words if len(word) > 2])
        
        if word_count < min_words:
            print(f"⚠️ Content too short: {word_count} words (need {min_words})")
            return False
        
        # Check for signs of non-text content
        low_quality_indicators = [
            "404", "not found", "page not found", "error",
            "access denied", "forbidden", "please enable javascript",
            "loading...", "please wait", "click here to continue"
        ]
        
        content_lower = content.lower()
        for indicator in low_quality_indicators:
            if indicator in content_lower:
                print(f"⚠️ Low quality content detected: {indicator}")
                return False
        
        # Check for good text-to-punctuation ratio
        text_chars = sum(1 for c in content if c.isalnum() or c.isspace())
        if text_chars / len(content) < 0.7:  # At least 70% text characters
            print("⚠️ Content appears to be mostly non-text")
            return False
        
        return True
    
    def scrape_content_with_browser(self, url, max_chars=5000):
        """
        Navigate to URL with browser and scrape content
        
        Args:
            url (str): URL to scrape
            max_chars (int): Maximum characters to extract
        """
        try:
            print(f"🌐 Navigating to: {url}")
            
            # Navigate to the URL
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Check if page is actually text-based content
            page_title = self.driver.title.lower()
            if any(media_word in page_title for media_word in 
                   ["video", "watch", "youtube", "image", "photo", "download"]):
                print(f"🚫 Skipping media page: {page_title}")
                return ""
            
            # Try to close any popups or cookie banners
            popup_selectors = [
                "button[aria-label*='close']",
                "button[aria-label*='Close']",
                ".close-button",
                ".cookie-banner button",
                "[id*='cookie'] button",
                ".modal-close",
                ".popup-close",
                "button:contains('Accept')",
                "button:contains('I agree')"
            ]
            
            for selector in popup_selectors:
                try:
                    popup = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if popup.is_displayed():
                        popup.click()
                        time.sleep(1)
                except:
                    continue
            
            # Extract text content from the page prioritizing main content
            content_selectors = [
                "article",
                ".main-content",
                ".content",
                "#content",
                ".post-content",
                ".entry-content",
                ".article-content",
                ".story-body",
                "main",
                ".container"
            ]
            
            content = ""
            for selector in content_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        content = elements[0].text
                        if self.is_content_text_rich(content):
                            break
                except:
                    continue
            
            # If no good content found, try body but with more filtering
            if not self.is_content_text_rich(content):
                try:
                    body_content = self.driver.find_element(By.TAG_NAME, "body").text
                    
                    # Remove navigation, header, footer text
                    lines = body_content.split('\n')
                    filtered_lines = []
                    
                    skip_keywords = [
                        "menu", "navigation", "nav", "header", "footer",
                        "subscribe", "newsletter", "follow us", "social media",
                        "cookie", "privacy policy", "terms", "copyright",
                        "loading", "please wait", "javascript"
                    ]
                    
                    for line in lines:
                        line = line.strip()
                        if (len(line) > 20 and  # Skip short lines
                            not any(skip in line.lower() for skip in skip_keywords)):
                            filtered_lines.append(line)
                    
                    content = ' '.join(filtered_lines)
                except:
                    content = ""
            
            # Final validation
            if self.is_content_text_rich(content, min_words=30):
                content = content[:max_chars] if len(content) > max_chars else content
                print(f"✅ Extracted {len(content)} characters of quality text")
                return content
            else:
                print(f"⚠️ Page content not suitable for analysis")
                return ""
            
        except Exception as e:
            print(f"❌ Error navigating to {url}: {e}")
            # Fallback to requests method
            return self.scrape_content(url, max_chars)
    
    def scrape_content(self, url, max_chars=5000):
        """
        Scrape content from a given URL using requests (fallback method)
        
        Args:
            url (str): URL to scrape
            max_chars (int): Maximum characters to extract
        """
        try:
            print(f"📖 Reading content from: {url}")
            
            # Use requests for faster content extraction
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            
            # Try to find main content areas
            content_areas = soup.find_all(['article', 'main', '.content', '.main-content'])
            
            if content_areas:
                text = ' '.join([area.get_text() for area in content_areas])
            else:
                text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:max_chars] if len(text) > max_chars else text
            
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return ""
    
    def analyze_with_ollama(self, content, query):
        """
        Analyze content using Ollama with fallback models
        
        Args:
            content (str): Content to analyze
            query (str): Original search query
        """
        # List of models to try (from smallest to largest)
        fallback_models = ["tinyllama", "phi", "mistral:7b-instruct-q4_0", self.model_name]
        
        # Remove duplicates and keep order
        models_to_try = []
        for model in fallback_models:
            if model not in models_to_try:
                models_to_try.append(model)
        
        prompt = f"""
        Analyze the following content related to the query: "{query}"
        
        Content:
        {content[:2000]}...  # Limit content length to reduce memory usage
        
        Please provide:
        1. Key insights and main points
        2. Important facts and statistics  
        3. Relevant conclusions
        4. How this relates to the original query
        
        Keep the analysis concise but comprehensive.
        """
        
        for model in models_to_try:
            try:
                print(f"🤖 Trying analysis with model: {model}")
                response = ollama.chat(
                    model=model,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                print(f"✅ Successfully analyzed with {model}")
                return response['message']['content']
                
            except Exception as e:
                error_msg = str(e).lower()
                if "memory" in error_msg or "system resources" in error_msg:
                    print(f"❌ {model} requires too much memory, trying smaller model...")
                    continue
                elif "not found" in error_msg or "model" in error_msg:
                    print(f"❌ Model {model} not found, trying next...")
                    continue
                else:
                    print(f"❌ Error with {model}: {e}")
                    continue
        
        # If all models fail, return basic analysis
        return f"Unable to analyze with AI models. Content summary: {content[:500]}..."
    
    def format_text_for_readability(self, text, max_line_length=80):
        """
        Format text with proper line wrapping and structure
        
        Args:
            text (str): Text to format
            max_line_length (int): Maximum characters per line
        
        Returns:
            str: Formatted text with proper line breaks
        """
        import textwrap
        
        # Split into paragraphs
        paragraphs = text.split('\n\n')
        formatted_paragraphs = []
        
        for paragraph in paragraphs:
            if paragraph.strip():
                # Handle numbered lists differently
                if paragraph.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '•', '-')):
                    # For lists, maintain indentation
                    lines = paragraph.split('\n')
                    formatted_lines = []
                    
                    for line in lines:
                        if line.strip():
                            if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '•', '-')):
                                # First line of list item
                                wrapped = textwrap.fill(line.strip(), 
                                                      width=max_line_length, 
                                                      initial_indent='', 
                                                      subsequent_indent='   ')
                            else:
                                # Continuation of list item
                                wrapped = textwrap.fill(line.strip(), 
                                                      width=max_line_length, 
                                                      initial_indent='   ', 
                                                      subsequent_indent='   ')
                            formatted_lines.append(wrapped)
                    
                    formatted_paragraphs.append('\n'.join(formatted_lines))
                else:
                    # Regular paragraph
                    wrapped = textwrap.fill(paragraph.strip(), width=max_line_length)
                    formatted_paragraphs.append(wrapped)
        
        return '\n\n'.join(formatted_paragraphs)
    
    def create_structured_report(self, query, research_results):
        """
        Create a well-formatted, readable research report
        
        Args:
            query (str): Original search query
            research_results (list): List of analyzed results
        
        Returns:
            str: Formatted report
        """
        from datetime import datetime
        
        # Report header
        header = f"""
{'='*80}
RESEARCH REPORT
{'='*80}

Query: {query}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Sources Analyzed: {len(research_results)}

{'='*80}
""".strip()
        
        # Executive Summary
        exec_summary = """
EXECUTIVE SUMMARY
-----------------
"""
        
        # Extract key points from all analyses for summary
        all_analyses = ' '.join([result.get('analysis', '') for result in research_results])
        summary_prompt = f"""
        Based on these research findings about "{query}", write a concise executive 
        summary (2-3 sentences) highlighting the most important insights:
        
        {all_analyses[:1500]}
        
        Keep it brief and focus on key takeaways.
        """
        
        try:
            # Generate executive summary
            models_to_try = ["tinyllama", "phi", "mistral:7b-instruct-q4_0", self.model_name]
            summary_text = "Research findings compiled from multiple sources."
            
            for model in models_to_try:
                try:
                    response = ollama.chat(
                        model=model,
                        messages=[{"role": "user", "content": summary_prompt}]
                    )
                    summary_text = response['message']['content']
                    break
                except:
                    continue
            
            exec_summary += self.format_text_for_readability(summary_text) + "\n"
            
        except:
            exec_summary += f"This report analyzes {len(research_results)} sources related to {query}.\n"
        
        # Key Findings Section
        key_findings = """
KEY FINDINGS
------------
"""
        
        for i, result in enumerate(research_results, 1):
            analysis = result.get('analysis', 'No analysis available')
            
            # Extract key points (first few sentences or bullet points)
            sentences = analysis.split('. ')
            key_points = '. '.join(sentences[:3]) + '.' if len(sentences) > 3 else analysis
            
            finding = f"""
{i}. {key_points}

"""
            key_findings += self.format_text_for_readability(finding)
        
        # Detailed Analysis Section
        detailed_analysis = """
DETAILED ANALYSIS
-----------------
"""
        
        for i, result in enumerate(research_results, 1):
            title = result.get('title', f'Source {i}')
            url = result.get('url', 'No URL')
            analysis = result.get('analysis', 'No analysis available')
            
            # Format URL for better readability
            if len(url) > 60:
                display_url = url[:57] + "..."
            else:
                display_url = url
            
            source_section = f"""
Source {i}: {title}
{'-' * min(len(f'Source {i}: {title}'), 78)}
URL: {display_url}

Analysis:
{analysis}

"""
            detailed_analysis += self.format_text_for_readability(source_section) + "\n"
        
        # Sources and References
        sources_section = """
SOURCES AND REFERENCES
----------------------
"""
        
        for i, result in enumerate(research_results, 1):
            title = result.get('title', f'Source {i}')
            url = result.get('url', 'No URL')
            
            source_ref = f"""
{i}. {title}
   URL: {url}

"""
            sources_section += self.format_text_for_readability(source_ref)
        
        # Conclusions
        conclusions = """
CONCLUSIONS
-----------
"""
        
        conclusion_prompt = f"""
        Based on the research about "{query}", provide 2-3 key conclusions and 
        recommendations in a concise format. Focus on actionable insights.
        
        Research summary: {all_analyses[:1000]}
        """
        
        try:
            for model in ["tinyllama", "phi", "mistral:7b-instruct-q4_0", self.model_name]:
                try:
                    response = ollama.chat(
                        model=model,
                        messages=[{"role": "user", "content": conclusion_prompt}]
                    )
                    conclusion_text = response['message']['content']
                    break
                except:
                    continue
            else:
                conclusion_text = f"The research on {query} reveals multiple important aspects that require further consideration and implementation."
            
            conclusions += self.format_text_for_readability(conclusion_text)
            
        except:
            conclusions += f"Further research and analysis of {query} is recommended based on the findings above."
        
        # Footer
        footer = f"""

{'='*80}
Report generated by Automated Research Assistant
{'='*80}
"""
        
        # Combine all sections
        full_report = (header + "\n\n" + 
                      exec_summary + "\n\n" + 
                      key_findings + "\n\n" + 
                      detailed_analysis + "\n\n" + 
                      sources_section + "\n\n" + 
                      conclusions + "\n" + 
                      footer)
        
        return full_report
    
    def conduct_research(self, query, num_sources=3):
        """
        Main method to conduct complete research
        
        Args:
            query (str): Research topic/query
            num_sources (int): Number of sources to analyze
        """
        print(f"🚀 Starting automated research for: {query}")
        print("=" * 60)
        
        try:
            # Setup browser
            self.setup_browser()
            
            # Search for topic
            search_results = self.search_topic(query, num_sources)
            
            if not search_results:
                print("❌ No search results found")
                return None
            
            # Analyze each source
            research_results = []
            for i, result in enumerate(search_results, 1):
                print(f"\n📊 Processing source {i}/{len(search_results)}: {result['title']}")
                
                # Use browser-based scraping first, fallback to requests
                content = self.scrape_content_with_browser(result['url'])
                
                if content and len(content) > 100:  # Only analyze if we got meaningful content
                    analysis = self.analyze_with_ollama(content, query)
                    research_results.append({
                        'title': result['title'],
                        'url': result['url'],
                        'content': content[:1000] + "..." if len(content) > 1000 else content,
                        'analysis': analysis
                    })
                    print(f"✅ Successfully analyzed: {result['title']}")
                else:
                    print(f"⚠️ Insufficient content from: {result['title']}")
                
                # Add delay between requests to be respectful
                time.sleep(2)
            
            # Generate final report
            if research_results:
                print("📊 Creating structured report...")
                final_report = self.create_structured_report(query, research_results)
                
                # Save report
                self.save_report(query, final_report, research_results)
                
                print("✅ Research completed successfully!")
                return final_report
            else:
                print("❌ No content could be analyzed")
                return None
                
        except Exception as e:
            print(f"❌ Research failed: {e}")
            return None
        
        finally:
            if self.driver:
                self.driver.quit()
    
    def save_report(self, query, report, research_data, formats=['txt', 'md']):
        """Save the research report in multiple formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as text file (readable format)
        if 'txt' in formats:
            report_filename = f"research_report_{timestamp}.txt"
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 Report saved as: {report_filename}")
        
        # Save as markdown (for better formatting)
        if 'md' in formats:
            md_filename = f"research_report_{timestamp}.md"
            md_report = self.convert_to_markdown(report, query, research_data)
            with open(md_filename, 'w', encoding='utf-8') as f:
                f.write(md_report)
            print(f"📝 Markdown report saved as: {md_filename}")
        
        # Save raw data as JSON
        data_filename = f"research_data_{timestamp}.json"
        with open(data_filename, 'w', encoding='utf-8') as f:
            json.dump({
                'query': query,
                'timestamp': timestamp,
                'sources': research_data,
                'report': report
            }, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Data saved as: {data_filename}")
    
    def convert_to_markdown(self, report, query, research_data):
        """Convert report to markdown format"""
        from datetime import datetime
        
        # Basic markdown conversion
        md_report = f"""# Research Report: {query}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Sources Analyzed:** {len(research_data)}

---

{report}

---

## Source Links

"""
        
        # Add clickable source links
        for i, result in enumerate(research_data, 1):
            title = result.get('title', f'Source {i}')
            url = result.get('url', '#')
            md_report += f"{i}. [{title}]({url})\n"
        
        md_report += f"""

---
*Report generated by Automated Research Assistant*
"""
        
        return md_report

# Usage example
if __name__ == "__main__":
    # Initialize the researcher
    researcher = AutomatedResearcher(
        model_name="llama2",  # Change to your preferred Ollama model
        headless=False  # Set to True to hide browser window
    )
    
    # Conduct research
    query = input("Enter your research topic: ")
    report = researcher.conduct_research(query, num_sources=3)
    
    if report:
        print("\n" + "="*60)
        print("FINAL REPORT")
        print("="*60)
        print(report)