
import json

def generate_prompt(schema_keys, scribe_result):
    scribe_json = json.dumps(scribe_result, ensure_ascii=False)
    verification_prompt = (
        f"You are a professional OCR Proofreader. \n"
        f"Here is the raw extraction from a Scribe: {scribe_json}\n"
        f"Task:\n"
    )
    
    # Dynamic Rules
    if "name" in schema_keys or "name_bn" in schema_keys:
        verification_prompt += f"1. Review 'name' (English) and 'name_bn' (Bangla). The Scribe uses a high-quality OCR (Hunyuan) which usually gets the characters right. Only correct if you see a clear spelling/spacing error or if the field is missing.\n"
    
    if "address_bn" in schema_keys:
        verification_prompt += f"3. Verify 'address_bn'. Trust the Scribe unless there is a major hallucination or missing text.\n"
    
    if "place_of_birth" in schema_keys:
        verification_prompt += f"4. Verify 'place_of_birth'.\n"

    if "mrz_line1" in schema_keys or "mrz_line2" in schema_keys or "mrz_line3" in schema_keys:
            verification_prompt += f"5. Extract the MRZ (Machine Readable Zone) lines at the bottom of the card into 'mrz_line1', 'mrz_line2', 'mrz_line3'. They consist of uppercase letters, numbers, and '<'. Ensure strict accuracy.\n"

    # Critical Preservation Rules
    verification_prompt += f"6. CRITICAL: Do NOT change 'dob', 'nid_no', 'issue_date', 'blood_group' unless they are visually contradictory to the image. Trust the Scribe's numbers/dates.\n"
    
    # Return Format
    verification_prompt += f"7. Return the corrected JSON object ONLY. No markdown."
    
    return verification_prompt

# Test Case
schema_keys = ["name", "name_bn", "dob", "nid_no"]
scribe_result = {
    "name": "Abdul Karim",
    "name_bn": "আব্দুল করিম",
    "dob": "1990-01-01",
    "nid_no": "1234567890"
}

print("--- Generated Judge Prompt ---")
print(generate_prompt(schema_keys, scribe_result))
