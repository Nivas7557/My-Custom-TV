# =========================================================================
# ⚙️ MULTI-SOURCE IPTV FILTERING SCRIPT (TESTING ENVIRONMENT)
# 📝 సూచన: ఈ కోడ్ 'testing_folder' లోపల ఉన్న ఫైల్స్ ఆధారంగా రన్ అవుతుంది.
# =========================================================================

import requests
import re
import os

# 1. లోకల్ ఫైల్స్ మరియు అవుట్‌పుట్ ప్లేలిస్ట్ పేర్లు
FILTER_TXT_FILE = "strict_channels_filter.txt"
SOURCES_TXT_FILE = "source_links.txt"
OUTPUT_FILE = "Multi_Source_Playlist.m3u"

def load_source_urls():
    """source_links.txt నుండి అన్ని IPTV సోర్స్ లింకులను రీడ్ చేసే ఫంక్షన్"""
    if not os.path.exists(SOURCES_TXT_FILE):
        print(f"Error: Missing '{SOURCES_TXT_FILE}'")
        return []
    urls = []
    with open(SOURCES_TXT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # హ్యాష్ గుర్తు ఉన్న లైన్లను, ఖాళీ లైన్లను వదిలేస్తుంది
            if line and not line.startswith("#") and line.startswith("SOURCE_M3U_URL="):
                urls.append(line.split("SOURCE_M3U_URL=")[-1].strip())
    return urls

def load_channels_from_txt():
    """channels_filter.txt నుండి గ్రూపులను, ఛానల్స్ లిస్ట్‌ను లోడ్ చేసే ఫంక్షన్"""
    if not os.path.exists(FILTER_TXT_FILE):
        print(f"Error: Missing '{FILTER_TXT_FILE}'")
        return None
    groups_and_channels = {}
    current_group = None
    with open(FILTER_TXT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # గ్రూప్ పేరును గుర్తించడం [Group Name]
            if line.startswith("[") and line.endswith("]"):
                current_group = line[1:-1].strip()
                groups_and_channels[current_group] = []
            elif current_group is not None:
                groups_and_channels[current_group].append(line)
    return groups_and_channels

def fetch_and_filter_m3u():
    """మెయిన్ ప్రాసెస్: అన్ని లింక్స్ డౌన్‌లోడ్ చేసి, ఫిల్టర్ చేసి, డూప్లికేట్స్ తీసేస్తుంది"""
    source_urls = load_source_urls()
    groups_and_channels = load_channels_from_txt()
    if not source_urls or not groups_and_channels:
        return

    custom_playlist = ["#EXTM3U"]
    saved_channels = set()  # 🚫 డూప్లికేట్స్ రాకుండా ఆపే గార్డ్ (Uniqueness Tracking)
    
    # ప్రతి లింక్ లోపలికి వెళ్లి డేటా తెస్తుంది
    for url in source_urls:
        print(f"Fetching data from: {url}")
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
        except Exception as e:
            print(f"Skipping link due to error: {e}")
            continue

        lines = response.text.splitlines()
        current_extinf = None
        for line in lines:
            if line.startswith("#EXTM3U"):
                continue
            if line.startswith("#EXTINF:"):
                current_extinf = line
            elif line.strip() and not line.startswith("#"):
                if current_extinf:
                    channel_name = current_extinf.split(',')[-1].strip()
                    
                    # డూప్లికేట్ ఉంటే ఇక్కడే స్కిప్ చేస్తుంది (No Duplications)
                    if channel_name in saved_channels:
                        current_extinf = None
                        continue
                    
                    matched_group = None
                    channel_number = None
                    # ఆటో-నంబరింగ్ మరియు గ్రూప్ అలొకేషన్ లాజిక్
                    for group_index, (group_name, channels) in enumerate(groups_and_channels.items(), start=1):
                        if channel_name in channels:
                            matched_group = group_name
                            channel_number = (group_index * 100) + (channels.index(channel_name) + 1)
                            break
                    
                    # కొత్త మెటాడేటాతో లైన్ బిల్డ్ చేయడం
                    if matched_group and channel_number:
                        cleaned_extinf = re.sub(r'\s*group-title="[^"]+"', '', current_extinf)
                        final_extinf = cleaned_extinf.replace('#EXTINF:', f'#EXTINF: group-title="{matched_group}" tvg-chno="{channel_number}"', 1)
                        custom_playlist.append(final_extinf)
                        custom_playlist.append(line)
                        saved_channels.add(channel_name) # సెట్ లో సేవ్ చేస్తుంది
                    current_extinf = None

    # ఫైనల్ ఫైల్ ని టెస్టింగ్ ఫోల్డర్ లోనే సేవ్ చేయడం
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(custom_playlist))
    print(f"Successfully generated unique playlist inside folder as '{OUTPUT_FILE}'")

if __name__ == "__main__":
    fetch_and_filter_m3u()
