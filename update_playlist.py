import requests
import re

# 1. Source Link (12k+ world channels)
ORIGINAL_M3U_URL = "https://github.io"
OUTPUT_FILE = "my_custom_playlist.m3u"

# 2. మీ లిస్ట్‌లోని ఛానల్స్ (ఫిల్టరింగ్ సులువుగా అవ్వడానికి చిన్న అక్షరాలతో ఇవ్వబడ్డాయి)
ALLOWED_CHANNELS = [
    # 1. News Group
    "10 tv", "abn andhra jyoti", "cvr news", "etv andhra pradesh", "etv news", 
    "etv telangana", "hmtv", "inews", "mahaa news", "mojo tv", "ntv telugu", 
    "prime9 news", "raj news telugu", "sakshi tv", "tv5 news", "tv9 telugu", 
    "v6 news", "zee telugu news",
    
    # 2. Entertainment Group
    "etv josh", "etv plus", "etv telugu hd", "etv telugu", "mahaa max", "mango mobile tv", 
    "star maa hd", "star maa", "telugu one", "vanitha tv", "vissa tv", "zee telugu hd", 
    "zee telugu", "sun gemini", "gemini tv",
    
    # 3. Movies Group
    "etv cinema", "sony pix", "star maa movies", "studio one", "tolly tv",
    
    # 4. Kids / Animation
    "cartoon network", "discovery kids", "disney channel", "disney junior", 
    "etv bal bharat", "hungama tv", "nickelodeon", "sonic", "sony yay", 
    "super hungama", "wow kidz telugu",
    
    # 5. Religious Group
    "aastha telugu", "bhakthi tv", "cvr om spiritual", "hindu dharmam", 
    "mahaa bhakti", "pmc telugu", "svbc",
    
    # 6. Music Group
    "etv beats", "etv music", "raj musix telugu",
    
    # 7. General Group
    "dd saptagiri",
    
    # 8. Documentary Group
    "history tv18", "discovery channel", "national geographic", "sony bbc earth",
    
    # 10. Comedy Group
    "etv comedy"
]

def fetch_and_filter_m3u():
    print("Fetching original 12k+ M3U playlist from iptv-org...")
    try:
        response = requests.get(ORIGINAL_M3U_URL, timeout=60)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching playlist: {e}")
        return

    lines = response.text.splitlines()
    custom_playlist = ["#EXTM3U"]
    
    current_extinf = None
    
    for line in lines:
        if line.startswith("#EXTM3U"):
            continue
            
        if line.startswith("#EXTINF:"):
            current_extinf = line
        elif line.strip() and not line.startswith("#"):
            if current_extinf:
                # ఛానల్ పేరును వేరు చేసి చిన్న అక్షరాల్లోకి మారుస్తుంది
                channel_name = current_extinf.split(',')[-1].strip().lower()
                
                # (1080p), (720p) లాంటి బ్రాకెట్ టెక్స్ట్‌లను తీసేసి కేవలం పేరును మాత్రమే చెక్ చేస్తుంది
                clean_name = re.sub(r'\s*\([^)]*\)', '', channel_name).strip()
                
                # పేరు మ్యాచ్ అయిందో లేదో చెక్ చేస్తుంది
                if any(allowed in clean_name for allowed in ALLOWED_CHANNELS):
                    # ఒరిజినల్ గ్రూప్ టైటిల్ ఉందో లేదో చూస్తుంది
                    group_match = re.search(r'group-title="([^"]+)"', current_extinf)
                    
                    if group_match:
                        final_extinf = current_extinf
                    else:
                        # ఒకవేళ గ్రూప్ లేకపోతే "Telugu" గ్రూప్ కింద యాడ్ చేస్తుంది
                        final_extinf = current_extinf.replace('#EXTINF:', '#EXTINF: group-title="Telugu"', 1)
                    
                    custom_playlist.append(final_extinf)
                    custom_playlist.append(line)
                    
                current_extinf = None

    # 3. కొత్త ఫైల్‌ను సేవ్ చేయడం
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(custom_playlist))
    print(f"Successfully updated! Your selected channels are filtered.")

if __name__ == "__main__":
    fetch_and_filter_m3u()
