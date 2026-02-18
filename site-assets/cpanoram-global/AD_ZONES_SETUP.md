# Carolina Panorama Ad Zone Setup Guide

## CSS Classes Created

Add these classes to your GHL custom HTML elements:

### Pop-Up Ads
- **`ad-zone-popup`** - Full video/image pop-up (centered, modal-style)
- **`ad-zone-popup-backdrop`** - Dark overlay behind pop-up
- **`ad-zone-slide-in`** - Slides in from bottom-right corner
- **`ad-zone-sticky-note`** - Fixed top-right corner (like a post-it)
- **`ad-zone-push-pin`** - Similar to sticky note, slightly lower

### Sidebar Ads  
- **`ad-zone-sidebar-top`** - Top of sidebar (sticky, stays visible on scroll)
- **`ad-zone-sidebar-middle`** - Middle of sidebar
- **`ad-zone-sidebar-bottom`** - Bottom of sidebar

### Banner Ads
- **`ad-zone-top-banner`** - Full-width banner at top of page
- **`ad-zone-footer`** - Full-width footer ad

### In-Story Ad
- **`ad-zone-instory`** - Automatically injected by JS (no manual setup needed)

---

## How to Add Ads in GHL

### 1. **In-Story Ad (Automatic)**
Just add this script to your article page template:
```html
<script src="YOUR_CDN/carolina-panorama-ads.js"></script>
```

The script will automatically inject:
```html
<broadstreet-zone zone-id="YOUR_INSTORY_ZONE_ID"></broadstreet-zone>
```
into the middle of your article content.

**To customize zone ID:** Edit line 34 in `carolina-panorama-ads.js`

---

### 2. **Pop-Up Ad with Backdrop**
Add two Custom HTML elements:

**Element 1 - Backdrop:**
```html
<div class="ad-zone-popup-backdrop" style="display: none;"></div>
```

**Element 2 - Pop-Up Content:**
```html
<div class="ad-zone-popup" style="display: none;">
    <broadstreet-zone zone-id="YOUR_POPUP_ZONE_ID"></broadstreet-zone>
</div>
```

**Activate it:**
- For time-delayed: Uncomment line 145 in JS file
- For exit-intent: Uncomment line 149 in JS file

---

### 3. **Sticky Note (Top Right)**
Add Custom HTML element with class:
```html
<div class="ad-zone-sticky-note">
    <broadstreet-zone zone-id="YOUR_STICKY_ZONE_ID"></broadstreet-zone>
</div>
```

---

### 4. **Slide-In Ad**
Add Custom HTML element:
```html
<div class="ad-zone-slide-in" style="display: none;">
    <broadstreet-zone zone-id="YOUR_SLIDEIN_ZONE_ID"></broadstreet-zone>
</div>
```

**Activate it:** Uncomment line 152 in JS file

---

### 5. **Top Banner**
Add Custom HTML element at top of page:
```html
<div class="ad-zone-top-banner">
    <broadstreet-zone zone-id="YOUR_BANNER_ZONE_ID"></broadstreet-zone>
</div>
```

---

### 6. **Sidebar Ads**
Add to your sidebar section:
```html
<!-- Top sidebar ad (sticky) -->
<div class="ad-zone-sidebar-top">
    <broadstreet-zone zone-id="YOUR_SIDEBAR_TOP_ZONE_ID"></broadstreet-zone>
</div>

<!-- Middle sidebar ad -->
<div class="ad-zone-sidebar-middle">
    <broadstreet-zone zone-id="YOUR_SIDEBAR_MID_ZONE_ID"></broadstreet-zone>
</div>

<!-- Bottom sidebar ad -->
<div class="ad-zone-sidebar-bottom">
    <broadstreet-zone zone-id="YOUR_SIDEBAR_BOT_ZONE_ID"></broadstreet-zone>
</div>
```

---

## Configuration Tips

### BroadStreet Zone IDs
Get these from your BroadStreet dashboard when creating each ad zone.

### Pop-Up Timing
Edit `carolina-panorama-ads.js`:
- **Line 145**: Time delay in seconds (default: 15)
- **Line 152**: Slide-in delay in seconds (default: 8)

### Mobile Behavior
- Sticky/Push Pin ads become static (non-fixed) on mobile
- Pop-ups scale to 95% of screen
- All ads are touch-friendly

---

## Files Modified/Created
1. `/cpanoram-global/carolina-panorama-global.css` - Ad zone styling
2. `/cpanoram-global/carolina-panorama-ads.js` - Ad injection & behavior

## Include in Your GHL Pages
Add to page `<head>` or footer:
```html
<link rel="stylesheet" href="YOUR_CDN/carolina-panorama-global.css">
<script src="YOUR_CDN/carolina-panorama-ads.js"></script>
```
