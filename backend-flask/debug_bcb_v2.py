
import requests
import json

def test_debug():
    # TR Check
    print("CHECKING TR (226)...")
    try:
        r = requests.get("https://api.bcb.gov.br/dados/serie/bcdata.sgs.226/dados?formato=json", timeout=10)
        print(f"Status: {r.status_code}")
        print(f"Content-Type: {r.headers.get('Content-Type')}")
        if r.status_code == 200:
            try:
                data = r.json()
                print(f"Success! Count: {len(data)}")
                if len(data) > 0: print(f"Last: {data[-1]}")
            except:
                print(f"JSON Decode Error. Preview: {r.text[:200]}")
        else:
            print(r.text[:200])
    except Exception as e:
        print(f"Error: {e}")

    # Focus Check
    print("\nCHECKING FOCUS OLINDA...")
    base = "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/ExpectativasMercadoAnuais"
    param = {
        "$filter": "Indicador eq 'Selic'",
        "$top": 5,
        "$orderby": "Data desc",
        "$format": "json"
    }
    try:
        r = requests.get(base, params=param, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            try:
                data = r.json()
                vals = data.get('value', [])
                print(f"Success! Count: {len(vals)}")
                if len(vals) > 0: print(f"First: {vals[0]}")
                else: print("Empty value list returned")
            except:
                print(f"JSON Decode Error. Preview: {r.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_debug()
