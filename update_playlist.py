import requests
import re

# 1. ఒరిజినల్ సోర్స్ లింక్
ORIGINAL_M3U_URL = "https://github.io"
OUTPUT_FILE = "my_custom_playlist.m3u"

# 2. మీరు ఇచ్చిన ఖచ్చితమైన ఛానల్స్ లిస్ట్ (ఎలాంటి మార్పులు లేకుండా సేమ్ టు సేమ్ ఇవ్వబడింది)
GROUPS_AND_CHANNELS = {
    "News Group": [
        "10 TV (720p)", "ABN Andhra Jyoti (720p)", "CVR News (576p)", "ETV Andhra Pradesh (1080p)", 
        "ETV News (1080p)", "ETV Telangana (1080p)", "HMTV (India) (720p)", "INews (720p)", 
        "Mahaa News (1080p)", "Mojo TV (576p)", "NTV Telugu (1080p)", "Prime9 News (1080p)", 
        "Raj News Telugu (576p)", "Sakshi TV (576p)", "TV5 News (576p)", "TV9 Telugu (720p)", 
        "V6 News (576p)", "Zee Telugu News (720p)"
    ],
    "Entertainment Group": [
        "ETV Josh (1080p)", "ETV Plus (396p)", "ETV Telugu HD (1080p)", "Mahaa Max (1080p)", 
        "Mango Mobile TV (1080p)", "Star Maa HD (720p)", "Telugu One (1080p)", "Vanitha TV (576p)", 
        "Vissa TV (576p)", "Zee Telugu HD (576p)", "Sun Gemini (576p)"
    ],
    "Movies Group": [
        "ETV Cinema (396p)", "ETV Cinema HD (1080p)", "Sony Pix HD (1080p)", 
        "Star Maa Movies HD (720p)", "Studio One + (720p)", "Tolly TV (1080p)"
    ],
    "Kids / Animation": [
        "Cartoon Network (India) (720p)", "Discovery Kids (720p)", "Disney Channel (India) HD (1080p)", 
        "Disney Junior (India) (576p)", "ETV Bal Bharat (576p)", "Hungama TV (576p)", 
        "Nickelodeon (India) (576p)", "Sonic (576p)", "Sony Yay! (576p)", "Super Hungama (576p)", 
        "WOW Kidz Telugu (720p)"
    ],
    "Religious Group": [
        "Aastha Telugu (576p)", "Bhakthi TV (720p)", "CVR OM Spiritual (576p)", 
        "Hindu Dharmam (1080p)", "Mahaa Bhakti (1080p)", "PMC Telugu (1080p)", "SVBC (1080p)"
    ],
    "Music Group": [
        "ETV Beats (1080p)", "ETV Music (1080p)", "Raj Musix Telugu (720p)"
    ],
    "General Group": [
        "DD Saptagiri (504p)"
    ],
    "Documentary Group": [
        "History TV18 (576p)", "Discovery Channel (India) (720p)", "National Geographic (India) (576p)", 
        "National Geographic Wild (India) HD (1080p)", "Sony BBC Earth HD (1080p)"
    ],
    "Comedy Group": [
        "ETV Comedy (1080p)"
    ]
}

def fetch_and_filter_m3u():
    print(f"Fetching original M3U from: {ORIGINAL_M3U_URL}")
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
                # ఒరిజినల్ సోర్స్ లోని ఛానల్ పేరును మాత్రమే విడదీస్తుంది (కామా తర్వాత ఉన్నది)
                # ఉదాహరణ: "#EXTINF:-1 ...,ETV News (1080p)" -> "ETV News (1080p)"
                channel_name = current_extinf.split(',')[-1].strip()
                
                matched_group = None
                # ఎటువంటి మార్పులు లేకుండా కచ్చితమైన పేరు మ్యాచ్ (Exact Match) ఉందో లేదో చూస్తుంది
                for group_name, channels in GROUPS_AND_CHANNELS.items():
                    if channel_name in channels:
                        matched_group = group_name
                        break
                
                # పేరు వంద శాతం మ్యాచ్ అయితేనే మీ కంప్లీట్ కస్టమ్ గ్రూప్ తో ఇన్సర్ట్ చేస్తుంది
                if matched_group:
                    # ఒరిజినల్ ఫైల్ లో ఉన్న పాత గ్రూప్ టైటిల్ ని పూర్తిగా తీసేస్తుంది
                    cleaned_extinf = re.sub(r'\s*group-title="[^"]+"', '', current_extinf)
                    # మీరు కోరుకున్న కస్టమ్ గ్రూప్ పేరును కొత్తగా యాడ్ చేస్తుంది
                    final_extinf = cleaned_extinf.replace('#EXTINF:', f'#EXTINF: group-title="{matched_group}"', 1)
                    
                    custom_playlist.append(final_extinf)
                    custom_playlist.append(line)
                    
                current_extinf = None

    # 3. కొత్త ఫైల్‌ను సేవ్ చేయడం
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(custom_playlist))
    print(f"Successfully updated! Filtered exactly matching channels.")

if __name__ == "__main__":
    fetch_and_filter_m3u()
