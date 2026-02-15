import html as html_module
import json
import httpx
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, Response

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# Base URL for sample audio (SoundHelix); we use track index % 16 + 1
AUDIO_BASE = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-{}.mp3"

# Global top 100 songs (title, artist, year) — diverse regions
TOP_100 = [
    ("Blinding Lights", "The Weeknd", 2020),
    ("Despacito", "Luis Fonsi & Daddy Yankee", 2017),
    ("Shape of You", "Ed Sheeran", 2017),
    ("Dynamite", "BTS", 2020),
    ("Someone Like You", "Adele", 2011),
    ("Bohemian Rhapsody", "Queen", 1975),
    ("Taki Taki", "DJ Snake, Selena Gomez, Ozuna, Cardi B", 2018),
    ("Mi Gente", "J Balvin & Willy William", 2017),
    ("Levitating", "Dua Lipa", 2020),
    ("Waka Waka (This Time for Africa)", "Shakira", 2010),
    ("Gangnam Style", "PSY", 2012),
    ("Hotel California", "Eagles", 1976),
    ("Smooth", "Santana feat. Rob Thomas", 1999),
    ("Kill This Love", "BLACKPINK", 2019),
    ("Viva la Vida", "Coldplay", 2008),
    ("Chandelier", "Sia", 2014),
    ("Havana", "Camila Cabello", 2017),
    ("La Bicicleta", "Carlos Vives & Shakira", 2016),
    ("Butter", "BTS", 2021),
    ("Billie Jean", "Michael Jackson", 1982),
    ("Calm Down", "Rema & Selena Gomez", 2022),
    ("Last Last", "Burna Boy", 2022),
    ("Love Nwantiti", "CKay", 2019),
    ("Essence", "Wizkid feat. Tems", 2020),
    ("Water", "Tyla", 2023),
    ("Flowers", "Miley Cyrus", 2023),
    ("As It Was", "Harry Styles", 2022),
    ("Bad Guy", "Billie Eilish", 2019),
    ("Rolling in the Deep", "Adele", 2010),
    ("Uptown Funk", "Bruno Mars", 2014),
    ("Stairway to Heaven", "Led Zeppelin", 1971),
    ("Imagine", "John Lennon", 1971),
    ("Hey Jude", "The Beatles", 1968),
    ("Thriller", "Michael Jackson", 1982),
    ("Smells Like Teen Spirit", "Nirvana", 1991),
    ("Wonderwall", "Oasis", 1995),
    ("Lose Yourself", "Eminem", 2002),
    ("Shallow", "Lady Gaga & Bradley Cooper", 2018),
    ("Old Town Road", "Lil Nas X", 2019),
    ("God's Plan", "Drake", 2018),
    ("Happy", "Pharrell Williams", 2013),
    ("Don't Stop Believin'", "Journey", 1981),
    ("We Will Rock You", "Queen", 1977),
    ("Africa", "Toto", 1982),
    ("Take On Me", "a-ha", 1984),
    ("Hallelujah", "Leonard Cohen", 1984),
    ("Yellow", "Coldplay", 2000),
    ("Fix You", "Coldplay", 2005),
    ("Creep", "Radiohead", 1992),
    ("Zombie", "The Cranberries", 1994),
    ("Bitter Sweet Symphony", "The Verve", 1997),
    ("Every Breath You Take", "The Police", 1983),
    ("With or Without You", "U2", 1987),
    ("La Vie en Rose", "Edith Piaf", 1945),
    ("Bella Ciao", "Traditional (Italy)", 1940),
    ("Sway", "Dean Martin", 1954),
    ("Volare", "Domenico Modugno", 1958),
    ("99 Luftballons", "Nena", 1983),
    ("Dragostea din tei", "O-Zone", 2003),
    ("Stereo Love", "Edward Maya & Vika Jigulina", 2009),
    ("Dernière Danse", "Indila", 2013),
    ("Alors on danse", "Stromae", 2009),
    ("Tous les mêmes", "Stromae", 2013),
    ("Formidable", "Stromae", 2013),
    ("Tunak Tunak Tun", "Daler Mehndi", 1998),
    ("Jai Ho", "A.R. Rahman & The Pussycat Dolls", 2008),
    ("Chammak Challo", "A.R. Rahman", 2011),
    ("Koi Mil Gaya", "Kavita Krishnamurthy", 2003),
    ("Senorita", "Shawn Mendes & Camila Cabello", 2019),
    ("Dakiti", "Bad Bunny & Jhay Cortez", 2020),
    ("Yonaguni", "Bad Bunny", 2021),
    ("Moscow Mule", "Bad Bunny", 2022),
    ("Provenza", "Karol G", 2022),
    ("TQG", "Karol G & Shakira", 2023),
    ("Shakira: Bzrp", "Bizarrap & Shakira", 2023),
    ("Me Rehúso", "Danny Ocean", 2016),
    ("Danza Kuduro", "Don Omar & Lucenzo", 2010),
    ("Gasolina", "Daddy Yankee", 2004),
    ("Con Calma", "Daddy Yankee & Snow", 2019),
    ("Reggaetón Lento", "CNCO", 2016),
    ("Safaera", "Bad Bunny", 2020),
    ("Pink Venom", "BLACKPINK", 2022),
    ("How You Like That", "BLACKPINK", 2020),
    ("Spring Day", "BTS", 2017),
    ("Boy With Luv", "BTS feat. Halsey", 2019),
    ("Life Goes On", "BTS", 2020),
    ("Anti-Hero", "Taylor Swift", 2022),
    ("Cruel Summer", "Taylor Swift", 2019),
    ("Easy On Me", "Adele", 2021),
    ("Hello", "Adele", 2015),
    ("Blinding Lights", "The Weeknd", 2019),
    ("Save Your Tears", "The Weeknd", 2020),
    ("Heat Waves", "Glass Animals", 2020),
    ("Good 4 U", "Olivia Rodrigo", 2021),
    ("Drivers License", "Olivia Rodrigo", 2021),
    ("Stay", "The Kid LAROI & Justin Bieber", 2021),
    ("Peaches", "Justin Bieber", 2021),
    ("Industry Baby", "Lil Nas X", 2021),
    ("Montero", "Lil Nas X", 2021),
    ("Rain on Me", "Lady Gaga & Ariana Grande", 2020),
    ("Bad Romance", "Lady Gaga", 2009),
    ("Thank U, Next", "Ariana Grande", 2018),
    ("No Tears Left to Cry", "Ariana Grande", 2018),
    ("Don't Start Now", "Dua Lipa", 2019),
    ("New Rules", "Dua Lipa", 2017),
    ("Sweet Child O' Mine", "Guns N' Roses", 1987),
    ("Purple Haze", "Jimi Hendrix", 1967),
    ("Like a Rolling Stone", "Bob Dylan", 1965),
    ("Let It Be", "The Beatles", 1970),
    ("Yesterday", "The Beatles", 1965),
    ("Piano Man", "Billy Joel", 1973),
    ("Livin' on a Prayer", "Bon Jovi", 1986),
    ("Eye of the Tiger", "Survivor", 1982),
    ("Roar", "Katy Perry", 2013),
    ("Shake It Off", "Taylor Swift", 2014),
    ("Counting Stars", "OneRepublic", 2013),
    ("Radioactive", "Imagine Dragons", 2012),
    ("Believer", "Imagine Dragons", 2017),
]


