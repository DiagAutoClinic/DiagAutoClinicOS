import json
import re

def merge_vag_rules():
    file_path = "src/vin/rules/dacos_vin_rules_v0.0.4.json"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all "VAG": { ... } blocks
    # We rely on indentation to find the matching closing brace
    # The blocks are at top level of "oem_profiles" (implied) or similar structure?
    # Actually dacos_vin_rules_v0.0.4.json structure is:
    # { ..., "architecture_layers": ..., "oem_profiles": { "VAG": { ... }, ... } }
    # Wait, let's check the top level structure again.
    
    # Based on previous Reads:
    # line 83: "VAG": { ... }
    # line 1106: "VAG": { ... }
    
    # We can try to regex find them.
    # Pattern: "VAG":\s*\{(?:[^{}]|(?R))*\}  (recursive regex not supported in re)
    
    # Simple approach: Find "VAG": { and count braces
    
    indices = [m.start() for m in re.finditer(r'"VAG":\s*\{', content)]
    print(f"Found {len(indices)} VAG blocks at {indices}")
    
    if len(indices) != 2:
        print("Error: Expected exactly 2 VAG blocks")
        return

    # Extract first block
    start1 = indices[0]
    end1 = find_matching_brace(content, start1 + content[start1:].find('{'))
    block1_text = content[start1:end1+1]
    
    # Extract second block
    start2 = indices[1]
    end2 = find_matching_brace(content, start2 + content[start2:].find('{'))
    block2_text = content[start2:end2+1]
    
    print(f"Block 1 length: {len(block1_text)}")
    print(f"Block 2 length: {len(block2_text)}")
    
    # Parse them
    # We need to wrap them in {} to make them valid JSON objects for json.loads
    obj1 = json.loads("{" + block1_text + "}")["VAG"]
    obj2 = json.loads("{" + block2_text + "}")["VAG"]
    
    # Merge obj2 into obj1
    # obj1 has wmi, plants
    # obj2 has markets, vds_strategies, vds_rules
    
    obj1.update(obj2)
    
    # Convert merged object back to JSON string with indentation
    merged_text = json.dumps({"VAG": obj1}, indent=4)
    # Remove the outer braces to get just "VAG": { ... }
    merged_text = merged_text[1:-1].strip() # removes { and }
    
    # Now replace
    # We replace the first block with merged text
    # We remove the second block (and potentially the preceding comma)
    
    new_content = content[:start1] + merged_text + content[end1+1:]
    
    # Now find the second block in the NEW content (indices shifted)
    # Actually, easier to replace second block first? No, replace first then remove second.
    # But second block position changed.
    
    # Re-find second block in new_content
    # It should be the first "VAG" block that matches the original second block signature?
    # No, we just replaced the first one. The second one is still there, further down.
    
    # Let's just re-run find on new_content
    indices_new = [m.start() for m in re.finditer(r'"VAG":\s*\{', new_content)]
    # The first one is our merged one. The second one is the old duplicate.
    
    if len(indices_new) < 2:
        print("Could not find second block after merge? Something is wrong.")
        # Maybe the merge text matches the regex? Yes it should.
    
    start2_new = indices_new[1]
    end2_new = find_matching_brace(new_content, start2_new + new_content[start2_new:].find('{'))
    
    # Remove the second block
    # We also need to remove the preceding comma if it exists, or trailing comma
    # Look at context around start2_new
    
    # Check for preceding comma
    pre_slice = new_content[:start2_new].rstrip()
    if pre_slice.endswith(','):
        # Remove comma
        cut_start = pre_slice.rfind(',')
        cut_end = end2_new + 1
        final_content = new_content[:cut_start] + new_content[cut_end:]
    else:
        # Check for trailing comma
        # This is safer to do manually or verify
        final_content = new_content[:start2_new] + new_content[end2_new+1:]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print("Successfully merged VAG blocks")

def find_matching_brace(text, start_index):
    count = 0
    for i in range(start_index, len(text)):
        if text[i] == '{':
            count += 1
        elif text[i] == '}':
            count -= 1
            if count == 0:
                return i
    return -1

if __name__ == "__main__":
    merge_vag_rules()
