import subprocess
import time
import os

def load_env_key():
    key = os.environ.get("POSTMAN_API_KEY")
    if key:
        return key
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                if line.startswith("POSTMAN_API_KEY="):
                    return line.strip().split("=", 1)[1]
    raise ValueError("POSTMAN_API_KEY not found in environment or .env file.")

db_path = os.path.abspath(r'complete-project\tooltown.db')
if os.path.exists(db_path):
    os.remove(db_path)
    print('Reset database tooltown.db')

# Start server
server = subprocess.Popen(['node', 'server.js'], cwd='complete-project')
time.sleep(2)

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
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print(res.stderr)
finally:
    server.terminate()
