// Cloudflare Worker: Classifieds Management
// Handles classifieds submissions from GoHighLevel after approval
// Integrates with Algolia for search functionality

// ===== CONFIGURATION =====
// Set these as environment variables in Cloudflare Worker settings:
// - ALGOLIA_APP_ID: Your Algolia Application ID
// - ALGOLIA_WRITE_API_KEY: Your Algolia Write API Key (keep secret!)
// - ALGOLIA_CLASSIFIEDS_INDEX: Your classifieds index name (e.g., "classifieds")
// - GHL_WEBHOOK_SECRET: Shared secret for validating GHL webhooks
// - CLASSIFIEDS_KV: KV namespace for storing classifieds metadata and expiration tracking

export default {
  async fetch(request, env) {
    // Add CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-GHL-Secret',
      'Content-Type': 'application/json'
    };

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    const url = new URL(request.url);
    const path = url.pathname;

    try {
      // Route requests
      switch (path) {
        case '/':
        case '/submit':
          if (request.method !== 'POST') {
            return new Response('Method not allowed', { status: 405, headers: corsHeaders });
          }
          return await handleSubmission(request, env, corsHeaders);
          
        case '/edit':
          if (request.method !== 'PUT') {
            return new Response('Method not allowed', { status: 405, headers: corsHeaders });
          }
          return await handleEdit(request, env, corsHeaders);
          
        case '/delete':
          if (request.method !== 'DELETE') {
            return new Response('Method not allowed', { status: 405, headers: corsHeaders });
          }
          return await handleDelete(request, env, corsHeaders);
          
        case '/expire':
          if (request.method !== 'POST') {
            return new Response('Method not allowed', { status: 405, headers: corsHeaders });
          }
          return await handleExpiration(request, env, corsHeaders);
          
        case '/health':
          return new Response(JSON.stringify({ status: 'ok', timestamp: new Date().toISOString() }), {
            headers: corsHeaders
          });
          
        default:
          return new Response('Not Found', { status: 404, headers: corsHeaders });
      }
    } catch (error) {
      console.error('Worker error:', error);
      return new Response(JSON.stringify({ 
        error: 'Internal server error', 
        message: error.message 
      }), {
        status: 500,
        headers: corsHeaders
      });
    }
  },

  // Handle scheduled events for expiration cleanup
  async scheduled(event, env, ctx) {
    console.log('Classifieds expiration cleanup started at', new Date().toISOString());
    
    try {
      await cleanupExpiredClassifieds(env);
      console.log('Expiration cleanup completed successfully');
    } catch (error) {
      console.error('Expiration cleanup failed:', error);
    }
  }
};

// Handle new classified submissions from GHL
async function handleSubmission(request, env, corsHeaders) {
  // Validate webhook secret
  const secret = request.headers.get('X-GHL-Secret');
  if (!secret || secret !== env.GHL_WEBHOOK_SECRET) {
    return new Response(JSON.stringify({ error: 'Invalid credentials' }), {
      status: 401,
      headers: corsHeaders
    });
  }

  const data = await request.json();
  
  // Validate required fields
  const requiredFields = ['title', 'description', 'category', 'contact', 'price'];
  const missing = requiredFields.filter(field => !data[field]);
  
  if (missing.length > 0) {
    return new Response(JSON.stringify({ 
      error: 'Missing required fields', 
      missing: missing 
    }), {
      status: 400,
      headers: corsHeaders
    });
  }

  // Create classified object for Algolia
  const classifiedId = generateClassifiedId();
  const now = new Date();
  const expirationDate = new Date();
  expirationDate.setDate(expirationDate.getDate() + (data.duration_days || 30));

  const classified = {
    objectID: classifiedId,
    title: sanitizeText(data.title),
    description: sanitizeText(data.description),
    category: data.category,
    subcategory: data.subcategory || null,
    price: parseFloat(data.price) || 0,
    price_type: data.price_type || 'fixed', // fixed, negotiable, free
    contact: {
      name: sanitizeText(data.contact.name || ''),
      email: data.contact.email || '',
      phone: data.contact.phone || '',
      preferred_method: data.contact.preferred_method || 'email'
    },
    location: {
      city: data.location?.city || '',
      state: data.location?.state || 'NC',
      zip: data.location?.zip || '',
      general_area: data.location?.general_area || ''
    },
    images: data.images || [],
    tags: data.tags || [],
    condition: data.condition || null, // new, like_new, good, fair, poor
    created_at: now.toISOString(),
    updated_at: now.toISOString(),
    expires_at: expirationDate.toISOString(),
    status: 'active',
    source: 'ghl_form',
    ghl_task_id: data.ghl_task_id || null
  };

  try {
    // Submit to Algolia
    await submitToAlgolia(classified, env);
    
    // Store metadata in KV for expiration tracking
    if (env.CLASSIFIEDS_KV) {
      await env.CLASSIFIEDS_KV.put(
        `classified:${classifiedId}`,
        JSON.stringify({
          id: classifiedId,
          expires_at: expirationDate.toISOString(),
          category: classified.category,
          title: classified.title,
          ghl_task_id: classified.ghl_task_id
        }),
        { expirationTtl: Math.floor((expirationDate.getTime() - now.getTime()) / 1000) }
      );
    }

    return new Response(JSON.stringify({ 
      success: true, 
      classified_id: classifiedId,
      expires_at: expirationDate.toISOString()
    }), {
      headers: corsHeaders
    });

  } catch (error) {
    console.error('Failed to submit classified:', error);
    return new Response(JSON.stringify({ 
      error: 'Failed to submit classified', 
      message: error.message 
    }), {
      status: 500,
      headers: corsHeaders
    });
  }
}

