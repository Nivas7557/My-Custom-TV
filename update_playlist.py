import requests
import re

# 1. Source Link (12k+ world channels)
ORIGINAL_M3U_URL = "https://github.io"
OUTPUT_FILE = "my_custom_playlist.m3u"

# 2. Add your selected channel names here (Use lowercase text)
ALLOWED_CHANNELS = [
    "hbo",
    "star sports 1",
    "discovery hd",
    "etv telugu",
    "maa tv",
    "tv9 telugu",
    "maa movies",
    "gemini tv"
    # Tip: You can expand this list by adding commas (,) and names in quotes
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
                # Extract the channel name after the last comma
                channel_name = current_extinf.split(',')[-1].strip().lower()
                
                # Check if the channel matches your allowed list
                if any(allowed in channel_name for allowed in ALLOWED_CHANNELS):
                    # Check if group-title already exists
                    group_match = re.search(r'group-title="([^"]+)"', current_extinf)
                    
                    if group_match:
                        final_extinf = current_extinf
                    else:
                        # Fallback group if iptv-org has no group for it
                        final_extinf = current_extinf.replace('#EXTINF:', '#EXTINF: group-title="Custom Channels"', 1)
                    
                    custom_playlist.append(final_extinf)
                    custom_playlist.append(line)
                    
                current_extinf = None

    # 3. Save the new filtered & grouped M3U file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(custom_playlist))
    print(f"Successfully updated! Filtered and Grouped playlist created.")

if __name__ == "__main__":
    fetch_and_filter_m3u()
