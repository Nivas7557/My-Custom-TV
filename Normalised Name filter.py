import requests
import re

# 1. CORRECTED SOURCE LINK
ORIGINAL_M3U_URL = "https://iptv-org.github.io/iptv/index.m3u"
OUTPUT_FILE = "my_custom_playlist.m3u"

# 2. ఫైనల్ ఛానల్స్ మరియు గ్రూపుల కాన్ఫిగరేషన్
GROUPS_AND_CHANNELS = {
    "Sports Channels": [
        "Star Sports 1", "Star Sports 2", "Star Sports 1 Hindi", "Star Sports First",
        "Sony Sports Ten 1", "Sony Sports Ten 2", "Sony Sports Ten 3", "Sony Sports Ten 5",
        "Sports18", "Eurosport", "DD Sports", "beIN SPORTS XTRA"
    ],
    "Entertainment Group": [
        "Star Maa", "Zee Telugu", "Sun Gemini", "ETV Telugu", 
        "ETV Plus", "ETV Josh", "Mahaa Max", "Mango Mobile TV", 
        "Telugu One", "Vanitha TV", "Vissa TV", "ETV Comedy", "DD Saptagiri"
    ],
    "Movies Group": [
        "Star Maa Movies", "ETV Cinema", "Tolly TV"
    ],
    "English Movie Group": [
        "HBO", "HBO Hits", "Sony Pix", "Star Movies", "Movies Now", 
        "Cinemax", "AMC", "Action 24", "Studio One"
    ],
    "Telugu Music": [
        "Gemini Music", "Sun Music", "ETV Music", "ETV Beats", "Raj Musix Telugu"
    ],
    "Music Group": [
        "9XM", "B4U Music", "Mastiii", "Zing", "Music India", 
        "VH1", "1HD Music Television", "4everMusic", "7 RadioVisione"
    ],
    "News Group": [
        "TV9 Telugu", "NTV Telugu", "ETV Andhra Pradesh", "ETV Telangana", 
        "ETV News", "ABN Andhra Jyoti", "TV5 News", "V6 News", 
        "10 TV", "Sakshi TV", "HMTV", "INews", 
        "Prime9 News", "Mahaa News", "CVR News", "Mojo TV", "Zee Telugu News"
    ],
    "Kids / Animation": [
        "Cartoon Network", "Nickelodeon", "Sonic", "Disney Channel", 
        "Disney Junior", "Hungama TV", "Super Hungama", "Discovery Kids", 
        "ETV Bal Bharat", "Sony Yay", "WOW Kidz Telugu"
    ],
    "Religious Group": [
        "Bhakthi TV", "SVBC", "Mahaa Bhakti", "Hindu Dharmam", 
        "CVR OM Spiritual", "Aastha Telugu", "PMC Telugu"
    ],
    "Documentary Group": [
        "National Geographic", "National Geographic Wild", "Discovery Channel", 
        "Sony BBC Earth", "History TV18"
    ]
}

def clean_channel_name(name):
    """Normalizes names by converting to lowercase and stripping common resolution/format tags."""
    name = name.lower()
    name = re.sub(r'\(.*?\)|hd|sd|i|p|\s+', '', name) # Removes (720p), (1080p), HD, spaces, etc.
    return name

def build_lookup_maps():
    """Generates an efficient flat map for O(1) tracking and matching."""
    lookup = {}
    for group_index, (group_name, channels) in enumerate(GROUPS_AND_CHANNELS.items(), start=1):
        for ch_index, ch_name in enumerate(channels, start=1):
            normalized_key = clean_channel_name(ch_name)
            chn_num = (group_index * 100) + ch_index
            lookup[normalized_key] = (group_name, chn_num)
    return lookup

def fetch_and_filter_m3u():
    print(f"Fetching original M3U from: {ORIGINAL_M3U_URL}")
    lookup_map = build_lookup_maps()
    
    try:
        # Stream response line by line to keep RAM usage extremely minimal
        response = requests.get(ORIGINAL_M3U_URL, timeout=60, stream=True)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching playlist: {e}")
        return

    custom_playlist = ["#EXTM3U"]
    current_extinf = None
    option_lines = []

    # Iterate line by line cleanly decoding bytes
    for raw_line in response.iter_lines():
        if not raw_line:
            continue
        line = raw_line.decode('utf-8').strip()

        if line.startswith("#EXTM3U"):
            continue

        if line.startswith("#EXTINF:"):
            current_extinf = line
            option_lines = [] # Reset options buffer for the new channel block
        elif line.startswith("#EXTVLCOPT:"):
            option_lines.append(line) # Safely capture playback parameters like User-Agents
        elif not line.startswith("#"): # This is the stream URL line
            if current_extinf:
                raw_channel_name = current_extinf.split(',')[-1].strip()
                normalized_input_name = clean_channel_name(raw_channel_name)
                
                # Check for flexible substring match against our configuration map
                matched = None
                for target_key, (group_name, chn_num) in lookup_map.items():
                    if target_key in normalized_input_name or normalized_input_name in target_key:
                        matched = (group_name, chn_num)
                        break

                if matched:
                    group_name, chn_num = matched
                    # Clean out any old group titles safely
                    cleaned_extinf = re.sub(r'\s*group-title="[^"]+"', '', current_extinf)
                    
                    # Modern attribute replacement using standard regex structures
                    final_extinf = re.sub(
                        r'^#EXTINF:([-0-9]*)', 
                        f'#EXTINF:\\1 group-title="{group_name}" tvg-chno="{chn_num}"', 
                        cleaned_extinf
                    )
                    
                    custom_playlist.append(final_extinf)
                    custom_playlist.extend(option_lines) # Injects missing #EXTVLCOPT headers if present
                    custom_playlist.append(line)
                
                current_extinf = None
                option_lines = []

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(custom_playlist))
    print(f"Successfully created custom playlist: '{OUTPUT_FILE}'!")

if __name__ == "__main__":
    fetch_and_filter_m3u()
