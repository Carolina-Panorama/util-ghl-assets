// Cloudflare Worker: RSS to Algolia Sync
// Runs 4x per day (every 6 hours) to sync RSS feed articles to Algolia

// ===== CONFIGURATION =====
// Set these as environment variables in Cloudflare Worker settings:
// - ALGOLIA_APP_ID: Your Algolia Application ID
// - ALGOLIA_ADMIN_API_KEY: Your Algolia Admin API Key (keep secret!)
// - ALGOLIA_INDEX_NAME: Your index name (e.g., "posts" or "articles")
// - RSS_FEED_URL: Your GHL RSS feed URL
// - RSS_SYNC_KV: KV namespace binding for storing last-modified info

// Cron trigger: 0 */6 * * * (runs at 00:00, 06:00, 12:00, 18:00 UTC)

export default {
  async scheduled(event, env, ctx) {
    console.log('RSS sync started at', new Date().toISOString());
    
    try {
      // Fetch RSS feed with conditional headers
      const rssUrl = env.RSS_FEED_URL || 'YOUR_RSS_FEED_URL_HERE';
      
      // Get last known Last-Modified and ETag from KV storage
      const lastModified = env.RSS_SYNC_KV ? await env.RSS_SYNC_KV.get('last-modified') : null;
      const lastETag = env.RSS_SYNC_KV ? await env.RSS_SYNC_KV.get('etag') : null;
      
      const headers = {};
      if (lastModified) {
        headers['If-Modified-Since'] = lastModified;
      }
      if (lastETag) {
        headers['If-None-Match'] = lastETag;
      }
      
      const response = await fetch(rssUrl, { headers });
      
      // 304 Not Modified - feed hasn't changed
      if (response.status === 304) {
        console.log('RSS feed not modified, skipping sync');
        return;
      }
      
      if (!response.ok) {
        throw new Error(`Failed to fetch RSS feed: ${response.status}`);
      }
      
      // Store new Last-Modified and ETag for next run
      const newLastModified = response.headers.get('Last-Modified');
      const newETag = response.headers.get('ETag');
      
      if (env.RSS_SYNC_KV) {
        if (newLastModified) {
          await env.RSS_SYNC_KV.put('last-modified', newLastModified);
        }
        if (newETag) {
          await env.RSS_SYNC_KV.put('etag', newETag);
        }
      }
      
      console.log('RSS feed has been updated, processing...');
      
      const xmlText = await response.text();
      
      // Parse RSS feed
      const articles = await parseRSS(xmlText);
      console.log(`Parsed ${articles.length} articles from RSS feed`);
      
      if (articles.length === 0) {
        console.log('No articles found in RSS feed');
        return;
      }
      
      // Push to Algolia
      await pushToAlgolia(articles, env);
      console.log('RSS sync completed successfully');
      
    } catch (error) {
      console.error('RSS sync failed:', error);
      // You could send an alert here (email, Slack, etc.)
    }
  },
  
  // Block all HTTP requests - this worker only runs on schedule
  async fetch(request, env, ctx) {
    return new Response('Not Found', { 
      status: 404,
      headers: { 'Content-Type': 'text/plain' }
    });
  }
};

// Parse RSS XML and extract article data
async function parseRSS(xmlText) {
  const articles = [];
  
  // Simple regex-based XML parsing (works for standard RSS 2.0)
  // For more complex XML, consider using a proper XML parser
  const itemRegex = /<item>([\s\S]*?)<\/item>/g;
  const items = xmlText.matchAll(itemRegex);
  
  for (const match of items) {
    const itemContent = match[1];
    
    // Extract fields
    const title = extractTag(itemContent, 'title');
    const link = extractTag(itemContent, 'link');
    const description = extractTag(itemContent, 'description');
    const pubDate = extractTag(itemContent, 'pubDate');
    const guid = extractTag(itemContent, 'guid') || link; // Use link as fallback
    
    // Optional: Extract category/tags
    const categories = extractAllTags(itemContent, 'category');
    
    // Extract image URL from various RSS image tags
    const image = extractImageUrl(itemContent);
    
    // Fetch author and tags from the article page
    const articleData = await fetchArticleMetadata(link);
    
    // Create Algolia record
    articles.push({
      objectID: guid, // Unique ID for Algolia
      title: cleanHTML(title),
      description: cleanHTML(description),
      url: link,
      image: image,
      author: articleData.author,
      tags: articleData.tags,
      publishedAt: pubDate ? new Date(pubDate).getTime() : Date.now(),
      categories: categories,
    });
  }
  
  return articles;
}

// Extract content from XML tag
function extractTag(xml, tagName) {
  const regex = new RegExp(`<${tagName}[^>]*>([\\s\\S]*?)<\/${tagName}>`, 'i');
  const match = xml.match(regex);
  return match ? match[1].trim() : '';
}

