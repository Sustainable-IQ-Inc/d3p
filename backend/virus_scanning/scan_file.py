import requests
import time

url = 'https://virus-scanner-c53ivjhyqa-uc.a.run.app/scan'
file_path = 'PATH_TO_FILE'

with open(file_path, 'rb') as file:
    print("sending file")
    start_time = time.time()
    response = requests.post(url, files={'file': file})
    end_time = time.time()

print("Time taken: ", end_time - start_time, "seconds")
print(response.text)