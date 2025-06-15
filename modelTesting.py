#!/usr/bin/env python3
"""
Memory-optimized test script for low-memory systems
"""

import ollama
from automated_researcher import AutomatedResearcher

def test_available_models():
    """Test which models work with current memory"""
    
    models_to_test = [
        "tinyllama",           # ~637MB
        "phi",                # ~1.6GB
        "mistral:7b-instruct-q4_0",  # ~4GB
        "llama2:7b-chat-q4_0"        # ~3.8GB
    ]
    
    working_models = []
    
    for model in models_to_test:
        try:
            print(f"🧪 Testing {model}...")
            
            # Test with a simple prompt
            response = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": "Hello, this is a test. Respond briefly."}]
            )
            
            if response and 'message' in response:
                print(f"✅ {model} works!")
                working_models.append(model)
            else:
                print(f"❌ {model} failed - no response")
                
        except Exception as e:
            error_msg = str(e).lower()
            if "memory" in error_msg:
                print(f"❌ {model} failed - insufficient memory")
            elif "not found" in error_msg:
                print(f"⚠️ {model} not installed")
            else:
                print(f"❌ {model} failed - {e}")
    
    print(f"\n✅ Working models: {working_models}")
    return working_models

def run_memory_optimized_research():
    """Run research with memory-optimized settings"""
    
    # Test models first
    working_models = test_available_models()
    
    if not working_models:
        print("❌ No working models found. Install tinyllama:")
        print("   ollama pull tinyllama")
        return
    
    # Use the first working model
    best_model = working_models[0]
    print(f"\n🚀 Using model: {best_model}")
    
    # Create researcher with memory-optimized settings
    researcher = AutomatedResearcher(
        model_name=best_model,
        headless=True  # Save memory by not showing browser
    )
    
    # Test with a simple query
    query = "renewable energy"
    print(f"\n🔍 Testing research: {query}")
    
    try:
        report = researcher.conduct_research(
            query=query,
            num_sources=2  # Use fewer sources to save memory
        )
        
        if report:
            print("\n✅ SUCCESS! Research completed.")
            print("="*50)
            print(report[:500] + "...")  # Show first 500 chars
            
            # Save report
            with open("test_report.txt", "w", encoding="utf-8") as f:
                f.write(report)
            print("\n💾 Full report saved as: test_report.txt")
            
        else:
            print("❌ Research failed - no report generated")
            
    except Exception as e:
        print(f"❌ Research failed: {e}")

def check_system_memory():
    """Check available system memory"""
    try:
        import psutil
        
        # Get memory info
        memory = psutil.virtual_memory()
        
        print("💾 SYSTEM MEMORY INFO:")
        print(f"   Total: {memory.total / (1024**3):.1f} GB")
        print(f"   Available: {memory.available / (1024**3):.1f} GB")
        print(f"   Used: {memory.used / (1024**3):.1f} GB")
        print(f"   Percentage: {memory.percent:.1f}%")
        
        if memory.available < 2 * (1024**3):  # Less than 2GB
            print("⚠️ WARNING: Low memory. Use tinyllama model only.")
        elif memory.available < 4 * (1024**3):  # Less than 4GB
            print("ℹ️ INFO: Medium memory. Use phi or mistral:q4_0.")
        else:
            print("✅ INFO: Good memory. Most models should work.")
            
    except ImportError:
        print("💾 Install psutil to check memory: pip install psutil")

if __name__ == "__main__":
    print("🔧 MEMORY-OPTIMIZED RESEARCH SETUP")
    print("=" * 50)
    
    # # Check system memory
    # check_system_memory()
    # print()
    
    # # Test models
    # test_available_models()
    # print()
    
    # Run optimized research
    run_memory_optimized_research()