def _esc(s):
    return html_module.escape(str(s)) if s else ""


@app.get("/stream")
async def stream_audio(url: str = Query(..., description="Audio URL to proxy")):
    """Proxy audio so the browser can play it (avoids CORS)."""
    if not url.startswith("https://"):
        return Response(status_code=400)
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(url, timeout=30.0)
            r.raise_for_status()
            return Response(
                content=r.content,
                media_type=r.headers.get("content-type", "audio/mpeg"),
                headers={"Accept-Ranges": "bytes"},
            )
    except Exception:
        return Response(status_code=502)


@app.get("/", response_class=HTMLResponse)
async def home():
    rows = "".join(
        f"""
        <li class="song-row" data-index="{i}">
          <button type="button" class="play-btn" onclick="play({i})" aria-label="Play">
            <span class="play-icon">&#9654;</span>
          </button>
          <span class="rank">{i + 1}</span>
          <div class="song-info">
            <span class="title">{_esc(title)}</span>
            <span class="artist">{_esc(artist)}</span>
          </div>
          <span class="year">{_esc(year)}</span>
        </li>"""
        for i, (title, artist, year) in enumerate(TOP_100[:100])
    )
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Bliss — Global Top 100</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Outfit', system-ui, sans-serif;
      min-height: 100vh;
      color: #e8e8ed;
      padding: 2rem 1rem 3rem;
      position: relative;
    }}
    body::before {{
      content: "";
      position: fixed;
      inset: 0;
      background: url("https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=1920&q=80") center/cover no-repeat;
      z-index: -2;
    }}
    body::after {{
      content: "";
      position: fixed;
      inset: 0;
      background: linear-gradient(135deg, rgba(18,15,28,0.94) 0%, rgba(35,28,52,0.92) 40%, rgba(22,28,45,0.93) 70%, rgba(12,14,22,0.96) 100%);
      z-index: -1;
    }}
    .wrap {{ max-width: 680px; margin: 0 auto; position: relative; z-index: 0; }}
    .header {{
      text-align: center;
      margin-bottom: 2rem;
      padding: 1.5rem 1rem;
      background: rgba(255,255,255,0.05);
      border-radius: 20px;
      border: 1px solid rgba(255,255,255,0.08);
      backdrop-filter: blur(12px);
    }}
    .header h1 {{ font-size: 2rem; font-weight: 700; letter-spacing: -0.03em; margin-bottom: 0.4rem; }}
    .header p {{ font-size: 0.95rem; color: #a0a0b8; }}
    .header .badge {{ display: inline-block; margin-top: 0.5rem; font-size: 0.75rem; font-weight: 600; color: #818cf8; background: rgba(99,102,241,0.2); padding: 0.3rem 0.65rem; border-radius: 999px; }}
    .list {{ list-style: none; display: flex; flex-direction: column; gap: 0.6rem; }}
    .song-row {{
      display: flex;
      align-items: center;
      gap: 1rem;
      padding: 1rem 1.2rem;
      background: rgba(255,255,255,0.06);
      border-radius: 14px;
      border: 1px solid rgba(255,255,255,0.08);
      backdrop-filter: blur(8px);
      transition: all 0.22s ease;
    }}
    .song-row:hover {{
      background: rgba(255,255,255,0.1);
      border-color: rgba(255,255,255,0.12);
      transform: translateX(4px);
      box-shadow: 0 8px 24px rgba(0,0,0,0.25);
    }}
    .song-row.playing {{ border-color: rgba(129,140,248,0.5); background: rgba(99,102,241,0.15); }}
    .play-btn {{
      width: 40px;
      height: 40px;
      flex-shrink: 0;
      border: none;
      border-radius: 50%;
      background: rgba(129,140,248,0.25);
      color: #c7d2fe;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background 0.2s, transform 0.1s;
    }}
    .play-btn:hover {{
      background: rgba(129,140,248,0.45);
      transform: scale(1.08);
    }}
    .song-row.playing .play-btn {{
      background: #6366f1;
      color: #fff;
    }}
    .play-icon {{ font-size: 0.9rem; margin-left: 2px; }}
    .rank {{
      width: 40px;
      font-size: 1rem;
      font-weight: 700;
      color: #818cf8;
      text-align: right;
      flex-shrink: 0;
      letter-spacing: -0.02em;
    }}
    .song-info {{ flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 0.2rem; }}
    .title {{ font-weight: 600; font-size: 1rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; letter-spacing: 0.01em; }}
    .artist {{ font-size: 0.82rem; color: #9090a8; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    .year {{
      font-size: 0.8rem;
      color: #707088;
      flex-shrink: 0;
      font-weight: 500;
      padding: 0.25rem 0.5rem;
      background: rgba(255,255,255,0.06);
      border-radius: 8px;
    }}
    .player-bar {{
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      padding: 0.75rem 1rem;
      background: rgba(18,15,28,0.95);
      border-top: 1px solid rgba(255,255,255,0.08);
      backdrop-filter: blur(12px);
      z-index: 10;
    }}
    .player-bar-inner {{ max-width: 680px; margin: 0 auto; }}
    .now-playing {{ font-size: 0.8rem; color: #9090a8; margin-bottom: 0.35rem; }}
    .now-playing strong {{ color: #fff; }}
    .player-bar audio {{ width: 100%; height: 36px; border-radius: 8px; }}
  </style>
</head>
<body>
  <div class="wrap">
    <header class="header">
      <h1>Bliss</h1>
      <p>Global top 100 songs — from every corner of the world</p>
      <span class="badge">100 songs</span>
    </header>
    <ul class="list" id="songList">{rows}</ul>
  </div>
  <div class="player-bar">
    <div class="player-bar-inner">
      <p class="now-playing" id="nowPlaying">Click a play button to start</p>
      <audio id="audio" controls></audio>
    </div>
  </div>
  <script>
    var audio = document.getElementById("audio");
    var nowEl = document.getElementById("nowPlaying");
    var baseUrl = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-";
    var tracks = {json.dumps([{"title": t[0], "artist": t[1], "year": t[2]} for t in TOP_100[:100]])};

    function play(i) {{
      var trackNum = (i % 16) + 1;
      var url = baseUrl + trackNum + ".mp3";
      audio.src = "/stream?url=" + encodeURIComponent(url);
      audio.play().catch(function() {{}});
      nowEl.innerHTML = "Now playing: <strong>" + tracks[i].title + "</strong> — " + tracks[i].artist;
      document.querySelectorAll(".song-row").forEach(function(row, j) {{
        row.classList.toggle("playing", j === i);
      }});
    }}
  </script>
</body>
</html>
"""