// Handle editing existing classifieds
async function handleEdit(request, env, corsHeaders) {
  // Validate webhook secret
  const secret = request.headers.get('X-GHL-Secret');
  if (!secret || secret !== env.GHL_WEBHOOK_SECRET) {
    return new Response(JSON.stringify({ error: 'Invalid credentials' }), {
      status: 401,
      headers: corsHeaders
    });
  }

  const data = await request.json();
  
  if (!data.classified_id) {
    return new Response(JSON.stringify({ error: 'Missing classified_id' }), {
      status: 400,
      headers: corsHeaders
    });
  }

  try {
    // Get existing classified from Algolia
    const existing = await getClassifiedFromAlgolia(data.classified_id, env);
    if (!existing) {
      return new Response(JSON.stringify({ error: 'Classified not found' }), {
        status: 404,
        headers: corsHeaders
      });
    }

    // Update allowed fields
    const updatedClassified = {
      ...existing,
      title: data.title ? sanitizeText(data.title) : existing.title,
      description: data.description ? sanitizeText(data.description) : existing.description,
      price: data.price !== undefined ? parseFloat(data.price) : existing.price,
      price_type: data.price_type || existing.price_type,
      condition: data.condition || existing.condition,
      images: data.images || existing.images,
      tags: data.tags || existing.tags,
      updated_at: new Date().toISOString()
    };

    // Submit updated version to Algolia
    await submitToAlgolia(updatedClassified, env);

    return new Response(JSON.stringify({ 
      success: true, 
      classified_id: data.classified_id,
      updated_at: updatedClassified.updated_at
    }), {
      headers: corsHeaders
    });

  } catch (error) {
    console.error('Failed to edit classified:', error);
    return new Response(JSON.stringify({ 
      error: 'Failed to edit classified', 
      message: error.message 
    }), {
      status: 500,
      headers: corsHeaders
    });
  }
}

// Handle classified deletion
async function handleDelete(request, env, corsHeaders) {
  // Validate webhook secret
  const secret = request.headers.get('X-GHL-Secret');
  if (!secret || secret !== env.GHL_WEBHOOK_SECRET) {
    return new Response(JSON.stringify({ error: 'Invalid credentials' }), {
      status: 401,
      headers: corsHeaders
    });
  }

  const data = await request.json();
  
  if (!data.classified_id) {
    return new Response(JSON.stringify({ error: 'Missing classified_id' }), {
      status: 400,
      headers: corsHeaders
    });
  }

  try {
    // Delete from Algolia
    await deleteFromAlgolia(data.classified_id, env);
    
    // Delete from KV
    if (env.CLASSIFIEDS_KV) {
      await env.CLASSIFIEDS_KV.delete(`classified:${data.classified_id}`);
    }

    return new Response(JSON.stringify({ 
      success: true, 
      classified_id: data.classified_id 
    }), {
      headers: corsHeaders
    });

  } catch (error) {
    console.error('Failed to delete classified:', error);
    return new Response(JSON.stringify({ 
      error: 'Failed to delete classified', 
      message: error.message 
    }), {
      status: 500,
      headers: corsHeaders
    });
  }
}

// Handle manual expiration requests
async function handleExpiration(request, env, corsHeaders) {
  // This endpoint can be called manually or by scheduled tasks
  const data = await request.json();
  
  if (data.classified_id) {
    // Expire specific classified
    try {
      await expireClassified(data.classified_id, env);
      return new Response(JSON.stringify({ 
        success: true, 
        expired: [data.classified_id] 
      }), {
        headers: corsHeaders
      });
    } catch (error) {
      return new Response(JSON.stringify({ 
        error: 'Failed to expire classified', 
        message: error.message 
      }), {
        status: 500,
        headers: corsHeaders
      });
    }
  } else {
    // Run cleanup of all expired classifieds
    try {
      const expired = await cleanupExpiredClassifieds(env);
      return new Response(JSON.stringify({ 
        success: true, 
        expired: expired 
      }), {
        headers: corsHeaders
      });
    } catch (error) {
      return new Response(JSON.stringify({ 
        error: 'Failed to cleanup expired classifieds', 
        message: error.message 
      }), {
        status: 500,
        headers: corsHeaders
      });
    }
  }
}

