# YouTube Widgets Guide

## Overview

Two widgets for embedding YouTube content on your site, both powered by the Carolina Panorama YouTube API:

1. **YouTube Playlist Carousel** - Featured video player with responsive episode list
2. **YouTube Channel Widget** - Grid of latest channel videos

Both widgets are themed with Carolina Panorama brand colors:
- **Carolina Navy**: #003366
- **Carolina Gold**: #dcb349

## Setup

### 1. Configure Your API Key

Add the YouTube API key to your deployment environment:
```bash
export YOUTUBE_API_KEY=your_api_key_here
```

### 2. Find Your IDs

**Channel ID:**
- Go to your YouTube channel
- Click "About" tab
- Look for the channel URL
- Format: `youtube.com/channel/UCxxxxxx`

**Playlist ID:**
- Go to your playlist
- URL format: `youtube.com/playlist?list=PLxxxxxx`
- The `PLxxxxxx` part is your playlist ID

---

## Widget 1: YouTube Playlist Carousel

### Description
Displays a featured video player with a responsive episode list. On desktop, shows episodes in a vertical sidebar. On mobile/tablet, episodes wrap to full-width grid below the player.

### File Location
```
site-assets/site-feed-widgets/youtube-playlist-carousel.html
```

### Configuration

Open the file and update the `YT_CONFIG` object:

```javascript
const YT_CONFIG = {
  channelId: 'UCxxxxx',      // Your channel ID
  playlistId: null,           // OR your playlist ID (use one or the other)
  apiBaseUrl: 'https://api.carolinapanorama.com/api/public/youtube'
};
```

**Choose ONE:**
- Use `channelId` to fetch from channel's uploads
- Use `playlistId` to fetch from a specific playlist

### Features

- **Responsive Layout**
  - Desktop (1200px+): Player on left, vertical episode list on right
  - Tablet/Mobile: Player on top, full-width grid of episodes below
  
- **Interactive Episode Selection**
  - Click any episode thumbnail to play it
  - Active episode is highlighted with blue border
  
- **Auto-fetch Latest Videos**
  - Pulls last 10 videos from your channel/playlist
  - Sorted by publish date (newest first)
  
- **Responsive Images**
  - Lazy-loaded thumbnails
  - Optimized for all screen sizes

### Customization

**Colors:**
```css
.yt-featured-player {
  background: #e0e7ef;  /* Change background color */
}

.yt-episode-btn.active {
  border-color: #2563eb;  /* Change active highlight */
}
```

**Player Max Width:**
```css
.yt-featured-player {
  max-width: 800px;  /* Adjust video width */
}
```

**Grid Columns (mobile):**
```css
.yt-episode-container {
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));  /* Adjust thumbnail width */
}
```

### Embedding

**HTML:**
```html
<div id="yt-playlist-widget"></div>
<script src="path/to/youtube-playlist-carousel.html"></script>
```

**GHL / External Widget:**
Simply embed the file as an external HTML widget - it's self-contained and CORS-enabled.

---

## Widget 2: YouTube Channel Widget

### Description
Grid layout displaying latest videos from a YouTube channel, similar to Elfsight YouTube widgets. Features channel header with subscribe button, and responsive video grid.

### File Location
```
site-assets/site-feed-widgets/youtube-channel-widget.html
```

### Configuration

Open the file and update the `YT_CHANNEL_CONFIG` object:

```javascript
const YT_CHANNEL_CONFIG = {
  channelId: 'UCxxxxx',      // Your channel ID
  apiBaseUrl: 'https://api.carolinapanorama.com/api/public/youtube'
};
```

### Adding Your Brand Logo

The channel widget supports an optional brand logo in the header. To enable it:

1. Open `youtube-channel-widget.html`
2. Find the line that says `<!-- Optional: Brand logo... -->`
3. Uncomment the logo image tag and set your logo URL:

```html
<img class="yt-channel-logo" src="https://your-domain.com/logo.png" alt="Brand Logo">
```

The logo will:
- Display on the left side of the header (before channel avatar)
- Auto-scale to fit the header height
- Be responsive and adjust on mobile devices
- Work with PNG, SVG, and JPG formats

### Features

- **Channel Header**
  - Optional brand logo
  - Channel avatar (YouTube channel picture)
  - Subscribe button (links to YouTube with subscription prompt)
  - Beautiful Carolina Navy gradient background with Carolina Gold accents
  
