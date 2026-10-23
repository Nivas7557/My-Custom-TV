import requests
import re

# 1. ఒరిజినల్ సోర్స్ లింక్
ORIGINAL_M3U_URL = "https://github.io"
OUTPUT_FILE = "my_custom_playlist.m3u"

# 2. మీ గ్రూపులు మరియు ఖచ్చితమైన ఛానల్స్ లిస్ట్
GROUPS_AND_CHANNELS = {
    "News": [
        "10 tv", "abn andhra jyoti", "cvr news", "etv andhra pradesh", "etv news", 
        "etv telangana", "hmtv", "inews", "mahaa news", "mojo tv", "ntv telugu", 
        "prime9 news", "raj news telugu", "sakshi tv", "tv5 news", "tv9 telugu", 
        "v6 news", "zee telugu news"
    ],
    "Entertainment": [
        "etv josh", "etv plus", "etv telugu hd", "etv telugu", "mahaa max", "mango mobile tv", 
        "star maa hd", "star maa", "telugu one", "vanitha tv", "vissa tv", "zee telugu hd", 
        "zee telugu", "sun gemini", "gemini tv"
    ],
    "Movies": [
        "etv cinema", "etv cinema hd", "sony pix hd", "sony pix", "star maa movies hd", "star maa movies", "studio one", "tolly tv"
    ],
    "Animation": [
        "cartoon network india", "cartoon network", "discovery kids", "disney channel india hd", "disney channel india", "disney channel", "disney junior india", "disney junior", 
        "etv bal bharat", "hungama tv", "nickelodeon india", "nickelodeon", "sonic", "sony yay", 
        "super hungama", "wow kidz telugu"
    ],
    "Religious": [
        "aastha telugu", "bhakthi tv", "cvr om spiritual", "hindu dharmam", 
        "mahaa bhakti", "pmc telugu", "svbc"
    ],
    "Music": [
        "etv beats", "etv music", "raj musix telugu"
    ],
    "General": [
        "dd saptagiri"
    ],
    "Documentary": [
        "history tv18", "discovery channel india", "discovery channel", "national geographic india", "national geographic", "national geographic wild", "sony bbc earth hd", "sony bbc earth"
    ],
    "Comedy": [
        "etv comedy"
    ]
}

def clean_name_for_strict_match(text):
    # చిన్న అక్షరాల్లోకి మారుస్తుంది
    text = text.lower().strip()
    # (1080p), (720p), [HD] లాంటి బ్రాకెట్లను, వాటి లోపల ఉన్న టెక్స్ట్‌లను పూర్తిగా తీసేస్తుంది
    text = re.sub(r'\s*\[[^\]]*\]', '', text)
    text = re.sub(r'\s*\([^)]*\)', '', text)
    # కేవలం అక్షరాలు, నంబర్లు, మరియు ఒకే ఒక స్పేస్ ఉండేలా క్లీన్ చేస్తుంది
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

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
                # ఒరిజినల్ ఛానల్ పేరును వేరు చేస్తుంది
                channel_name = current_extinf.split(',')[-1].strip()
                
                # పేరును పక్కాగా పోల్చడానికి వీలుగా క్లీన్ చేస్తుంది
                # ఉదాహరణ: "Cartoon Network (India) (720p)" -> "cartoon network india"
                # ఉదాహరణ: "ETV News Odisha" -> "etv news odisha"
                cleaned_source_name = clean_name_for_strict_match(channel_name)
                
                matched_group = None
                for group_name, channels in GROUPS_AND_CHANNELS.items():
                    for allowed_channel in channels:
                        cleaned_allowed = clean_name_for_strict_match(allowed_channel)
                        
                        # ఇక్కడ ఖచ్చితమైన మ్యాచ్ (Exact Match) జరుగుతుంది
                        # దీనివల్ల "cartoon network" కి కేవలం అదే పేరున్నది వస్తుంది, "cartoon network pakistan" రాదు.
                        # ఒకవేళ ఒరిజినల్ పేరులో "cartoon network india" అని ఉంటే, అది కూడా మ్యాచ్ అవుతుంది.
                        if cleaned_source_name == cleaned_allowed or cleaned_source_name == cleaned_allowed + " india" or cleaned_source_name + " india" == cleaned_allowed:
                            matched_group = group_name
                            break
                    if matched_group:
                        break
                
                if matched_group:
                    # పాత గ్రూపులను తీసేసి కొత్త కస్టమ్ గ్రూపులను మాత్రమే ఉంచుతుంది
                    cleaned_extinf = re.sub(r'\s*group-title="[^"]+"', '', current_extinf)
                    final_extinf = cleaned_extinf.replace('#EXTINF:', f'#EXTINF: group-title="{matched_group}"', 1)
                    
                    custom_playlist.append(final_extinf)
                    custom_playlist.append(line)
                    
                current_extinf = None

    # 3. కొత్త కస్టమ్ ఫైల్‌ను సేవ్ చేయడం
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(custom_playlist))
    print(f"Successfully updated! Strict filter applied across all groups.")

if __name__ == "__main__":
    fetch_and_filter_m3u()
