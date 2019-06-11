import logging
import sys
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from watchdog.events import PatternMatchingEventHandler


class FileHandler(PatternMatchingEventHandler):
    def FileParsing(self, event):
        if event.event_type == "modified":
            fileName = event.src_path
            try:
                f = open(fileName, 'r', encoding='cp949')
                beforeLine = ""
                lastLine = ""
                while True:
                    line = f.readline()
                    if len(line) == 0:
                        print('beforeLine : [', beforeLine, '] lastLien : [', lastLine, ']')
                        break;
                    beforeLine = lastLine
                    lastLine = line
            except:
                print('에러발생')
                pass
            finally:
                f.close()

    def on_modified(self, event):
        self.FileParsing(event)



if __name__ == "__main__":
    pattenrs = ["*.txt", "*.text"]
    # logging.basicConfig(level=logging.INFO,
    #                     format='%(asctime)s - %(message)s',
    #                     datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = FileHandler(pattenrs)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
