import requests
import re
import os

# ఫైల్ పాత్స్ కాన్ఫిగరేషన్
FILTER_TXT_FILE = os.path.join("..", "channels_filter.txt")
SOURCES_TXT_FILE = os.path.join("..", "source_links.txt")
OUTPUT_FILE = os.path.join("..", "my_custom_playlist.m3u")

def load_source_urls():
    """source_links.txt ఫైల్ నుండి అన్ని URLలను ఒక లిస్ట్‌గా లోడ్ చేసే ఫంక్షన్"""
    if not os.path.exists(SOURCES_TXT_FILE):
        print(f"Error: మెయిన్ ఫోلడర్ లో '{SOURCES_TXT_FILE}' ఫైల్ దొరకలేదు!")
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
    """channels_filter.txt ఫైల్ లోంచి గ్రూపులను, ఛానల్స్ లిస్ట్‌ను లోడ్ చేసే ఫంక్షన్"""
    if not os.path.exists(FILTER_TXT_FILE):
        print(f"Error: మెయిన్ ఫోల్డర్ లో '{FILTER_TXT_FILE}' ఫైల్ దొరకలేదు!")
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
    # 1. ఫైల్స్ లోడ్ చేయడం
    source_urls = load_source_urls()
    groups_and_channels = load_channels_from_txt()
    
    if not source_urls:
        print("Error: 'source_links.txt' లో ఎలాంటి URL లింకులు దొరకలేదు!")
        return
    if not groups_and_channels:
        return

    print(f"Found {len(source_urls)} source links to process.")
    print(f"Loaded {len(groups_and_channels)} groups from filter text file.")
    
    custom_playlist = ["#EXTM3U"]
    
    # డూప్లికేట్స్ రాకుండా ట్రాక్ చేయడానికి ఒక 'Set' ని వాడుతున్నాం.
    # ఇందులో రికార్డ్ అయిన ఛానల్ మళ్లీ ప్లేలిస్ట్ లోకి యాడ్ అవ్వదు.
    saved_channels = set()
    
    # 2. ప్రతి URL నుండి డేటాను సేకరించడం (Looping through all URLs)
    for url in source_urls:
        print(f"\nFetching data from: {url}")
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
        except Exception as e:
            print(f"Skipping link due to error: {e}")
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
                    
                    # డూప్లికేట్ చెక్: ఈ ఛానల్ ఆల్రెడీ యాడ్ అయి ఉంటే స్కిప్ చేసేస్తుంది
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
                        
                        # ఛానల్ ని సెట్ లో సేవ్ చేసుకుంటున్నాం (ట్రాకింగ్ కోసం)
                        saved_channels.add(channel_name)
                        channels_found_in_this_link += 1
                        
                    current_extinf = None
                    
        print(f"Found and added {channels_found_in_this_link} unique channels from this source.")

    # 3. ఫైనల్ ఫైల్ సేవ్ చేయడం
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(custom_playlist))
    print(f"\n[DONE] Processing complete! Final unique playlist saved at: '{OUTPUT_FILE}'")

if __name__ == "__main__":
    fetch_and_filter_m3u()
