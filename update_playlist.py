import requests
import re

# 1. CORRECTED SOURCE LINK: ఒరిజినల్ సోర్స్ లింక్ ఇక్కడ అప్‌డేట్ చేయబడింది
ORIGINAL_M3U_URL = "https://iptv-org.github.io/iptv/index.m3u"
OUTPUT_FILE = "my_custom_playlist.m3u"

# 2. ఫైనల్ ఛానల్స్ మరియు గ్రూపుల కాన్ఫిగరేషన్
GROUPS_AND_CHANNELS = {
    "Sports Channels": [
        "Star Sports 1 (720p)", "Star Sports 2 (720p)", "Star Sports 1 Hindi (720p)", "Star Sports First (576i)",
        "Sony Sports Ten 1 HD (1080p)", "Sony Sports Ten 2 HD (1080p)", "Sony Sports Ten 3 HD (1080p)", "Sony Sports Ten 5 HD (1080p)",
        "Sports18 (720p)", "Eurosport (720p)", "DD Sports (576i)", "DD Sports (1080p)", "beIN SPORTS XTRA (1080p)"
    ],
    "Entertainment Group": [
        "Star Maa HD (720p)", "Zee Telugu HD (576p)", "Sun Gemini (576p)", "ETV Telugu HD (1080p)", 
        "ETV Plus (396p)", "ETV Josh (1080p)", "Mahaa Max (1080p)", "Mango Mobile TV (1080p)", 
        "Telugu One (1080p)", "Vanitha TV (576p)", "Vissa TV (576p)", "ETV Comedy (1080p)", "DD Saptagiri (504p)"
    ],
    "Movies Group": [
        "Star Maa Movies HD (720p)", "ETV Cinema (396p)", "ETV Cinema HD (1080p)", "Tolly TV (1080p)"
    ],
    "English Movie Group": [
        "HBO (United States) (720p)", "HBO Hits (720p)", "Sony Pix HD (1080p)", 
        "Star Movies (720p)", "Movies Now (1080p)", "Cinemax (United States) West (720p)", "AMC (United States) (720p)", 
        "Action 24 (1080p)", "Studio One + (720p)"
    ],
    "Telugu Music": [
        "Gemini Music (576p)", "Sun Music (576p)", "ETV Music (1080p)", "ETV Beats (1080p)", "Raj Musix Telugu (720p)"
    ],
    "Music Group": [
        "9XM (1080p)", "B4U Music (1080p)", "Mastiii (576p)", "Zing (576p)", "Music India (576i)", 
        "VH1 (576p)", "1HD Music Television (1080p)", "4everMusic (1080p)", "7 RadioVisione (720p)"
    ],
    "News Group": [
        "TV9 Telugu (720p)", "NTV Telugu (1080p)", "ETV Andhra Pradesh (1080p)", "ETV Telangana (1080p)", 
        "ETV News (1080p)", "ABN Andhra Jyoti (720p)", "TV5 News (576p)", "V6 News (576p)", 
        "10 TV (720p)", "Sakshi TV (576p)", "HMTV (India) (720p)", "INews (720p)", 
        "Prime9 News (1080p)", "Mahaa News (1080p)", "CVR News (576p)", "Mojo TV (576p)", "Zee Telugu News (720p)"
    ],
    "Kids / Animation": [
        "Cartoon Network (India) (720p)", "Nickelodeon (India) (576p)", "Sonic (576p)", "Disney Channel (India) HD (1080p)", 
        "Disney Junior (India) (576p)", "Hungama TV (576p)", "Super Hungama (576p)", "Discovery Kids (720p)", 
        "ETV Bal Bharat (576p)", "Sony Yay! (576p)", "WOW Kidz Telugu (720p)"
    ],
    "Religious Group": [
        "Bhakthi TV (720p)", "SVBC (1080p)", "Mahaa Bhakti (1080p)", "Hindu Dharmam (1080p)", 
        "CVR OM Spiritual (576p)", "Aastha Telugu (576p)", "PMC Telugu (1080p)"
    ],
    "Documentary Group": [
        "National Geographic (India) (576p)", "National Geographic Wild (India) HD (1080p)", "Discovery Channel (India) (720p)", 
        "Sony BBC Earth HD (1080p)", "History TV18 (576p)"
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
                # Isolate the exact channel name after the comma
                channel_name = current_extinf.split(',')[-1].strip()
                
                matched_group = None
                channel_number = None
                
                # కచ్చితమైన పేరు మ్యాచ్ లాజిక్ మరియు ఆటో-నంబరింగ్ సిస్టమ్
                for group_index, (group_name, channels) in enumerate(GROUPS_AND_CHANNELS.items(), start=1):
                    if channel_name in channels:
                        matched_group = group_name
                        # 1వ గ్రూప్‌కు 101, 102... 2వ గ్రూప్‌కు 201, 202... నంబర్లు కేటాయిస్తుంది
                        channel_number = (group_index * 100) + (channels.index(channel_name) + 1)
                        break
                
                if matched_group and channel_number:
                    # పాత ఇండెక్స్ గ్రూప్ టైటిల్‌ను డిలీట్ చేస్తుంది
                    cleaned_extinf = re.sub(r'\s*group-title="[^"]+"', '', current_extinf)
                    # కస్టమ్ గ్రూప్‌తో పాటు `tvg-chno` అనే కచ్చితమైన నంబర్‌ను యాడ్ చేస్తుంది
                    final_extinf = cleaned_extinf.replace(
                        '#EXTINF:', 
                        f'#EXTINF: group-title="{matched_group}" tvg-chno="{channel_number}"', 1
                    )
                    
                    custom_playlist.append(final_extinf)
                    custom_playlist.append(line)
                    
                current_extinf = None

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(custom_playlist))
    print(f"Successfully updated custom playlist with strict numbers and corrected source URL!")

if __name__ == "__main__":
    fetch_and_filter_m3u()
