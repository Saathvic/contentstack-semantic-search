import React, { useState } from 'react';
import axios from 'axios';
import './SearchInterface.css';

function SearchInterface() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [expandedQueries, setExpandedQueries] = useState([]);

  // Force localhost for development (debugging CORS)
  const API_BASE_URL = 'http://localhost:5000';

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError('');
    setResults([]);
    setExpandedQueries([]);

    try {
      const response = await axios.post(`${API_BASE_URL}/search`, {
        query: query,
        top_k: 10,
        rewrite: true
      });

      setResults(response.data.results || []);
      setExpandedQueries(response.data.expanded_queries || []);
    } catch (err) {
      console.error('Search error:', err);
      setError(err.response?.data?.error || 'Search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    setLoading(true);
    setError('');

    try {
      await axios.post(`${API_BASE_URL}/sync?content_type=product`);
      alert('Content sync completed successfully!');
    } catch (err) {
      console.error('Sync error:', err);
      setError('Sync failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="search-container">
      <header className="search-header">
        <h1>🔍 Contentstack Semantic Search</h1>
        <p>Find products using natural language queries powered by AI</p>
      </header>

      <div className="search-controls">
        <form onSubmit={handleSearch} className="search-form">
          <div className="search-input-group">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search for products (e.g., 'red sneakers', 'wireless headphones')"
              className="search-input"
              disabled={loading}
            />
            <button
              type="submit"
              className="search-button"
              disabled={loading || !query.trim()}
            >
              {loading ? '🔄 Searching...' : '🔍 Search'}
            </button>
          </div>
        </form>

        <button
          onClick={handleSync}
          className="sync-button"
          disabled={loading}
        >
          🔄 Sync Content
        </button>
      </div>

      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}

      {expandedQueries.length > 1 && (
        <div className="expanded-queries">
          <h3>📝 Search expanded to:</h3>
          <div className="query-tags">
            {expandedQueries.map((q, index) => (
              <span key={index} className="query-tag">
                {q}
              </span>
            ))}
          </div>
        </div>
      )}

      {results.length > 0 && (
        <div className="results-section">
          <h2>🎯 Search Results ({results.length})</h2>
          <div className="results-grid">
            {results.map((result, index) => (
              <div key={result.product_id} className="result-card">
                <div className="result-header">
                  <h3>{result.name || result.title || `Product ${result.product_id}`}</h3>
                  <div className="result-score">
                    Score: {(result.score * 100).toFixed(1)}%
                  </div>
                </div>

                {result.description && (
                  <p className="product-description">{result.description}</p>
                )}

                <div className="product-details">
                  {result.price && result.price > 0 && (
                    <span className="product-price">${result.price}</span>
                  )}
                  {result.category && (
                    <span className="product-category">{result.category}</span>
                  )}
                  {result.brand && (
                    <span className="product-brand">{result.brand}</span>
                  )}
                </div>

                <div className="result-meta">
                  <span className="product-id">ID: {result.product_id}</span>
                  {result.metadata?.content_type && (
                    <span className="content-type">{result.metadata.content_type}</span>
                  )}
                </div>

                {result.query_used && result.query_used !== query && (
                  <div className="query-used">
                    Found via: "{result.query_used}"
                  </div>
                )}

                {result.metadata?.url && (
                  <a
                    href={result.metadata.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="result-link"
                  >
                    View Product →
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {results.length === 0 && !loading && query && !error && (
        <div className="no-results">
          <h3>� Continue exploring</h3>
          <p>Try searching with different keywords to discover more products.</p>
        </div>
      )}
    </div>
  );
}

export default SearchInterface;