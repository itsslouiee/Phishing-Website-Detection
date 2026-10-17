import os
import math
from bs4 import BeautifulSoup
from collections import Counter
from urllib.parse import urlparse, parse_qs,urljoin
import pandas as pd
import tldextract
import logging
import re
import ipaddress
from . import Additional_Common_Methods as acm
import csv
import pickle
from Levenshtein import distance 
from thefuzz import fuzz
from pathlib import Path
BASE_DIR = Path(__file__).parent
#file_path_su = r"Feature Extraction\shortUrls.txt" 
#file_path_fhs = r"Feature Extraction\free_hosting_services.txt" 
file_path_su = BASE_DIR / "shortUrls.txt"
file_path_fhs = BASE_DIR / "free_hosting_services.txt"


#function to read brand names file
def read_brand_names_from_csv (file_path, column_index):
    brand_names = []
    with open(file_path, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile)       
        for row in reader:           
                brand_name = row[column_index]                
                brand_names.append(brand_name)             
    return brand_names

# %%
#calling the fucntion to append csv file data of brands to a list 

brand_names_file = BASE_DIR / "sample_brands_new.csv"
brand_names_column = 0  
brand_names = read_brand_names_from_csv(brand_names_file, brand_names_column)

#function to extract domain

import tldextract
def extract_domain(url):
       domain = urlparse(url).netloc    
       if domain.startswith("www."):
              domain = domain[4:]
       return domain

#creating a function to return domain without the top level domains..

def domain_without_tld(dom):
    extracted=tldextract.extract(dom) 
    return extracted.domain  

# %%
#creating a function to return only the top level domain of a particular domain
def tld(dom):
    extracted=tldextract.extract(dom)
    return extracted.suffix

# %%
#function to return the subdomain..if present.
def subdomain(dom):
    extracted=tldextract.extract(dom)
    if extracted.subdomain !='':
            return extracted.subdomain
    else:
            return ''

# %%
#function to return the path and hostname of a URL
def extract_path(url):
    parsed_url = urlparse(url)
    path = parsed_url.path     
    netloc=parsed_url.netloc     
    return (path,netloc)

# %%
#function to create sublists of URLs which contain a primary domain..eg google.com, co.in, play.google,googleapis,facebook,facebooklive..
def create_sublists(brand_list):
    sublists = {}
    for entry in brand_list:        
        if len(domain_without_tld(entry))>=6: 
             
            brand_found = False
            for brand_name in sublists:               
                if brand_name in entry:                
                    sublists[brand_name].append(entry)
                    brand_found = True
                    break             
            if not brand_found:
                brand_name = domain_without_tld(entry)
                sublists[brand_name] = [entry]

    return sublists

sublists = create_sublists(brand_names)

#checks if a brand name is seperated by a - or _. example face-book.com. can b used for domain as well as subdomain.Also able to
# check if seperator is present with typo like http://face-b00k.com      
def seperator(without_seperator,threshold=90):
    d=0
    for brand,sublist in sublists.items():
        #print(" without sep:"+ without_seperator+ "to check with" + brand)
        pr=(fuzz.partial_ratio(brand,without_seperator.lower())+fuzz.ratio(brand,without_seperator.lower()))/2
        if without_seperator==brand or pr>=threshold : #or added
             d=1
    if d==1:
         return 1
    else:
         return 0   

# 1.function to check if  brand name is present in the path or query without any seperator i.e - or _ or %
def is_brand_in_path_query(url): 
    brand_in_path_query=0
    domain=domain_without_tld(extract_domain(url))
    if extract_path(url)[0]!='/' and extract_path(url)[0]!='' or urlparse(url).query!='':                                                                          
            #print(urlparse(url).query)
            for brand_name, sublist in sublists.items():
                special_symbol=['-','_','%']
                if brand_name in (extract_path(url)[0]).lower():
                    brand_in_path_query=1
                    #print("In path"+brand_name)
                    for special in special_symbol:                
                        if special+brand_name in (extract_path(url)[0]).lower() or brand_name+special in (extract_path(url)[0]).lower() or (brand_name==domain and brand_name in (extract_path(url)[0]).lower()) :
                            brand_in_path_query=0
                            
                else:
                    if brand_name in (urlparse(url).query).lower():
                        brand_in_path_query=1   
                        #print("In query"+brand_name)
            if brand_in_path_query==1:
                return 1  
    return 0

