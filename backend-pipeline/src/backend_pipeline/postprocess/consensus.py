
import json
import logging

logger = logging.getLogger(__name__)

def consensus(ocr_outputs: list) -> str:
    """
    Merge OCR outputs from multiple views.
    ocr_outputs is a list of dicts: {"result": api_response, "offset_x": int, "offset_y": int}
    """
    if not ocr_outputs:
        return ""
        
    # 1. Parse all outputs
    parsed_views = []
    logger.info(f"Consensus received {len(ocr_outputs)} views")
    for i, item in enumerate(ocr_outputs):
        api_res = item["result"]
        off_x = item["offset_x"]
        off_y = item["offset_y"]
        
        try:
            content = api_res["choices"][0]["message"]["content"]
            logger.info(f"View {i} content length: {len(content)}")
            try:
                start = content.find('[')
                end = content.rfind(']')
                if start != -1 and end != -1:
                    json_str = content[start:end+1]
                    lines = json.loads(json_str)
                    for line in lines:
                        if "box" in line:
                            b = line["box"]
                            line["box"] = [b[0]+off_x, b[1]+off_y, b[2]+off_x, b[3]+off_y]
                    parsed_views.append({"lines": lines, "raw": content, "idx": i})
                else:
                    parsed_views.append({"lines": [], "raw": content, "idx": i})
            except:
                parsed_views.append({"lines": [], "raw": content, "idx": i})
        except Exception as e:
            logger.error(f"Failed to parse view {i} result: {e}")
            continue

    # 2. Logic: If we have structured lines with boxes, merge them.
    # Otherwise return the raw text of the full view (index 0).
    
    # Check if full view (index 0) has structured lines
    # We need to find the parsed view that corresponds to original view (idx=0)
    view_0 = next((v for v in parsed_views if v["idx"] == 0), None)
    
    if view_0 and view_0["lines"]:
        merged_lines = view_0["lines"]
        # (Simple merge logic - just return view 0 lines for now)
        return json.dumps(merged_lines)
    
    # Fallback: Return concatenated raw text from all views
    # This ensures we capture text that might be present in one view but missing in others (like Bangla text in View 2)
    if parsed_views:
        all_raw = "\n".join([v["raw"] for v in parsed_views])
        logger.info(f"Consensus returning concatenated raw text (len={len(all_raw)})")
        return all_raw
        
    return ""
