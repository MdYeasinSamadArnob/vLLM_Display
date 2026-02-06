
BN_TO_EN = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
EN_TO_BN = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")

def bn_to_en(text: str) -> str:
    if not text: return ""
    return text.translate(BN_TO_EN)

def en_to_bn(text: str) -> str:
    if not text: return ""
    return text.translate(EN_TO_BN)