#2.function to check if brand name or missplet brand name is present in the subdomain of the suspicious URL (also handles if present as a substring)
                 #example- facebook.abc.com or thisismyfakebook.abc.com
 

def brand_in_subdomain(domain,threshold=90):
    brand_in_subdomain=0
    if subdomain(domain)!='':        
        if '.' in subdomain(domain) or '_' in subdomain(domain) or '-' in subdomain(domain):
            #print("dot in subdomain")
            without_seperator=subdomain(domain).replace('-', '').replace('_', '').replace('.','')  
            if seperator(without_seperator)==1:      #func call to check for prsence of - or _ in brand as subdomain eg-face-book.login.com   
                #print("seperator in subdomain with or without squatting")
                return 1
            subdomain_tokens= re.split(r'[._-]', subdomain(domain))
            #print(subdomain_tokens)
            for subdomain_token in subdomain_tokens:
                for brand,sublist in sublists.items():                                                 
                    if len(brand)>=6 and len(subdomain_token)>=6: 
                        #print(" suspicious subdomain"+subdomain_token.lower()+ "2 b matched with "+brand )                       
                        pr=(fuzz.partial_ratio(brand,subdomain_token.lower())+fuzz.ratio(brand,subdomain_token.lower()))/2
                        #print(pr) 
                        if abs(len(brand)-len(subdomain_token)) <=2:  #use levenstein distance for terms with diff in length <=2
                            if distance(brand,subdomain_token)==0:
                                #print("subdomain same as a brand")
                                brand_in_subdomain=1
                                break                    
                           # elif 0 < distance(brand,subdomain_token)<=2 or 100> pr>=threshold:
                            elif 0 < distance(brand,subdomain_token)<=2 or 100> pr>=threshold: 
                                #print("misspelt brand in subdomain returned true")
                                brand_in_subdomain=1
                                break
                        else:                                 
                                            
                            if fuzz.partial_ratio(brand,subdomain_token.lower())==100 and len(subdomain_token)>=len(brand):
                                #print(brand  +"brand in or as substring in subdomain")        
                                brand_in_subdomain=1
                                break
                            else:
                                if 100>pr>=threshold : #or added
                                    #print(" subdomain is a missplet brand"+brand)            
                                    brand_in_subdomain=1 
                                    break
                if brand_in_subdomain==1:
                   break                
        else:
               
                for brand,sublist in sublists.items():           
                    #print(" suspicious subdomain"+subdomain(domain).lower()+ "2 b matched with "+brand ) 
                    if len(brand)>=6 and len(subdomain(domain))>=6: 
                        pr=(fuzz.partial_ratio(brand,subdomain(domain).lower())+fuzz.ratio(brand,subdomain(domain).lower()))/2
                        #print(pr) 
                        if abs(len(brand)-len(subdomain(domain))) <=2:  #use levenstein distance for terms with diff in length <=2
                            if distance(brand,subdomain(domain))==0:
                                #print("subdomain same as a brand")
                                brand_in_subdomain=1
                                break                    
                            elif 0 < distance(brand,subdomain(domain))<=2 or pr>=threshold: #or added
                                #print("misspelt brand in subdomain returned true")
                                brand_in_subdomain=1
                                break
                        else:                                 
                                            
                            if fuzz.partial_ratio(brand,subdomain(domain).lower())==100:
                                #print(brand  +"brand in or as substring in subdomain")        
                                brand_in_subdomain=1
                                break
                            else:
                                if 100>pr>=threshold: #or added
                                    #print(" subdomain is a missplet brand"+brand)            
                                    brand_in_subdomain=1 
                                    break                           
    if brand_in_subdomain==1:
        return 1
    else:
        return 0                   



