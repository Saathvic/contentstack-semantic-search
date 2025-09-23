import os
import google.generativeai as genai
from config import config
from typing import List
import json

class QueryRewriter:
    def __init__(self):
        api_key = config.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY not configured")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def rewrite_query(self, query: str, num_rewrites: int = 3) -> List[str]:
        """Rewrite a query into multiple semantically similar forms"""
        prompt = f"""
        Given the search query: "{query}"
        
        Generate {num_rewrites} different but semantically similar search queries that would help find the same or related products. 
        
        Focus on:
        - Synonyms and related terms
        - Different ways to express the same intent
        - Common variations people might search for
        - Broader or narrower related concepts
        
        Return only the rewritten queries as a JSON array of strings, no other text.
        
        Examples:
        Original: "red sneakers"
        Rewrites: ["red athletic shoes", "crimson sneakers", "red running shoes"]
        
        Original: "wireless headphones"
        Rewrites: ["bluetooth headphones", "wireless earbuds", "cordless headphones"]
        """

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Try to parse as JSON
            try:
                rewrites = json.loads(result_text)
                if isinstance(rewrites, list) and all(isinstance(r, str) for r in rewrites):
                    return rewrites[:num_rewrites]  # Limit to requested number
            except json.JSONDecodeError:
                # Fallback: extract queries from text
                lines = result_text.split('\n')
                rewrites = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('[') and not line.startswith(']'):
                        # Remove quotes and commas
                        line = line.strip('"').strip("'").strip(',')
                        if line:
                            rewrites.append(line)
                return rewrites[:num_rewrites]
                
        except Exception as e:
            print(f"Error rewriting query: {e}")
            return []

    def expand_query(self, query: str, num_expansions: int = 5) -> List[str]:
        """Expand a query with multiple related search terms"""
        rewrites = self.rewrite_query(query, num_expansions)
        
        # Always include the original query
        if query not in rewrites:
            rewrites.insert(0, query)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_rewrites = []
        for rewrite in rewrites:
            if rewrite.lower() not in seen:
                seen.add(rewrite.lower())
                unique_rewrites.append(rewrite)
        
        return unique_rewrites

def main():
    """Test the query rewriter"""
    try:
        rewriter = QueryRewriter()
        
        test_queries = [
            "red high top sneakers",
            "wireless bluetooth headphones",
            "leather wallet",
            "smart watch"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Original: {query}")
            rewrites = rewriter.expand_query(query, 4)
            print("📝 Rewrites:")
            for i, rewrite in enumerate(rewrites, 1):
                print(f"  {i}. {rewrite}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()