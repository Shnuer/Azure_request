import requests
import json
import time
import random
import string

import aiohttp  

import asyncio
sem = asyncio.Semaphore(20)

list_with_created_user = []
host_for_create_user = 'https://graph.windows.net/questinterntest.onmicrosoft.com/users?api-version=1.6'

#Host for working client
host_for_work_with_clients = 'https://graph.windows.net/questinterntest.onmicrosoft.com/users?api-version=1.6'

host = 'https://login.microsoftonline.com/common/oauth2/token'

#Dict with admin value

with open('auth_data.json', 'r') as dict_with_auth_params_json:
    dict_with_auth_params = json.loads(dict_with_auth_params_json.read())


def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def randomUser():
    
    dict_with_users = {
    #// All of these properties are required to create consumer users.

    "accountEnabled": True,
    "displayName": randomString(10) + randomString(10),                #// a value that can be used for displaying to the end user
    "mailNickname": randomString(10),                       # // an email alias for the user
    "passwordProfile": {
        "password": '2F'+randomString(10)+'D',
        "forceChangePasswordNextLogin": False  # // always set to false
        },
    "userPrincipalName":randomString(10)+'@questinterntest.onmicrosoft.com'
    }
    
    list_with_created_user.append(dict_with_users)
    
    return dict_with_users

# Make async request for create user
async def make_request_for_create(session):
    async with sem:
        response = await session.post(host_for_create_user, headers = header, json = randomUser())
        print(response.status)
        

async def run_create(counter):
    async with aiohttp.ClientSession() as session: 
        await asyncio.gather(*[make_request_for_create(session) for i in range(counter)])

async def make_request_for_delete(user, session):
    async with sem:
        response = await session.delete('https://graph.windows.net/questinterntest.onmicrosoft.com/users/' + user["userPrincipalName"] + '?api-version=1.6',headers = header)
        print(response.status)
        
        
async def run_delete():
    async with aiohttp.ClientSession() as session: 
        await asyncio.gather(*[make_request_for_delete(user, session) for user in list_with_created_user])

#Requests for token
answer = requests.post(host, data=dict_with_auth_params)


# Text2Dict
answer_to_dict = json.loads(answer.text)
    
#Get token and bearer for authorization
token = answer_to_dict['access_token']
bearer = answer_to_dict['token_type']

Authorization = bearer + ' ' + token
Authorization = Authorization.rstrip()

header = {
    'Authorization': Authorization,
    'Content-Type': 'application/json'
}

#Getting 'users' info
get_me = requests.get(host_for_work_with_clients, headers=header)
print(get_me.status_code)
print('Im get token')

users = json.loads(get_me.text)

# Headers for working with user
header = {
    'Authorization': Authorization,
    'Content-Type': 'application/json'
}

asyncio.get_event_loop().run_until_complete(run_create(2000))
print('I created users')

asyncio.run(run_delete())
print('I deleted users')