// Extract all occurrences of a tag
function extractAllTags(xml, tagName) {
  const regex = new RegExp(`<${tagName}[^>]*>([\\s\\S]*?)<\/${tagName}>`, 'gi');
  const matches = xml.matchAll(regex);
  const results = [];
  
  for (const match of matches) {
    results.push(match[1].trim());
  }
  
  return results;
}

// Extract image URL from RSS feed (supports multiple formats)
function extractImageUrl(xml) {
  // Try media:thumbnail with url attribute
  let match = xml.match(/<media:thumbnail[^>]*url=["']([^"']+)["']/i);
  if (match) return match[1];
  
  // Try media:content with url attribute
  match = xml.match(/<media:content[^>]*url=["']([^"']+)["']/i);
  if (match) return match[1];
  
  // Try enclosure tag with image type
  match = xml.match(/<enclosure[^>]*url=["']([^"']+)["'][^>]*type=["']image/i);
  if (match) return match[1];
  
  // Try content:encoded or description for img tags
  match = xml.match(/<img[^>]*src=["']([^"']+)["']/i);
  if (match) return match[1];
  
  return null;
}

// Fetch author and tags from article page
async function fetchArticleMetadata(url) {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      return { author: null, tags: [] };
    }
    
    const html = await response.text();
    
    // Extract author
    let author = null;
    
    // Try blog-author-name class (GHL specific)
    let match = html.match(/<p[^>]*class=["'][^"']*blog-author-name[^"']*["'][^>]*>([^<]+)<\/p>/i);
    if (match) author = match[1];
    
    // Try various author meta tags
    if (!author) {
      match = html.match(/<meta[^>]*name=["']author["'][^>]*content=["']([^"']+)["']/i);
      if (match) author = match[1];
    }
    
    if (!author) {
      match = html.match(/<meta[^>]*property=["']article:author["'][^>]*content=["']([^"']+)["']/i);
      if (match) author = match[1];
    }
    
    // Try JSON-LD structured data
    if (!author) {
      const jsonLdMatch = html.match(/<script[^>]*type=["']application\/ld\+json["'][^>]*>(.*?)<\/script>/is);
      if (jsonLdMatch) {
        try {
          const jsonLd = JSON.parse(jsonLdMatch[1]);
          if (jsonLd.author?.name) {
            author = jsonLd.author.name;
          }
        } catch (e) {
          // Invalid JSON-LD, skip
        }
      }
    }
    
    // Extract tags/keywords
    const tags = [];
    
    // Try keywords meta tag
    match = html.match(/<meta[^>]*name=["']keywords["'][^>]*content=["']([^"']+)["']/i);
    if (match) {
      tags.push(...match[1].split(',').map(t => t.trim()).filter(t => t));
    }
    
    // Try article:tag meta tags (multiple)
    const tagMatches = html.matchAll(/<meta[^>]*property=["']article:tag["'][^>]*content=["']([^"']+)["']/gi);
    for (const tagMatch of tagMatches) {
      tags.push(tagMatch[1].trim());
    }
    
    return {
      author: author ? cleanHTML(author) : null,
      tags: [...new Set(tags)] // Remove duplicates
    };
    
  } catch (error) {
    console.error(`Error fetching metadata from ${url}:`, error);
    return { author: null, tags: [] };
  }
}

// Clean HTML entities and tags
function cleanHTML(text) {
  if (!text) return '';
  
  // Remove CDATA wrappers
  text = text.replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, '$1');
  
  // Remove HTML tags
  text = text.replace(/<[^>]*>/g, '');
  
  // Decode common HTML entities
  text = text
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, ' ');
  
  return text.trim();
}

// Push articles to Algolia
async function pushToAlgolia(articles, env) {
  const appId = env.ALGOLIA_APP_ID;
  const apiKey = env.ALGOLIA_ADMIN_API_KEY;
  const indexName = env.ALGOLIA_INDEX_NAME || 'posts';
  
  if (!appId || !apiKey) {
    throw new Error('Algolia credentials not configured');
  }
  
  // Algolia API endpoint
  const url = `https://${appId}-dsn.algolia.net/1/indexes/${indexName}/batch`;
  
  // Prepare batch request
  const requests = articles.map(article => ({
    action: 'updateObject', // Updates if exists, creates if not
    body: article
  }));
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'X-Algolia-API-Key': apiKey,
      'X-Algolia-Application-Id': appId,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ requests })
  });
  
  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Algolia API error: ${response.status} - ${error}`);
  }
  
  const result = await response.json();
  console.log(`Pushed ${articles.length} articles to Algolia:`, result);
  
  return result;
}
