import subprocess		#for sub process like clear screen
import sys				#for exceptions handling
import requests
from bs4 import BeautifulSoup
import sys
from urllib.parse import urljoin, urlparse
from datetime import datetime

s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"

# function to get all forms
def get_forms(url):
    soup = BeautifulSoup(s.get(url).content, "html.parser")
    return soup.find_all("form")

def form_details(form):
    detailsOfForm = {}
    action = form.attrs.get("action")
    method = form.attrs.get("method", "get").lower()
    inputs = []
    
    for input_tag in form.find_all("input"):
        input_type = input_tag.attrs.get("type", "text")
        input_name = input_tag.attrs.get("name")
        input_value = input_tag.attrs.get("value", "")
        inputs.append({
            "type" : input_type,
            "name" : input_name,
            "value" : input_value
        })

    detailsOfForm['action'] = action
    detailsOfForm['method'] = method
    detailsOfForm['inputs'] = inputs
    return detailsOfForm

def vulnerable(response):
    errors = {"quoted strings not properly terminated",
              "unclosed quotation marks afters characters string",
              "you have an error in your SQL syntax"}
    for error in errors:
        if error in response.content.decode().lower():
            return True
    return False

def sql_injection_scan(url):

    # 1. Prepare Filename (Sanitize URL to be safe for OS filenames)
    domain = urlparse(url).netloc
    filename = f"{domain}_scan_results_{datetime.now()}.txt"

    forms = get_forms(url)
    print(f"[+] Detected {len(forms)} forms on {url}.")

    # Open file for writing results
    with open(filename, "w") as f:
        f.write(f"SQLi Scan Report for: {url}\n")
        f.write("="*50 + "\n")

    for form in forms:
        details = form_details(form)

        for i in "\"'":
            data = {}
            for input_tag in details["inputs"]:
                if input_tag["type"] == "hidden" or input_tag["value"]:
                    data[input_tag['name']] = input_tag["value"] + i
                elif input_tag["type"] != "submit":
                    data[input_tag['name']] =f"test{i}"
            print(url)
            form_details(form)

            if details["method"] == "post":
                res = s.post(url, data = data)
            elif details["method"] == "get":
                res = s.get(url, params=data)
            if vulnerable(res):
                result_msg = "Sql injection attack vulnerability in link : " + url
                print(result_msg)
                #print("Sql injection attack vulnerability in link : ", url)
                f.write(result_msg)
                f.write(f"Payload Data: {data}\n\n")
            else:
                result_msg = "No Sql injection attack vulnerability detected in link : " + url
                print(result_msg)
                with open(filename, "a") as f:
                    f.write(result_msg + "\n")
                break

if __name__ == "__main__":
    #clear all text from screen
    subprocess.call('clear', shell=True)
    print("="*100)							# print = 60 times on console
    print(" "*20,"SYNTECXHUB SQLi VULNERABILITES SCANNER")		# print SYNTECXHUB on console
    print("="*100)
    
    try:
        urlToBeChecked = input("Please enter website to find vulnerabiliteis e.g. 'https://www.yahoo.com' : ")
        sql_injection_scan(urlToBeChecked)
    except KeyboardInterrupt:
	    print ("You pressed Ctrl + C")
	    sys.exit()
