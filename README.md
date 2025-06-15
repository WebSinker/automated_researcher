# Automated Researcher

A powerful Python-based automated research tool that leverages AI models and web scraping to conduct comprehensive research on any given topic. (PS: just a program for fun where i just want to develop a system that can automatically open up browser and perform action on it)

## Features

- 🔍 **Intelligent Web Searching**: Automatically searches and filters web content for high-quality, text-based sources
- 🤖 **AI-Powered Analysis**: Uses Ollama models for content analysis with automatic fallback to smaller models
- 🌐 **Smart Web Scraping**: Browser-based scraping with anti-detection measures and fallback to requests
- 📊 **Structured Reports**: Generates well-formatted research reports with executive summaries and detailed analysis
- 🎯 **Content Filtering**: Advanced URL and content filtering to focus on high-quality, text-based sources
- 💾 **Multiple Output Formats**: Saves reports in TXT, MD, and JSON formats
- 🎨 **Customizable Research Profiles**: Pre-configured settings for academic, news, and tech research

## Requirements

- Python 3.x
- Chrome Browser
- [Ollama](https://ollama.ai/) with at least one of these models:
  - tinyllama (~637MB)
  - phi (~1.6GB)
  - mistral:7b-instruct-q4_0 (~4GB)
  - llama2:7b-chat-q4_0 (~3.8GB)
  - OR your own preferences

## Installation

1. Clone the repository
2. Install required packages:
```bash
pip install selenium beautifulsoup4 requests ollama psutil
```
3. Install at least one Ollama model:
```bash
ollama pull tinyllama 
```

## Usage

### Basic Usage

```python
from automated_researcher import AutomatedResearcher

# Initialize researcher
researcher = AutomatedResearcher(
    model_name="mistral:7b-instruct-q4_0",
    headless=False  # Set to True to hide browser
)

# Conduct research
report = researcher.conduct_research(
    query="artificial intelligence applications in healthcare",
    num_sources=3
)
```

### With Research Profiles

```python
# Use pre-configured academic research profile
researcher = AutomatedResearcher(**ResearchProfiles.ACADEMIC)
report = researcher.conduct_research("quantum computing applications")
```

### Custom Source Filtering

```python
class CustomResearcher(AutomatedResearcher):
    def is_text_based_url(self, url, title=""):
        if not super().is_text_based_url(url, title):
            return False
            
        # Add custom preferences
        preferred_domains = [
            "arxiv.org", "nature.com", "science.org",
            "ieee.org", "acm.org"
        ]
        
        return any(domain in url.lower() for domain in preferred_domains)

researcher = CustomResearcher(model_name="llama2")
```

## Testing and Memory Management

The project includes a `modelTesting.py` script to:
- Check available system memory
- Test which models work on your system
- Run memory-optimized research

```python
python modelTesting.py
```

## Examples

See `Process.py` for various usage examples including:
- Filtered research with text-only sources
- Batch research with categories
- Academic research with custom source preferences

## Report Format

Generated reports include:
- Executive Summary
- Key Findings
- Detailed Analysis of Each Source
- Sources and References
- Conclusions and Recommendations

## Notes

- Remember to respect websites' terms of service and robots.txt
- Add delays between requests to avoid overloading servers
- Consider memory requirements when choosing AI models
- Use headless mode for batch processing
- Check source validity with is_text_based_url() before analysis

## License

This project is open source and available under the MIT License.

## Contributing

Contributions, issues, and feature requests are welcome!