# %%
#3.function to check if a domain has a brand as substring example- dffdamazondsf.com
def brand_as_substring_in_domain(domain): 
    brand_as_substring=0 
    brand_found=0   
    for brand,sublist in sublists.items(): 
        if brand_found==1:
            break
        if len(brand)>=6 and len(domain_without_tld(domain))>=6 and len(domain_without_tld(domain))>len(brand):                     
            #print(domain_without_tld(domain).lower()+"2 b matched for brand as substring in domain  :"+ brand)
            pr=fuzz.partial_ratio(brand,domain_without_tld(domain).lower())       
            if pr==100:             #means if brand is either same or a substring in domain
                if brand!=domain_without_tld(domain).lower() :  #means the brand is not same as the domain..hence substring
                    brand_as_substring=1
                    brand_found=1
                    #print(domain_without_tld(domain) +" has a substring of "+brand)
                    #print(sublist)
                    for entry in sublists[brand]:  #to check if the brand as substring is genuine or not..eg-facebooklive.com
                        
                        if domain_without_tld(domain)== domain_without_tld(entry):
                            #print("domain match with sublist entry..so genuine")
                            brand_as_substring=0                             
                            break                        
                    #if domain is same as the brand                    
                else:
                    break     
                 
    if brand_as_substring==1:
        return 1
    else:
        return 0    

#function to check if a domain is same as brand   
def domain_as_brand(domain):
    d=0
    for brand,sublist in sublists.items():
         
         if domain_without_tld(domain)==brand: 
              
              d=1
              break
    if d==1:
         return 1
    else:
         return 0
     
          

# %%
#4.function to check if a domain has typosquatting of a brand..eg-anazom.com or shopanazom.com((also handles if present as a substring). Also 

def brand_typo_in_domain(domain,brand_names,threshold=90):
    brand_typo=0    
    if domain_as_brand(domain) ==1:
       return 0  # if the domain is same as that of a brand without any typo 
    else:         
        if '_' in domain or '-' in domain: # checks for presence of seperators like - or _ in domain like http://asu-kuronekoyzmuto-jp.icu
            #print("seperator in domain")           
            without_seperator=domain_without_tld(domain).replace('-', '').replace('_', '')  
            if seperator(without_seperator)==1:      #func call to check for prsence of - or _ in brand as domain eg-face-book.com   
                #print("seperator in domain with or without squatting")
                return 1
            domain_tokens= re.split(r'[_-]', domain_without_tld(domain)) 
            for token in domain_tokens :
                for brand,sublist in sublists.items():                         
                        if len(brand)>=6 and len(token)>=6:
                            #print("suspicious token:"+token+"2 b matchd with:"+ brand)
                            pr=(fuzz.partial_ratio(brand,token.lower())+fuzz.ratio(brand,token.lower()))/2
                            #print(pr)
                            if abs(len(brand)-len(token)) <=2:  #use levenstein distance for terms with diff in length <=2
                                if len(brand)>=7 or len(token)>=7:
                                    if  distance(brand,token)==0:
                                        break
                                    elif 0 < distance(brand,token)<=2 or pr>=threshold :  #or added
                                        
                                        brand_typo=1
                                        break
                            else:                                                         
                                
                                #print(any(char.isupper() for char in domain_without_tld(domain)))
                                if fuzz.partial_ratio(brand,domain_without_tld(domain).lower())==100 and any(char.isupper() for char in domain_without_tld(domain))==False:
                                    
                                    break
                                if fuzz.partial_ratio(brand,domain_without_tld(domain).lower())==100 and brand == domain_without_tld(domain).lower() and any(char.isupper() for char in domain_without_tld(domain))==True:                        
                                    brand_typo=1     #domain is same as a brand but with some capital letters
                                    break
                                if 100>pr>=threshold : #or added  # means brand is not preset as a substring or as a whole in the domain but is similar
                                    #print("partial ratio of domain >threshold")            
                                   
                                    brand_typo= 1
                                    break
        else:  # this code works for those domain which dont have any seperator present
             for brand,sublist in sublists.items(): 
                        #print("suspicious domain:"+domain_without_tld(domain)+"2 b matchd with:"+ brand)
                        if len(brand)>=6 and len(domain_without_tld(domain))>=6:
                            pr=(fuzz.partial_ratio(brand,domain_without_tld(domain).lower())+fuzz.ratio(brand,domain_without_tld(domain).lower()))/2
                            
                            if abs(len(brand)-len(domain_without_tld(domain))) <=2:  #use levenstein distance for terms with diff in length <=2
                                if len(brand)>=7 or len(domain_without_tld(domain))>=7:
                                    if  distance(brand,domain_without_tld(domain))==0:
                                        break
                                    elif 0 < distance(brand,domain_without_tld(domain))<=2 or pr>=threshold: # or added
                                        
                                        brand_typo=1
                                        break
                            else:                                                                                 
                                
                                if fuzz.partial_ratio(brand,domain_without_tld(domain).lower())==100 and any(char.isupper() for char in domain_without_tld(domain))==False:
                                   
                                    break
                                if fuzz.partial_ratio(brand,domain_without_tld(domain).lower())==100 and brand == domain_without_tld(domain).lower() and any(char.isupper() for char in domain_without_tld(domain))==True:                        
                                    brand_typo=1     #domain is same as a brand but with some capital letters
                                    break
                                if 100>pr>=threshold: #or added   # means brand is not preset as a substring or as a whole in the domain but is similar
                                    
                                    brand_typo= 1
                                    break       
        if brand_typo==1:
            return 1
        else:           
            return 0    


