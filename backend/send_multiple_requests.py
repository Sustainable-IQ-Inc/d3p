import requests
import json

url = "http://0.0.0.0:5000/webhook"
headers = {
  'Content-Type': 'application/json'
}


records = ['recVCGXoj0EB6gmxs',
            'reczJHX6IPSZb64Nb',
            'rec1GY6oOMLudb5bk',
            'reckwmGAVX8zhU8fP',
            'recKt0pw7qM0zUoHV',
            'recSZ4VEtH8EkZuUP',
            'recj60IZXLtUN7UvX',
            'recFNZmstJVGsdWl3',
            'recGmvv5H1UZty1Ti',
            'recBvI5rUXtB7mh41',
            'rec6zIvrrTA6BkEVl',
            'recaUiFr6qvdYkII1',
            'recVcjMqsRIS0J5CS',
            'recOUjlcho5aFZrpK',
            'recPnsjpzwDKFAqsb',
            'recNhDUlPdsEaqjIt',
            'recykJaEux0e9yUGz',
            'recEoA04hW03AbPXA',
            'rec6Ez09lY1OtNSQ7',
            'rec3brWdVAXUbFkKs',
            'recMah50e95VVOvDq',
            'rec2xQcxJEWgxW0CJ',
            'recndN3Qo928Hjz2Y',
            'rec5TYsWYqALRdEnk',
            'rec3R3YF3wxaA8he7',
            'rechKyf61ZbK1yhZL',
            'recTOa8aTLbffK2J0',
            'recxDhWYFmwM4HcMw',
            'recYAYwjXP8rN2ffP',
            'reckolGXPYafjvy5V']

for uuid in records:
    payload = json.dumps({
      "uuid": uuid,
      "uploadType": "SINGLE_UPLOAD",
      "send_email": False,
      "check_duplicates": False
    })

    response = requests.post(url, headers=headers, data=payload)
    
    # Print the response for each request
    print(response.text)