// Submit classified to Algolia
async function submitToAlgolia(classified, env) {
  const appId = env.ALGOLIA_APP_ID;
  const apiKey = env.ALGOLIA_WRITE_API_KEY;
  const indexName = env.ALGOLIA_CLASSIFIEDS_INDEX || 'classifieds';
  
  if (!appId || !apiKey) {
    throw new Error('Algolia credentials not configured');
  }

  const url = `https://${appId}-dsn.algolia.net/1/indexes/${indexName}/${classified.objectID}`;

  const response = await fetch(url, {
    method: 'PUT',
    headers: {
      'X-Algolia-API-Key': apiKey,
      'X-Algolia-Application-Id': appId,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(classified)
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Algolia API error: ${response.status} - ${error}`);
  }

  const result = await response.json();
  console.log(`Submitted classified ${classified.objectID} to Algolia:`, result);
  
  return result;
}

// Get classified from Algolia
async function getClassifiedFromAlgolia(classifiedId, env) {
  const appId = env.ALGOLIA_APP_ID;
  const apiKey = env.ALGOLIA_WRITE_API_KEY;
  const indexName = env.ALGOLIA_CLASSIFIEDS_INDEX || 'classifieds';
  
  if (!appId || !apiKey) {
    throw new Error('Algolia credentials not configured');
  }

  const url = `https://${appId}-dsn.algolia.net/1/indexes/${indexName}/${classifiedId}`;

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'X-Algolia-API-Key': apiKey,
      'X-Algolia-Application-Id': appId
    }
  });

  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Algolia API error: ${response.status} - ${error}`);
  }

  return await response.json();
}

// Delete classified from Algolia
async function deleteFromAlgolia(classifiedId, env) {
  const appId = env.ALGOLIA_APP_ID;
  const apiKey = env.ALGOLIA_WRITE_API_KEY;
  const indexName = env.ALGOLIA_CLASSIFIEDS_INDEX || 'classifieds';
  
  if (!appId || !apiKey) {
    throw new Error('Algolia credentials not configured');
  }

  const url = `https://${appId}-dsn.algolia.net/1/indexes/${indexName}/${classifiedId}`;

  const response = await fetch(url, {
    method: 'DELETE',
    headers: {
      'X-Algolia-API-Key': apiKey,
      'X-Algolia-Application-Id': appId
    }
  });

  if (!response.ok && response.status !== 404) {
    const error = await response.text();
    throw new Error(`Algolia API error: ${response.status} - ${error}`);
  }

  console.log(`Deleted classified ${classifiedId} from Algolia`);
}

// Expire a specific classified
async function expireClassified(classifiedId, env) {
  // Update status in Algolia
  const existing = await getClassifiedFromAlgolia(classifiedId, env);
  if (!existing) {
    throw new Error('Classified not found');
  }

  const expiredClassified = {
    ...existing,
    status: 'expired',
    updated_at: new Date().toISOString()
  };

  await submitToAlgolia(expiredClassified, env);
  
  // Remove from KV (no longer needs expiration tracking)
  if (env.CLASSIFIEDS_KV) {
    await env.CLASSIFIEDS_KV.delete(`classified:${classifiedId}`);
  }
  
  console.log(`Expired classified ${classifiedId}`);
}

// Cleanup expired classifieds (run on schedule)
async function cleanupExpiredClassifieds(env) {
  if (!env.CLASSIFIEDS_KV) {
    console.log('No KV namespace configured for expiration tracking');
    return [];
  }

  const expired = [];
  const now = new Date();

  // List all classifieds in KV
  const { keys } = await env.CLASSIFIEDS_KV.list({ prefix: 'classified:' });

  for (const key of keys) {
    try {
      const metadata = await env.CLASSIFIEDS_KV.get(key.name, { type: 'json' });
      if (!metadata) continue;

      const expiresAt = new Date(metadata.expires_at);
      if (now > expiresAt) {
        await expireClassified(metadata.id, env);
        expired.push(metadata.id);
      }
    } catch (error) {
      console.error(`Error processing expired classified ${key.name}:`, error);
    }
  }

  console.log(`Cleaned up ${expired.length} expired classifieds:`, expired);
  return expired;
}

// Generate unique classified ID
function generateClassifiedId() {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2, 8);
  return `clf_${timestamp}_${random}`;
}

// Sanitize text input
function sanitizeText(text) {
  if (!text) return '';
  
  // Remove potentially harmful characters and limit length
  return text
    .replace(/[<>]/g, '') // Remove < and >
    .replace(/javascript:/gi, '') // Remove javascript: protocol
    .replace(/on\w+=/gi, '') // Remove event handlers
    .trim()
    .substring(0, 1000); // Limit length
}