#result= brand_typo_in_domain("ibtimes.co.uk",brand_names)
#print(result) 

# %%
#5.function to check if a URL has same domain as a brand but with a fake TLD
def brand_with_fake_tld(domain): 
    #print("in func for fake tld")
    #print("suspicious :"+domain) 
    fake_tld=0     
    for brand,sublist in sublists.items():                                          
        if brand in domain_without_tld(domain).lower():   #checks if the domain matches with the sublist head..eg-google         
            #print("matched with brand.now check the sublist")
            for entry in sublists[brand]:                  #now check the sublist for the matched brand eg-googledrive,topgoogle,facebooklive
                #print("sublist entry is:"+entry)
                if domain_without_tld(domain).lower()==domain_without_tld(entry):   #if domain matches with an entry in the sublist
                    fake_tld=1
                    if tld(domain)==tld(entry):                             #but not with the top level domain 
                         fake_tld=0
                         break
            break
            
    if fake_tld==1:
        return 1
    else:               
        return 0       




#function to return url_length feature as 1 if its more than avg length of phishing urls                
def calculate_url(url, mean_phishing_length): 
    return 1 if len(url) >= mean_phishing_length else 0


#function to return domain feature as 1 if its more than avg length of phishing urls                
def calculate_domain(domain, mean_domain_length):
    return 1 if len(domain) >= mean_domain_length else 0

# Define risky extensions and known shortened URL domains
risky_extensions = [
    ".exe", ".msi", ".bat", ".cmd", ".vbs", ".ps1", ".jar", ".scr",
    ".app", ".dmg", ".pkg", ".sh", ".run", ".bin", ".py", ".air", ".apk", ".elf",
    ".zip", ".rar", ".7z"
]

def is_shortened_url(url):
    SHORTENED_DOMAINS = acm.read_file_to_array(file_path_su)
    domain = urlparse(url).netloc.lower()
    return int(domain in SHORTENED_DOMAINS)

def is_free_hosting(url):
    free_domains = acm.read_file_to_array(file_path_fhs)
    domain = urlparse(url).netloc.lower()
    return int(any(domain.endswith(free) for free in free_domains))

def url_contains_ip(url):
    try:
        hostname = get_hostname(url)
        if hostname is None:
            return 0
        
        # Standard IPv4
        ipv4_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
        # Hexadecimal IPv4 (e.g., 0xC0.0xA8.0x01.0x01)
        hex_ipv4_pattern = re.compile(r'^(0x[0-9a-fA-F]{1,2}\.){3}0x[0-9a-fA-F]{1,2}$')
        # Integer IP (e.g., 3232235777 → 192.168.1.1)
        int_ip_pattern = re.compile(r'^\d{8,10}$')  # matches long decimal number IPs
        # Standard IPv6
        ipv6_pattern = re.compile(r'^([a-fA-F0-9:]+)$')
        if (ipv4_pattern.match(hostname) or
            hex_ipv4_pattern.match(hostname) or
            int_ip_pattern.match(hostname) or
            ipv6_pattern.match(hostname)):
            return 1  # phishing
        else:
            return 0  # legitimate
    except:
        return 0  # fail-safe return
    
