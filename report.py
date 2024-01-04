import database
from diffhtml import *
import logging
import mutate
import json
import report_html

FLAG = "BASELINE_DIFF"
def to_file(filename, content):
    f = open(filename, 'w')
    f.write(content)
    f.close()

def process_baseline(records):
    to_file("html1.html", records[0][4].decode("utf-8"))

    for record in records:
        if records[0][4] != record[4]:
            break
    else: # if all baselines are identical
        global FLAG
        FLAG = "BASELINE_SAME"
        return records[0][4].decode("utf-8")
    
    #print(records[0][4].decode("utf-8"))
    #print(records[1][4].decode("utf-8"))
    #a = 1/0
    to_file("html2.html", records[1][4].decode("utf-8"))
    #to_file("html3.html", records[2][4].decode("utf-8"))

    parser = EDEFuzzHTMLParser()
    parser.feed(records[0][4].decode("utf-8"))
    DOM = parser.dom
    for i in range(1, len(records)):
        parser_t = EDEFuzzHTMLParser()
        parser_t.feed(records[i][4].decode("utf-8"))
        DOM_t = parser_t.dom
        DOM.mark_uncommon(DOM_t)
    
    return DOM

def compare(baseline, record):
    if isinstance(baseline, str):
        #print(record)
        return baseline == record
    parser = EDEFuzzHTMLParser()
    parser.feed(record)
    DOM = parser.dom
    return baseline == DOM


def report(target, local_opt_filter=0):
    logger = logging.getLogger("log")
    ch = logging.FileHandler("report_stat.csv")
    logger.addHandler(ch)
    
    FLAG_NO_BASELINE = False
    FLAG_BASELINE_FAIL = False
    
    db = database.Connection(target)
    baselines = db.get_baseline()
    if len(baselines) == 0:
        FLAG_NO_BASELINE = True
        baseline = "dummy_text_indicating_no_baseline"
        #raise Exception("No baseline record. Did the non-mutated API response produce an HTML?")
    else:
        try:
            baseline = process_baseline(baselines)
        except:
            FLAG_BASELINE_FAIL = True
            baseline = "dummy_text_indicating_no_baseline"
    
    executed = 0
    f = open("tests/" + target + ".json", "r")
    response = json.load(f)
    f.close()
    total = sum(1 for _ in mutate.leaf(response))
    timestamp = []

    f = open("tests/" + target + ".csv", "w")
    flagged_fields = []
    for record in db.get_result():
        executed += 1
        timestamp.append(record[5])
        if compare(baseline, record[4].decode("utf-8")):
            #print("Excessive data exposure: " + record[2].decode("utf-8"))
            f.write(record[2].decode("utf-8") + "\n")
            flagged_fields.append(record[2].decode("utf-8"))

    f.close()

    report_html.process(target)
    
    if len(timestamp) < 2:
        duration = -1
    else:
        timestamp.sort()
        duration = timestamp[-1] - timestamp[0]
        last = timestamp[0]
        for t in timestamp:
            if t - last > 600:
                duration -= t - last
            last = t
        duration = int(duration / 60)
    
    print(len(flagged_fields), "/", total, "field(s) flagged.")
    print("List of flagged fields in tests/" + target + ".csv")
    print("Flagged fields are highlighted in tests/" + target + "_flagged.html")
    
    logger.error(target + "," + str(duration+1) + "," + str(total) + "," + str(executed) + "," + str(len(flagged_fields)) + "," + ",BASELINE_FAIL" * FLAG_BASELINE_FAIL + ",FLAG_NO_BASELINE" * FLAG_NO_BASELINE)


if __name__ == "__main__":
    report("ilive")
