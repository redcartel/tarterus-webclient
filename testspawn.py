import subprocess
import time

if __name__ == "__main__":
    subprocess.Popen(['python3', 'spawnmap.py', '54321', '1000', '1000'])
    stat = 'x'
    while stat != 'done':
        try:
            with open('tmp/54321.stat', 'r') as f:
                stat = f.readline()
        except Exception:
            pass
        print(stat)
        time.sleep(1)
