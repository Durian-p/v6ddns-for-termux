import os
import sys
from flask import Flask
import keyReqTest
import threading
import subprocess

app = Flask(__name__)


@app.route('/', methods=('GET',))
def hello():
    return "<h1>xjy我搞好啦，但你还没跟我晚安就睡啦</h1>"


@app.route('/update', methods=('POST',))
def update():
    return myserver.main()

def run_flask(host):
    return subprocess.call([sys.executable, sys.argv[0], host])

def main(argv):
    port = 19999
    debug = False

    if argv:
        app.run(host=argv[0], port=port, debug=debug)
    else:
        hosts = [
            "::",
            "0.0.0.0",
        ]

        threads = list()
        for host in hosts:
            threads.append(threading.Thread(target=run_flask, args=(host,)))

        for idx, thread in enumerate(threads):
            print("Starting on {0:s}:{1:d}".format(hosts[idx], port))
            thread.start()



if __name__ == "__main__":
    print("Python {0:s} {1:d}bit on {2:s}\n".format(" ".join(item.strip() for item in sys.version.split("\n")), 64 if sys.maxsize > 0x100000000 else 32, sys.platform))
    main(sys.argv[1:])
    print("\nDone.")
