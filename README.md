
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
  You can see the spider names in: demo/demo/spiders/file_name.py
  
  example:
   
    scrapy crawl CatholicAndEthnicNewspaper -o CatholicAndEthnicNewspaper.csv -t csv
  
  With spiders using argument to crawl, you can pass argument to crawl lie:
  
    scrapy crawl CatholicAndEthnicNewspaper -o CatholicAndEthnicNewspaper.csv -t csv -a page=1000

    
  
  
  There are list name of spiders:
  
  + CatholicAndEthnicNewspaper
  + CorporateFinanceReview
  + EnterpriseForumNewspaper
  + BusinessAndBrandVietnam
  + CivilEngineeringNewspaper             (argument)
  + ConstructorMagazine
  + BuildingMaterialsMagazine
  + JournalOfConstructionPlanning
  + EconomicsAndUrbanNewspaper
  + VietnamHeritageMagazine
  + Heritage
  + GeneralDepartmentOfVietnamCustoms
  + TheSaigonTimesWeekly
  + SecurityReview
  + VietnamBanksAssociationSpider
  + VietnamChamberOfCommerceAndIndustry
  + VietnamBusinessForum
  + MekongASEANReview              (argument)
  + BiddingReview
  + EconomyAndForecastReview
  + VietnamIndustrialZoneReview


Note: I use scrapy selenium for 44th website. You need Google chrome version 86 to run it.