from flask import Flask, render_template_string, request, jsonify
import json
import re
import urllib.request
import os

app = Flask(__name__)

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "AIzaSyCOWy4Qlfw7Kzj08akPy1UsheTSvAgXXXA")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyC2SZjrMhwHTP0MeofzT8MK7GMyXLBXly0")

def gemini(prompt):
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}]
    }).encode()
    req = urllib.request.Request(
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-2.5-flash:generateContent?key=" + GEMINI_API_KEY,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode())
    return result["candidates"][0]["content"]["parts"][0]["text"]

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>KaraokeCousinz Post Generator</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root { --gold:#c9a84c; --dark:#1a1a2e; --card:#16213e; --text:#eaeaea; --muted:#a0a0b0; --radius:14px; }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { background:var(--dark); color:var(--text); font-family:'DM Sans',sans-serif; min-height:100vh; padding:2rem 1rem; }
  .header { text-align:center; margin-bottom:2.5rem; }
  .header h1 { font-family:'Playfair Display',serif; font-size:2.2rem; color:var(--gold); letter-spacing:1px; }
  .header p { color:var(--muted); font-size:0.95rem; margin-top:6px; }
  .container { max-width:860px; margin:0 auto; }
  .form-card { background:var(--card); border-radius:var(--radius); padding:2rem; border:0.5px solid rgba(201,168,76,0.2); margin-bottom:2rem; }
  .form-grid { display:grid; grid-template-columns:1fr 1fr; gap:1rem; }
  .form-group { display:flex; flex-direction:column; gap:6px; }
  .form-group.full { grid-column:1/-1; }
  label { font-size:12px; font-weight:500; color:var(--gold); letter-spacing:0.5px; text-transform:uppercase; }
  input, textarea { background:rgba(255,255,255,0.05); border:0.5px solid rgba(255,255,255,0.15); border-radius:8px; padding:10px 14px; color:var(--text); font-family:'DM Sans',sans-serif; font-size:14px; outline:none; transition:border 0.2s; }
  input:focus, textarea:focus { border-color:var(--gold); }
  input.auto-filled, textarea.auto-filled { border-color:#1D9E75; background:rgba(29,158,117,0.08); }
  textarea { resize:vertical; min-height:80px; }
  .btn { width:100%; padding:14px; background:var(--gold); color:var(--dark); font-family:'DM Sans',sans-serif; font-size:15px; font-weight:500; border:none; border-radius:10px; cursor:pointer; margin-top:1.5rem; transition:opacity 0.2s; }
  .btn:hover { opacity:0.88; }
  .btn:disabled { opacity:0.5; cursor:not-allowed; }
  .btn-fetch { width:100%; padding:10px; background:transparent; color:var(--gold); font-family:'DM Sans',sans-serif; font-size:13px; font-weight:500; border:0.5px solid var(--gold); border-radius:10px; cursor:pointer; margin-top:0.5rem; transition:all 0.2s; }
  .btn-fetch:hover { background:rgba(201,168,76,0.1); }
  .status { font-size:13px; text-align:center; margin:8px 0; min-height:20px; }
  .status.loading { color:var(--muted); }
  .status.success { color:#1D9E75; }
  .status.error { color:#e94560; }
  .fields-section { display:none; margin-top:1.5rem; }
  .spinner { display:none; text-align:center; color:var(--muted); font-size:14px; margin:1rem 0; }
  .results { display:none; }
  .platform-card { background:var(--card); border-radius:var(--radius); padding:1.5rem; border:0.5px solid rgba(255,255,255,0.08); margin-bottom:1.2rem; }
  .platform-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem; }
  .platform-name { font-size:13px; font-weight:500; padding:4px 14px; border-radius:20px; }
  .fb { background:rgba(24,119,242,0.2); color:#5b9bd5; }
  .ig { background:rgba(233,69,96,0.2); color:#e94560; }
  .tw { background:rgba(160,160,176,0.2); color:var(--muted); }
  .wa { background:rgba(37,211,102,0.15); color:#25d366; }
  .copy-btn { font-size:12px; padding:4px 12px; background:transparent; border:0.5px solid rgba(255,255,255,0.2); border-radius:6px; color:var(--muted); cursor:pointer; transition:all 0.2s; }
  .copy-btn:hover { border-color:var(--gold); color:var(--gold); }
  .copy-btn.copied { border-color:#1D9E75; color:#1D9E75; }
  .post-content { font-size:13px; line-height:1.8; color:var(--text); white-space:pre-wrap; background:rgba(255,255,255,0.03); border-radius:8px; padding:14px; }
  .cost-note { text-align:center; font-size:12px; color:var(--muted); margin-top:1rem; }
  .auto-tag { font-size:11px; color:#1D9E75; margin-left:6px; font-weight:400; text-transform:none; letter-spacing:0; }
  .free-badge { display:inline-block; font-size:11px; background:rgba(29,158,117,0.2); color:#1D9E75; padding:2px 8px; border-radius:20px; margin-left:8px; vertical-align:middle; }
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>KaraokeCousinz</h1>
    <p>Post Generator - Our YouTube Fame Karaoke Singers Bas & Sumathy
      <span class="free-badge">Powered by Gemini - FREE</span>
    </p>
  </div>

  <div class="form-card">

    <div class="form-group full">
      <label>YouTube Link</label>
      <input type="text" id="yt_link" placeholder="https://youtu.be/..." />
      <button class="btn-fetch" onclick="fetchAndExtract()">Auto-fetch & Extract All Details</button>
      <div class="status" id="fetch_status"></div>
    </div>

    <div class="fields-section" id="fields_section">
      <div class="form-grid">
        <div class="form-group full">
          <label>Song Name <span class="auto-tag" id="tag_song"></span></label>
          <input type="text" id="song_name" placeholder="e.g. Ennodu Nee Irundhaal" />
        </div>
        <div class="form-group">
          <label>Movie Name <span class="auto-tag" id="tag_movie"></span></label>
          <input type="text" id="movie_name" placeholder="e.g. Dharmadurai" />
        </div>
        <div class="form-group">
          <label>Movie Year <span class="auto-tag" id="tag_year"></span></label>
          <input type="text" id="movie_year" placeholder="e.g. 1991" />
        </div>
        <div class="form-group">
          <label>Composer <span class="auto-tag" id="tag_composer"></span></label>
          <input type="text" id="composer" placeholder="e.g. Ilaiyaraaja" />
        </div>
        <div class="form-group">
          <label>Originally Sung By <span class="auto-tag" id="tag_singers"></span></label>
          <input type="text" id="original_singers" placeholder="e.g. K.J. Yesudas & Swarnalatha" />
        </div>
        <div class="form-group">
          <label>Director <span class="auto-tag" id="tag_director"></span></label>
          <input type="text" id="director" placeholder="e.g. Rajashekar" />
        </div>
        <div class="form-group">
          <label>Lyricist <span class="auto-tag" id="tag_lyricist"></span></label>
          <input type="text" id="lyricist" placeholder="e.g. Panju Arunachalam" />
        </div>
        <div class="form-group full">
          <label>Special Note <span class="auto-tag" id="tag_note"></span></label>
          <textarea id="special_note" placeholder="e.g. Viewer request from Malaysia..."></textarea>
        </div>
      </div>
      <button class="btn" id="generateBtn" onclick="generatePosts()">Generate Posts for All Platforms</button>
    </div>

  </div>

  <div class="spinner" id="spinner">Generating your posts with Gemini AI... please wait!</div>

  <div class="results" id="results">
    <div class="platform-card">
      <div class="platform-header">
        <span class="platform-name fb">Facebook Page</span>
        <button class="copy-btn" id="copy_fb" onclick="copyText('fb_content','copy_fb')">Copy</button>
      </div>
      <div class="post-content" id="fb_content"></div>
    </div>
    <div class="platform-card">
      <div class="platform-header">
        <span class="platform-name ig">Instagram</span>
        <button class="copy-btn" id="copy_ig" onclick="copyText('ig_content','copy_ig')">Copy</button>
      </div>
      <div class="post-content" id="ig_content"></div>
    </div>
    <div class="platform-card">
      <div class="platform-header">
        <span class="platform-name tw">Twitter / X</span>
        <button class="copy-btn" id="copy_tw" onclick="copyText('tw_content','copy_tw')">Copy</button>
      </div>
      <div class="post-content" id="tw_content"></div>
    </div>
    <div class="platform-card">
      <div class="platform-header">
        <span class="platform-name wa">WhatsApp Channel</span>
        <button class="copy-btn" id="copy_wa" onclick="copyText('wa_content','copy_wa')">Copy</button>
      </div>
      <div class="post-content" id="wa_content"></div>
    </div>
    <div class="cost-note">Cost this run: Rs. 0.00 - Gemini is FREE!</div>
  </div>
</div>

<script>
function extractVideoId(url) {
  const patterns = [
    /youtu\\.be\\/([^?&]+)/,
    /youtube\\.com\\/watch\\?v=([^&]+)/,
    /youtube\\.com\\/shorts\\/([^?&]+)/
  ];
  for (const p of patterns) {
    const m = url.match(p);
    if (m) return m[1];
  }
  return null;
}

async function fetchAndExtract() {
  const url = document.getElementById('yt_link').value.trim();
  if (!url) { setStatus('Please paste a YouTube link first!', 'error'); return; }
  const videoId = extractVideoId(url);
  if (!videoId) { setStatus('Could not read video ID. Please check the link!', 'error'); return; }

  setStatus('Step 1 of 2 - Fetching video from YouTube...', 'loading');

  const res = await fetch('/fetch_video', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({video_id: videoId})
  });
  const data = await res.json();
  if (data.error) { setStatus('Error: ' + data.error, 'error'); return; }

  setStatus('Step 2 of 2 - Extracting song details with Gemini AI...', 'loading');

  const res2 = await fetch('/extract_details', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({title: data.title, description: data.description})
  });
  const details = await res2.json();

  if (details.error) { setStatus('Gemini error: ' + details.error, 'error'); return; }

  document.getElementById('fields_section').style.display = 'block';

  let filled = 0;
  filled += fillField('song_name', details.song_name, 'tag_song');
  filled += fillField('movie_name', details.movie_name, 'tag_movie');
  filled += fillField('movie_year', details.movie_year, 'tag_year');
  filled += fillField('composer', details.composer, 'tag_composer');
  filled += fillField('original_singers', details.original_singers, 'tag_singers');
  filled += fillField('director', details.director, 'tag_director');
  filled += fillField('lyricist', details.lyricist, 'tag_lyricist');
  filled += fillField('special_note', details.special_note, 'tag_note');

  if (filled > 0) {
    setStatus('All done! ' + filled + ' fields auto-filled. Click Generate Posts!', 'success');
  } else {
    setStatus('Video found but no song details in description. Please fill manually!', 'error');
  }
}

function fillField(id, value, tagId) {
  if (value && value.trim() !== '' && value !== 'N/A') {
    const el = document.getElementById(id);
    el.value = value.trim();
    el.classList.add('auto-filled');
    document.getElementById(tagId).textContent = 'auto-filled';
    return 1;
  }
  return 0;
}

function setStatus(msg, type) {
  const el = document.getElementById('fetch_status');
  el.textContent = msg;
  el.className = 'status ' + type;
}

async function generatePosts() {
  const data = {
    yt_link: document.getElementById('yt_link').value,
    song_name: document.getElementById('song_name').value,
    movie_name: document.getElementById('movie_name').value,
    movie_year: document.getElementById('movie_year').value,
    composer: document.getElementById('composer').value,
    original_singers: document.getElementById('original_singers').value,
    director: document.getElementById('director').value,
    lyricist: document.getElementById('lyricist').value,
    special_note: document.getElementById('special_note').value
  };
  document.getElementById('generateBtn').disabled = true;
  document.getElementById('spinner').style.display = 'block';
  document.getElementById('results').style.display = 'none';
  const res = await fetch('/generate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  });
  const result = await res.json();
  document.getElementById('fb_content').textContent = result.facebook;
  document.getElementById('ig_content').textContent = result.instagram;
  document.getElementById('tw_content').textContent = result.twitter;
  document.getElementById('wa_content').textContent = result.whatsapp;
  document.getElementById('spinner').style.display = 'none';
  document.getElementById('results').style.display = 'block';
  document.getElementById('generateBtn').disabled = false;
}

function copyText(id, btnId) {
  navigator.clipboard.writeText(document.getElementById(id).textContent);
  const btn = document.getElementById(btnId);
  btn.textContent = 'Copied!';
  btn.classList.add('copied');
  setTimeout(() => { btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 2000);
}
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/fetch_video', methods=['POST'])
def fetch_video():
    data = request.json
    video_id = data.get('video_id')
    try:
        api_url = (
            f"https://www.googleapis.com/youtube/v3/videos"
            f"?part=snippet&id={video_id}&key={YOUTUBE_API_KEY}"
        )
        with urllib.request.urlopen(api_url) as response:
            result = json.loads(response.read().decode())
        if not result.get('items'):
            return jsonify({'error': 'Video not found'})
        snippet = result['items'][0]['snippet']
        return jsonify({
            'title': snippet.get('title', ''),
            'description': snippet.get('description', '')
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/extract_details', methods=['POST'])
def extract_details():
    data = request.json
    title = data.get('title', '')
    description = data.get('description', '')

    prompt = f"""Extract song details from this YouTube video title and description.
Return ONLY a raw JSON object, no markdown, no code blocks, no extra text at all.

{{
  "song_name": "",
  "movie_name": "",
  "movie_year": "",
  "composer": "",
  "original_singers": "",
  "director": "",
  "lyricist": "",
  "special_note": ""
}}

Rules:
- song_name: the name of the song being performed
- movie_name: the film this song is from
- movie_year: the year of the film
- composer: music composer / music director
- original_singers: who originally sang this song
- director: film director
- lyricist: who wrote the lyrics
- special_note: any special context like viewer request, occasion, dedication etc.
- If not found leave as empty string

TEXT:
Title: {title}
Description: {description}"""

    try:
        raw = gemini(prompt)
        raw = raw.strip()
        if raw.startswith("```"):
            raw = re.sub(r'```[a-z]*', '', raw).strip().strip('`').strip()
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        result = json.loads(match.group())
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json

    prompt = f"""You are a social media content creator for KaraokeCousinz, a YouTube karaoke channel.

Generate social media posts for the following video. STRICT RULES:
- ALWAYS include the exact phrase "Our YouTube Fame Karaoke Singers Bas & Sumathy" in EVERY post prominently
- The word is always "COUSINZ" not "cousins" — never spell it as "cousins"
- Never say just "Hey Cousinz" — always say enriching words like "Hey Cousinz Family", "Dear Cousinz Supporters", "Dear Cousinz Community", "Hey Cousinz Viewers", "Beloved Cousinz Fans" or similar warm stylish greetings
- Make each post unique in tone for its platform
- Be warm, energetic and inviting to attract viewers
- Include all song details naturally
- Facebook: long, warm, emotional, detailed — start with "Dear Followers and Well-wishers"
- Instagram: punchy, energetic, rich hashtags
- Twitter: short and sharp, max 280 characters, 2-3 hashtags only
- WhatsApp: friendly, personal, encourage sharing — use warm greeting like "Dear Cousinz Family" or "Hey Cousinz Supporters"

VIDEO DETAILS:
- YouTube Link: {data['yt_link']}
- Song: {data['song_name']}
- Movie: {data['movie_name']} ({data['movie_year']})
- Director: {data['director']}
- Lyricist: {data['lyricist']}
- Composer: {data['composer']}
- Originally Sung By: {data['original_singers']}
- Special Note: {data['special_note']}

Return ONLY a raw JSON object, no markdown, no code blocks, no extra text:
{{
  "facebook": "full facebook post here",
  "instagram": "full instagram post with hashtags here",
  "twitter": "short twitter post here",
  "whatsapp": "friendly whatsapp post here"
}}"""

    try:
        raw = gemini(prompt)
        raw = raw.strip()
        if raw.startswith("```"):
            raw = re.sub(r'```[a-z]*', '', raw).strip().strip('`').strip()
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        result = json.loads(match.group())
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
