import json

transcript_path = "/Users/bhawna/.gemini/antigravity-ide/brain/294c6b8f-f89c-454b-8b53-401aca3b9f69/.system_generated/logs/transcript_full.jsonl"

app_content = None
card_content = None
found_massive_prompt = False

with open(transcript_path, 'r') as f:
    for line in f:
        data = json.loads(line)
        
        # Check if this is the massive user prompt
        if data.get('type') == 'USER_INPUT' and 'Here\'s a polished, ready-to-paste prompt' in data.get('content', ''):
            found_massive_prompt = True
            break
            
        # Track file contents if they appear in tool calls or responses
        # Specifically, we know replace_file_content and write_to_file have 'ReplacementContent' or 'CodeContent'
        # But we also have view_file responses.
        # Let's just track the last view_file response or the file state.
        # Wait, the easiest way is to look at replace_file_content tool calls for App.jsx and RecommendationCard.jsx BEFORE the massive prompt.
        # Actually, let's just grab the last full file content from view_file responses.
        if data.get('type') == 'TOOL_RESPONSE' and data.get('tool_name') == 'view_file':
            output = data.get('content', '')
            if 'frontend/src/App.jsx' in output and 'The above content shows the entire, complete file contents' in output:
                app_content = output
            if 'frontend/src/components/RecommendationCard.jsx' in output and 'The above content shows the entire, complete file contents' in output:
                card_content = output
                
        # Also, check replace_file_content tool responses because they show diffs, but we need the FULL file. 
        # I did run a view_file on both App.jsx and RecommendationCard.jsx right when the massive prompt started.
        # Wait, right at the start of handling the massive prompt, I ran view_file on App.jsx. Let's capture that!
        
        # If I can't find it, I'll just manually revert.
        
with open('restore_log.txt', 'w') as f:
    f.write(f"Found massive prompt: {found_massive_prompt}\n")
    f.write(f"App.jsx captured: {bool(app_content)}\n")
    f.write(f"Card captured: {bool(card_content)}\n")
