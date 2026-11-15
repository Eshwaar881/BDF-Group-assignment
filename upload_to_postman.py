import urllib.request
import json
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

API_KEY = load_env_key()
HEADERS = {
    "X-Api-Key": API_KEY,
    "Content-Type": "application/json"
}

def get_workspaces():
    req = urllib.request.Request("https://api.getpostman.com/workspaces", headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def upload_collection(workspace_id=None):
    collection_path = os.path.abspath(r"task6-postman-and-readme\postman\ToolTown.postman_collection.json")
    with open(collection_path, "r", encoding="utf-8") as f:
        col_data = json.load(f)
    
    payload = json.dumps({"collection": col_data}).encode("utf-8")
    url = "https://api.getpostman.com/collections"
    if workspace_id:
        url += f"?workspace={workspace_id}"
    
    req = urllib.request.Request(url, data=payload, headers=HEADERS, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def create_environment(workspace_id=None):
    env_data = {
        "name": "ToolTown Local",
        "values": [
            {
                "key": "baseUrl",
                "value": "http://localhost:3000",
                "type": "default",
                "enabled": True
            }
        ]
    }
    payload = json.dumps({"environment": env_data}).encode("utf-8")
    url = "https://api.getpostman.com/environments"
    if workspace_id:
        url += f"?workspace={workspace_id}"
    
    req = urllib.request.Request(url, data=payload, headers=HEADERS, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

if __name__ == "__main__":
    print("Fetching user workspaces...")
    ws = get_workspaces()
    print("Workspaces found:", len(ws.get("workspaces", [])))
    workspace_id = None
    for w in ws.get("workspaces", []):
        print(f" - [{w.get('type')}] {w.get('name')} (id: {w.get('id')})")
        if not workspace_id:
            workspace_id = w.get("id")
    
    print(f"\nUploading collection to workspace: {workspace_id}...")
    col_res = upload_collection(workspace_id)
    print("Collection uploaded successfully!")
    col_id = col_res.get("collection", {}).get("id")
    col_uid = col_res.get("collection", {}).get("uid")
    print(f"Collection ID: {col_id}")
    print(f"Collection UID: {col_uid}")

    print("\nCreating 'ToolTown Local' environment...")
    env_res = create_environment(workspace_id)
    env_id = env_res.get("environment", {}).get("id")
    env_uid = env_res.get("environment", {}).get("uid")
    print(f"Environment created! ID: {env_id}, UID: {env_uid}")