- **Responsive Video Grid**
  - Desktop (1200px+): 4-5 columns
  - Tablet (768px+): 3 columns
  - Mobile: 2 columns with stacked layout
  
- **Video Cards with Metadata**
  - Thumbnail with hover zoom effect
  - Video title (clamped to 2 lines)
  - Relative time ("2 days ago", "1 month ago", etc.)
  - Simulated view count (randomized for demo)
  
- **Interactive Elements**
  - Hover effects with elevation (gold border accent)
  - Links directly to YouTube
  - Opens in new tab
  - Carolina Navy and Gold brand colors throughout

### Customization

**Channel Name:**
Currently uses the channel ID. To display a custom channel name:
```javascript
// In renderChannelHeader() function, change:
channelName.textContent = 'Your Channel Name';  // Custom name
```

**Colors - Header Gradient:**
```css
.yt-channel-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  /* Change the color codes to customize */
}
```

### Customization

Both widgets are pre-styled with your brand colors (Carolina Navy #003366 and Carolina Gold #dcb349), but you can customize them:

**Header Colors (Channel Widget):**
```css
.yt-channel-header {
  background: linear-gradient(135deg, #003366 0%, #004d99 100%);  /* Update colors here */
}
```

**Subscribe Button:**
```css
.yt-channel-subscribe {
  background: #dcb349;  /* Carolina Gold */
}

.yt-channel-subscribe:hover {
  background: #e8c969;  /* Lighter gold on hover */
}
```

**Video Card Hover Border:**
```css
.yt-video-card:hover {
  border-color: #dcb349;  /* Gold accent on hover */
}
```

**Grid Columns:**
```css
.yt-videos-grid {
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  /* minmax(240px, 1fr): Adjust first number to change card width */
}
```

**Card Border Radius:**
```css
.yt-video-card {
  border-radius: 12px;  /* Change corner roundness */
}
```

### Responsive Breakpoints

| Screen Size | Grid Columns |
|-------------|--------------|
| Desktop (1200px+) | 5 columns |
| Tablet (768px+) | 3-4 columns |
| Mobile (480px+) | 2 columns |
| Small Mobile (<480px) | 2 columns (tighter) |

### Embedding

**HTML:**
```html
<div id="yt-channel-widget"></div>
<script src="path/to/youtube-channel-widget.html"></script>
```

**GHL / External Widget:**
Simply embed as an external HTML widget - CORS-enabled and self-contained.

---

## API Integration Details

Both widgets use: `/api/public/youtube?channel_id=UCxxxxx&max_results=10`

### API Response Format

```json
{
  "success": true,
  "data": [
    {
      "video_id": "dQw4w9WgXcQ",
      "title": "Video Title",
      "description": "Video description...",
      "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/mqdefault.jpg",
      "published_at": "2024-02-14T10:30:00Z",
      "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    },
    ...
  ],
  "count": 10,
  "source": "channel"
}
```

---

## Troubleshooting

### "API key not configured" Error
- Ensure `YOUTUBE_API_KEY` environment variable is set in deployment
- Restart the application after adding the key

### CORS Errors
- Widgets only work when embedded on `carolinapanorama.com` or `*.carolinapanorama.org`
- Check browser console for exact error message
- Verify the API base URL is correct

### No Videos Showing
1. Verify channel/playlist ID is correct
2. Check that the channel/playlist has public videos
3. Ensure you're within the YouTube API quota (10,000 units/day)

### Thumbnails Not Loading
- Check that YouTube API is returning valid thumbnail URLs
- Verify image URLs are accessible (check CORS on image domain)

---

## YouTube API Quota

Free tier provides **10,000 quota units per day**.

**Cost per request:**
- Get channel uploads playlist: ~150 units
- Fetch playlist items: ~1 unit per video
- **Total per full request: ~160 units**

This allows **~60 API calls per day** for each widget. For 2 widgets calling twice daily = ~4 calls/day, well within quota.

For high-traffic sites, consider caching results in your CMS database with hourly or daily refresh.

---

## Advanced: Custom Styling

Both widgets use CSS custom properties (variables) for easy theming. You can override them with a `<style>` block:

```html
<style>
  :root {
    --cp-primary: #2563eb;
    --cp-text: #1e293b;
    --cp-bg: #e0e7ef;
  }
</style>
```

Or edit the CSS directly in each widget HTML file.

---

## Support & Documentation

- Full API docs: See [YOUTUBE_API.md](YOUTUBE_API.md)
- Widget API: `/api/public/youtube`
- Error handling implemented for missing/invalid configurations
