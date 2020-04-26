import json
import codecs
    
## Phrase contains start_time, end_time and the max 10 word text
def generate_phrases(transcript):
    ts = json.load(transcript)
    items = ts['results']['items']

    phrase =  {}
    phrases = []
    nPhrase = True
    puncDelimiter = False
    x = 0

    for item in items:
        # if it is a new phrase, then get the start_time of the first item
        if nPhrase == True:
            if item["type"] == "pronunciation":
                phrase["start_time"] = get_time_code(float(item["start_time"]))
                nPhrase = False
        else:
            # We need to determine if this pronunciation or puncuation here
            # Punctuation doesn't contain timing information, so we'll want
            # to set the end_time to whatever the last word in the phrase is.
            # Since we are reading through each word sequentially, we'll set 
            # the end_time if it is a word
            if item["type"] == "pronunciation":
                phrase["end_time"] = get_time_code(float(item["end_time"]) )
            else:
                puncDelimiter = True

        # in either case, append the word to the phrase...
        transcript_word = item['alternatives'][0]["content"]

        if ("words" not in phrase):
            phrase["words"] = [ transcript_word ]
        else:
            phrase["words"].append(transcript_word)

        x += 1

        # now add the phrase to the phrases, generate a new phrase, etc.
        if x == 10 or puncDelimiter:
            #print c, phrase
            phrases.append(phrase)
            phrase = {}
            nPhrase = True
            puncDelimiter = False
            x = 0

    return phrases

def generate_srt(transcript):
    phrases = generate_phrases(transcript)
    srt_content = generate_srt_from_phrases(phrases)
    return srt_content
    
def generate_srt_from_phrases(phrases):
    tokens = []
    c = 1

    for phrase in phrases:
        tokens.append(str(c))
        tokens.append(phrase["start_time"] + " --> " + phrase["end_time"])
        tokens.append(" ".join(phrase["words"]))
        tokens.append("\n")
        c += 1

    output = "\n".join(tokens)
    return output


def get_time_code(seconds):
# Format and return a string that contains the converted number of seconds into SRT format
    thund = int(seconds % 1 * 1000)
    tseconds = int(seconds)
    tsecs = ((float(tseconds) / 60) % 1) * 60
    tmins = int(tseconds / 60)
    return str( "%02d:%02d:%02d,%03d" % (00, tmins, int(tsecs), thund))


if __name__ == "__main__":
    phrases = generate_phrases('/Users/annsarapaul/GitHub/TTB:video_upload_backend/Sample Video/TTB_12_Hindi_Sampoorn_Kranti_NPO_Part_1__Final__1587422077475_1587424530_transcript_job.json')
    print(phrases)

