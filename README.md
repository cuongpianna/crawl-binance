
### Install requirements (windows)
  Open command line and go inside the project. 
  
  Example: cd: D:\news_spider
  
  Create virtualenv for project:
  
      virtualenv venv
      
  Active venv:
  
    venv\Script\active
    
  Install dependencies:
  
    pip install -r requirements.txt

### Run the project
  Go to scrapy project. Enter command:
  
    cd demo

  Run project:

  scrapy crawl SPIDER_NAME -o CSV_NAME.csv -t csv



### Note:
  You can see the spider names in: demo/demo/spiders/filename.py
  
  example:
   
    scrapy crawl CatholicAndEthnicNewspaper -o CatholicAndEthnicNewspaper.csv -t csv
