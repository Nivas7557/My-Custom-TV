import requests
import re

# Source endpoint and requested output filename
ORIGINAL_M3U_URL = "https://iptv-org.github.io/iptv/index.m3u"
OUTPUT_FILE = "Normalized Channels.m3u"

# Target channel mapping configuration
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

def normalize_text(text):
    """Converts text to lowercase and strips resolution tags and spaces for resilient matching."""
    text = text.lower()
    text = re.sub(r'\(.*?\)|hd|sd|fhd|uhd|i|p|\s+', '', text)
    return text

def create_lookup_map():
    """Generates an inverted map for lookups."""
    mapping = {}
    for g_idx, (group_name, channels) in enumerate(GROUPS_AND_CHANNELS.items(), start=1):
        for ch_idx, ch_name in enumerate(channels, start=1):
            norm_key = normalize_text(ch_name)
            channel_num = (g_idx * 100) + ch_index = ch_idx
            mapping[norm_key] = (group_name, channel_num)
    return mapping

def generate_normalized_m3u():
    print(f"Downloading stream source from: {ORIGINAL_M3U_URL}")
    lookup_table = create_lookup_map()
    
    try:
        response = requests.get(ORIGINAL_M3U_URL, timeout=60, stream=True)
        response.raise_for_status()
    except Exception as error:
        print(f"Failed to access source playlist: {error}")
        return

    m3u_output = ["#EXTM3U"]
    active_extinf = None
    vlc_options_buffer = []

    for raw_bytes in response.iter_lines():
        if not raw_bytes:
            continue
        line = raw_bytes.decode('utf-8').strip()

        if line.startswith("#EXTM3U"):
            continue

        if line.startswith("#EXTINF:"):
            active_extinf = line
            vlc_options_buffer = []
        elif line.startswith("#EXTVLCOPT:"):
            vlc_options_buffer.append(line)
        elif not line.startswith("#"): # URL stream line
            if active_extinf:
                parsed_name = active_extinf.split(',')[-1].strip()
                norm_input = normalize_text(parsed_name)
                
                matched_data = None
                for target_key, data in lookup_table.items():
                    if target_key in norm_input or norm_input in target_key:
                        matched_data = data
                        break

                if matched_data:
                    group, num = matched_data
                    clean_extinf = re.sub(r'\s*group-title="[^"]+"', '', active_extinf)
                    adjusted_extinf = re.sub(
                        r'^#EXTINF:([-0-9]*)', 
                        f'#EXTINF:\\1 group-title="{group}" tvg-chno="{num}"', 
                        clean_extinf
                    )
                    
                    m3u_output.append(adjusted_extinf)
                    m3u_output.extend(vlc_options_buffer)
                    m3u_output.append(line)
                
                active_extinf = None
                vlc_options_buffer = []

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file_out:
        file_out.write("\n".join(m3u_output))
    print(f"Process complete. File saved as '{OUTPUT_FILE}'")

if __name__ == "__main__":
    generate_normalized_m3u()
