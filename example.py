"""
Example usage of the Advanced Web Scraper
"""

from advanced_scraper import AdvancedWebScraper
import json


def example_1_scrape_url():
    """Example 1: Scrape a single URL"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Scraping a single URL")
    print("="*80)
    
    scraper = AdvancedWebScraper()
    
    # Scrape Wikipedia article about Python
    result = scraper.scrape_url("https://codeavecjonathan.com/scraping/recette")
    
    if result:
        print(f"\nTitle: {result.title}")
        print(f"URL: {result.url}")
        print(f"Content length: {len(result.content)} characters")
        print(f"Number of links: {len(result.links)}")
        print(f"Number of images: {len(result.images)}")
        print(f"\nContent preview:")
        print("-" * 80)
        print(result.content[:500] + "...")
        
        # Save results
        scraper.save_results([result], "example_1_python_scrape.json")
        print("\n✓ Results saved to example_1_python_scrape.json and .html")
    
    scraper.close()


def example_2_search_topic():
    """Example 2: Search and scrape a topic"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Searching and scraping a topic")
    print("="*80)
    
    scraper = AdvancedWebScraper()
    
    # Research machine learning from multiple sources
    topic = "machine learning"
    print(f"\nResearching topic: '{topic}'")
    
    results = scraper.scrape_topic(topic, num_sites=3, include_wikipedia=True)
    
    print(f"\nFound {len(results)} sources:\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.title}")
        print(f"   Source: {result.source}")
        print(f"   URL: {result.url}")
        print(f"   Content length: {len(result.content)} chars")
        print()
    
    # Save results
    scraper.save_results(results, "example_2_machine_learning_research.json")
    print("✓ Results saved to example_2_machine_learning_research.json and .html")
    
    scraper.close()


def example_3_google_search():
    """Example 3: Just search Google"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Google search only")
    print("="*80)
    
    scraper = AdvancedWebScraper()
    
    query = "best practices web scraping"
    print(f"\nSearching Google for: '{query}'")
    
    urls = scraper.search_web(query, num_results=5)
    
    print(f"\nFound {len(urls)} URLs:")
    for i, url in enumerate(urls, 1):
        print(f"{i}. {url}")
    
    # Scrape the found URLs
    if urls:
        results = []
        for url in urls[:3]:  # Scrape first 3 URLs
            try:
                result = scraper.scrape_url(url)
                if result:
                    results.append(result)
            except Exception as e:
                print(f"Failed to scrape {url}: {e}")
        
        if results:
            scraper.save_results(results, "example_3_web_scraping_best_practices.json")
            print(f"\n✓ Scraped and saved {len(results)} results to example_3_web_scraping_best_practices.json and .html")
    
    scraper.close()


def example_4_wikipedia_only():
    """Example 4: Get Wikipedia summary"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Wikipedia summary only")
    print("="*80)
    
    scraper = AdvancedWebScraper()
    
    topics = ["Quantum Computing", "Neural Networks", "Blockchain"]
    results = []
    
    for topic in topics:
        print(f"\n--- {topic} ---")
        result = scraper.get_wikipedia_summary(topic)
        
        if result:
            print(f"Title: {result.title}")
            print(f"URL: {result.url}")
            print(f"\nSummary:")
            print(result.content[:300] + "...")
            results.append(result)
    
    # Save all Wikipedia summaries
    if results:
        scraper.save_results(results, "example_4_wikipedia_summaries.json")
        print(f"\n✓ Saved {len(results)} Wikipedia summaries to example_4_wikipedia_summaries.json and .html")
    
    scraper.close()


def example_5_custom_processing():
    """Example 5: Custom data processing"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Custom data processing")
    print("="*80)
    
    scraper = AdvancedWebScraper()
    
    # Scrape and analyze
    results = scraper.scrape_topic("climate change", num_sites=3)
    
    # Custom analysis
    total_content_length = sum(len(r.content) for r in results)
    total_links = sum(len(r.links) for r in results)
    sources = [r.source for r in results]
    
    print(f"\nAnalysis of {len(results)} sources:")
    print(f"  - Total content: {total_content_length:,} characters")
    print(f"  - Total links: {total_links}")
    print(f"  - Sources breakdown: {dict((x, sources.count(x)) for x in set(sources))}")
    
    # Extract specific information
    print("\n--- Titles ---")
    for result in results:
        print(f"  • {result.title}")
    
    # Save results
    if results:
        scraper.save_results(results, "example_5_climate_change_analysis.json")
        print(f"\n✓ Results saved to example_5_climate_change_analysis.json and .html")
    
    scraper.close()


def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("ADVANCED WEB SCRAPER - EXAMPLES")
    print("="*80)
    
    examples = [
        ("1", "Scrape a single URL", example_1_scrape_url),
        ("2", "Search and scrape a topic", example_2_search_topic),
        ("3", "Google search only", example_3_google_search),
        ("4", "Wikipedia summaries", example_4_wikipedia_only),
        ("5", "Custom processing", example_5_custom_processing),
    ]
    
    print("\nAvailable examples:")
    for num, desc, _ in examples:
        print(f"  {num}. {desc}")
    print("  0. Run all examples")
    
    choice = input("\nEnter example number (or press Enter for all): ").strip()
    
    if not choice or choice == "0":
        # Run all examples
        for _, _, func in examples:
            func()
            print("\n" + "-"*80)
    else:
        # Run specific example
        for num, _, func in examples:
            if num == choice:
                func()
                break
        else:
            print(f"Invalid choice: {choice}")


if __name__ == "__main__":
    main()



# """
# Example usage of the Advanced Web Scraper
# """

