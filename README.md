# login_auth
# Overall Workflow
Initially:
User
   │
   ▼
Username
Password
   │
   ▼
login.py
   │
   ▼
users.json
   │
   ▼
Login OK

After adding MFA:

             Username
                │
                ▼
            Password
                │
                ▼
           login.py
                │
      Password correct?
                │
          Yes ──┘
                ▼
       Read mfa_secret.txt
                │
                ▼
    HMAC(secret, username)
                │
                ▼
      Generate expected code
                │
                ▼
Compare with user's MFA code
                │
        Correct? ── Yes ──► login ok
                │
                No
                ▼
          login failed
# Run a successful password-only login
usage: login.py USERNAME PASSWORD :
"python3 login.py alice wonderland"
---> login ok
BASE = Path("/home/labex/project") ----> change to ur directory "pwd" 
# mfa-check
usage : mfa-check.py [password-only|secret|generator|enforced|all] : 
python3 mfa-check.py password-only
---> password-only: complete
 
