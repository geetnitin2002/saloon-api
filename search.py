# from src.dbAccess import DataAccess
# from src.apputils import AppUtils
from dbAccess import DataAccess
from apputils import AppUtils
from booking import BookingUtils
import urllib.parse

import config
import json

class Search:

    def searchBusinessByName(self, businessName):
        print('business name is: ',businessName)
        # businesses=DataAccess().getAllBusinesses()
        businesses=DataAccess().getBusinessesByName(businessName)
        # for business in businesses:
        #     print('businesses :',business.businessName)
        #     if (business.businessName==businessName):
        #         return business
        return businesses



    def getServiceAndBusinessList(self, businessId):

        services=DataAccess().getBusinessServices(businessId,'A')
        servicesOfCategory=[]

        # "select business_id, name, num_of_subslots, if_double_time, price, currency, if_ticket_based, " \
        # "total_ticket_count, max_tickets_sold_per_booking, category_name, top_category_name, duration, description " \
        # "from business_services where business_id=%s"

        for service in services:
            priceAndDuration = 'R' + str(service.price) + ', ' + str(service.duration) + 'mins'
            servicesOfCategory.append((businessId,service.name, service.price, service.subslotsCount,service.ifTicketBasedService, priceAndDuration))
        return servicesOfCategory



    def getServicesByCategory (self, servicesOfCategory):

        businessServiceList=[]
        for serviceOfCategory in servicesOfCategory:
            serviceDict={}
            serviceDict["name"]=serviceOfCategory[1]
            serviceDict["price"]=serviceOfCategory[2]
            # serviceDict["duration"]=len(serviceOfCategory[3])*15
            # serviceDict["duration"] = len(serviceOfCategory[3]) * config.gSingleTimeslotDuration
            serviceDict["duration"] = serviceOfCategory[3]
            serviceDict["ifTicket"] = serviceOfCategory[4]
            serviceDict["description"] = serviceOfCategory[5]
            serviceDict["priceAndDuration"] = 'R'+str(serviceOfCategory[2])+', '+str(serviceOfCategory[3])+'mins'
            businessServiceList.append((serviceOfCategory[0],serviceDict))

        allServicesDict=AppUtils().convert2ElementsTupleListToDict(businessServiceList)
        print('allServicesDict')
        print(json.dumps(allServicesDict))
        sublistOfServices=AppUtils().getSublist(allServicesDict, 3)
        # print('sublistOfServices')
        # print(json.dumps(sublistOfServices))

        businessesServicesDictList=[]

        for businessId, serviceList in sublistOfServices.items():
            businessesServicesDict = {}
            print('business id and name')
            print(businessId)
            if (DataAccess().getBusinessMainFields(businessId)!=None):
                businessName=DataAccess().getBusinessMainFields(businessId).businessName
                address=BookingUtils().getBusinessAddressForDisplay( businessId, style='Continuous')
                # addressObj=DataAccess().getBusinessAddress(businessId)
                print(businessName)
                businessesServicesDict["businessId"] = businessId
                businessesServicesDict["businessName"] = businessName

                businessesServicesDict["businessNameUrlEncoded"] = urllib.parse.quote_plus(businessName)
                print('encoded val: '+urllib.parse.quote_plus(businessName))
                businessesServicesDict["services"] = serviceList
                # address=addressObj.addressLine1+' '+addressObj.addressLine2 +' ' + addressObj.cityLocation+' '+ addressObj.city+ ' '+ addressObj.province+' '+ addressObj.postalCode
                businessesServicesDict["address"] = address
                businessesServicesDictList.append(businessesServicesDict)

        return businessesServicesDictList



    def getServicesCategoriesByTopCategorries (self):

        servicesCategories=DataAccess().getServiceCategories(None)
        return servicesCategories


    def getLocations(self):
        locations=DataAccess().getLocations(None)
        locationsList=[]
        for location in locations:
            locationsList.append(location[1]+', '+location[0])

        return locationsList



    def getServiceCategoriesAndBusinesses(self):

        categoryAndTopCategoryList=DataAccess().getServiceCategories(None)
        categories=[]
        for categoryAndTopCat in categoryAndTopCategoryList:
            # categories.append({categoryAndTopCat[0]:'service'})
            oneDict={}
            oneDict["type"] = 'service'
            # oneDict["value"] = categoryAndTopCat[0]
            oneDict["value"] = categoryAndTopCat
            # print('in categoryAndTopCat=', categoryAndTopCat[0])
            # print('in categoryAndTopCat=', categoryAndTopCat)
            # oneDict["id"] = categoryAndTopCat[0]
            oneDict["id"] = categoryAndTopCat
            categories.append(oneDict)

        # businesses=DataAccess().getAllBusinesses()
        # # businessesWithAddress=[]
        # for business in businesses:
        #     address=DataAccess().getBusinessAddress(business.businessId,'A')
        #     businessWithAddress = business.businessName
        #     if(address!=None):
        #         businessWithAddress=businessWithAddress+ ' at '
        #         if (address.cityLocation!=None):
        #             businessWithAddress=businessWithAddress+ ' '+address.cityLocation
        #         if (address.city!=None):
        #             businessWithAddress=businessWithAddress+ ' '+address.city
        #         # if (address.province!=None):
        #         #     businessWithAddress=businessWithAddress+ ' '+address.province
        #     # else:
        #         # businessWithAddress = business.businessName
        #     oneDictB={}
        #     oneDictB["type"] = 'business'
        #     oneDictB["value"] = businessWithAddress
        #     oneDictB["id"] = business.businessName
        #     categories.append(oneDictB)
        # #     businessesWithAddress.append(oneDictB)
        # # categories.extend(businessesWithAddress)

        return  categories



    def searchByCriteria(self, serviceCategory, businessName, location):

        businessesServicesDictList =[]
        # servicesOfCategory =[]
        if (serviceCategory!=None ):
            servicesOfCategory = DataAccess().getServicesOfCategory(serviceCategory)
            # print('serviceCategory=')
            # print(json.dumps(servicesOfCategory))
            businessesServicesDictList=self.getServicesByCategory(servicesOfCategory)
            # print('businessesServicesDict')
            # print(json.dumps(businessesServicesDictList))
        elif (businessName!=None):
            print('in searching by business name')
            # business=self.searchBusinessByName(businessName)
            # servicesOfCategory=self.getServiceAndBusinessList(business.businessId)
            # # print('serviceCategory=')
            # # print(json.dumps(servicesOfCategory))
            # businessesServicesDictList = self.getServicesByCategory(servicesOfCategory)
            businesses=self.searchBusinessByName(businessName)
            businessesServicesDictList = []
            for business in businesses:
                servicesOfCategory=self.getServiceAndBusinessList(business.businessId)
                # # print('serviceCategory=')
                # # print(json.dumps(servicesOfCategory))
                for services in self.getServicesByCategory(servicesOfCategory):
                    businessesServicesDictList.append(services)

        if (  (location!=None) and (businessesServicesDictList!=None) and (len(businessesServicesDictList)!=0)   ):
            locationFilteredDictList=[]
            for businessServiceCombo in businessesServicesDictList:
                address=DataAccess().getBusinessAddress(businessServiceCombo["businessId"],'A')
                if (self.checkIfBusinessInLocation(address, location)):
                    locationFilteredDictList.append(businessServiceCombo)
            return locationFilteredDictList
        return businessesServicesDictList



    def checkIfBusinessInLocation(self, businessAddress, location):
        # province, city, suburb = location
        city, suburb = location

        if (businessAddress!=None):
            # if (businessAddress.province == province):
            if(businessAddress.city == city or city == ''):
                if (businessAddress.cityLocation == suburb or suburb == ''):
                    return True
        return False
