import subprocess
import time
import os
import sys
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, 'complete-project')

def free_port_3000():
    try:
        out = subprocess.check_output('netstat -ano | findstr :3000', shell=True).decode()
        for line in out.strip().split('\n'):
            parts = line.split()
            if len(parts) >= 5 and 'LISTENING' in line:
                pid = parts[-1]
                subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
                print(f'Closed previous server on port 3000 (PID {pid})')
                time.sleep(1)
    except Exception:
        pass

def load_env_key():
    key = os.environ.get("POSTMAN_API_KEY")
    if key:
        return key
    env_file = os.path.join(BASE_DIR, ".env")
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                if line.startswith("POSTMAN_API_KEY="):
                    return line.strip().split("=", 1)[1]
    raise ValueError("POSTMAN_API_KEY not found in environment or .env file.")

# 1. Kill any existing process on port 3000
free_port_3000()

# 2. Reset database file
db_path = os.path.join(PROJECT_DIR, 'tooltown.db')
if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print('Reset database tooltown.db')
    except Exception as e:
        print(f'Note: Could not delete db file directly ({e}), will reset via API')

# 3. Start fresh server
print(f'Starting API server in {PROJECT_DIR}...')
server = subprocess.Popen(['node', 'server.js'], cwd=PROJECT_DIR, shell=True)
time.sleep(2)

# Make sure server is reset to initial state
try:
    req = urllib.request.Request('http://localhost:3000/reset', data=b'{}', headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(req)
    print('Verified database reset to initial seed data.')
except Exception as e:
    pass

api_key = load_env_key()
col_url = f'https://api.getpostman.com/collections/59365787-699f3d15-5ee9-49ac-931f-495340245dbb?apikey={api_key}'
env_url = f'https://api.getpostman.com/environments/59365787-ee4b5488-2b09-46e5-b247-e980773ea29b?apikey={api_key}'

cmd = [
    'npx.cmd',
    'newman',
    'run',
    col_url,
    '--environment',
    env_url
]

try:
    print('Running Postman tests via Newman against Postman Cloud...\n')
    subprocess.run(cmd, shell=True)
finally:
    server.terminate()
