import requests
p = r"c:\Users\HP SPECTRE\Downloads\Edureka (Final Project)\ai_agent_rag_system\data\uploads\enterprise_ai.txt"
with open(p, 'rb') as f:
    r = requests.post('http://127.0.0.1:9011/upload', files={'file': ('enterprise_ai.txt', f)})
    print(r.status_code)
    print(r.text)
