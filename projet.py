import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from bs4.element import Tag
from time import sleep
import csv
from parsel import Selector
import parameters
import numpy
import flask
import requests
from flask import request,jsonify
from pymongo import MongoClient


class api :
    app = None
    def __init__(self ):
         
        self.nbp = 1
        self.myclient = MongoClient('localhost',27017)
        self.db = self.myclient['SonicHr']
        self.collection_profiles = self.db['profiles']
        self.links = []
        self.titles = []
        self.descriptions = []
        self.driver = webdriver.Chrome()
        self.soup=None 
        self.result_div =None
    
    def home(self):

        self.links = []
        
    

    
        if 'query' in request.args:
            query = str(request.args['query'])
            print(query)
        else:
            return "Error: No id field provided. Please specify an idQuery."

        if 'nbp' in request.args:
            nbp = str(request.args['nbp'])
            print(nbp)
        else:
            return "Error: No id field provided. Please specify an idPages."
        if 'idf' in request.args:
            idf = str(request.args['idf'])
            print(idf)
        else:
            return "Error: No id field provided. Please specify an idf."
        if 'idUser' in request.args:
            idUser = str(request.args['idUser'])
            print(idUser)
        else:
            return "Error: No id field provided. Please specify an idUser."
      
        # specifies the path to the chromedriver.exe
        


        # driver.get method() will navigate to a page given by the URL address
        self.driver.get('https://www.linkedin.com')

        # locate email form by_class_name
        if 'username' in locals():
            username = self.driver.find_element_by_id('session_key')
    

            # send_keys() to simulate key strokes
            username.send_keys(parameters.linkedin_username)
            sleep(0.5)

            # locate password form by_class_name
            password = self.driver.find_element_by_id('session_password')

            # send_keys() to simulate key strokes
            password.send_keys(parameters.linkedin_password)
            sleep(0.5)

            # locate submit button by_class_name
            log_in_button = self.driver.find_element_by_class_name('sign-in-form__submit-button')

            # .click() to mimic button click
            log_in_button.click()
            sleep(0.5)


        # driver.get method() will navigate to a page given by the URL address
        self.driver.get('https://www.google.com')
        sleep(3)

        # locate search form by_name
        search_query = self.driver.find_element_by_name('q')

        # send_keys() to simulate the search text key strokes
        search_query.send_keys(query)

        # .send_keys() to simulate the return key 
        search_query.send_keys(Keys.RETURN)

        self.soup = BeautifulSoup(self.driver.page_source,'lxml')
        self.result_div = self.soup.find_all('div', attrs={'class': 'g'})

    
        
            
        # initialize empty lists
        
    
    

        # Function call x10 of function profiles_loop; you can change the number to as many pages of search as you like. 
        self.repeat_fun(self.nbp, self.profiles_loop)


        # Separates out just the First/Last Names for the titles variable
        titles01 = [i.split()[0:2] for i in self.titles]
        
        for link in self.links:
            origin=link[8:link.index('.')]
           

            body=link[link.rfind('/')+1:]

            finalLink="https://www.linkedin.com/in/"+body+"?=originalSubdomain="+origin
  
            print(finalLink)
            response = requests.get('http://127.0.0.1:5000/api?url='+finalLink)
            
            data = response.json()
            data['idFolder'] = [idf]
            data['idUser'] = [idUser]
            self.collection_profiles.insert_one(data)
            print(data) 

        return data
        
        

    # Function call extracting title and linkedin profile iteratively
    def find_profiles(self):
        for r in self.result_div:
            # Checks if each element is present, else, raise exception
            try:
                link = r.find('a', href=True)
                title = None
                title = r.find('h3')
                
                # returns True if a specified object is of a specified type; Tag in this instance 
                if isinstance(title,Tag):
                    title = title.get_text()
        
                description = None
                description = r.find('span', attrs={'class': 'st'})
        
                if isinstance(description, Tag):
                    description = description.get_text()
        
                # Check to make sure everything is present before appending
                if link != '' and title != '' and description != '':
                    self.links.append(link['href'])
                    self.titles.append(title)
                    self.descriptions.append(description)
        

                
        
            # Next loop if one element is not present
            except Exception as e:
                print(e)
                continue
            
    # This function iteratively clicks on the "Next" button at the bottom right of the search page. 
    def profiles_loop(self):
        print('before find profiles')
        self.find_profiles()
        
        next_button = self.driver.find_element_by_xpath('//*[@id="pnnext"]') 
        next_button.click()
        
        
    def repeat_fun(self,times, f):
        for i in range(times): f()



app = flask.Flask(__name__)
app.config["DEBUG"] = True   


apiinstence= api()  
@app.route('/', methods=['GET'])
def start():
    print('start')
    return apiinstence.home() 
      


start
app.run(port=5001)
