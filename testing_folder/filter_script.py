import requests
import re
import os

# Path configurations traversing backwards out of testing_folder into the parent directory
FILTER_TXT_FILE = os.path.join("..", "channels_filter.txt")
SOURCES_TXT_FILE = os.path.join("..", "source_links.txt")
OUTPUT_FILE = os.path.join("..", "my_custom_playlist.m3u")

def load_source_urls():
    """Reads all target M3U URLs listed inside source_links.txt."""
    if not os.path.exists(SOURCES_TXT_FILE):
        print(f"Error: Required file missing at '{SOURCES_TXT_FILE}'!")
        return []
    
    urls = []
    with open(SOURCES_TXT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and line.startswith("SOURCE_M3U_URL="):
                url = line.split("SOURCE_M3U_URL=")[-1].strip()
                urls.append(url)
    return urls

def load_channels_from_txt():
    """Parses target categories and channel strings from channels_filter.txt."""
    if not os.path.exists(FILTER_TXT_FILE):
        print(f"Error: Required file missing at '{FILTER_TXT_FILE}'!")
        return None
        
    groups_and_channels = {}
    current_group = None
    
    with open(FILTER_TXT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                current_group = line[1:-1].strip()
                groups_and_channels[current_group] = []
            elif current_group is not None:
                groups_and_channels[current_group].append(line)
                
    return groups_and_channels

def fetch_and_filter_m3u():
    source_urls = load_source_urls()
    groups_and_channels = load_channels_from_txt()
    
    if not source_urls:
        print("Error: No valid playlist source URLs detected inside source_links.txt!")
        return
    if not groups_and_channels:
        return

    print(f"Found {len(source_urls)} source links to process.")
    print(f"Loaded {len(groups_and_channels)} category groupings from tracking file.")
    
    custom_playlist = ["#EXTM3U"]
    saved_channels = set()  # Tracks added items to guarantee strict uniqueness
    
    for url in source_urls:
        print(f"\nProcessing streams from network address: {url}")
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
        except Exception as e:
            print(f"Skipping server path due to connection exception: {e}")
            continue

        lines = response.text.splitlines()
        current_extinf = None
        channels_found_in_this_link = 0
        
        for line in lines:
            if line.startswith("#EXTM3U"):
                continue
                
            if line.startswith("#EXTINF:"):
                current_extinf = line
            elif line.strip() and not line.startswith("#"):
                if current_extinf:
                    channel_name = current_extinf.split(',')[-1].strip()
                    
                    # Deduplication guardrail condition
                    if channel_name in saved_channels:
                        current_extinf = None
                        continue
                    
                    matched_group = None
                    channel_number = None
                    
                    for group_index, (group_name, channels) in enumerate(groups_and_channels.items(), start=1):
                        if channel_name in channels:
                            matched_group = group_name
                            channel_number = (group_index * 100) + (channels.index(channel_name) + 1)
                            break
                    
                    if matched_group and channel_number:
                        cleaned_extinf = re.sub(r'\s*group-title="[^"]+"', '', current_extinf)
                        final_extinf = cleaned_extinf.replace(
                            '#EXTINF:', 
                            f'#EXTINF: group-title="{matched_group}" tvg-chno="{channel_number}"', 1
                        )
                        
                        custom_playlist.append(final_extinf)
                        custom_playlist.append(line)
                        
                        saved_channels.add(channel_name)
                        channels_found_in_this_link += 1
                        
                    current_extinf = None
                    
        print(f"Successfully processed {channels_found_in_this_link} new unique channels from this path.")

    # Save finalized export to the parent directory file path
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(custom_playlist))
    print(f"\n[DONE] Finished bundling playlist. Clean file generated at: '{OUTPUT_FILE}'")

if __name__ == "__main__":
    fetch_and_filter_m3u()
