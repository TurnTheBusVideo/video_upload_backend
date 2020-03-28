import pickle

with open('token.pickle', 'rb') as token:
    delegated_credentials = pickle.load(token)

delegated_credentials.refresh()
#2020-03-06 07:05:24.627886