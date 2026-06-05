#!/usr/bin/env python3
"""Scrape real plumbers from Google Maps and rebuild the directory site."""
import json, re, time, os
from pathlib import Path
from hermes_tools import terminal, write_file, search_files

def scrape_plumbers():
    """Use browser to scrape Google Maps results."""
    results = []
    
    # Navigate to Google Maps search
    terminal("browser_navigate", url="https://www.google.com/maps/search/plumber+Tucson+Arizona/")
    time.sleep(5)
    
    # Scroll to load more results
    for _ in range(5):
        terminal("browser_scroll", direction="down")
        time.sleep(2)
    
    # Get page content
    resp = terminal("browser_snapshot", full=True)
    print(resp[:2000])
    
    # Extract business info via JS
    js_code = """
    const items = document.querySelectorAll('[role="feed"] > div > div, [role="feed"] article');
    const results = [];
    items.forEach(item => {
        const nameEl = item.querySelector('a[href*="/maps/place"]');
        const name = nameEl?.textContent?.trim();
        if (!name) return;
        
        const ratingEl = item.querySelector('[aria-label*="star"], [aria-label*="نجمة"]');
        const rating = ratingEl?.getAttribute('aria-label')?.match(/[\\d.]+/)?.[0];
        
        const infoEl = item.querySelectorAll('div[role="feed"] > div > div > div > div > div');
        const text = item.textContent;
        
        // Try to extract phone
        const phoneMatch = text.match(/\\(?\\d{3}\\)?[-.\\s]?\\d{3}[-.\\s]?\\d{4}/);
        const phone = phoneMatch ? phoneMatch[0] : '';
        
        // Try to extract address
        const addressMatch = text.match(/\\d+\\s+[A-Z][a-z]+\\s+(Street|Avenue|Road|Drive|Boulevard|Way|Lane|Circle|Dr|Rd|Ave|Blvd|St)/i);
        const address = addressMatch ? addressMatch[0] : 'Tucson, AZ';
        
        // Try to extract website
        const siteEl = item.querySelector('a[href*="http"]:not([href*="google"])');
        const website = siteEl?.href || '';
        
        results.push({ name, rating, phone, address, website, snippet: text.substring(0, 200) });
    });
    return JSON.stringify(results);
    """
    
    resp = terminal("browser_console", expression=js_code)
    try:
        data = json.loads(resp)
        if data:
            results.extend(data)
    except:
        pass
    
    return results

if __name__ == "__main__":
    plumbers = scrape_plumbers()
    print(json.dumps(plumbers, indent=2))