# from advanced_scraper import AdvancedWebScraper
# import json


# def example_1_scrape_url():
#     """Example 1: Scrape a single URL"""
#     print("\n" + "="*80)
#     print("EXAMPLE 1: Scraping a single URL")
#     print("="*80)
    
#     scraper = AdvancedWebScraper()
    
#     # Scrape Wikipedia article about Python
#     result = scraper.scrape_url("https://en.wikipedia.org/wiki/Python_(programming_language)")
    
#     if result:
#         print(f"\nTitle: {result.title}")
#         print(f"URL: {result.url}")
#         print(f"Content length: {len(result.content)} characters")
#         print(f"Number of links: {len(result.links)}")
#         print(f"Number of images: {len(result.images)}")
#         print(f"\nContent preview:")
#         print("-" * 80)
#         print(result.content[:500] + "...")
    
#     scraper.close()


# def example_2_search_topic():
#     """Example 2: Search and scrape a topic"""
#     print("\n" + "="*80)
#     print("EXAMPLE 2: Searching and scraping a topic")
#     print("="*80)
    
#     scraper = AdvancedWebScraper()
    
#     # Research machine learning from multiple sources
#     topic = "machine learning"
#     print(f"\nResearching topic: '{topic}'")
    
#     results = scraper.scrape_topic(topic, num_sites=3, include_wikipedia=True)
    
#     print(f"\nFound {len(results)} sources:\n")
    
#     for i, result in enumerate(results, 1):
#         print(f"{i}. {result.title}")
#         print(f"   Source: {result.source}")
#         print(f"   URL: {result.url}")
#         print(f"   Content length: {len(result.content)} chars")
#         print()
    
#     # Save results
#     scraper.save_results(results, "machine_learning_research.json")
#     print("Results saved to machine_learning_research.json")
    
#     scraper.close()


# def example_3_google_search():
#     """Example 3: Just search Google"""
#     print("\n" + "="*80)
#     print("EXAMPLE 3: Google search only")
#     print("="*80)
    
#     scraper = AdvancedWebScraper()
    
#     query = "best practices web scraping"
#     print(f"\nSearching Google for: '{query}'")
    
#     urls = scraper.google_search(query, num_results=5)
    
#     print(f"\nFound {len(urls)} URLs:")
#     for i, url in enumerate(urls, 1):
#         print(f"{i}. {url}")
    
#     scraper.close()


# def example_4_wikipedia_only():
#     """Example 4: Get Wikipedia summary"""
#     print("\n" + "="*80)
#     print("EXAMPLE 4: Wikipedia summary only")
#     print("="*80)
    
#     scraper = AdvancedWebScraper()
    
#     topics = ["Quantum Computing", "Neural Networks", "Blockchain"]
    
#     for topic in topics:
#         print(f"\n--- {topic} ---")
#         result = scraper.get_wikipedia_summary(topic)
        
#         if result:
#             print(f"Title: {result.title}")
#             print(f"URL: {result.url}")
#             print(f"\nSummary:")
#             print(result.content[:300] + "...")
    
#     scraper.close()


# def example_5_custom_processing():
#     """Example 5: Custom data processing"""
#     print("\n" + "="*80)
#     print("EXAMPLE 5: Custom data processing")
#     print("="*80)
    
#     scraper = AdvancedWebScraper()
    
#     # Scrape and analyze
#     results = scraper.scrape_topic("climate change", num_sites=3)
    
#     # Custom analysis
#     total_content_length = sum(len(r.content) for r in results)
#     total_links = sum(len(r.links) for r in results)
#     sources = [r.source for r in results]
    
#     print(f"\nAnalysis of {len(results)} sources:")
#     print(f"  - Total content: {total_content_length:,} characters")
#     print(f"  - Total links: {total_links}")
#     print(f"  - Sources breakdown: {dict((x, sources.count(x)) for x in set(sources))}")
    
#     # Extract specific information
#     print("\n--- Titles ---")
#     for result in results:
#         print(f"  • {result.title}")
    
#     scraper.close()


# def main():
#     """Run all examples"""
#     print("\n" + "="*80)
#     print("ADVANCED WEB SCRAPER - EXAMPLES")
#     print("="*80)
    
#     examples = [
#         ("1", "Scrape a single URL", example_1_scrape_url),
#         ("2", "Search and scrape a topic", example_2_search_topic),
#         ("3", "Google search only", example_3_google_search),
#         ("4", "Wikipedia summaries", example_4_wikipedia_only),
#         ("5", "Custom processing", example_5_custom_processing),
#     ]
    
#     print("\nAvailable examples:")
#     for num, desc, _ in examples:
#         print(f"  {num}. {desc}")
#     print("  0. Run all examples")
    
#     choice = input("\nEnter example number (or press Enter for all): ").strip()
    
#     if not choice or choice == "0":
#         # Run all examples
#         for _, _, func in examples:
#             func()
#             print("\n" + "-"*80)
#     else:
#         # Run specific example
#         for num, _, func in examples:
#             if num == choice:
#                 func()
#                 break
#         else:
#             print(f"Invalid choice: {choice}")


# if __name__ == "__main__":
#     main()