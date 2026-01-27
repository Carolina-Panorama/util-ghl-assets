export default {
  async fetch(request, env) {
    // Add CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Content-Type': 'application/json'
    };

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    // Security: Only allow root path requests
    const url = new URL(request.url);
    if (url.pathname !== '/' && url.pathname !== '') {
      return new Response('Not Found', { 
        status: 404,
        headers: { 'Content-Type': 'text/plain' }
      });
    }

    // Security: Only allow requests from carolinapanorama.com or .org (including subdomains)
    const referer = request.headers.get('Referer') || '';
    const origin = request.headers.get('Origin') || '';
    
    const allowedDomains = ['carolinapanorama.com', 'carolinapanorama.org'];
    
    const checkDomain = (urlString) => {
      if (!urlString) return false;
      try {
        const hostname = new URL(urlString).hostname.toLowerCase();
        return allowedDomains.some(domain => 
          hostname === domain || hostname.endsWith('.' + domain)
        );
      } catch {
        return false;
      }
    };
    
    if (!checkDomain(referer) && !checkDomain(origin)) {
      return new Response('Forbidden', { 
        status: 403,
        headers: { 'Content-Type': 'text/plain' }
      });
    }

    try {
      // List all objects in the bucket
      const listed = await env.MY_BUCKET.list();
      
      // Filter and format files
      const fileList = {};
      
      for (const object of listed.objects) {
        // Only include PDF files with date pattern
        if (object.key.match(/\d+-\d+-\d+.*\.pdf$/i)) {
          const dateMatch = object.key.match(/(\d+-\d+-\d+)/);
          if (dateMatch) {
            // Construct public URL
            const publicUrl = `https://files.carolinapanorama.org/${object.key}`;
            fileList[publicUrl] = dateMatch[1];
          }
        }
      }
      
      return new Response(JSON.stringify(fileList), {
        headers: corsHeaders
      });
      
    } catch (error) {
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: corsHeaders
      });
    }
  }
};