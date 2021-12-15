'''Script to monitor main.py progress. Invoke with:
    watch python get_stats.py
'''
import glob
print(len(glob.glob("processed/*/main_text.txt")), "documents")
