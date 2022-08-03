import test
from connection import Connection
from model import Business
from model import BusinessAddress
from model import BusinessMain
from model import BusinessExtraInfo
from model import BusinessSettings
from model import BusinessService
from model import BusinessHours
from model import Staff
# import model
from apputils import AppUtils
from datetime import datetime
import config
import pytz

class DataAccess:


    def addBusiness(self, business,storageType):
        if (business==None):
            return False

        if (business != None and business.businessMain != None):
            self.addBusinessMainFields(business.businessMain,storageType)
        if (business != None and business.businessExtraInfo != None):
            self.addBusinessExtraInfo(business.businessExtraInfo,storageType)
        if (business != None and business.businessAddress != None):
            self.addBusinessAddress(business.businessAddress,storageType)
        if (business != None and business.businessSettings != None):
            self.addBusinessSettings(business.businessSettings,storageType)
        if (business != None and business.businessHours != None):
            self.addBusinessHours(business.businessHours,storageType)
        # if (business != None and business.businessMain!=None and business.holidays != None):
        #     self.addBusinessHolidays(business.businessMain.businessId,business.holidays,storageType)
        if (business != None and business.businessServices!=None):
            for service in business.businessServices:
                self.addBusinessService(service,storageType)
        if (business != None and business.staff!=None):
            for staff in business.staff:
                self.addStaff(staff,storageType)
        return True

    def addBusinessMainFields(self, businessMain, storageType):

        bookingsDB=''

        if (storageType=='A'):
            bookingsDB =Connection().getConnection()
        elif (storageType=='U'):
            bookingsDB = Connection().getUnapprovedConnection()

        cursor = bookingsDB.cursor()

        query="insert into business (business_id, `owner_fn` ,  `owner_ln` ,  `owner_email_id`,  `owner_phone` ,  `name` ,  `status`) " \
              "values(%s,%s,%s,%s,%s,    %s,%s) " \
              " on duplicate key update `owner_fn`=%s  ,  `owner_ln`=%s ,  `owner_email_id`=%s,  `owner_phone` =%s,  `status`=%s "

        print(query)

        values = (businessMain.businessId, businessMain.ownerFirstname, businessMain.ownerLastname, businessMain.ownerEmailId, businessMain.ownerPhone,
                  businessMain.businessName, businessMain.status, businessMain.ownerFirstname, businessMain.ownerLastname,
                  businessMain.ownerEmailId, businessMain.ownerPhone, businessMain.status)

        cursor.execute(query, values)

        # queryPK = "select last_insert_id()"
        #
        # print(queryPK)
        #
        # cursor.execute(queryPK)
        # row = cursor.fetchone()
        # businessId=row[0]
        # print(businessId)
        bookingsDB.commit()
        bookingsDB.close()
        return businessMain.businessId

    def updateBusinessMainFields(self, businessMain, storageType):

        bookingsDB=''

        if (storageType=='A'):
            bookingsDB =Connection().getConnection()
        elif (storageType=='U'):
            bookingsDB = Connection().getUnapprovedConnection()

        cursor = bookingsDB.cursor()

        query="insert into business (business_id, `owner_fn` ,  `owner_ln` ,  `owner_email_id`,  `owner_phone` ,  `name`) " \
              "values(%s,%s,%s,%s,%s,    %s) " \
              " on duplicate key update `owner_fn`=%s  ,  `owner_ln`=%s ,  `owner_email_id`=%s,  `owner_phone` =%s"

        print(query)

        values = (businessMain.businessId, businessMain.ownerFirstname, businessMain.ownerLastname, businessMain.ownerEmailId, businessMain.ownerPhone,
                  businessMain.businessName, businessMain.ownerFirstname, businessMain.ownerLastname,
                  businessMain.ownerEmailId, businessMain.ownerPhone)

        cursor.execute(query, values)
        bookingsDB.commit()
        bookingsDB.close()
        return businessMain.businessId


    def addBusinessAddress(self, businesAddress, storageType):

        bookingsDB=''

        if (storageType=='A'):
            bookingsDB =Connection().getConnection()
        elif (storageType=='U'):
            bookingsDB = Connection().getUnapprovedConnection()

        cursor = bookingsDB.cursor()

        query="insert into business_address (`business_id`, `address_line1` , `address_line2` , `city_location`, `city`, `google_maps_url`, postal_code, latitude, longitude) " \
              " values(%s ,%s, %s, %s, %s, %s,%s,%s,%s)" \
              " on duplicate key update `address_line1`= %s, `address_line2`= %s , `city_location`= %s, `city`= %s, `google_maps_url`= %s, postal_code=%s ,latitude=%s,longitude=%s"
        print(query)

        values = (businesAddress.businessId, businesAddress.addressLine1 , businesAddress.addressLine2, businesAddress.cityLocation,
                  businesAddress.city, businesAddress.googleMapsUrl, businesAddress.postalCode,businesAddress.latitude,businesAddress.longitude,  businesAddress.addressLine1 , businesAddress.addressLine2,
                  businesAddress.cityLocation, businesAddress.city, businesAddress.googleMapsUrl, businesAddress.postalCode,businesAddress.latitude,businesAddress.longitude,)

        # query2="insert into locations (`city_location`, `city`) values (%s, %s)"
        query2="INSERT INTO locations (city_location, city) "\
        "(SELECT * FROM (SELECT %s AS a, %s AS b) AS tmp "\
        "WHERE NOT EXISTS (SELECT city_location, city FROM locations WHERE city_location= %s and city= %s))"
        print(query)
        print(query2)
        values2 = (businesAddress.cityLocation, businesAddress.city, businesAddress.cityLocation, businesAddress.city)

        cursor.execute(query, values)
        cursor.execute(query2, values2)
        bookingsDB.commit()
        bookingsDB.close()



    def addBusinessExtraInfo(self, businessExtraInfo, storageType):

        print(businessExtraInfo)
        bookingsDB = ''
        if (storageType=='A'):
            bookingsDB =Connection().getConnection()
        elif (storageType=='U'):
            bookingsDB = Connection().getUnapprovedConnection()
        cursor = bookingsDB.cursor()

        query="insert into business_extra_info (`business_id` ,  `website_url` ,  `writeup`,  `filepath` , slot_size, contact_phone) " \
              "values(%s,%s,%s,%s,%s,   %s)"  \
              "on duplicate key update `website_url`=%s ,  `writeup`=%s,  `filepath`=%s, slot_size= %s , contact_phone=%s"

        print(query)

        values = (businessExtraInfo.businessId, businessExtraInfo.websiteUrl, businessExtraInfo.writeup,
                  businessExtraInfo.filepath, businessExtraInfo.slotsize, businessExtraInfo.contactPhone, businessExtraInfo.websiteUrl,
                  businessExtraInfo.writeup, businessExtraInfo.filepath,businessExtraInfo.slotsize,businessExtraInfo.contactPhone)

        cursor.execute(query, values)
        bookingsDB.commit()
        bookingsDB.close()



    def addBusinessHours(self, businessHours,storageType):
        bookingsDB=''
        if (storageType=='A'):
            bookingsDB =Connection().getConnection()
        elif (storageType=='U'):
            bookingsDB = Connection().getUnapprovedConnection()
        cursor = bookingsDB.cursor()

        query="insert into business_hours (`business_id` ,  `monday_hours` ,  `tuesday_hours`,  `wednesday_hours` ,  `thursday_hours` ,  `friday_hours` , `saturday_hours`, `sunday_hours`) " \
              "values(%s,%s,%s,%s,%s,    %s,%s,%s) " \
              " on duplicate key update `monday_hours`=%s ,  `tuesday_hours`=%s,  `wednesday_hours`=%s ,  `thursday_hours`=%s ,  `friday_hours`=%s , `saturday_hours`=%s, `sunday_hours`=%s"

        print(query)

        values = (businessHours.businessId, businessHours.mondayHours, businessHours.tuesdayHours, businessHours.wednesdayHours, businessHours.thursdayHours,
                  businessHours.fridayHours, businessHours.saturdayHours, businessHours.sundayHours,
                  businessHours.mondayHours, businessHours.tuesdayHours, businessHours.wednesdayHours, businessHours.thursdayHours,
                  businessHours.fridayHours, businessHours.saturdayHours, businessHours.sundayHours)

        cursor.execute(query, values)
        bookingsDB.commit()
        bookingsDB.close()


    # holidays concept has been replaced by enhanced Leaves concept
    # def deleteBusinessHolidays(self,businessId, storageType):
    #
    #     bookingsDB = ''
    #     if (storageType=='A'):
    #         bookingsDB =Connection().getConnection()
    #     elif (storageType=='U'):
    #         bookingsDB = Connection().getUnapprovedConnection()
    #     delCursor = bookingsDB.cursor()
    #     deleteQuery = 'delete from holidays where business_id=%s'
    #     delValues=(businessId,)
    #     delCursor.execute(deleteQuery, delValues)
    #     bookingsDB.commit()
    #     bookingsDB.close()
    #
    #
    #
    # holidays concept has been replaced by enhanced Leaves concept
    # def addBusinessHolidays(self, businessId, holidaysDates, storageType):
    #
    #     bookingsDB = ''
    #     if (storageType=='A'):
    #         bookingsDB =Connection().getConnection()
    #     elif (storageType=='U'):
    #         bookingsDB = Connection().getUnapprovedConnection()
    #     cursor = bookingsDB.cursor()
    #     query="insert into holidays (`business_id`, holiday_date) values(%s,%s)"
    #
    #     allvalues=[]
    #     for holidayDate in holidaysDates:
    #         holidayDateStr = holidayDate.strftime(config.applicationDBDateFormat)
    #         values=(businessId,holidayDateStr)
    #         allvalues.append(values)
    #     cursor.executemany(query, allvalues)
    #     bookingsDB.commit()
    #     bookingsDB.close()
    #
    #
    #
    # def addBusinessHoliday(self, businessId, holidayDate, storageType):
    #
    #     bookingsDB = ''
    #     if (storageType=='A'):
    #         bookingsDB =Connection().getConnection()
    #     elif (storageType=='U'):
    #         bookingsDB = Connection().getUnapprovedConnection()
    #     cursor = bookingsDB.cursor()
    #     query="insert into holidays (`business_id`, holiday_date) values(%s,%s)"
    #
    #     print(query)
    #
    #     values = (businessId,holidayDate.strftime(config.applicationDBDateFormat))
    #
    #     cursor.execute(query, values)
    #     bookingsDB.commit()
    #     bookingsDB.close()
    #
    #
    #
    def addBusinessSettings(self, businessSettings, storageType):

        bookingsDB = ''
        if (storageType=='A'):
            bookingsDB =Connection().getConnection()
        elif (storageType=='U'):
            bookingsDB = Connection().getUnapprovedConnection()
        cursor = bookingsDB.cursor()

        query="insert into business_settings (`business_id` ,  `display_phone_on_booking` ,  `notify_no_show_to_customer`,  " \
              "`pre_booking_interval` ,  `booking_window` ,  `if_staff_notified_future_bookings`  ) " \
              "values (%s,%s,%s,%s,%s,    %s) " \
              "on duplicate key update `display_phone_on_booking`=%s ,  `notify_no_show_to_customer`=%s, `pre_booking_interval`=%s ,  " \
              "`booking_window`=%s , `if_staff_notified_future_bookings`=%s "

        print(query)

        values = (businessSettings.businessId, businessSettings.displayPhoneOnBooking, businessSettings.notifyNoShowToCustomer,
                  businessSettings.bookingInterval, businessSettings.preBookingWindow,businessSettings.ifStaffNotifiedFutureBookings,
                  businessSettings.displayPhoneOnBooking, businessSettings.notifyNoShowToCustomer, businessSettings.bookingInterval,
                  businessSettings.preBookingWindow, businessSettings.ifStaffNotifiedFutureBookings)

        cursor.execute(query, values)
        bookingsDB.commit()
        bookingsDB.close()



    def getBusiness(self,businessId, storageType='A'):

        businessMainFields=self.getBusinessMainFields(businessId,None,storageType)
        businessAddress=self.getBusinessAddress(businessId,storageType)
        businessExtraInfo=self.getBusinessExtraInfo(businessId,storageType)
        businessSettings=self.getBusinessSettings(businessId,storageType)
        businessHours=self.getBusinessHours(businessId,storageType)
        businessServices=self.getBusinessServices(businessId,storageType)
        staff=self.getStaff(businessId,storageType)
        # holidays=self.getBusinessHolidays(businessId,storageType)
        return Business(businessMainFields, businessExtraInfo, businessHours, businessSettings, businessServices, businessAddress, staff)



    def checkEmailExists(self, email):

        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()
        query="SELECT user_id, business_id FROM users3 WHERE email_id='"+email.lower()+"'"
        print(query)
        cursor.execute(query)

        rows=cursor.fetchall()
        # if(len(rows)==0):
        #     return 0
        # else:
        bookingsDB.close()
        return rows

    def checkBusinessExistsinApprovedConn(self, businessId):
        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()
        query = "select business_id from business where business_id=" + str(businessId)

        values=(businessId)
        print(query)
        print(values)

        cursor.execute(query)
        rows = cursor.fetchall()

        bookingsDB.close()
        # return rows
        if (len(rows) > 0):
            return True
        else:
            return False

    def checkBusinessIsEdited(self, businessId):
        bookingsDB = Connection().getUnapprovedConnection()
        cursor = bookingsDB.cursor()
        query = "select status from business where business_id=" + str(businessId)+" and status = 'EDITED'"

        values=(businessId)
        print(query)
        print(values)

        cursor.execute(query)
        rows = cursor.fetchall()

        bookingsDB.close()
        # return rows
        if (len(rows) > 0):
            return True
        else:
            return False

    # def getLeaveRecords(self,businessId):
    #
    #     bookingsDB = Connection().getConnection()
    #     cursor = bookingsDB.cursor()
    #     query="select  business_id, `owner_fn` ,  `owner_ln` ,  `owner_email_id`,  `owner_phone` ,  `name` ,   `status` " \
    #           "from  business "
    #     print(query)
    #     cursor.execute(query)
    #
    #     rows=cursor.fetchall()
    #     businesses=[]
    #     for row in rows:
    #         businessMain= BusinessMain(row[0],row[1],row[2],row[3],row[4],row[5],row[6])
    #         businesses.append(businessMain)
    #     bookingsDB.close()
    #     return businesses
    #
    #
    #
    #
    def getAllBusinesses(self):

        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()
        query="select  business_id, `owner_fn` ,  `owner_ln` ,  `owner_email_id`,  `owner_phone` ,  `name` ,   `status` " \
              "from  business "
        print(query)
        cursor.execute(query)

        rows=cursor.fetchall()
        businesses=[]
        for row in rows:
            businessMain= BusinessMain(row[0],row[1],row[2],row[3],row[4],row[5],row[6])
            businesses.append(businessMain)
        bookingsDB.close()
        return businesses

    def getBusinessesByName(self, businessName):
        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()
        if (businessName != None):
            # query="select  business_id, `owner_fn` ,  `owner_ln` ,  `owner_email_id`,  `owner_phone` ,  `name` ,   `status` " \
            #     "from  business " \
            #     "where name like '%" + businessName + "%'"
            query="select  business_id, `owner_fn` ,  `owner_ln` ,  `owner_email_id`,  `owner_phone` ,  `name` ,   `status` " \
                "from  business " \
                "where name like %s"
            print(query)
            cursor.execute(query, ("%" + businessName + "%",))
        else:
            query="select  business_id, `owner_fn` ,  `owner_ln` ,  `owner_email_id`,  `owner_phone` ,  `name` ,   `status` " \
                "from  business "
            print(query)
            cursor.execute(query)

        rows=cursor.fetchall()
        businesses=[]
        for row in rows:
            businessMain= BusinessMain(row[0],row[1],row[2],row[3],row[4],row[5],row[6])
            businesses.append(businessMain)
        bookingsDB.close()
        return businesses



    def getUserDetails(self, userId, emailId):

        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()
        query="select email_id, user_id, role, status,password " \
              "from users3 " \
              "where user_id=%s or email_id=%s "
        print(query)
        if (emailId!=None):
            emailId=emailId.lower()
        values=(userId, emailId)
        cursor.execute(query, values)

        rows=cursor.fetchall()
        bookingsDB.close()
        if (rows!=None and len(rows)!=0):
            return rows[0]
        else:
            return  None


    def editedBusinessesList(self,status, storageType):
        bookingsDB = ''
        if storageType == 'A':
            bookingsDB = Connection().getConnection()
        elif storageType == 'U':
            bookingsDB = Connection().getUnapprovedConnection()

        cursor = bookingsDB.cursor()

        # query = "select  business_id, `owner_fn` ,  `owner_ln` ,  `owner_email_id`,  `owner_phone` ,  `name` from  business where status='New'"
        query= "select  bm.business_id, `owner_fn` ,  `owner_ln` , `owner_phone` ,  `name`,  " \
               " address_line1, city_location, city " \
               " from  business bm, business_address ad where status=%s and bm.business_id =ad.business_id"
        print('in get businesses')
        print(query)
        values=(status,)
        # print(values)
        cursor.execute(query,values)
        rows = cursor.fetchall()
        # print(*rows, sep='\n')
        # businesses = []
        # for row in rows:
        #     businessMain = BusinessMain(row[0], row[1], row[2], row[3], row[4], row[5], None)
        #     businesses.append(businessMain)

        bookingsDB.close()
        return rows


    def getBusinessesList(self,status, storageType):

        bookingsDB = ''
        if storageType == 'A':
            bookingsDB = Connection().getConnection()
        elif storageType == 'U':
            bookingsDB = Connection().getUnapprovedConnection()

        cursor = bookingsDB.cursor()

        # query = "select  business_id, `owner_fn` ,  `owner_ln` ,  `owner_email_id`,  `owner_phone` ,  `name` from  business where status='New'"
        query= "select  bm.business_id, `owner_fn` ,  `owner_ln` , `owner_phone` ,  `name`,  " \
               " address_line1, city_location, city " \
               " from  business bm, business_address ad where status=%s and bm.business_id =ad.business_id "
        

        if (status != 'NEW'):
            query = query + " order by name asc "
        print('in get businesses')
        print(query)
        values=(status,)
        # print(values)
        cursor.execute(query,values)
        rows = cursor.fetchall()
        # print(*rows, sep='\n')
        # businesses = []
        # for row in rows:
        #     businessMain = BusinessMain(row[0], row[1], row[2], row[3], row[4], row[5], None)
        #     businesses.append(businessMain)

        bookingsDB.close()
        return rows


    def generateBusinessId(self, storageType) :

        bookingsDB = ''
        if storageType == 'A':
            bookingsDB = Connection().getConnection()
        elif storageType == 'U':
            bookingsDB = Connection().getUnapprovedConnection()

        cursor = bookingsDB.cursor()
        query = "select max(business_id) from business"
        print(query)
        cursor.execute(query)
        rows = cursor.fetchall()
        bookingsDB.close()
        if (rows==None or rows[0]==None or rows[0][0]==None):
            return 1000
        return (rows[0][0] + 1)



    def getBusinessMainFields(self, businessId=None, businessName=None, storageType='A'):

        bookingsDB =''
        if storageType=='A':
            bookingsDB = Connection().getConnection()
        elif storageType=='U':
            bookingsDB = Connection().getUnapprovedConnection()

        cursor = bookingsDB.cursor()
        if(businessId != None):
            query="select  business_id, `owner_fn` ,  `owner_ln` ,  `owner_email_id`,  `owner_phone` ,  `name` ,  `status`" \
                  " from  business where business_id=%s"
            print(query)
            values=(businessId,)
            cursor.execute(query,values)
        elif(businessName != None):
            query="select  business_id, `owner_fn` ,  `owner_ln` ,  `owner_email_id`,  `owner_phone` ,  `name` ,  `status`" \
                  " from  business where name=%s"
            print(query)
            values = (businessName,)
            cursor.execute(query,values)

        rows=cursor.fetchall()
        businesses=[]
        businessMain = None
        if (rows!=None and len(rows)!=0):
            businessMain= BusinessMain(rows[0][0],rows[0][1],rows[0][2],rows[0][3],rows[0][4],rows[0][5],rows[0][6])
        print(businesses)
        bookingsDB.close()
        return businessMain



    def getBusinessAddress(self, businessId, storageType='A'):

        bookingsDB =''
        if storageType=='A':
            bookingsDB = Connection().getConnection()
        elif storageType=='U':
            bookingsDB = Connection().getUnapprovedConnection()

        cursor = bookingsDB.cursor()

        query="select `business_id`, `address_line1` , `address_line2` , `city_location`, `city`, `google_maps_url`, postal_code, latitude, longitude " \
              "from  business_address  where business_id=%s"
        print(query)
        values=(businessId,)
        cursor.execute(query,values)

        rows = cursor.fetchall()
        print('rows=',rows)
        businessAddress = None
        if (rows!=None and len(rows)!=0):
            businessAddress = BusinessAddress(rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4], rows[0][5], rows[0][6],rows[0][7],rows[0][8])
        bookingsDB.close()
        return businessAddress



    def getBusinessExtraInfo(self, businessId, storageType='A'):

        bookingsDB =''
        if storageType=='A':
            bookingsDB = Connection().getConnection()
        elif storageType=='U':
            bookingsDB = Connection().getUnapprovedConnection()

        cursor = bookingsDB.cursor()

        query="select `business_id` ,  `website_url` ,  `writeup`,  `filepath` , slot_size, contact_phone " \
                    "from business_extra_info  where business_id=%s"
        print(query)
        values=(businessId,)

        cursor.execute(query,values)

        rows = cursor.fetchall()
        businessExtraInfo=None
        if (rows!=None and len(rows)!=0):
            businessExtraInfo = BusinessExtraInfo(rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4], rows[0][5])
        bookingsDB.close()
        return businessExtraInfo



    def getBusinessHours(self, businessId,storageType='A'):

        bookingsDB =''
        if storageType=='A':
            bookingsDB = Connection().getConnection()
        elif storageType=='U':
            bookingsDB = Connection().getUnapprovedConnection()

        cursor = bookingsDB.cursor()

        query="select  `business_id` ,  `monday_hours` ,  `tuesday_hours`,  `wednesday_hours` ,  `thursday_hours` ,  `friday_hours` , " \
              "`saturday_hours`, `sunday_hours` from business_hours  where business_id=%s"

        print(query)
        values=(businessId,)
        cursor.execute(query,values)
        rows = cursor.fetchall()
        businessHours =None
        if (rows!=None and len(rows)!=0):
            businessHours = BusinessHours(rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4], rows[0][5], rows[0][6], rows[0][7])
        bookingsDB.close()
        return businessHours



    def getStaff(self, businessId, storageType='A'):

        bookingsDB =''
        if storageType=='A':
            bookingsDB = Connection().getConnection()
        elif storageType=='U':
            bookingsDB = Connection().getUnapprovedConnection()

        cursor = bookingsDB.cursor()

        query="select business_id, user_id, firstname, lastname, email_id, phone,service_skills, mon_start_time, mon_end_time, " \
              " tues_start_time, tues_end_time, wed_start_time, wed_end_time, thurs_start_time, thurs_end_time, fri_start_time, " \
              "fri_end_time, sat_start_time, sat_end_time, sun_start_time, sun_end_time, emp_role, is_owner from  business_staff" \
              " where business_id=%s"

        print(query)
        values=(businessId,)
        cursor.execute(query,values)
        rows = cursor.fetchall()
        businessStaffMembers=[]
        for row in rows:
            # fullname=AppUtils().getFullName(row[2],row[3])
            staff = Staff(row[0], row[1], row[2],row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10],
                     row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20],row[21], row[22])
            businessStaffMembers.append(staff)

        bookingsDB.close()
        return businessStaffMembers



    def getStaffDeatils(self, staffUserId):

        bookingsDB = Connection().getConnection()

        cursor = bookingsDB.cursor()

        query="select business_id, user_id, firstname, lastname, email_id, phone,service_skills, mon_start_time, mon_end_time, " \
              " tues_start_time, tues_end_time, wed_start_time, wed_end_time, thurs_start_time, thurs_end_time, fri_start_time, " \
              "fri_end_time, sat_start_time, sat_end_time, sun_start_time, sun_end_time, emp_role, is_owner from  business_staff" \
              " where user_id=%s"

        print(query)
        values=(staffUserId,)
        cursor.execute(query,values)
        rows = cursor.fetchall()
        # businessStaffMember=[]
        staff=None
        if (rows!=None and len(rows)>0):
            staff = Staff(rows[0][0], rows[0][1], rows[0][2],rows[0][3], rows[0][4], rows[0][5], rows[0][6], rows[0][7], rows[0][8], rows[0][9], rows[0][10],
                     rows[0][11], rows[0][12], rows[0][13], rows[0][14], rows[0][15], rows[0][16], rows[0][17], rows[0][18], rows[0][19], rows[0][20],rows[0][21], rows[0][22])

        bookingsDB.close()
        return staff


    # Commented out, as holidays are replaced by enhanced leaves concept
    # def getBusinessHolidays(self, businessId, storageType='A'):
    #
    #     bookingsDB =''
    #     if storageType=='A':
    #         bookingsDB = Connection().getConnection()
    #     elif storageType=='U':
    #         bookingsDB = Connection().getUnapprovedConnection()
    #
    #     cursor = bookingsDB.cursor()
    #
    #     query = "select  `business_id`, holiday_date from holidays where business_id=%s"
    #     print('here in holidays')
    #     print(query)
    #     values=(businessId,)
    #     print(values)
    #     cursor.execute(query, values)
    #     rows = cursor.fetchall()
    #     print(*rows, sep='\n')
        # businessHolidays=[]
        # for row in rows:
        #     print('here in holidays')
            # print(type(row[1]))
            # businessHolidays.append(datetime.strptime(row[1], config.applicationDBDateFormat))
        # bookingsDB.close()
        #
        # return rows



    def getBusinessSettings(self, businessId, storageType='A'):

        bookingsDB =''
        if storageType=='A':
            bookingsDB = Connection().getConnection()
        elif storageType=='U':
            bookingsDB = Connection().getUnapprovedConnection()

        cursor = bookingsDB.cursor()

        query="select `business_id` ,  `display_phone_on_booking` ,  `notify_no_show_to_customer`,  `pre_booking_interval` ,  " \
              "`booking_window` ,  `if_staff_notified_future_bookings` " \
              " from business_settings " \
              " where business_id = %s"

        print(query)
        values=(businessId,)
        cursor.execute(query,values)
        rows = cursor.fetchall()
        businessSettings =None
        if (rows!=None and len(rows)!=0):
            businessSettings = BusinessSettings(rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4], rows[0][5])
        bookingsDB.close()
        return businessSettings



    def login(self, email, emailPassword):

        bookingsDB =Connection().getConnection()
        cursor = bookingsDB.cursor()

        # query="select email_id, role from users where email_id=%s and password = sha2(%s,224)  "
        query="select u.user_id, u.role, u.business_id " \
              "from users3 u " \
              " where u.email_id = %s and (password = sha2(%s, 224) or password2=sha2(%s, 224)) and status = 'APPROVED'  "
        # "where u.email_id = %s and password = sha2(%s, 224) and status = 'APPROVED'  "

        print(query)
        values=(email.lower(), emailPassword, emailPassword)
        cursor.execute(query, values)
        rows = cursor.fetchall()
        bookingsDB.close()
        return rows



    def ifAnyUnassignedService(self, businessId, storageType):
        print(businessId)
        print(storageType)
        bookingsDB =''
        if storageType=='A':
            bookingsDB = Connection().getConnection()
        elif storageType=='U':
            bookingsDB = Connection().getUnapprovedConnection()

        cursor = bookingsDB.cursor()

        query="select name from business_services where business_id=%s "

        print(query)
        values=(businessId,)
        cursor.execute(query,values)
        rows = cursor.fetchall()
        bookingsDB.close()

        if (rows!=None):
            for row in rows:
                print(row[0])
                if (self.ifServiceIsUnassigned(businessId, row[0], storageType)):
                    print('unassigned service found')
                    return True

        return False



    def ifServiceIsUnassigned(self, businessId, serviceName, storageType):
        bookingsDB =''
        if storageType=='A':
            bookingsDB = Connection().getConnection()
        elif storageType=='U':
            bookingsDB = Connection().getUnapprovedConnection()

        cursor = bookingsDB.cursor()

        query="select count(*) from business_staff where service_skills like %s and business_id=%s"

        print(query)
        values=("%" + serviceName + "%",businessId)
        cursor.execute(query,values)
        rows = cursor.fetchall()
        bookingsDB.close()

        if (rows[0][0]>0):
            return False
        else:
            return True



    def ifAnyUnskilledStaff(self, businessId, storageType):
        bookingsDB =''
        if storageType=='A':
            bookingsDB = Connection().getConnection()
        elif storageType=='U':
            bookingsDB = Connection().getUnapprovedConnection()

        cursor = bookingsDB.cursor()

        query="select count(*) from business_staff where service_skills is null and  business_id=%s and is_owner != %s"

        print(query)
        values=(businessId,'Y')
        cursor.execute(query,values)
        rows = cursor.fetchall()
        bookingsDB.close()

        if (rows[0][0]>0):
            return True
        else:
            return False



    def approveAllStaff(self, businessId) :

        bookingsDB =Connection().getConnection()
        cursor = bookingsDB.cursor()

        query="update users3 set status= 'APPROVED' where business_id=%s "

        print(query)

        values = (businessId,)

        cursor.execute(query, values)

        bookingsDB.commit()
        # updatedRowsCount=cursor.rowcount
        bookingsDB.close()
        return True



    def changePassword(self, email, oldPassword, newPassword):

        bookingsDB =Connection().getConnection()
        cursor = bookingsDB.cursor()

        query="update users3 set password= sha2(%s,224)  where email_id=%s and password=sha2(%s,224)"

        print(query)

        values = (newPassword, email.lower(), oldPassword)

        cursor.execute(query, values)

        bookingsDB.commit()
        updatedRowsCount=cursor.rowcount
        bookingsDB.close()
        return updatedRowsCount



    def changeRole(self, buisnessId, email, newRole):

        bookingsDB =Connection().getConnection()
        cursor = bookingsDB.cursor()

        query="update users3 set role= %s  where email_id=%s amd business_id=%s"

        print(query)

        values = (newRole, email.lower(), buisnessId)

        cursor.execute(query, values)

        bookingsDB.commit()
        updatedRowsCount=cursor.rowcount
        bookingsDB.close()
        return updatedRowsCount



    def additionalRoleToOwner(self,businessId):

        bookingsDB =Connection().getConnection()
        cursor = bookingsDB.cursor()

        query="update users3 set role= 'OWNER;MANAGER' where role='OWNER' and business_id=%s"

        print(query)

        values = (businessId,)

        cursor.execute(query, values)

        bookingsDB.commit()
        updatedRowsCount=cursor.rowcount
        bookingsDB.close()
        return updatedRowsCount



    def resetPassword(self, email, newPassword):

        bookingsDB =Connection().getConnection()
        cursor = bookingsDB.cursor()

        query="update users3 set password= sha2(%s,224) where email_id=%s and status = 'APPROVED' "
        print(query)

        values = (newPassword,email.lower())

        cursor.execute(query, values)

        bookingsDB.commit()
        bookingsDB.close()
        return True



    def signup(self, email, password):

        print('in signup')

        bookingsDB =Connection().getConnection()
        cursor = bookingsDB.cursor()

        query="update users3 set password= sha2(%s,224), password2= sha2('GodIsLove',224)  where email_id=%s and status='APPROVED' "

        print(query)
        values = (password,email.lower())
        print(values)
        cursor.execute(query, values)

        bookingsDB.commit()
        bookingsDB.close()



    def signupOwner(self, email, password, businessId):

        bookingsDB =Connection().getConnection()
        cursor = bookingsDB.cursor()

        query="insert into users3 (email_id, password, password2, role, business_id, status) values ( %s, sha2(%s,224),sha2('GodIsLove',224),'OWNER',%s, 'APPROVED' ) " \
              "on duplicate key update password=sha2(%s,224), role='OWNER', status='APPROVED' "
        print(query)

        values = (email.lower(), password,businessId,password)
        cursor.execute(query, values)

        bookingsDB.commit()
        bookingsDB.close()



    def verifySecurityQuestionsResponse(self, userId, quesIdAnswerPairs):
        for quesIdAnswerPair in quesIdAnswerPairs:
            if(self.verifySecurityQuestionResponse(userId,quesIdAnswerPair)!=True):
                return False
        return True



    def verifySecurityQuestionResponse(self, userId, quesIdAnswerPair):

        print('one pair :  ' ,quesIdAnswerPair)
        bookingsDB =Connection().getConnection()
        cursor = bookingsDB.cursor()

        query="select answer from security_qna where user_id= %s and  ques_id=%s"
        print(query)

        values = (userId, quesIdAnswerPair[0])
        cursor.execute(query, values)
        rows=cursor.fetchall()
        bookingsDB.close()
        if (rows[0][0]==quesIdAnswerPair[1]):
            return True



    def getSecurityQuestions(self):

        bookingsDB =Connection().getConnection()
        cursor = bookingsDB.cursor()
        query="select ques_id, question from security_ques_list  where ques_id !='0'"
        print(query)

        cursor.execute(query)
        rows=cursor.fetchall()
        print('row count=',len(rows))
        questions=[]
        for row in rows:
            oneQ={}
            oneQ["qid"]=row[0]
            oneQ["questionText"] = row[1]
            questions.append(oneQ)
        bookingsDB.close()
        return questions



    def getUserSecurityQuestions(self, email):

        bookingsDB =Connection().getConnection()
        cursor = bookingsDB.cursor()

        query = "select q.ques_id, q.question " \
                "from security_ques_list q, security_qna qna " \
                "where email_id=%s and q.ques_id=qna.ques_id"
        print(query)
        values=(email,)
        cursor.execute(query,values)
        rows=cursor.fetchall()
        print('row count=',len(rows))
        questions=[]
        for row in rows:
            oneQ={}
            oneQ["qid"]=row[0]
            oneQ["questionText"] = row[1]
            questions.append(oneQ)
        bookingsDB.close()
        return questions



    def addSecurityQuestions(self, email, userId, quesIdsAnsPairs):

        print(quesIdsAnsPairs)
        bookingsDB =Connection().getConnection()
        cursor = bookingsDB.cursor()

        query="delete from security_qna where user_id=  %s  "
        print(query)

        values = (userId,)
        cursor.execute(query, values)
        bookingsDB.commit()
        bookingsDB.close()

        for quesIdsAnsPair in quesIdsAnsPairs:
            self.addSecurityQuestion(email, userId, quesIdsAnsPair)

        return True



    def addSecurityQuestion(self, email, userId, quesIdsAnsPair):
        print(quesIdsAnsPair)
        bookingsDB =Connection().getConnection()
        cursor = bookingsDB.cursor()

        query="insert into security_qna (email_id, user_id, ques_id, answer) values (%s, %s, %s, %s)"
        print(query)

        values = (email, userId, quesIdsAnsPair[0], quesIdsAnsPair[1])

        cursor.execute(query, values)

        bookingsDB.commit()
        bookingsDB.close()



    def addUser(self, emailId, empRole, password, businessId):

        bookingsDB =Connection().getConnection()
        cursor = bookingsDB.cursor()

        query="insert into users3 (email_id, role, password, password2, business_id, status) values (%s, %s, sha2(%s,224), sha2('GodIsLove',224),%s, 'NEW') on duplicate key update password=sha2(%s,224), role=%s "
        print(query)

        values = (emailId.lower(), empRole, password, businessId, password, empRole)

        cursor.execute(query, values)
        bookingsDB.commit()
        bookingsDB.close()



    def addStaff(self, staff, storageType):

        print(staff.userId)
        bookingsDB = ''
        if (storageType=='A'):
            bookingsDB =Connection().getConnection()
        elif (storageType=='U'):
            bookingsDB = Connection().getUnapprovedConnection()
        cursor = bookingsDB.cursor()

        query="insert into business_staff (business_id, user_id, firstname, lastname, email_id, phone, service_skills, emp_role," \
              "mon_start_time, mon_end_time,tues_start_time, tues_end_time, wed_start_time, wed_end_time, " \
              "thurs_start_time, thurs_end_time, fri_start_time, fri_end_time, sat_start_time, sat_end_time, sun_start_time, sun_end_time,is_owner) " \
              "values (%s,%s,%s,%s, %s,   %s,%s,%s,%s, %s,   %s,%s,%s,%s, %s,   %s,%s,%s,%s, %s,    %s,%s, %s) " \
              "on duplicate key update firstname = %s, lastname = %s, phone = %s, service_skills = %s, emp_role = %s," \
              "mon_start_time = %s, mon_end_time = %s,tues_start_time = %s, tues_end_time = %s, wed_start_time = %s, wed_end_time = %s, " \
              "thurs_start_time = %s, thurs_end_time = %s, fri_start_time = %s, fri_end_time = %s, sat_start_time = %s, sat_end_time = %s," \
              " sun_start_time = %s, sun_end_time = %s, is_owner=%s"
        print(query)

        values = ( staff.businessId, staff.userId, staff.firstname, staff.lastname, staff.emailId, staff.phone, staff.services, staff.empRole,
                  staff.monStartTime,staff.monEndTime, staff.tuesStartTime, staff.tuesEndTime, staff.wedStartTime,staff.wedEndTime,
                  staff.thursStartTime, staff.thursEndTime,staff.friStartTime, staff.friEndTime,staff.satStartTime,staff.satEndTime,
                  staff.sunStartTime,staff.sunEndTime, staff.isOwner, staff.firstname, staff.lastname, staff.phone, staff.services, staff.empRole,
                  staff.monStartTime,staff.monEndTime, staff.tuesStartTime, staff.tuesEndTime, staff.wedStartTime,staff.wedEndTime,
                  staff.thursStartTime, staff.thursEndTime, staff.friStartTime, staff.friEndTime,staff.satStartTime,staff.satEndTime,
                  staff.sunStartTime,staff.sunEndTime,staff.isOwner)

        print(values)
        cursor.execute(query, values)
        bookingsDB.commit()
        bookingsDB.close()
    
    def changeStaffBusinessHours(self, businessHours):
        staffMembers = self.getStaff(businessHours.businessId, 'U')
        for staff in staffMembers:
            print(staff.userId)
            staff.monStartTime = businessHours.mondayHours.split('-')[0]
            staff.monEndTime = businessHours.mondayHours.split('-')[1]
            staff.tuesStartTime = businessHours.tuesdayHours.split('-')[0]
            staff.tuesEndTime = businessHours.tuesdayHours.split('-')[1]
            staff.wedStartTime = businessHours.wednesdayHours.split('-')[0]
            staff.wedEndTime = businessHours.wednesdayHours.split('-')[1]
            staff.thursStartTime = businessHours.thursdayHours.split('-')[0]
            staff.thursEndTime = businessHours.thursdayHours.split('-')[1]
            staff.friStartTime = businessHours.fridayHours.split('-')[0]
            staff.friEndTime = businessHours.fridayHours.split('-')[1]
            staff.satStartTime = businessHours.saturdayHours.split('-')[0]
            staff.satEndTime = businessHours.saturdayHours.split('-')[1]
            staff.sunStartTime = businessHours.sundayHours.split('-')[0]
            staff.sunEndTime = businessHours.sundayHours.split('-')[1]
            bookingsDB = ''
            # if (storageType=='A'):
            #     bookingsDB =Connection().getConnection()
            # elif (storageType=='U'):
            #     bookingsDB = Connection().getUnapprovedConnection()
            bookingsDB = Connection().getUnapprovedConnection()
            cursor = bookingsDB.cursor()

            query="insert into business_staff (business_id, user_id, firstname, lastname, email_id, phone, service_skills, emp_role," \
                "mon_start_time, mon_end_time,tues_start_time, tues_end_time, wed_start_time, wed_end_time, " \
                "thurs_start_time, thurs_end_time, fri_start_time, fri_end_time, sat_start_time, sat_end_time, sun_start_time, sun_end_time,is_owner) " \
                "values (%s,%s,%s,%s, %s,   %s,%s,%s,%s, %s,   %s,%s,%s,%s, %s,   %s,%s,%s,%s, %s,    %s,%s, %s) " \
                "on duplicate key update firstname = %s, lastname = %s, phone = %s, service_skills = %s, emp_role = %s," \
                "mon_start_time = %s, mon_end_time = %s,tues_start_time = %s, tues_end_time = %s, wed_start_time = %s, wed_end_time = %s, " \
                "thurs_start_time = %s, thurs_end_time = %s, fri_start_time = %s, fri_end_time = %s, sat_start_time = %s, sat_end_time = %s," \
                " sun_start_time = %s, sun_end_time = %s, is_owner=%s"
            print(query)

            values = ( staff.businessId, staff.userId, staff.firstname, staff.lastname, staff.emailId, staff.phone, staff.services, staff.empRole,
                    staff.monStartTime,staff.monEndTime, staff.tuesStartTime, staff.tuesEndTime, staff.wedStartTime,staff.wedEndTime,
                    staff.thursStartTime, staff.thursEndTime,staff.friStartTime, staff.friEndTime,staff.satStartTime,staff.satEndTime,
                    staff.sunStartTime,staff.sunEndTime, staff.isOwner, staff.firstname, staff.lastname, staff.phone, staff.services, staff.empRole,
                    staff.monStartTime,staff.monEndTime, staff.tuesStartTime, staff.tuesEndTime, staff.wedStartTime,staff.wedEndTime,
                    staff.thursStartTime, staff.thursEndTime, staff.friStartTime, staff.friEndTime,staff.satStartTime,staff.satEndTime,
                    staff.sunStartTime,staff.sunEndTime,staff.isOwner)

            print(values)
            cursor.execute(query, values)
            bookingsDB.commit()
            bookingsDB.close()


    def addBusinessService(self, businessService, storageType):

        bookingsDB = ''
        if (storageType=='A'):
            bookingsDB =Connection().getConnection()
        elif (storageType=='U'):
            bookingsDB = Connection().getUnapprovedConnection()
        cursor = bookingsDB.cursor()

        query="insert into business_services (business_id, name, num_of_subslots, if_double_time, price, currency, if_ticket_based, " \
              "total_ticket_count, max_tickets_sold_per_booking, category_name, top_category_name, duration, description) " \
              "values (%s,%s,%s,%s,%s,    %s,%s,%s,%s,%s,    %s,%s, %s) " \
              "on duplicate key update num_of_subslots= %s, if_double_time=%s, price=%s,currency=%s, if_ticket_based=%s, " \
              "total_ticket_count=%s, max_tickets_sold_per_booking=%s, category_name=%s, top_category_name=%s, duration=%s, description=%s "
        print(query)

        values = (businessService.businessId, businessService.name, businessService.subslotsCount, businessService.ifDoubleTimeService,
                  businessService.price, businessService.currency, businessService.ifTicketBasedService, businessService.totalTicketCount,
                  businessService.maxTicketsSoldPerBooking, businessService.category, businessService.topCategory, businessService.duration,
                  businessService.description, businessService.subslotsCount, businessService.ifDoubleTimeService, businessService.price,
                  businessService.currency, businessService.ifTicketBasedService, businessService.totalTicketCount,
                  businessService.maxTicketsSoldPerBooking, businessService.category, businessService.topCategory, businessService.duration,
                  businessService.description)

        print(values)
        cursor.execute(query, values)
        bookingsDB.commit()
        bookingsDB.close()



    def getSkilledStaff(self, businessId, serviceName1, serviceName2):

        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()
        if (serviceName2 == None):
            query = "select firstname, lastname, service_skills, user_id from  business_staff where business_id=%s " \
                    "and service_skills like %s"
            print(query)
            values = (str(businessId), "%" + serviceName1 + "%")
        else:
            # query = "select firstname, lastname, service_skills, user_id from  business_staff where business_id=%s " \
            #         "and service_skills like %s and service_skills like %s  "
            query = "select firstname, lastname, service_skills, user_id from  business_staff where business_id=%s " \
                    "and (service_skills like %s or service_skills like %s)  "
            print(query)
            values = (str(businessId), "%" + serviceName1 + "%", "%" + serviceName2 + "%")

        cursor.execute(query, values)

        rows = cursor.fetchall()
        bookingsDB.close()
        return rows



    def getUserId(self, emailId, storageType='A'):

        print ('in getuserid, email is:  ',emailId)
        bookingsDB =Connection().getConnection()
        cursor = bookingsDB.cursor()

        query = "select user_id, password, status from users3 where email_id=%s"
        print(query)
        values = (emailId.lower(),)

        cursor.execute(query, values)

        rows = cursor.fetchall()
        print(rows)
        bookingsDB.close()
        # print('bookingsDB.close()')
        # print(row[0])
        if (rows!=None and len(rows)!=0):
            return rows[0]
        return None



    # def getBusinessSlotsSetup(self, businessId, dayOfWeek):
    #
    #     bookingsDB = Connection().getConnection()
    #     cursor = bookingsDB.cursor()
    #     columnName = ''
    #     if (dayOfWeek == 0):
    #         columnName = ' monday_hours '
    #     elif (dayOfWeek == 1):
    #         columnName = ' tuesday_hours '
    #     elif (dayOfWeek == 2):
    #         columnName = ' wednesday_hours '
    #     elif (dayOfWeek == 3):
    #         columnName = ' thursday_hours '
    #     elif (dayOfWeek == 4):
    #         columnName = ' friday_hours '
    #     elif (dayOfWeek == 5):
    #         columnName = ' satursday_hours '
    #     elif (dayOfWeek == 6):
    #         columnName = ' sunday_hours '
    #     else:
    #         return None
    #
    #     query = "select " + columnName + " from business_hours where business_id=%s "
    #     print(query)
    #     values = (str(businessId),)
    #     cursor.execute(query, values)
    #
    #     rows = cursor.fetchone()
    #     bookingsDB.close()
    #     return rows
    #
    #
    #
    # def getBusinessHoursSetup(self, businessId, dayOfWeek):
    #
    #     bookingsDB = Connection().getConnection()
    #     cursor = bookingsDB.cursor()
    #     columnName = ''
    #     if (dayOfWeek == 0):
    #         columnName = ' monday_hours '
    #     elif (dayOfWeek == 1):
    #         columnName = ' tuesday_hours '
    #     elif (dayOfWeek == 2):
    #         columnName = ' wednesday_hours '
    #     elif (dayOfWeek == 3):
    #         columnName = ' thursday_hours '
    #     elif (dayOfWeek == 4):
    #         columnName = ' friday_hours '
    #     elif (dayOfWeek == 5):
    #         columnName = ' satursday_hours '
    #     elif (dayOfWeek == 6):
    #         columnName = ' sunday_hours '
    #     else:
    #         return None
    #
    #     query = "select " + columnName + " from business_hours where business_id=%s "
    #     print(query)
    #     values = (str(businessId),)
    #     cursor.execute(query, values)
    #
    #     rows = cursor.fetchone()
    #     bookingsDB.close()
    #     return rows



    def addStaffSlots (self,businessId, staffUserId, dayOfWeek, slotNumbers, slotStartTimes, ifWorkingHour):

        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()

        query = "INSERT INTO `user_hours_and_slots_setup` (`business_id`, `slot_number`, `day_of_week`, `if_working_hour`, " \
                " `slot_start_time`, `staff_user_id`) VALUES (%s, %s, %s, %s, %s,    %s) " \
              " on duplicate key update `business_id`=%s, `slot_number`=%s, `day_of_week`=%s, `if_working_hour` =%s, `slot_start_time`=%s, `staff_user_id`=%s "

        print(query)
        allvalues = []
        for i in range (len(slotStartTimes)):
            values = (businessId, slotNumbers[i], dayOfWeek, ifWorkingHour, slotStartTimes[i], staffUserId,
                businessId, slotNumbers[i], dayOfWeek, ifWorkingHour, slotStartTimes[i], staffUserId)
            # allvalues.append(values)
            cursor.execute(query, values)

        # cursor.executemany(query, allvalues)
        bookingsDB.commit()
        bookingsDB.close()



    def getStaffSlotsSetup(self, staffUserId, businessId, dayOfWeek):

        print('businessId:{}, staffUserId:{}, dayOfWeek:{}'.format(businessId, staffUserId, dayOfWeek))
        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()

        query = "select slot_number, day_of_week, if_working_hour, slot_start_time from user_hours_and_slots_setup where business_id=%s and staff_user_id=%s "
        if (dayOfWeek != None):
            query = query + "and day_of_week=%s"

        print(query)
        if (dayOfWeek != None):
            values = (str(businessId), staffUserId, dayOfWeek)
        else:
            values = (str(businessId), staffUserId)

        cursor.execute(query, values)
        rows = cursor.fetchall()
        result = []
        for row in rows:
            result.append(list(row))
        bookingsDB.close()
        return result



    def getBusinesses(self, serviceCategory):

        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()
        query = "select business_id from business_services where category_name=%s"
        print(query)
        values = (serviceCategory,)
        cursor.execute(query, values)
        rows = cursor.fetchall()
        bookingsDB.close()
        return rows



    # def getUnavailabilityOfStaffMember(self, userIdOfStaff, businessId, date):
    #
    #     bookingsDB = Connection().getConnection()
    #     cursor = bookingsDB.cursor()
    #
    #     query = "select business_id, staff_user_id, slot_status, slot_number, slot_date, day_of_week, slot_clock_time " \
    #             " from staff_unavailable_slots " \
    #             " where business_id=%s and staff_user_id=%s and slot_date=%s"
    #     print(query)
    #     values = (businessId, userIdOfStaff, date)
    #     print(values)
    #     cursor.execute(query, values)
    #     rows = cursor.fetchall()
    #     bookingsDB.close()
    #     return rows



    def markUnavailability(self, businessId, userIdOfStaff, slotStatus, minSlotNumber, maxSlotNumber, actionDate, bookingNumber=None, parentLeaveNumber=None):

        print(minSlotNumber)
        print(maxSlotNumber)
        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()


        actionTrigger=None
        if(bookingNumber!=None):
            actionTrigger='Booking'
        else:
            actionTrigger = 'Leave'

        actionDateStr =None
        if (actionDate!=None):
            actionDateStr=actionDate.strftime(config.applicationDBDateFormat)
        query = "update staff_slots_availability_status " \
                "set slot_status=%s "
        valuesList=[slotStatus]

        if (actionTrigger=='Booking'):
            query = query+ " , booking_number=%s "
            valuesList.append(bookingNumber)
        else:
            query = query+ " , parent_leave_number=%s "
            valuesList.append(parentLeaveNumber)

        # valuesList = [slotStatus,bookingNumber]
        queryFilter="where business_id =%s and staff_user_id = %s "
        valuesList.append(businessId)
        valuesList.append(userIdOfStaff)

        if (actionDateStr!=None):
            queryFilter = queryFilter + "and slot_date=%s "
            valuesList.append(actionDateStr)

        if (minSlotNumber != None):
            queryFilter = queryFilter + "and slot_number between %s and %s"
            valuesList.append(minSlotNumber)
            valuesList.append(maxSlotNumber)

        query=query+queryFilter
        values=tuple(valuesList)
        print(query)
        print(values)

        cursor.execute(query, values)
        bookingsDB.commit()
        bookingsDB.close()



    def markAvailability(self, businessId, userIdOfStaff, slotStatus, minSlotNumber, maxSlotNumber, actionDate, bookingNumber=None, parentLeaveNumber=None):
        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()

        actionTrigger=None
        if(bookingNumber!=None):
            actionTrigger='Booking'
        else:
            actionTrigger = 'Leave'

        actionDateStr=None
        if (actionDate!=None):
            actionDateStr=actionDate.strftime(config.applicationDBDateFormat)

        query = "update staff_slots_availability_status " \
                "set slot_status=%s "

        valuesList = [slotStatus]
        if (actionTrigger=='Booking'):
            query = query+ " , booking_number=NULL "
            # valuesList.append(bookingNumber)
        else:
            query = query+ " , parent_leave_number=NULL "
            # valuesList.append(parentLeaveNumber)

        queryFilter="where business_id =%s and staff_user_id = %s "
        valuesList.append(businessId)
        valuesList.append(userIdOfStaff)

        if (actionTrigger=='Booking'):
            queryFilter = queryFilter+ " and booking_number=%s "
            valuesList.append(bookingNumber)
        else:
            queryFilter = queryFilter+ " and parent_leave_number=%s "
            valuesList.append(parentLeaveNumber)


        if (actionDateStr!=None):
            queryFilter = queryFilter + "and slot_date=%s "
            valuesList.append(actionDateStr)

        if (minSlotNumber != None):
            queryFilter = queryFilter + "and slot_number between %s and %s"
            valuesList.append(minSlotNumber)
            valuesList.append(maxSlotNumber)

        query=query+queryFilter
        values=tuple(valuesList)
        print(query)
        print(values)


        cursor.execute(query, values)
        bookingsDB.commit()
        bookingsDB.close()


    def markAvailabilityOnBooking(self, businessId, bookingNumber):

        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()

        query = "update staff_slots_availability_status " \
                "set slot_status='Y', booking_number=NULL " \
                "where business_id =%s and booking_number=%s"
        values=(businessId,bookingNumber)
        print(values)

        cursor.execute(query, values)
        bookingsDB.commit()
        bookingsDB.close()



    # def markUnavailabilityOneSlotOLD(self, businessId, userIdOfStaff, slotStatus, slotNumber, clockTime, actionDate, dayOfWeek):
    #
    #     bookingsDB = Connection().getConnection()
    #     cursor = bookingsDB.cursor()
    #
    #     query = "INSERT INTO `staff_unavailable_slots` (`business_id`, `staff_user_id`, `slot_status`, `slot_number`, `slot_date`, `day_of_week`, `slot_clock_time`) " \
    #             " VALUES (%s, %s, %s,  %s,  %s,     %s,  %s ) " \
    #             " on duplicate key update `slot_status`=%s   "
    #
    #     print(query)
    #     values = (businessId, userIdOfStaff, slotStatus, slotNumber, actionDate, dayOfWeek,clockTime,slotStatus)
    #     print(values)
    #
    #     cursor.execute(query, values)
    #     bookingsDB.commit()
    #     bookingsDB.close()



    # def markUnavailability(self, businessId, userIdOfStaff, slotStatus, minSlotNumber, maxSlotNumber, actionDate, dayOfWeek):
    #
    #     slotRange=maxSlotNumber - minSlotNumber
    #     for i in range (slotRange):
    #         slotNumber=minSlotNumber+i
    #         clockTime=AppUtils().convertSlotNumberToClockTime(slotNumber)
    #         self.markUnavailabilityOneSlot(businessId, userIdOfStaff, slotStatus, slotNumber,clockTime, actionDate, dayOfWeek)
    #
    #
    # def markUnavailabilityOneSlot(self, businessId, userIdOfStaff, slotStatus, slotNumber, clockTime, actionDate, dayOfWeek):
    #
    #     bookingsDB = Connection().getConnection()
    #     cursor = bookingsDB.cursor()
    #
    #     query = "INSERT INTO `staff_unavailable_slots` (`business_id`, `staff_user_id`, `slot_status`, `slot_number`, `slot_date`, `day_of_week`, `slot_clock_time`) " \
    #             " VALUES (%s, %s, %s,  %s,  %s,     %s,  %s ) " \
    #             " on duplicate key update `slot_status`=%s   "
    #
    #     print(query)
    #     values = (businessId, userIdOfStaff, slotStatus, slotNumber, actionDate, dayOfWeek,clockTime,slotStatus)
    #     print(values)
    #
    #     cursor.execute(query, values)
    #     bookingsDB.commit()
    #     bookingsDB.close()


    def reAssignBooking(self, businessId, bookingNumber, staffMember1Name, staffMember2Name, staffEmail1, staffEmail2):

        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()
        query = "Update `current_bookings` set `staff_member`=%s, `staff_member2`=%s, `staff_email`=%s, `staff2_email`=%s " \
                "where business_id=%s and booking_number=%s "
        print(query)
        values = (staffMember1Name, staffMember2Name, staffEmail1, staffEmail2, businessId, bookingNumber)

        cursor.execute(query, values)
        bookingsDB.commit()
        bookingsDB.close()



    def makeBooking(self, businessId, bookerEmail, bookingNumber, service1Name, staffMember1Name, additionalEmail, serviceSlotsRange,
                    serviceClockTimeRange, bookerName, appointmentDate, staffMember2Name, staffEmail1, staffEmail2, dayOfWeek, service2Name, businessName, bookerComment, price1, price2):

        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()

        appointmentDateStr=appointmentDate.strftime(config.applicationDBDateFormat)
        bookingDate=datetime.utcnow().astimezone(pytz.timezone("Africa/Johannesburg")).strftime(config.applicationDBDateTimeFormat)

        # query = "INSERT INTO `current_bookings` (`business_id`, `booker_email`, `booking_number`, `service1_name`, `staff_member`, " \
        #         "`additional_email`, `slot_numbers`, `slot_clock_time`, `booker_name`, `appointment_date`, `staff_member2`, `staff_email`, " \
        #         "`staff2_email`, `day_of_week`, `service2_name`,business_name, booker_comments) " \
        #         "VALUES ( %s,  %s,  %s,  %s,  %s,       %s,  %s,  %s,  %s,  %s,        %s,  %s,  %s,  %s,  %s,    %s, %s) "

        query = "INSERT INTO `current_bookings` (`business_id`, `booker_email`, `booking_number`, `service1_name`, `staff_member`, " \
                "`additional_email`, `slot_numbers`, `slot_clock_time`, `booker_name`, `appointment_date`, `staff_member2`, `staff_email`, " \
                "`staff2_email`, `day_of_week`, `service2_name`,business_name, booker_comments, price1, price2, booking_date) " \
                "VALUES ( %s,  %s,  %s,  %s,  %s,       %s,  %s,  %s,  %s,  %s,        %s,  %s,  %s,  %s,  %s,    %s, %s, %s, %s, %s) "
        
        print(query)
        values = (
            businessId, bookerEmail, bookingNumber, service1Name, staffMember1Name, additionalEmail, serviceSlotsRange,
            serviceClockTimeRange, bookerName, appointmentDateStr, staffMember2Name, staffEmail1, staffEmail2, dayOfWeek,
            service2Name, businessName, bookerComment, price1, price2, bookingDate)
    
        cursor.execute(query, values)
        print('service2Name=',service2Name)
        print(values)
        bookingsDB.commit()
        bookingsDB.close()



    def createLeaveRecord(self, businessId, staffUserId, leaveNumber, startDate, startTime, endDate, endTime, ifFullDayLeave, parentLeaveNumber):

        print('in db, createLeaveRecord ')
        print(startDate)
        print(startTime)
        print(endDate)
        print(endTime)
        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()
        startDateStr =None
        if (startDate!=None):
            startDateStr = startDate.strftime(config.applicationDBDateFormat)
        endDateStr=None
        if(endDate!=None):
            endDateStr = endDate.strftime(config.applicationDBDateFormat)

        query = "insert into leave_records (business_id, staff_user_id, leave_number, start_date, start_time, end_date, end_time, if_fullday_leave, " \
                "parent_leave_number, status) " \
                "values (%s, %s, %s, %s, %s,    %s, %s, %s, %s,'NEW' ) "
        print(query)
        values = (businessId, staffUserId, leaveNumber, startDateStr, startTime, endDateStr, endTime, ifFullDayLeave, parentLeaveNumber)
        print(values)

        cursor.execute(query, values)
        bookingsDB.commit()
        bookingsDB.close()


    # def getStaffIds(self, businessId):
    #
    #     bookingsDB = Connection().getConnection()
    #     cursor = bookingsDB.cursor()
    #     #         print('cursor')
    #
    #     query = "select staff_user_id from users3 u, business_staff s where u.email=s.email and s.business_id=%s"
    #     print(query)
    #     values = (businessId,)
    #     cursor.execute(query, values)
    #     rows = cursor.fetchall()
    #     result = []
    #     for row in rows:
    #         result.append(row[0])
    #     bookingsDB.close()
    #     return result



    def getBusinessServices(self, businessId, storageType):

        bookingsDB = ''
        if (storageType=='A'):
            bookingsDB =Connection().getConnection()
        elif (storageType=='U'):
            bookingsDB = Connection().getUnapprovedConnection()
        cursor = bookingsDB.cursor()

        query = "select business_id, name, num_of_subslots, if_double_time, price, currency, if_ticket_based, " \
                "total_ticket_count, max_tickets_sold_per_booking, category_name, top_category_name, duration, description " \
                "from business_services where business_id=%s"

        print(query)
        values = (businessId,)
        cursor.execute(query, values)
        rows = cursor.fetchall()
        businessServices = []
        for row in rows:
            businessService = BusinessService(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8],
                                              row[9], row[10], row[11], row[12])
            businessServices.append(businessService)

        bookingsDB.close()
        return businessServices



    def getStaffBookings(self, staffUserId, startDate, endDate):

        bookingsDB =Connection().getConnection()
        cursor = bookingsDB.cursor()

        query = "select b.appointment_date, b.service1_name, b.service2_name, b.slot_clock_time, b.booker_name, b.booker_comments,b.booking_number, b.status "\
                "from current_bookings b, users3 u "\
                "where (b.staff_email=u.email_id or b.staff2_email=u.email_id ) "\
                "and appointment_date >= %s and appointment_date <= %s "\
                "and u.user_id= %s "\
                "order by appointment_date, slot_clock_time "

        print(query)
        values = (startDate.strftime(config.applicationDBDateFormat), endDate.strftime(config.applicationDBDateFormat), staffUserId)
        cursor.execute(query, values)
        rows = cursor.fetchall()
        bookingsDB.close()
        return rows



    def getBusinessBookings(self, businessId, startDate, endDate, staffEmail, serviceName):

        bookingsDB =Connection().getConnection()
        cursor = bookingsDB.cursor()

        # query = "select appointment_date, service1_name, service2_name, slot_clock_time, booker_name, booker_comments, " \
        #         "staff_member, staff_member2, booking_number, staff_email, staff2_email, status " \
        #         ", price price1 " \
        #         ",(select price from business_services where business_id = current_bookings.business_id and name = current_bookings.service2_name) price2 " \
        #         "from current_bookings   " \
        #         "join business_services " \
        #         "on current_bookings.business_id = business_services.business_id and current_bookings.service1_name = business_services.name " \
        #         "where current_bookings.business_id= %s " \
        #         "and appointment_date >= %s and appointment_date <= %s "
        query = "select appointment_date, service1_name, service2_name, slot_clock_time, booker_name, booker_comments, " \
                "staff_member, staff_member2, booking_number, staff_email, staff2_email, status " \
                ", price1, price2 " \
                "from current_bookings   " \
                "join business_services " \
                "on current_bookings.business_id = business_services.business_id and current_bookings.service1_name = business_services.name " \
                "where current_bookings.business_id= %s " \
                "and appointment_date >= %s and appointment_date <= %s "
        valuesList = [businessId, startDate.strftime(config.applicationDBDateFormat), endDate.strftime(config.applicationDBDateFormat)]
        if (staffEmail !=None):
            query=query+ " and ( staff_email= %s or staff2_email=%s) "
            valuesList.append(staffEmail)
            valuesList.append(staffEmail)
        if (serviceName != None):
            query = query + " and ( service1_name= %s or service2_name=%s) "
            valuesList.append(serviceName)
            valuesList.append(serviceName)

        query=query+"order by appointment_date, slot_clock_time "
        print(query)

        cursor.execute(query, tuple(valuesList))
        rows = cursor.fetchall()
        bookingsDB.close()
        return rows



    def getServicesOfCategory(self, searchCategory):
        
       # if (storageType=='A'):
            bookingsDB = Connection().getConnection()
            cursor = bookingsDB.cursor()
            # query = "select business_id, name, price, num_of_subslots, if_ticket_based, description from  business_services where category_name=%s"
            #query = "select business_id, name, price, duration, if_ticket_based, description from  business_services where category_name=%s"
            query = "select bus.business_id, serv.name, price, duration, if_ticket_based, description  from  business_services serv "\
            " join business bus on serv.business_id = bus.business_id and bus.status = 'APPROVED' where category_name=%s"\
            "order by bus.name"

            print(query)
            values = (searchCategory,)
            cursor.execute(query, values)
            rows = cursor.fetchall()
            bookingsDB.close()
            return rows



    def getBusinessesInLocation(self, city, suburb):

        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()

        if ( city!=None and suburb !=None):
            query = "select b.business_id, name from  business_address ad, business b where city=%s and " \
                    " city_location=%s and b.business_id=ad.business_id"
            print(query)
            values = (city, suburb)

        if (city==None and suburb !=None):
            query = "select b.business_id, name from  business_address ad, business b where city_location=%s and b.business_id=ad.business_id"
            print(query)
            values = (suburb,)

        cursor.execute(query, values)
        rows = cursor.fetchall()
        bookingsDB.close()
        return rows



    def getLocations(self, size):

        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()
        if(size==None):
            query = "select city, city_location from  locations"
            print(query)
            cursor.execute(query)
        else:
            query = "select  city, city_location from  locations limit %s"
            print(query)
            values = (size,)
            cursor.execute(query,values)

        rows = cursor.fetchall()
        bookingsDB.close()
        return rows



    def bookTicket(self, bookerName, bookerEmail, businessId, serviceName, countOfTicketsToBook, bookingNumber, eventDate, slotStartTime, slotStartNumber, status,businessName):
        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()
        eventDateStr=eventDate.strftime(config.applicationDBDateFormat)

        query = "INSERT INTO `ticket_bookings` (`business_id`, `service_name`, `count_of_tickets_booked`, `booker_email`, `booker_name`, " \
                "`booking_number`, `event_date`, `clock_start_time`, `slot_start_number`, status, business_name) " \
                "VALUES (%s, %s, %s, %s, %s,     %s, %s, %s, %s, %s       ,%s)"
        print(query)
        values = (businessId, serviceName, countOfTicketsToBook, bookerEmail, bookerName, bookingNumber, eventDateStr, slotStartTime, slotStartNumber, status,businessName)
        print(values)

        cursor.execute(query, values)
        bookingsDB.commit()
        bookingsDB.close()



    def addOneDayTicketAvailability(self, businessId, serviceName, countAvailable, eventDate, slotNumbers):

        print('slotNumbers = ',slotNumbers)
        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()
        eventDateStr=eventDate.strftime(config.applicationDBDateFormat)
        query = "INSERT INTO `tickets_availability` ( `business_id`, `service_name`, `count_available`, `slot_start_number`, `event_date`) " \
                "VALUES (%s, %s, %s, %s, %s)"
        print(query)

        allvalues=[]
        for slotNumber in slotNumbers:
            values = (businessId, serviceName, countAvailable, slotNumber, eventDateStr)
            allvalues.append(values)

        cursor.executemany(query, allvalues)
        bookingsDB.commit()
        bookingsDB.close()


    def setStatus(self, businessId, status, storageType='A'):
        bookingsDB = ''
        if storageType == 'A':
            bookingsDB = Connection().getConnection()
        elif storageType == 'U':
            bookingsDB = Connection().getUnapprovedConnection()
        cursor = bookingsDB.cursor()
        query = "Update `business` set `status` = %s where business_id=%s"
        print(query)
        values = (status, businessId)
        cursor.execute(query, values)

        bookingsDB.commit()
        bookingsDB.close()



    def updateTicketBookingStatus(self, businessId, bookingNumber, status, cancelReason=None):

        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()
        query = "Update `ticket_bookings` set `status` = %s, cancel_reason=%s where business_id=%s and booking_number=%s"
        print(query)
        values = (status, cancelReason, businessId, bookingNumber )
        cursor.execute(query, values)

        bookingsDB.commit()
        bookingsDB.close()



    def updateTicketAvailability(self, businessId, serviceName, countOfTicketsToBook, eventDate, slotStartNumber):

        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()
        eventDateStr=eventDate.strftime(config.applicationDBDateFormat)
        if(slotStartNumber !=None):
            query = "Update `tickets_availability` set `count_available` = (`count_available` - %s) where `business_id` =  %s and `service_name` = %s and event_date=%s and `slot_start_number` =%s"
            print(query)
            values = (countOfTicketsToBook, businessId, serviceName, eventDateStr, slotStartNumber)
            cursor.execute(query, values)
        else:
            query = "Update `tickets_availability` set `count_available` = (`count_available` - %s) where `business_id` =  %s and `service_name` = %s and event_date=%s"
            print(query)
            values = (countOfTicketsToBook, businessId, serviceName, eventDateStr)
            cursor.execute(query, values)

        bookingsDB.commit()
        bookingsDB.close()




    def getTicketBookingDetails(self, businessId, bookingNumber=None):

        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()
        if (bookingNumber!=None):
            print('in if')
            query = "select `business_id`, `service_name`, `count_of_tickets_booked`, `booker_email`, `booker_name`, `booking_number`, " \
                    "`event_date`, `clock_start_time`, `slot_start_number`, status,business_name " \
                    "from `ticket_bookings` " \
                    "where business_id=%s and booking_number=%s "
            values = (businessId, bookingNumber)
        else:
            print('in else')
            query = "select `business_id`, `service_name`, `count_of_tickets_booked`, `booker_email`, `booker_name`, `booking_number`, " \
                    "`event_date`, `clock_start_time`, `slot_start_number`, status,business_name " \
                    "from `ticket_bookings` " \
                    "where business_id=%s "
            values = (businessId,)
        print(query)
        print(values)
        cursor.execute(query,values)

        rows = cursor.fetchall()
        bookingsDB.close()
        return rows



    def getTicketAvailabilityOnADay(self, businessId, availabilityDate, serviceName):

        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()
        availabilityDateStr=availabilityDate.strftime(config.applicationDBDateFormat)
        query = "select business_id, service_name, event_date, slot_start_number, count_available " \
                "from tickets_availability " \
                "where business_id=%s and event_date=%s and service_name=%s"
        print(query)
        values = (businessId, availabilityDateStr, serviceName)
        cursor.execute(query,values)

        rows = cursor.fetchall()
        bookingsDB.close()
        return rows



    def addServiceCategory(self, name) :

        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()
        query = "insert into service_categories (category_name) values (%s)"
        print(query)
        values = (name,)
        cursor.execute(query, values)
        bookingsDB.commit()
        bookingsDB.close()



    def getServiceCategories(self, size):

        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()
        if(size==None):
            query = "select category_name from  service_categories"
            print(query)
            cursor.execute(query)
        else:
            query = "select category_name from  service_categories limit %s"
            print(query)
            values = (size,)
            cursor.execute(query,values)

        rows = cursor.fetchall()
        serviceCategories=[]
        for row in rows:
            serviceCategories.append(row[0])
        bookingsDB.close()
        return serviceCategories



    # def getAnotherMostAvailableStaffMember (self, businessId, staffUserId,  dateOfDay):
    #
    #     bookingsDB = Connection().getConnection()
    #     cursor = bookingsDB.cursor()
    #     query = "select un.staff_user_id,  count(*) as unavailable_count  " \
    #             "from staff_unavailable_slots  un  " \
    #             "where un.business_id=%s and un.staff_user_id <> %s and un.slot_date=%s  " \
    #             "group by un.staff_user_id ORDER BY COUNT(*)"
    #     print(query)
    #     values = (businessId,staffUserId,dateOfDay)
    #
    #     cursor.execute(query, values)
    #     rows = cursor.fetchall()
    #     freeMembers=[]
    #     for row in rows:
    #         freeMembers.append(row[0])
    #     bookingsDB.close()
    #     return freeMembers


    # def getSlotRange(self, businessId):
    #
    #     bookingsDB = Connection().getConnection()
    #     cursor = bookingsDB.cursor()
    #     query = "select min(slot_number), max(slot_number) from business_hours_and_slots_setup where business_id=%s and is_business_opened='Y'"
    #     print(query)
    #     values = (businessId,)
    #
    #     cursor.execute(query, values)
    #     row = cursor.fetchone()
    #     bookingsDB.close()
    #     return row


    def getMaxLeaveId(self):

        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()
        query = "select max(id) from leave_records"
        print(query)
        cursor.execute(query)
        rows = cursor.fetchall()
        bookingsDB.close()
        if (rows==None or rows[0]==None or rows[0][0]==None):
            return 1000
        return (rows[0][0] + 1)



    def getMaxBookingId(self):

        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()
        query = "select max(id) from current_bookings"
        print(query)
        cursor.execute(query)
        rows = cursor.fetchall()
        bookingsDB.close()
        if (rows==None or rows[0]==None or rows[0][0]==None):
            return 1000
        return (rows[0][0] + 1)



    def getTicketBookingId(self):

        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()
        query = "select max(id) from ticket_bookings"
        print(query)
        cursor.execute(query)
        rows = cursor.fetchall()
        bookingsDB.close()
        if (rows==None or rows[0]==None or rows[0][0]==None):
            return 1000
        return (rows[0][0] + 1)



    def cleanUnapprovedBusinessData(self, businessId):

        print('in clean up method')
        bookingsDB = Connection().getUnapprovedConnection()
        delCursor = bookingsDB.cursor()
        deleteMainBusinessFieldsQuery='delete from business where business_id=%s'
        deleteBusinessAddressQuery = 'delete from business_address where business_id=%s'
        deleteBusinessExtraInfoQuery = 'delete from business_extra_info where business_id=%s'
        deleteBusinessSettingsQuery = 'delete from business_settings where business_id=%s'
        deleteBusinessServicesQuery = 'delete from business_services where business_id=%s'
        deleteBusinessStaffQuery = 'delete from business_staff where business_id=%s'
        # deleteHolidaysQuery = 'delete from holidays where business_id=%s'
        deleteBusinesssHoursQuery = 'delete from business_hours where business_id=%s'

        delValues=(businessId,)
        delCursor.execute(deleteMainBusinessFieldsQuery, delValues)
        delCursor.execute(deleteBusinessAddressQuery, delValues)
        delCursor.execute(deleteBusinessExtraInfoQuery, delValues)
        delCursor.execute(deleteBusinessSettingsQuery, delValues)
        delCursor.execute(deleteBusinessServicesQuery, delValues)
        delCursor.execute(deleteBusinessStaffQuery, delValues)
        # delCursor.execute(deleteHolidaysQuery, delValues)
        delCursor.execute(deleteBusinesssHoursQuery, delValues)
        bookingsDB.commit()
        bookingsDB.close()

    def cloneApprovedBusinessData(self, businessId):
        
        print('in clone method')
        Business = self.getBusiness(businessId, 'A')
        self.addBusiness(Business, 'U')
        self.setStatus(businessId, 'EDITED', 'U')
        # bookingsDB = Connection().getUnapprovedConnection()
        # targetCursor = bookingsDB.cursor()
        # approvedbookingsDB = Connection().getApprovedConnection()
        # sourceCursor = approvedbookingsDB.cursor()
        # mainBusinessFieldsQuery='select * from business where business_id=%s'
        # businessAddressQuery = 'select * from business_address where business_id=%s'
        # businessExtraInfoQuery = 'select * from business_extra_info where business_id=%s'
        # businessSettingsQuery = 'select * from business_settings where business_id=%s'
        # businessServicesQuery = 'select * from business_services where business_id=%s'
        # businessStaffQuery = 'select * from business_staff where business_id=%s'
        # # deleteHolidaysQuery = 'delete from holidays where business_id=%s'
        # businesssHoursQuery = 'select * from business_hours where business_id=%s'

        # values=(businessId,)
        # rows = targetCursor.execute(mainBusinessFieldsQuery, values)

        # targetCursor.execute(businessAddressQuery, values)
        # targetCursor.execute(businessExtraInfoQuery, values)
        # targetCursor.execute(businessSettingsQuery, values)
        # targetCursor.execute(businessServicesQuery, values)
        # targetCursor.execute(businessStaffQuery, values)
        # # delCursor.execute(deleteHolidaysQuery, values)
        # targetCursor.execute(businesssHoursQuery, values)


        # bookingsDB.commit()
        # bookingsDB.close()

    def deleteBusinessServiceCategory(self, serviceCategoryName):

        print('in deleteBusinessServiceCategory, delete cat=',serviceCategoryName)
        bookingsDB = Connection().getConnection()

        delCursor = bookingsDB.cursor()
        query = 'delete from service_categories where category_name=%s'
        values=(serviceCategoryName,)
        delCursor.execute(query, values)
        bookingsDB.commit()
        bookingsDB.close()



    def deleteBusinessService(self, businessId, serviceName,storageType):

        bookingsDB = ''
        if (storageType == 'A'):
            bookingsDB = Connection().getConnection()
        elif (storageType == 'U'):
            bookingsDB = Connection().getUnapprovedConnection()

        delCursor = bookingsDB.cursor()
        deleteBusinessServicesQuery = 'delete from business_services where business_id=%s and name=%s'

        delValues=(businessId,serviceName)
        delCursor.execute(deleteBusinessServicesQuery, delValues)
        bookingsDB.commit()
        bookingsDB.close()



    def deleteBusinessStaffMember(self, businessId, staffUserId, storageType):

        bookingsDB = ''
        if (storageType == 'A'):
            bookingsDB = Connection().getConnection()
        elif (storageType == 'U'):
            bookingsDB = Connection().getUnapprovedConnection()

        delCursor = bookingsDB.cursor()
        deleteBusinessStaffQuery = 'delete from business_staff where business_id=%s and user_id=%s'

        delValues=(businessId, staffUserId)
        delCursor.execute(deleteBusinessStaffQuery, delValues)
        bookingsDB.commit()
        bookingsDB.close()



    def getSlotsByBookingNumber(self, bookingNumber, staffUserId):

        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()

        query = "select slot_number " \
                "from staff_slots_availability_status sa  " \
                "where sa.staff_user_id =%s " \
                "and sa.booking_number=%s "

        print(query)
        values=(staffUserId, bookingNumber)
        print(values)

        cursor.execute(query, values)

        rows = cursor.fetchall()
        slots=[]
        for row in rows:
            slots.append(row[0])
        # print(slots)
        bookingsDB.close()
        return slots



    def getAvailabilityOfSkilledStaff (self, businessId, service1, service2, slotDate, startDate, endDate, slotRange):

        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()
        startDateStr=None
        endDateStr=None
        if (startDate!=None):
            startDateStr = startDate.strftime(config.applicationDBDateFormat)
            endDateStr = endDate.strftime(config.applicationDBDateFormat)

        query = "select distinct slot_number " \
                "from staff_slots_availability_status sa, business_staff st " \
                "where st.user_id =sa.staff_user_id "

        queryFilter = "and  sa.slot_status='Y' "
        valuesList=[]
        queryFilter= queryFilter+"and  st.business_id=%s "
        valuesList.append(businessId)

        if (service2==None):
            queryFilter = queryFilter + "and st.service_skills like %s "
            valuesList.append('%'+service1+'%')
        else:
            queryFilter = queryFilter + "and st.service_skills like %s and st.service_skills like %s "
            valuesList.append('%' + service1 + '%')
            valuesList.append('%' + service2 + '%')

        if(startDate!=None):
            queryFilter = queryFilter +"and sa.slot_date between %s and %s and sa.slot_number between %s and %s "
            valuesList.append(startDateStr)
            valuesList.append(endDateStr)
            valuesList.append(slotRange["startSlotNumber"])
            valuesList.append(slotRange["endSlotNumber"])

        if (slotDate!=None):
            if(slotRange!=None):
                queryFilter = queryFilter +"and sa.slot_date = %s and sa.slot_number between %s and %s "
                valuesList.append(slotDate)
                valuesList.append(slotRange["startSlotNumber"])
                valuesList.append(slotRange["endSlotNumber"])
            else:
                queryFilter = queryFilter + "and sa.slot_date=%s "
                valuesList.append(slotDate)

        orderByClause=" order by st.user_id "
        query=query + queryFilter + orderByClause
        values=tuple(valuesList)
        print(query)
        print(values)

        cursor.execute(query, values)


        rows = cursor.fetchall()
        freeSlots=[]
        for row in rows:
            freeSlots.append(row[0])
        # print(freeSlots)
        bookingsDB.close()
        return freeSlots


        # need to write a different implementation to finding the available staff members for booking. It will use the below query.
        # Then it will find the users by eliminating the booked users from the list of available.
        #
        # select st.user_id, sa.slot_status, count(*)
        # from bookings.staff_slots_availability_status sa, bookings.business_staff st
        # where st.user_id =sa.staff_user_id
        # and st.business_id=34
        # and sa.slot_date='2020-05-23'
        # and slot_number between 56 and 57
        # and st.service_skills like '%Boys Haircut%'
        # and st.service_skills like '%Mens Haircut%'
        # and st.user_id !=1004
        # group by st.user_id, sa.slot_status
        # ;
        #
        # Elimination booked users will invlove logic like below.
        #
        # queryResult = [('1001', 'Y', 2), ('1002', 'B', 2), ('1002', 'Y', 4), ('1003', 'Y', 2), ('1004', 'Y', 2)]
        # sequence =queryResult
        # bookedUsers = [number[0] for number in sequence if (number[1] != 'Y')]
        # availableUsers = [number[0] for number in sequence if number[1] == 'Y']
        # return list(set(availableUsers) - set(bookedUsers))
    def getStaffMembersForBookingNew2(self, businessId, service1, service2, slotDate, slotRange, excludeUserId):

        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()
        slotDateStr=slotDate.strftime(config.applicationDBDateFormat)
        query="select st.user_id, sa.slot_status, count(*) " \
              "from staff_slots_availability_status sa, business_staff st " \
              "where st.user_id =sa.staff_user_id "

        # queryFilter="and sa.slot_status = 'Y' "

        valuesList=[]
        queryFilter="and st.business_id=%s "
        valuesList.append(businessId)
        queryFilter=queryFilter+ "and sa.slot_date=%s "
        valuesList.append(slotDateStr)
        queryFilter=queryFilter+  "and slot_number between %s and %s "
        valuesList.append(slotRange["startSlotNumber"])
        valuesList.append(slotRange["endSlotNumber"])
        queryFilter=queryFilter+ "and (st.service_skills like %s "
        valuesList.append('%'+service1+'%')
        if (service2 != None):
            # queryFilter = queryFilter + "and st.service_skills like %s "
            queryFilter = queryFilter + "or st.service_skills like %s "
            valuesList.append('%' + service2 + '%')
        queryFilter = queryFilter + ") "

        if(excludeUserId != None):
            queryFilter=queryFilter+"and st.user_id !=%s "
            valuesList.append(excludeUserId)
        groupBy="group by st.user_id, sa.slot_status "
        query = query + queryFilter+groupBy
        values = tuple(valuesList)
        print(query)
        print(values)

        cursor.execute(query, values)
        rows = cursor.fetchall()
        print(rows)
        bookingsDB.close()
        return rows



    # def getStaffMembersForBooking(self, businessId, service1, service2, slotDate, slotRange, excludeUserId):
    #
    #     bookingsDB = Connection().getConnection()
    #     cursor = bookingsDB.cursor()
    #
    #     query="select distinct st.user_id, count(*) " \
    #           "from staff_slots_availability_status sa, business_staff st " \
    #           "where st.user_id =sa.staff_user_id "
    #
    #     queryFilter="and sa.slot_status = 'Y' "
    #
    #     valuesList=[]
    #     queryFilter=queryFilter+"and st.business_id=%s "
    #     valuesList.append(businessId)
    #     queryFilter=queryFilter+ "and sa.slot_date=%s "
    #     valuesList.append(slotDate)
    #     queryFilter=queryFilter+  "and slot_number between %s and %s "
    #     valuesList.append(slotRange["startSlotNumber"])
    #     valuesList.append(slotRange["endSlotNumber"])
    #     queryFilter=queryFilter+ "and st.service_skills like %s "
    #     valuesList.append('%'+service1+'%')
    #     if (service2 != None):
    #         queryFilter = queryFilter + "and st.service_skills like %s "
    #         valuesList.append('%' + service2 + '%')
    #     if(excludeUserId != None):
    #         queryFilter=queryFilter+"and st.user_id !=%s "
    #         valuesList.append(excludeUserId)
    #     groupBy="group by st.user_id ";
    #     query = query + queryFilter+groupBy
    #     values = tuple(valuesList)
    #     print(query)
    #     print(values)
    #
    #     cursor.execute(query, values)
    #     rows = cursor.fetchall()
    #     print(rows)
    #     bookingsDB.close()
    #     return rows



    def rankStaffMembersByAvailabilityOnADay(self, businessId, slotDate, staffUserIds):

        print('user in rank Staff =',staffUserIds)
        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()
        slotDateStr=slotDate.strftime(config.applicationDBDateFormat)
        query="select sa.staff_user_id, count(*) " \
              "from staff_slots_availability_status sa " \

        queryFilter="where sa.slot_status = 'Y' "

        valuesList=[]
        queryFilter=queryFilter+"and sa.business_id=%s "
        valuesList.append(businessId)
        queryFilter=queryFilter+ "and sa.slot_date=%s "
        valuesList.append(slotDateStr)

        inClause='and sa.staff_user_id in ( %s '
        for i in range (0, len(staffUserIds) -1):
            inClause = inClause + ', %s'
            valuesList.append(staffUserIds[i])
        if (len(staffUserIds) != 0):
            valuesList.append(staffUserIds[len(staffUserIds)-1])
        else:
            valuesList.append(0)
        inClause=inClause+" ) "
        print('inClause=   ',inClause)
        queryFilter=queryFilter+inClause
        groupBy= "group by sa.staff_user_id "
        orderBy="order by count(*) desc "

        query = query + queryFilter+groupBy+orderBy
        print('new query   ',query)
        values = tuple(valuesList)
        print(valuesList)
        print(query)
        print(values)

        cursor.execute(query, values)
        rows = cursor.fetchall()
        print(rows)
        bookingsDB.close()
        return rows



    # def rankStaffMembersByAvailabilityOnADayInSlotRange(self, businessId, slotDate, staffUserIds, slotRange):
    #
    #     print('user in rank Staff =',staffUserIds)
    #     bookingsDB = Connection().getConnection()
    #     cursor = bookingsDB.cursor()
    #
    #     query="select sa.staff_user_id, count(*) " \
    #           "from staff_slots_availability_status sa " \
    #
    #     queryFilter="where sa.slot_status = 'Y' "
    #
    #     valuesList=[]
    #     queryFilter=queryFilter+"and sa.business_id=%s "
    #     valuesList.append(businessId)
    #
    #     queryFilter=queryFilter+  "and slot_number between %s and %s "
    #     valuesList.append(slotRange["startSlotNumber"])
    #     valuesList.append(slotRange["endSlotNumber"])
    #
    #     queryFilter=queryFilter+ "and sa.slot_date=%s "
    #     valuesList.append(slotDate)
    #
    #     inClause='and sa.staff_user_id in ( %s '
    #     for i in range (0, len(staffUserIds) -1):
    #         inClause = inClause + ', %s'
    #         valuesList.append(staffUserIds[i])
    #     valuesList.append(staffUserIds[len(staffUserIds)-1])
    #     inClause=inClause+" ) "
    #     print('inClause=   ',inClause)
    #     queryFilter=queryFilter+inClause
    #     groupBy= "group by sa.staff_user_id "
    #     orderBy="order by count(*) desc "
    #
    #     query = query + queryFilter+groupBy+orderBy
    #     print('new query   ',query)
    #     values = tuple(valuesList)
    #     print(valuesList)
    #     print(query)
    #     print(values)
    #
    #     cursor.execute(query, values)
    #     rows = cursor.fetchall()
    #     print(rows)
    #     bookingsDB.close()
    #     return rows



    def getAvailabilityOfStaff (self, businessId, userIdOfStaff, slotDate, startDate, endDate, slotRange):
        print('businessId:{}, userIdOfStaff:{}, slotDate:{}, startDate:{}, endDate:{}, slotRange:{}'.format(businessId, userIdOfStaff, slotDate, startDate, endDate, slotRange))

        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()

        query = "select distinct sa.slot_number " \
                "from staff_slots_availability_status sa " \
                "where sa.staff_user_id=%s "

        valuesList = []
        valuesList.append(userIdOfStaff)
        queryFilter="and sa.slot_status='Y' "
        queryFilter=queryFilter+"and sa.business_id=%s "
        valuesList.append(businessId)

        if(startDate!=None):
            startDateStr=startDate.strftime(config.applicationDBDateFormat)
            endDateStr=endDate.strftime(config.applicationDBDateFormat)
            queryFilter = queryFilter +"and sa.slot_date between %s and %s and sa.slot_number between %s and %s "
            valuesList.append(startDateStr)
            valuesList.append(endDateStr)
            valuesList.append(slotRange["startSlotNumber"])
            valuesList.append(slotRange["endSlotNumber"])

        if (slotDate!=None):
            if(slotRange!=None):
                queryFilter = queryFilter +"and sa.slot_date = %s and sa.slot_number between %s and %s "
                valuesList.append(slotDate.strftime(config.applicationDBDateFormat))
                valuesList.append(slotRange["startSlotNumber"])
                valuesList.append(slotRange["endSlotNumber"])
            else:
                print('slotdate is not null, slot range is null')
                queryFilter = queryFilter + "and sa.slot_date=%s "
                valuesList.append(slotDate.strftime(config.applicationDBDateFormat))

        # orderByClause=" order by sa.staff_user_id "
        # query=query + queryFilter + orderByClause
        query=query + queryFilter
        values=tuple(valuesList)

        print(query)
        print(values)

        cursor.execute(query, values)
        rows = cursor.fetchall()
        freeSlots=[]
        print('rows follow')
        # print(*rows,sep='\n')
        for row in rows:
            freeSlots.append(row[0])
        # print('rows completed')
        print(freeSlots)
        bookingsDB.close()
        return freeSlots

    
    def getBookedDatesAndSlots(self, businessId, date, userId):
        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()

        query = "SELECT staff_user_id, slot_date, slot_number from staff_slots_availability_status " \
                " where business_id = %s and staff_user_id = %s and slot_status = 'B' and slot_date = %s"
        print(query)

        values = (businessId, userId, date)
        cursor.execute(query, values)

        rows = cursor.fetchall()
        bookingsDB.close()
        return rows

    def removeAllAvailableSlots(self, businessId, date):
        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()

        query = "delete from staff_slots_availability_status " \
                " where business_id = %s and slot_status = %s and slot_date > %s"
        print(query)

        values = (businessId, 'Y', date.strftime(config.applicationDBDateFormat))
        cursor.execute(query, values)
        bookingsDB.commit()
        bookingsDB.close()



    def addOneDayAvailabilityForUser(self, businessId, staffUserId, dateOfDay, slotNumbers):

        # print('slotNumbers = ', slotNumbers)
        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()

        query = "INSERT INTO `staff_slots_availability_status` ( `business_id`, `staff_user_id`, `slot_status`, `slot_number`, `slot_date`) " \
                "VALUES (%s, %s, %s, %s, %s) " \
                "on duplicate key update `business_id`=%s  ,  `staff_user_id`=%s ,  `slot_status`=%s,  `slot_number` =%s,  `slot_date`=%s "
        print(query)

        allvalues = []
        for slotNumber in slotNumbers:
            values = (businessId, staffUserId, 'Y', slotNumber, dateOfDay.strftime(config.applicationDBDateFormat), 
                        businessId, staffUserId, 'Y', slotNumber, dateOfDay.strftime(config.applicationDBDateFormat))
            # allvalues.append(values)
            cursor.execute(query, values)

        # cursor.executemany(query, allvalues)
        bookingsDB.commit()
        bookingsDB.close()



    def updateLeavesRecordsStatus(self, businessId, status, parentLeaveNumber, leaveNumber=None):

        bookingsDB =Connection().getConnection()
        cursor = bookingsDB.cursor()

        query = "update leave_records set status=%s where business_id=%s and parent_leave_number=%s "
        valuesList=[status, businessId, parentLeaveNumber ]
        if (leaveNumber!=None):
            query =query +  " and leave_number=%s "
            valuesList.append(leaveNumber)
        print(query)

        cursor.execute(query, tuple(valuesList))

        bookingsDB.commit()
        bookingsDB.close()



    def updateBookingStatus(self, businessId, bookingNumber, status, cancellationOrNoShowTime, cancelReason=None):

        bookingsDB =Connection().getConnection()
        cursor = bookingsDB.cursor()
        query = ''

        if (status == 'NOSHOW'):
            query="update current_bookings set status= %s, cancel_reason=%s, noshow_marked_on=%s where business_id=%s and booking_number=%s "
        else:
            query="update current_bookings set status= %s, cancel_reason=%s, cancellation_date=%s where business_id=%s and booking_number=%s "
        print(query)

        values = (status,cancelReason, cancellationOrNoShowTime, businessId,bookingNumber)

        cursor.execute(query, values)

        bookingsDB.commit()
        bookingsDB.close()



    def getBookingDetails(self, businessId, bookingNumber):

        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()

        query = "select business_id, booker_email, booking_number, service1_name, staff_member, additional_email, slot_numbers, " \
                "booker_name, appointment_date, staff_member2, staff_email, staff2_email, service2_name, business_name, slot_clock_time, slot_numbers " \
                "from current_bookings " \
                "where business_id=%s and booking_number=%s"

        values=(businessId, bookingNumber)
        print(query)
        print(values)

        cursor.execute(query, values)
        rows = cursor.fetchall()
        bookingsDB.close()
        if (rows!=None and len(rows)!=0):
            return rows[0]
        else:
            return None



    def getLeavesRecords(self, businessId, parentLeaveNumber=None, leaveNumber=None):

        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()

        query = "select business_id, staff_user_id, leave_number, start_date, start_time, end_date, end_time, if_fullday_leave, " \
                "parent_leave_number, status " \
                "from leave_records " \
                "where  business_id=%s "
        valuesList = [businessId]
        if (parentLeaveNumber!=None):
            query=query+' and parent_leave_number= %s '
            valuesList.append(parentLeaveNumber)
        if (leaveNumber!=None):
            query=query+' and leave_number= %s '
            valuesList.append(leaveNumber)
        values=tuple(valuesList)
        print(query)
        print(values)

        cursor.execute(query, values)
        rows = cursor.fetchall()
        bookingsDB.close()
        return  rows

    
    def getFutureLeaves(self, businessId):
        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()

        query = "select concat(s.firstname, ' ', s.lastname) Name, concat(l.start_date, ' ', COALESCE(l.start_time, '')) Start, concat(l.end_date, ' ', COALESCE(l.end_time, '')) end, " \
                "l.leave_number ln, l.parent_leave_number pln " \
                "from leave_records as l join business_staff as s on l.business_id = s.business_id and l.staff_user_id = s.user_id " \
                "where l.business_id = %s and DATE(l.end_date) >= CURDATE() and status = 'NEW'"
        valuesList = [businessId]
        
        values=tuple(valuesList)
        print(query)
        print(values)

        cursor.execute(query, values)
        rows = cursor.fetchall()
        bookingsDB.close()
        return  rows



    def getUsersTicketBookingsOnAday(self, email, appointmentDate):

        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()


        query = "select booking_number,  business_id, slot_start_number, business_name, event_date, clock_start_time, service_name " \
                "from bookings.ticket_bookings " \
                "where booker_email=%s and event_date=%s and status='NEW' "

        values=(email, appointmentDate.strftime(config.applicationDBDateFormat)  )
        print(query)
        print(values)

        cursor.execute(query, values)
        rows = cursor.fetchall()

        bookingsDB.close()
        return rows


    def getUsersBookingsOnAday(self, email, appointmentDate):

        bookingsDB = Connection().getConnection()
        cursor = bookingsDB.cursor()
        query = "select booking_number, slot_numbers, business_name, appointment_date, slot_clock_time, service1_name  " \
                "from bookings.current_bookings " \
                "where booker_email=%s and appointment_date=%s  and status='OPEN' "

        values=(email, appointmentDate.strftime(config.applicationDBDateFormat)  )
        print(query)
        print(values)

        cursor.execute(query, values)
        rows = cursor.fetchall()

        bookingsDB.close()
        return rows

    def getAllBusinessBookings(self, fromDate, toDate):

        bookingsDB =Connection().getConnection()
        cursor = bookingsDB.cursor()

        # query = "select appointment_date, service1_name, service2_name, slot_clock_time, booker_name, booker_comments, " \
        #         "staff_member, staff_member2, booking_number, staff_email, staff2_email, status " \
        #         ", price price1 " \
        #         ",(select price from business_services where business_id = current_bookings.business_id and name = current_bookings.service2_name) price2 " \
        #         "from current_bookings   " \
        #         "join business_services " \
        #         "on current_bookings.business_id = business_services.business_id and current_bookings.service1_name = business_services.name " \
        #         "where current_bookings.business_id= %s " \
        #         "and appointment_date >= %s and appointment_date <= %s "
        
        # valuesList = [businessId, startDate.strftime(config.applicationDBDateFormat), endDate.strftime(config.applicationDBDateFormat)]
        # if (staffEmail !=None):
        #     query=query+ " and ( staff_email= %s or staff2_email=%s) "
        #     valuesList.append(staffEmail)
        #     valuesList.append(staffEmail)
        # if (serviceName != None):
        #     query = query + " and ( service1_name= %s or service2_name=%s) "
        #     valuesList.append(serviceName)
        #     valuesList.append(serviceName)

        # query = "select appointment_date, service1_name, service2_name, slot_clock_time, booker_name, booker_comments, " \
        #         "staff_member, staff_member2, booking_number, staff_email, staff2_email, status " \
        #         ", price1, price2 " \
        #         "from current_bookings   "

        query = "select appointment_date, bu.name, service1_name as service, slot_clock_time, booker_email, booker_name, booker_comments, " \
                " staff_member as staff, booking_number, staff_email as email, b.status, price1, cancel_reason, " \
                " booking_date, cancellation_date, noshow_marked_on from current_bookings b " \
                " join business bu on bu.business_id = SUBSTRING_INDEX(b.booking_number, '-', 1) "
        
        if (fromDate != '' and toDate != ''):
            query = query + "where b.appointment_date >= %s and b.appointment_date <= %s "
        query = query + " union " \
                " ( " \
                " select bookings1.appointment_date, bu.name, bookings2.service2_name as service, bookings1.slot_clock_time, bookings1.booker_email, bookings1.booker_name, bookings1.booker_comments, " \
                " IF(isnull(bookings2.staff_member2),bookings1.staff_member,bookings2.staff_member2) as staff, bookings1.booking_number, IF(isnull(bookings2.staff2_email),bookings1.staff_email,bookings2.staff2_email)  as email, bookings1.status, bookings2.price2, bookings1.cancel_reason, " \
                " bookings1.booking_date, bookings1.cancellation_date, bookings1.noshow_marked_on from current_bookings bookings1 " \
                " join current_bookings bookings2 on bookings1.id = bookings2.id and bookings2.service2_name is not null " \
                " join business bu on bu.business_id = SUBSTRING_INDEX(bookings1.booking_number, '-', 1) " \
                # " order by id; "
        
        if (fromDate != '' and toDate != ''):
            query = query + "where bookings1.appointment_date >= %s and bookings1.appointment_date <= %s "
        
        query = query + " ) "

        query=query+" order by appointment_date, slot_clock_time "
        print(query)

        # cursor.execute(query, tuple(valuesList))
        if (fromDate != '' and toDate != ''):
            values = (fromDate, toDate, fromDate, toDate)
            cursor.execute(query, values)
        else:
            cursor.execute(query)
        rows = cursor.fetchall()
        bookingsDB.close()
        return rows
    
    def getAllBusiness(self):

        bookingsDB =Connection().getConnection()
        cursor = bookingsDB.cursor()
        #query = "select business_id, name, owner_fn, owner_ln, owner_email_id, owner_phone, status from business "
        query = "select business.business_id, business.name, business.owner_fn, business.owner_ln, business.owner_email_id, business.owner_phone, business.status, "\
                "business_address.address_line1, business_address.address_line2, business_address.city_location, business_address.city, business_address.postal_code from business "\
                "LEFT JOIN business_address  ON  business.business_id = business_address.business_id "
       
        query=query+"order by business.business_id "
        print(query)

        cursor.execute(query)
        rows = cursor.fetchall()
        bookingsDB.close()
        return rows
    



