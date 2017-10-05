"""
Pre-process a syllabus (class schedule) file. 

"""
import arrow   # Dates and times
import logging
logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)

base = arrow.now()   # Default, replaced if file has 'begin: ...'
visittime = arrow.now()

def process(raw):
    """
    Line by line processing of syllabus file.  Each line that needs
    processing is preceded by 'head: ' for some string 'head'.  Lines
    may be continued if they don't contain ':'.  If # is the first
    non-blank character on a line, it is a comment ad skipped. 
    """
    field = None
    entry = {}
    cooked = []
    for line in raw:
        log.debug("Line: {}".format(line))
        line = line.strip()
        if len(line) == 0 or line[0] == "#":
            log.debug("Skipping")
            continue
        parts = line.split(':')
        if len(parts) == 1 and field:
            entry[field] = entry[field] + line + " "
            continue
        if len(parts) == 2:
            field = parts[0]
            content = parts[1]
        else:
            raise ValueError("Trouble with line: '{}'\n".format(line) +
                             "Split into |{}|".format("|".join(parts)))

        if field == "begin":
            try:
                base = arrow.get(content, "MM/DD/YYYY")
                #print("Base date {}".format(base.isoformat()))
            except:
                raise ValueError("Unable to parse date {}".format(content))

        elif field == "week":
            if entry:
                cooked.append(entry)
                entry = {}
            entry['topic'] = ""
            entry['project'] = ""
            entry['week'] = "Week" + content
            #entry['week'] = content + " " + base.format('MMMM DD, YYYY')          #in case want in week column
            weeknum = int(content.split()[0]) - 1      #extract integer from content
            startofweek = base.shift(weeks=weeknum)    #init start of respective week
            endofweek = base.shift(weeks=weeknum + 1)  #init end of respective week
            if (visittime < endofweek) and (visittime > startofweek):           #if visittime is between week dates, set val to 1
                entry['curweek'] = 1
            else:
                entry['curweek'] = 0
            entry['date'] = base.shift(weeks=weeknum)
        elif field == 'topic' or field == 'project':
            entry[field] = content

        else:
            raise ValueError("Syntax error in line: {}".format(line))

    if entry:
        cooked.append(entry)

    return cooked

def main():
    f = open("data/schedule.txt")
    parsed = process(f)
    print(parsed)


if __name__ == "__main__":
    main()
