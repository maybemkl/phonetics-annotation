import json
import re
import spacy

nlp = spacy.blank("en")
stopwords = nlp.Defaults.stop_words

input_file = "GB_0_3.jsonl"
output_file = "patterns.jsonl"

pattern_to_keep = r"[^a-zA-Z0-9\s]"
seen = set()
kept = 0

with open(output_file, "w", encoding="utf-8") as fout, open(input_file, "r", encoding="utf-8") as fin:
    for line in fin:
        if not line.strip():
            continue
        data = json.loads(line)
        words = list(data.get("words", {}).keys())
        for w in words:
            # original lowercased and cleaned
            for variant in {w.lower(), re.sub(pattern_to_keep, "", w.lower())}:
                if (
                    variant
                    and len(variant) > 2
                    and variant not in stopwords
                    and variant not in seen
                ):
                    seen.add(variant)
                    tokens = [{"lower": t} for t in variant.split()]
                    fout.write(json.dumps({"label": "PHONETIC", "pattern": tokens}, ensure_ascii=False) + "\n")
                    kept += 1

print(f"Wrote {kept} patterns (after stopword filter) to {output_file}")