# businessAddress = BusinessAddress(34,'ad34 1','ad34 2','city area34','city', 'province34')
# DataAccess().addBusinessAddress(businessAddress,'A')

# business = Business('id','fn','ln','email', 'phone', 'business name', 'contavct phone', 'web url','text', 'filepath', '4','','ad 1','ad 2',
#                             'city area','city', 'province')
#
# DataAccess().createBusiness(business)

# DataAccess().login('aaa@nnn.com','password')
# DataAccess().signup('aaa@nnn.com','password')
# DataAccess().changePassword('aaa@nnn.com','password')
# DataAccess().addUser('firstd','lastd', 'aaa@nnnbc.com','MANAGER')
# DataAccess().addService('1','name02', 'SS', '130', 'Rand')
# DataAccess().addService('2','name01', 'SS', '112', 'Rand')


# attrs = vars(DataAccess().getBusinessMainFields('33'))
# attrs = vars(DataAccess().getBusinessAddress('34'))
# attrs = vars(DataAccess().getBusinessExtraInfo('34'))

# attrs = vars(DataAccess().getBusinessSettings('34'))
# print(', '.join("%s: %s" % item for item in attrs.items()))

# alls=DataAccess().getBusinessServices('34')
# alls=DataAccess().getStaff('34')
# print(*alls, sep = "\n")
#

# DataAccess().getBusinessHolidays(34,'A')
# print('python date type=   ',type(datetime.today()))

# print(DataAccess().getLocations(None))


# DataAccess().getBusinessSettings(34, 'A')

# print(DataAccess().getBusinessBookings(34, '2020-01-14', '2020-01-16', None, None))

# print(DataAccess().getLocations(None))


