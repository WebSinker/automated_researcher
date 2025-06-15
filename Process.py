# Updated usage examples with improved filtering

from automated_researcher import AutomatedResearcher

def run_filtered_research():
    """Example of running research with text-only filtering"""
    
    # Initialize researcher with filtering enabled
    researcher = AutomatedResearcher(
        model_name="llama2",
        headless=False  # Set True to hide browser
    )
    
    # Research topics
    queries = [
        "artificial intelligence trends 2024",
        "renewable energy technologies",
        "quantum computing applications",
        "machine learning healthcare",
        "blockchain security"
    ]
    
    for query in queries:
        print(f"\n{'='*60}")
        print(f"🔍 RESEARCHING: {query}")
        print(f"{'='*60}")
        
        report = researcher.conduct_research(
            query=query,
            num_sources=4  # Will filter to get 4 text-based sources
        )
        
        if report:
            # Save individual reports
            filename = f"report_{query.replace(' ', '_')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"💾 Report saved: {filename}")
        
        print(f"✅ Completed: {query}\n")

def test_url_filtering_live():
    """Test the filtering with real search results"""
    
    researcher = AutomatedResearcher(model_name="llama2")
    researcher.setup_browser()
    
    try:
        # Perform a search
        results = researcher.search_topic("machine learning tutorial", num_results=10)
        
        print(f"🔍 Found {len(results)} filtered results:")
        print("="*60)
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   Snippet: {result['snippet'][:100]}...")
            print()
            
            # Test if we can get good content
            is_valid = researcher.is_text_based_url(result['url'], result['title'])
            print(f"   ✅ Valid text source: {is_valid}")
            print("-" * 40)
    
    finally:
        researcher.driver.quit()

def batch_research_with_categories():
    """Research multiple topics with category-based filtering"""
    
    research_topics = {
        "Technology": [
            "artificial intelligence ethics",
            "cloud computing security",
            "5G network applications"
        ],
        "Science": [
            "climate change solutions",
            "gene therapy advances",
            "space exploration technology"
        ],
        "Business": [
            "remote work productivity",
            "cryptocurrency regulation",
            "sustainable business practices"
        ]
    }
    
    for category, topics in research_topics.items():
        print(f"\n🏷️ CATEGORY: {category}")
        print("="*50)
        
        for topic in topics:
            researcher = AutomatedResearcher(
                model_name="llama2",
                headless=True  # Run in background for batch processing
            )
            
            print(f"📝 Researching: {topic}")
            report = researcher.conduct_research(topic, num_sources=3)
            
            if report:
                # Organize by category
                import os
                os.makedirs(category, exist_ok=True)
                
                filename = f"{category}/{topic.replace(' ', '_')}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"CATEGORY: {category}\n")
                    f.write(f"TOPIC: {topic}\n")
                    f.write("="*60 + "\n\n")
                    f.write(report)
                
                print(f"✅ Saved: {filename}")
            else:
                print(f"❌ Failed: {topic}")

def custom_source_research():
    """Research with custom source preferences"""
    
    class CustomResearcher(AutomatedResearcher):
        def is_text_based_url(self, url, title=""):
            """Override with custom filtering rules"""
            
            # Call parent method first
            if not super().is_text_based_url(url, title):
                return False
            
            # Add custom preferences
            highly_preferred = [
                "arxiv.org", "nature.com", "science.org",
                "ieee.org", "acm.org", "scholar.google.com"
            ]
            
            # Boost academic sources
            for domain in highly_preferred:
                if domain in url.lower():
                    print(f"🎯 High priority academic source: {domain}")
                    return True
            
            # Additional custom filtering
            avoid_domains = [
                "quora.com", "answers.com", "yahoo.com/answers"
            ]
            
            for domain in avoid_domains:
                if domain in url.lower():
                    print(f"🚫 Avoiding low-quality source: {domain}")
                    return False
            
            return True
    
    # Use custom researcher
    researcher = CustomResearcher(model_name="llama2")
    
    academic_topics = [
        "machine learning algorithms comparison",
        "quantum computing theoretical foundations",
        "neural network architecture optimization"
    ]
    
    for topic in academic_topics:
        print(f"\n🎓 Academic Research: {topic}")
        report = researcher.conduct_research(topic, num_sources=5)
        
        if report:
            with open(f"academic_{topic.replace(' ', '_')}.txt", 'w') as f:
                f.write(report)
            print("✅ Academic report generated")

# Configuration for different research types
class ResearchProfiles:
    """Pre-configured research profiles for different use cases"""
    
    ACADEMIC = {
        "model_name": "llama2",
        "headless": True,
        "num_sources": 5,
        "preferred_domains": [
            "arxiv.org", "nature.com", "science.org", 
            "ieee.org", "acm.org", ".edu"
        ]
    }
    
    NEWS = {
        "model_name": "llama2", 
        "headless": False,
        "num_sources": 3,
        "preferred_domains": [
            "reuters.com", "bbc.com", "npr.org",
            "ap.org", "cnn.com"
        ]
    }
    
    TECH = {
        "model_name": "llama2",
        "headless": True, 
        "num_sources": 4,
        "preferred_domains": [
            "techcrunch.com", "wired.com", "arstechnica.com",
            "theverge.com", "engadget.com"
        ]
    }

if __name__ == "__main__":
    # Run different types of research
    # print("🚀 Starting filtered research examples...")
    
    # # Test URL filtering first
    # print("\n1. Testing URL filtering...")
    # test_url_filtering_live()
    
    # Run single research
    print("\n2. Single topic research...")
    researcher = AutomatedResearcher(model_name="mistral:7b-instruct-q4_0")
    report = researcher.conduct_research("artificial intelligence applications in healthcare")
    
    # # Batch research
    # print("\n3. Batch research...")
    # batch_research_with_categories()
    
    print("\n✅ All research examples completed!")