def special_character_count(url):
    special_characters_list = ['@',',','$','%20','&','=','%','?','_','-',';']
    return sum(url.count(c) for c in special_characters_list )

def has_asterisk(url):
    if url.count("*")>0:
        return 1
    return 0

def has_or(url):
    if url.count("|")>0:
        return 1
    return 0

def http_token_count(url):
    if url.count("http://") + url.count("https://") >1 :
        return 1
    return 0 

def calculate_entropy(url):
    if not url:
        return 0.0
    
    char_counts = Counter(url)
    total_chars = len(url)

    entropy = -sum((count / total_chars) * math.log2(count / total_chars) 
                   for count in char_counts.values())
    
    return entropy

def has_redirections(url):
    positions = [m.start() for m in re.finditer('//', url)]
    if len(positions) > 1 and positions[-1] > 6:
        return 1  # phishing-like redirection
    else:
        return 0  # legitimate
    
def has_punycode(hostname):
    if 'xn--' in hostname:
        return 1
    return 0 

def count_www_in_url(url):
    return sum('www' in word for word in re.split(r'\W+', url))

def count_com_in_url(url):
    return sum('com' in word for word in re.split(r'\W+', url))

def has_downloadable_extension(url):
    url = url.lower()
    for ext in risky_extensions:
        if ext in url:
            return 1  # phishing
    return 0  # legitimate

from urllib.parse import urlparse

def has_port(url):
    parsed = urlparse(url)
    return 1 if parsed.port else 0

import re

# Tokenizer: splits URL into meaningful word-like components
def tokenize_url(url):
    return re.split(r'\W+', url)

# Total number of words in URL
def length_word_raw(words_raw):
    return len(words_raw)

# Average word length in URL
def average_word_length(words_raw):
    if len(words_raw) == 0:
        return 0
    return sum(len(word) for word in words_raw) / len(words_raw)

# Longest word length in URL
def longest_word_length(words_raw):
    if len(words_raw) == 0:
        return 0
    return max(len(word) for word in words_raw)

# Shortest word length in URL
def shortest_word_length(words_raw):
    if len(words_raw) == 0:
        return 0
    return min(len(word) for word in words_raw)

def contains_executable_link(html, url):
    soup = BeautifulSoup(html, 'html.parser')
    all_tags = soup.find_all(['a', 'link', 'script', 'img', 'iframe', 'form'])

    for tag in all_tags:
        url_attr = tag.get('href') or tag.get('src') or tag.get('action')
        if not url_attr:
            continue
        full_url = urljoin(url, url_attr.strip())
        path = urlparse(full_url).path
        ext = os.path.splitext(path)[1].lower()
        if ext in risky_extensions:
            return 1  # phishing (downloadable file detected)

    return 0  # no risky file links


def detect_suspicious_js(html):
    patterns = [
        r"eval\s*\(",
        r"atob\s*\(",
        r"(\+.*?){3,}",
        r"addEventListener\s*\(\s*['\"]keydown['\"]",
        r"window\.location",
        r"setTimeout\s*\(",
        r"setInterval\s*\("
    ]
    return int(any(re.search(p, html) for p in patterns))

def is_favicon_mismatch(soup, base_url):
        base_domain = urlparse(base_url).netloc.lower()
        favicon_links = soup.find_all("link", rel=lambda r: r and "icon" in r.lower())
        for link in favicon_links:
            href = link.get("href", "")
            full_url = urljoin(base_url, href)
            if urlparse(full_url).netloc.lower() != base_domain:
                return 1
        return 0

def get_hostname(url):
    extracted = tldextract.extract(url)
    # Combine all non-empty parts to reconstruct the hostname
    hostname = ".".join(part for part in [extracted.subdomain, extracted.domain, extracted.suffix] if part)
    return hostname.lower()

