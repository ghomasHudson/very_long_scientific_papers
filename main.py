'''Scraper for long arxiv.org documents'''
from bs4 import BeautifulSoup
import requests
import xmltodict
import tarfile
import os
import shutil
import signal
import sys
import subprocess

######################################
## Functions
##

def filter_html(html):
    '''Remove math, figures, tables. Replace headings etc...'''
    soup = BeautifulSoup(html, 'html.parser')

    # Replace math
    for c in ["ltx_Math", "mjx-math"]:
        for i in soup.find_all(class_=c):
            i.replace_with('@xmath')

    # Replace figures
    for c in ["ltx_figure", "ltx_table", "ltx_markedasmath"]:
        for i in soup.find_all(class_=c):
            i.replace_with(' ')

    for i in range(1, 7):
        c = "h" + str(i)
        for el in soup.find_all(c):
            el.replace_with("\n" + ("#" * i) + " " + el.text + "\n\n")
    return soup.prettify("utf-8")


def filter_text(text):
    # Find abstract section
    for i, line in enumerate(text.split("\n")):
        abstract_words = ["abstract", "summary"]
        text_started = False
        line = line.lower()
        line = line.split()
        for aw in abstract_words:
            if len(line) > 1 and line[1] == aw:
                text_started = True
                break

        if text_started:
            break
    if text_started:
        text = "\n".join(text.split("\n")[i+2:])
    else:
        print("Can't find abstract")
        return

    abstract = text.split("\n#", 1)[0]
    text = text.split("\n#", 1)[1]

    # Find Conclusion
    for i, line in enumerate(text.split("\n")):
        conclusion_words = ["references", "bibliography"]
        text_started = False
        line = line.lower()
        line = line.split()
        for aw in conclusion_words:
            if len(line) > 1 and line[1] == aw:
                text_started = True
                break
        if text_started:
            break
    if text_started:
        text = "\n".join(text.split("\n")[:i-1])
    else:
        print("Can't find bib")
        return
    return {
        "abstract": abstract,
        "text": text
    }


def run_cmd(cmd, timeout_s=600):
    '''Runs command with timeout'''
    cmd = cmd.split(" ")
    try:
        p = subprocess.Popen(cmd, start_new_session=True)
        p.wait(timeout=timeout_s)
        return p.returncode
    except subprocess.TimeoutExpired:
        print(f'Timeout for {cmd} ({timeout_s}s) expired')
        print('Terminating the whole process group...')
        os.killpg(os.getpgid(p.pid), signal.SIGTERM)
        return 1


########################################################
## Main Code
##


# os.unlink("output/index.html")
try:
    os.unlink("/tmp/filtered.html")
    os.unlink("/tmp/filtered.txt")
except:
    pass

PAGE_SIZE = 10
for start in range(720, 30000, PAGE_SIZE):
    data = {}
    while "feed" not in data.keys() or "entry" not in data["feed"].keys():
        r = requests.get("http://export.arxiv.org/api/query?search_query=all:thesis&start=" + str(start) + "&max_results=" + str(start + PAGE_SIZE))
        data = xmltodict.parse(r.text)
    for paper in data["feed"]["entry"]:
        try:
            paper_id = paper["id"].split("/")[-1]

            output_dir = "processed/" + paper_id
            try:
                os.mkdir(output_dir)
            except:
                print("SKIPPING...")
                continue

            # Download source
            print(paper["title"])
            source_url = paper["id"].replace("/abs/", "/e-print/")
            filename = "source/" + paper["id"].split("/")[-1] + ".tar.gz"
            r = requests.get(source_url, allow_redirects=True)
            with open(filename, "wb") as f:
                f.write(r.content)
            print("Downloaded")

            # Convert to html
            print("Convert to html...")
            cmd = """docker run -v /home/thomas/Documents/scientific_papers:/workdir -w /workdir arxivvanity/engrafo engrafo """ + filename + " output/"


            # os.system(cmd)
            # proc = subprocess.run(cmd, shell = True, timeout = 600, capture_output = True, check=True)
            # proc.wait()
            if run_cmd(cmd, timeout_s=600) != 0:
                print("CMD errored - SKIPPING...")
                continue
            os.unlink(filename)


            # Filter HTML
            html = filter_html(open("output/index.html").read())
            with open("/tmp/filtered.html", 'wb') as f:
                f.write(html)




            # Convert to txt and filter
            os.system("pandoc -s /tmp/filtered.html -t plain -o /tmp/filtered.txt")
            try:
                doc = filter_text(open("/tmp/filtered.txt").read())
            except:
                doc = None
            if doc is not None:

                if len(doc["text"].split()) > 10000:
                    print("SAVING to file")
                    with open(output_dir + "/abstract.txt", 'w') as f:
                        f.write(doc["abstract"])
                    with open(output_dir + "/main_text.txt", 'w') as f:
                        f.write(doc["text"])
                else:
                    print("Too short")

            # Save intemediate files to dir
            shutil.copy("output/index.html", output_dir + "/orig.html")
            shutil.copy("/tmp/filtered.html", output_dir + "/filtered.html")
            shutil.copy("/tmp/filtered.txt", output_dir + "/filtered.txt")
        except:
            pass

