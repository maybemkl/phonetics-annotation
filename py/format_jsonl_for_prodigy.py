import json
import os

ROOT = 'input'
GEMINI_DATA = ROOT + '/gemini_outputs'
PRODIGY_DATA = ROOT + '/prodigy'

for file in os.listdir(GEMINI_DATA):
  if file != '.DS_Store':
    print(file)
    PATH_IN = GEMINI_DATA + '/' + file
    PATH_OUT = PRODIGY_DATA + '/' + file
    with open(PATH_IN) as fin, open(PATH_OUT, "w") as fout:
      for line in fin:
          row = json.loads(line)
          fout.write(json.dumps({
              "text": row["utterance"],
              "meta": {
                  "speaker": row.get("speaker"),
                  "speaker_in_char_list": row.get("speaker_in_char_list"),
                  "addressee": row.get("addressee"),
                  "addressee_in_char_list": row.get("addressee_in_char_list"),
              }
          }) + "\n")