#function to detect gibbereish in domain of length>=10
model_data = pickle.load(open(BASE_DIR / 'gib_model.pki', 'rb'))
def normalize(line):
    """ Return only the subset of chars from accepted_chars.
    This helps keep the  model relatively small by ignoring punctuation, 
    infrequenty symbols, etc. """

    accepted_chars = 'abcdefghijklmnopqrstuvwxyz '
    return [c.lower() for c in line if c.lower() in accepted_chars]

def ngram(n, l):
    """ Return all n grams from l after normalizing """
    filtered = normalize(l)
    for start in range(0, len(filtered) - n + 1):
        yield ''.join(filtered[start:start + n])

def avg_transition_prob(l, log_prob_mat):
    """ Return the average transition prob from l through log_prob_mat. """
    accepted_chars = 'abcdefghijklmnopqrstuvwxyz '
    pos = dict([(char, idx) for idx, char in enumerate(accepted_chars)])

    log_prob = 0.0
    transition_ct = 0
    for a, b in ngram(2, l):
        log_prob += log_prob_mat[pos[a]][pos[b]]
        transition_ct += 1
    # The exponentiation translates from log probs to probs.
    return math.exp(log_prob / (transition_ct or 1))

def detect_noisy_domains(inpUrl):
    model_mat = model_data['mat']
    threshold = model_data['thresh']

    domain = domain_without_tld(inpUrl)
    
    subdom=subdomain(inpUrl)
    noiseFlagdomain = 0
    noiseFlagsubdomain=0
    if (len(domain) >= 10):
        #validFlag = avg_transition_prob(domainName, model_mat) > threshold
        noiseFlagdomain = avg_transition_prob(domain, model_mat) <= threshold
    if (len(subdom) >= 10):
            #validFlag = avg_transition_prob(domainName, model_mat) > threshold
            noiseFlagsubdomain = avg_transition_prob(subdom, model_mat) <= threshold
            #validFlag = avg_transition_prob(domainName, model_mat) > threshold
            
    if noiseFlagdomain ==1 or noiseFlagsubdomain==1:  # 1 for noise domains else 0 
        return 1
    else:
        return 0  

