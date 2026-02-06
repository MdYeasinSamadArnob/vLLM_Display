
from typing import Dict, Any, List
import logging
import re
from .digits import bn_to_en

logger = logging.getLogger(__name__)

def run_schema_pipeline(schema: Dict[str, Any], ocr_text: str, image: Any) -> Dict[str, Any]:
    """
    Extract fields based on schema.
    1. Parse OCR text (if JSON) or use raw text
    2. Apply Regex/Rules
    3. Fallback to VL model (Qwen3-VL) if needed
    """
    result = {}
    
    # 1. Parse OCR Text
    # If ocr_text is JSON list of lines
    import json
    lines = []
    full_text = ocr_text
    
    try:
        data = json.loads(ocr_text)
        if isinstance(data, list):
            # Flatten to text for regex
            full_text = "\n".join([l.get("text", "") if isinstance(l, dict) else str(l) for l in data])
        elif isinstance(data, dict):
            # Direct mapping if keys match
            logger.info("Schema Engine received Dict structure")
            if "name_en" in data: result["name"] = data["name_en"]
            if "name_bn" in data: result["name_bn"] = data["name_bn"]
            if "father_name" in data: result["father_name"] = data["father_name"]
            if "mother_name" in data: result["mother_name"] = data["mother_name"]
            if "date_of_birth" in data: result["dob"] = data["date_of_birth"]
            if "nid_no" in data: result["nid_no"] = data["nid_no"]
            
            # Also set full_text for regex fallback/augment
            full_text = json.dumps(data, ensure_ascii=False)
        else:
            full_text = str(ocr_text)
    except:
        full_text = ocr_text
        
    # Normalize digits
    full_text = bn_to_en(full_text)
    logger.info(f"Schema Engine Text: {full_text}")
    
    # 2. Simple Rule-Based Extraction
    for field, description in schema.items():
        result[field] = None
        
        # NID
        if "nid" in field.lower():
             match = re.search(r'\b\d{10,17}\b', full_text)
             if match:
                 result[field] = match.group(0)
        
        # DOB
        if "dob" in field.lower() or "date of birth" in description.lower():
            # Matches: 09 Apr 1999, 15 Oct 1985, etc.
            match = re.search(r'(?:Date of Birth|DOB)[:\s]*(\d{1,2}[\s\-/]+[A-Za-z]+[\s\-/]+\d{4}|\d{2}[\s\-/]+\d{2}[\s\-/]+\d{4})', full_text, re.IGNORECASE)
            if match:
                result[field] = match.group(1)

        # Name
        if field.lower() == "name" or "name" in description.lower():
            # Specific handling for different name fields
            
            # 1. Bangla Name (name_bn)
            if "bn" in field.lower() or "bangla" in description.lower():
                 # Match নাম: ...
                 # \u09a8\u09be\u09ae = নাম
                 pattern = r'(?:\u09a8\u09be\u09ae|Name \(Bangla\))[:\s]+([^\n]+)'
                 match = re.search(pattern, full_text)
                 if match:
                     result[field] = match.group(1).strip()
                     logger.info(f"Matched {field}: {result[field]}")
                 else:
                     logger.info(f"Failed to match {field} with pattern {pattern}")
                     # Debug: find where "নাম" is in text
                     idx = full_text.find('\u09a8\u09be\u09ae')
                     if idx != -1:
                         logger.info(f"Found 'নাম' at index {idx}. Context: {full_text[idx:idx+50]}")
                     else:
                         logger.info("'নাম' not found in text")

            # 2. English Name (name)
            
            # 2. English Name (name)
            elif field.lower() == "name":
                match = re.search(r'(?<!Father\'s )(?<!Mother\'s )Name[:\s]+([^\n]+)', full_text, re.IGNORECASE)
                if match:
                    result[field] = match.group(1).strip()
            
            # 3. Father's Name
            elif "father" in field.lower():
                # Match Father's Name or পিতা
                # \u09aa\u09bf\u09a4\u09be = পিতা
                match = re.search(r'(?:Father\'?s? Name|\u09aa\u09bf\u09a4\u09be)[:\s]+([^\n]+)', full_text, re.IGNORECASE)
                if match:
                    result[field] = match.group(1).strip()
            
            # 4. Mother's Name
            elif "mother" in field.lower():
                # Match Mother's Name or মাতা
                # \u09ae\u09be\u09a4\u09be = মাতা
                match = re.search(r'(?:Mother\'?s? Name|\u09ae\u09be\u09a4\u09be)[:\s]+([^\n]+)', full_text, re.IGNORECASE)
                if match:
                    result[field] = match.group(1).strip()

        # Blood Group
        if "blood" in field.lower() or "group" in field.lower():
            match = re.search(r'(?:Blood Group|BG)[:\s]+([A-Za-z]{1,2}\s*[+-]?(?:ve)?)', full_text, re.IGNORECASE)
            if match:
                result[field] = match.group(1).strip()

        # Place of Birth
        if "place" in field.lower() and "birth" in field.lower():
             match = re.search(r'(?:Place of Birth|Birth Place)[:\s]+([^\n]+)', full_text, re.IGNORECASE)
             if match:
                 result[field] = match.group(1).strip()

        # Issue Date
        if "issue" in field.lower() and "date" in field.lower():
            match = re.search(r'(?:Issue Date|Date of Issue|প্রদানের তারিখ)[:\s]+(\d{1,2}[\s\-/]+[A-Za-z]+[\s\-/]+\d{4}|\d{2}[\s\-/]+\d{2}[\s\-/]+\d{4})', full_text, re.IGNORECASE)
            if match:
                result[field] = match.group(1).strip()
        
        # Address (Bangla/English) - often multiline
        if "address" in field.lower() or "thikana" in field.lower():
            # Match Address or ঠিকানা until a double newline or specific keywords
            match = re.search(r'(?:Address|Thikana|ঠিকানা)[:\s]+([\s\S]+?)(?:\n\s*\n|Blood Group|Place of Birth|$)', full_text, re.IGNORECASE)
            if match:
                result[field] = match.group(1).strip()

        # Generic Regex Fallback for any other field
        if result[field] is None:
            search_terms = [field]
            if description and description != field:
                search_terms.append(description)
            for term in search_terms:
                safe_term = re.escape(term)
                pattern = rf'{safe_term}[:\s]+([^\n]+)'
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    result[field] = match.group(1).strip()
                    logger.info(f"Generic Match for {field} using term '{term}': {result[field]}")
                    break

    # 3. Fallback to VL Model (Not implemented in this turn, but planned)
    # if any(v is None for v in result.values()):
    #     result = call_qwen_vl(schema, image)
        
    return result