def extract_features(serial_number, url, label, html,mean_phishing_length,mean_domain_length):
    parsed = urlparse(url)
    hostname = get_hostname(url)
    #General Features
    features = {
        "serial_number": serial_number,
        "url": url,
        "label": label
    }
    #URL Features
    
    features["brand_subdomain"] =brand_in_subdomain(extract_domain(url))  
    features["brand_substring_domain"] = brand_as_substring_in_domain(extract_domain(url)) 
    features["brand_typo_dom"] = brand_typo_in_domain(extract_domain(url),brand_names) 
    features["fake_tld"] = brand_with_fake_tld(extract_domain(url)) 
    features["brand_in_path_query"]=is_brand_in_path_query(url)
    features["dots_path"]=extract_path(url)[0].count('.')
    features["url_more_than_mean"]=calculate_url(url, mean_phishing_length)
    features["domain_more_than_mean"] = calculate_domain(extract_domain(url),mean_domain_length)
    features["gibberish"]=detect_noisy_domains(extract_domain(url))
    features["domain_length"]=len(extract_domain(url))
    features["url_length"] = len(url)
    features["url_contains_ip"] = url_contains_ip(url)
    features["presence_of_url_shortener"] = is_shortened_url(url)
    features["special_characters_count"] = special_character_count(url)
    features["no_of_at"] = url.count('@')
    features["no_of_comma"] = url.count(',')
    features["no_of_dollar"] = url.count('$')
    features["no_of_semicolon"] = url.count(';')
    features["no_of_space"] = url.count(' ')+ url.count('@')
    features["no_of_ampersand"] = url.count('&')
    features["no_of_dots"] = url.count('.')
    features["no_of_equal"] = url.count('=')
    features["no_of_percent"] = url.count('%')
    features["no_of_underscore"] = url.count('_')
    features["no_of_hyphen"] = url.count('-')
    features["no_of_questionmark"] = url.count('?')
    features["no_of_colon"] = url.count(':')
    features["no_of_slashes_inpath"] = parsed.path.count('/')
    features["has_asterisk"] = has_asterisk(url)
    features["has_or"] = has_or(url)
    features["has_embedded_url"] = http_token_count(url)
    features["uses_https"] = int(parsed.scheme == "https")  
    features["num_query_params"] =  len(parse_qs(parsed.query))
    features["numeric_proportion"] = sum(c.isdigit() for c in url) / len(url) if len(url) else 0
    features["url_entropy"] = calculate_entropy(url)
    if hostname:
        digit_count = len(re.sub(r"[^0-9]", "", hostname))
        total_length = len(hostname)
        features['hostname_digit_ratio'] = digit_count / total_length
    else:
        features['hostname_digit_ratio'] = 0

    features['has_redirections'] = has_redirections(url)
    features['has_punycode'] = has_punycode(hostname)
    features['count_www'] = count_www_in_url(url)
    features['count_com'] = count_com_in_url(url)
    features['url_has_high_risk_extension'] = has_downloadable_extension(url)
    features['has_explicit_port'] = has_port(url)
    words_raw = tokenize_url(url)
    features['total_words_url'] = length_word_raw(words_raw)
    features['average_length_of_words'] = average_word_length(words_raw)
    features['longest_word_length'] = longest_word_length(words_raw)
    features['shortest_word_length'] = shortest_word_length(words_raw)
    features['presence_of_free_hosting'] = is_free_hosting(url)
    #HTML Content Features
    soup = BeautifulSoup(html, "html.parser")
    body = soup.body

    features["no_of_forms"] = len(soup.find_all("form"))
    features["no_of_Images"] = len(soup.find_all("img"))

    href_links = soup.find_all(href=True)
    src_links = soup.find_all(src=True)
    form_links = soup.find_all('form')

    empty_patterns = {"", "null", "javascript:void(0)"}
    self_pattern = "#"
   
    parsed_base = urlparse(url)
    base_domain = parsed_base.netloc

    internal_count = 0
    external_count = 0
    empty_count = 0
    self_count = 0
    shortened_count = 0
    # Consider all href and src attributes
    tags = href_links + src_links

    for tag in tags:
        link = tag.get('href') or tag.get('src') or ''
        link_clean = link.strip().lower()

        if link_clean == self_pattern:
            self_count += 1
            continue
        elif link_clean in empty_patterns:
            empty_count += 1
            continue
        
        full_url = urljoin(url, link_clean)
        parsed = urlparse(full_url)
        netloc = parsed.netloc.lower()
        
        if is_shortened_url(full_url):
            shortened_count += 1

        if netloc == base_domain:
            internal_count += 1
        else:
            external_count += 1
    
    # Process <form action="">
    for form in form_links:
        action = form.get('action', '').strip().lower()
        if action == self_pattern:
            self_count += 1
            continue
        elif action in empty_patterns or action == "":
            empty_count += 1
            continue

        full_url = urljoin(url, action)
        parsed = urlparse(full_url)
        netloc = parsed.netloc.lower()

        if is_shortened_url(full_url):
            shortened_count += 1

        if netloc == base_domain:
            internal_count += 1
        else:
            external_count += 1

    total_links = internal_count+external_count+empty_count+self_count
    features['no_of_hyperlinks'] = total_links
    features['no_of_external_links'] = external_count
    features['no_of_internal_links'] = internal_count
    features['no_of_null_links'] = empty_count + self_count
    features["no_of_selfreference_links"] = self_count
    features["no_of_empty_links"] = empty_count
    features["EmptyToExternalLinksRatio"] = (
        features["no_of_empty_links"] / features["no_of_external_links"]
        if features["no_of_external_links"] else 0
    )
    #To check if any links in html has downloadable executable file or malware
    features['Risky_extensions_In_Html'] = contains_executable_link(html,url)
    features['presence_of_shorten_url_html'] = int(shortened_count > 0)
    
    hidden_flag = 0
    for tag in soup.find_all(style=True):
        style = tag["style"].lower()
        if "display:none" in style or "visibility:hidden" in style:
            hidden_flag = 1

    for tag in soup.find_all(class_=True):
        if any(cls.lower() in ['hidden', 'hide', 'invisible'] for cls in tag.get("class", [])):
            hidden_flag = 1

    features["hidden_elements_html"] = hidden_flag

    features["Script_loaded_from_ext_domain"] = int(any(
        urlparse(script.get("src", "")).netloc not in hostname
        for script in soup.find_all("script") if script.get("src")
    ))

    features["suspicious_inline_js"] = detect_suspicious_js(html)
    
    #Branding mismatch features
    parts = hostname.split(".")

    if len(parts) >= 2:
        domain_core = parts[-2]
    else:
        domain_core = parts[0] if parts else ""
    # 1. Footer mismatch
    footer = soup.find("footer")
    footer_text = footer.get_text(strip=True).lower() if footer else ""
    is_footer_mismatch = 1 if footer_text and domain_core not in footer_text else 0

    # 2. Header mismatch
    header = soup.find("header")
    header_text = header.get_text(strip=True).lower() if header else ""
    is_header_mismatch = 1 if header_text and domain_core not in header_text else 0

    # 3. Copyright mismatch using Unicode regex
    symbols = r'(\u00A9|\u2122|\u00AE)'  # ©, ™, ®
    content_text = soup.get_text(" ", strip=True)
    matches = list(re.finditer(symbols, content_text))
    copyright_mismatch = 1
    if matches:
        for m in matches:
            start = max(0, m.start() - 50)
            end = m.end() + 50
            window = content_text[start:end].lower()
            if domain_core in window:
                # Domain is mentioned near copyright
                copyright_mismatch = 0
                break

    # 4. Social media link mismatch
    social_domains = ["facebook.com", "twitter.com", "linkedin.com", "instagram.com"]
    social_links = [tag.get("href", "") for tag in soup.find_all("a", href=True)]
    found_social = any(any(sd in link for sd in social_domains) for link in social_links)
    mismatched_social = 0
    if found_social:
        matching_links = [link for link in social_links if domain_core in link]
        if len(matching_links) == 0:
            mismatched_social = 1

    features["is_footer_mismatch"] = is_footer_mismatch
    features["is_header_mismatch"] = is_header_mismatch
    features["is_copyright_mismatch"] = copyright_mismatch
    features["is_socials_mismatch"] = mismatched_social

    

    features["is_favicon_mismatch"] = is_favicon_mismatch(soup, url)

    # Get the title safely and normalize
    title_tag = soup.title.string.strip().lower() if soup.title and soup.title.string else ""

    # Feature 1: Missing or generic title
    generic_titles = {"index", "home", "page", ""}
    features["has_missing_title"] = int(title_tag in generic_titles)

    # Feature 2: Title mismatch with domain core
    features["title_mismatch_with_domain"] = int(domain_core.lower() not in title_tag)

    features["has_inline_event_handlers"] = int(any(
        tag.get("onclick") or tag.get("onmouseover") for tag in soup.find_all(["a", "button"])
    ))

    features["form_action_external"] = int(any(
        urlparse(urljoin(url, form.get("action", ""))).netloc.lower() != hostname
        for form in soup.find_all("form") if form.get("action")
    ))

    return features

def main(URLdict, dataset_path):
    data = []

    # Step 1: Extract phishing URLs and compute mean length
    phishing_urls = [url for (_, url, label) in URLdict['data'] if label == 1]
    mean_phishing_length = sum(len(url) for url in phishing_urls) / len(phishing_urls) if phishing_urls else 0
    print(mean_phishing_length)
    mean_domain_length= sum(len(extract_domain(url)) for url in phishing_urls) / len(phishing_urls) if phishing_urls else 0
    print(mean_domain_length)

    for serial, url, label in URLdict['data']:
        try:
            html_file_path = os.path.join(dataset_path, f"{serial}.txt")
            print(html_file_path)
            with open(html_file_path, "r", encoding="utf-8") as f:
                html = f.read()
            feat = extract_features(serial, url, label, html,mean_phishing_length,mean_domain_length)
            data.append(feat)
            print(f"Processed: {serial}")
        except Exception as e:
            logging.error(f"Skipped {serial} due to error: {e}")
            print(f"Skipped {serial} due to error: {e}")
    df = pd.DataFrame(data)
    df.fillna(0, inplace=True)
    df.to_excel("All_Features_threshold90.xlsx", index=False)
    print("Extraction completed. Saved to excel file")

