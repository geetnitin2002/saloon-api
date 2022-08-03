from datetime import timedelta, date, datetime
# from model import BusinessSettings
# from model import Business
# from model import BusinessHours
# from model import BusinessMain
from model import BusinessExtraInfo
from model import Staff
# from model import BusinessAddress
from booking import BookingUtils
from dbAccess import DataAccess
from ticketing import Tickets
from apputils import AppUtils
from apperror import AppError
import config

class BusinessReviewAndSetup:

    def deleteBusinessServiceCategory(self, serviceCategoryName):

        DataAccess().deleteBusinessServiceCategory(serviceCategoryName)
        return True

    def approveBusiness(self, businessId):

        business = DataAccess().getBusiness(businessId, 'U')

        response = {}
        countServices=0
        countStaff=0
        if (business.businessServices!=None):
            countServices= len(business.businessServices)
            print(countServices)
        if (business.staff!=None):
            countStaff= len(business.staff)
            print(countStaff)
        if (countServices==0 and countStaff>=0):
        #     print('0,0')
        #     response["responseType"] = 'errors'
        #     response["errors"] = [{"field": "email", "message": "Atleast one service should be setup"}]
        # elif (countServices==0 and countStaff>0):
            print('0,n')
            response["responseType"] = 'errors'
            response["errors"] = [{"field": "service", "message": "Atleast one service should be setup"}]
            return response
        elif (countServices>0 and countStaff==0 and business.businessServices[0].ifTicketBasedService=='N'):
            print('n,0')
            response["responseType"] = 'errors'
            response["errors"] = [{"field": "staffMember", "message": "Atleast one staff member should be setup"}]
            return response
        elif (DataAccess().ifAnyUnassignedService(businessId, 'U') ):
            print('unassigned service')
            response["responseType"] = 'errors'
            response["errors"] = [{"field": "service", "message": "All services should be assigned to atleast one staff member"}]
            return response
        elif (DataAccess().ifAnyUnskilledStaff(businessId, 'U')):
            response["responseType"] = 'errors'
            response["errors"] = [{"field": "service", "message": "All staff members should have atleast one skill"}]
            return response
        else:
            print('n,n')
            self.saveReviewedBusinessSetup(businessId, business)
            DataAccess().setStatus(businessId, 'APPROVED')
            DataAccess().additionalRoleToOwner(businessId)
            DataAccess().approveAllStaff(businessId);
            response["responseType"] = 'success'
            response["success"] = [{"message": "The business "+business.businessMain.businessName+ " has been approved successfully"}]

        return response




    def saveReviewedBusinessSetup(self, businessId, business):

        if (business.businessMain!=None):
            DataAccess().addBusinessMainFields(business.businessMain,'A')
        if (business.businessExtraInfo!=None):
            DataAccess().addBusinessExtraInfo(business.businessExtraInfo, 'A')
        else:
            extraInfo=BusinessExtraInfo(businessId,None,None,None,config.gSingleTimeslotDuration,None)
            DataAccess().addBusinessExtraInfo(extraInfo, 'A')
        if (business.businessAddress != None):
            DataAccess().addBusinessAddress(business.businessAddress, 'A')
        if (business.businessHours != None):
            DataAccess().addBusinessHours(business.businessHours, 'A')
        if (business.businessSettings != None):
            DataAccess().addBusinessSettings(business.businessSettings,'A')
        if (business.businessServices != None):
            for businessService in business.businessServices:
                DataAccess().addBusinessService(businessService,'A')
                if (businessService.ifTicketBasedService=='Y'):
                    Tickets().addTicketsForNewBusiness(businessId, businessService.name,
                        businessService.totalTicketCount, business.businessSettings.preBookingWindow, business.businessHours,
                        businessService.duration // config.gSingleTimeslotDuration)

        if (business.businessServices != None):
            for staff in business.staff:
                # BusinessSetup().addBusinessStaff(staff,'REVIEWER')
                DataAccess().addStaff(staff,'A')
                print('before adding staff')
                print(staff)
                workingSlotNumbers, workingSlotStartTimes, nonWorkingSlotNumbers, nonWorkingSlotStartTimes=BookingUtils().convertWorkingHoursToStaffSlotSetup(staff.monStartTime,staff.monEndTime)
                print('workingSlotNumbers:{}, workingSlotStartTimes:{}, nonWorkingSlotNumbers:{}, nonWorkingSlotStartTimes:{}'.format(workingSlotNumbers, workingSlotStartTimes, nonWorkingSlotNumbers, nonWorkingSlotStartTimes))
                DataAccess().addStaffSlots(businessId,staff.userId,0,workingSlotNumbers, workingSlotStartTimes,'Y')
                DataAccess().addStaffSlots(businessId, staff.userId, 0,  nonWorkingSlotNumbers, nonWorkingSlotStartTimes, 'N')

                workingSlotNumbers, workingSlotStartTimes, nonWorkingSlotNumbers, nonWorkingSlotStartTimes=BookingUtils().convertWorkingHoursToStaffSlotSetup(staff.tuesStartTime,staff.tuesEndTime)
                DataAccess().addStaffSlots(businessId,staff.userId,1,workingSlotNumbers, workingSlotStartTimes,'Y')
                DataAccess().addStaffSlots(businessId, staff.userId, 1,  nonWorkingSlotNumbers, nonWorkingSlotStartTimes, 'N')

                workingSlotNumbers, workingSlotStartTimes, nonWorkingSlotNumbers, nonWorkingSlotStartTimes=BookingUtils().convertWorkingHoursToStaffSlotSetup(staff.wedStartTime,staff.wedEndTime)
                DataAccess().addStaffSlots(businessId,staff.userId,2,workingSlotNumbers, workingSlotStartTimes,'Y')
                DataAccess().addStaffSlots(businessId, staff.userId, 2, nonWorkingSlotNumbers, nonWorkingSlotStartTimes, 'N')

                workingSlotNumbers, workingSlotStartTimes, nonWorkingSlotNumbers, nonWorkingSlotStartTimes=BookingUtils().convertWorkingHoursToStaffSlotSetup(staff.thursStartTime,staff.thursEndTime)
                DataAccess().addStaffSlots(businessId,staff.userId,3,workingSlotNumbers, workingSlotStartTimes,'Y')
                DataAccess().addStaffSlots(businessId, staff.userId, 3,  nonWorkingSlotNumbers, nonWorkingSlotStartTimes, 'N')

                workingSlotNumbers, workingSlotStartTimes, nonWorkingSlotNumbers, nonWorkingSlotStartTimes=BookingUtils().convertWorkingHoursToStaffSlotSetup(staff.friStartTime,staff.friEndTime)
                DataAccess().addStaffSlots(businessId,staff.userId,4,workingSlotNumbers, workingSlotStartTimes,'Y')
                DataAccess().addStaffSlots(businessId, staff.userId, 4, nonWorkingSlotNumbers, nonWorkingSlotStartTimes, 'N')

                workingSlotNumbers, workingSlotStartTimes, nonWorkingSlotNumbers, nonWorkingSlotStartTimes=BookingUtils().convertWorkingHoursToStaffSlotSetup(staff.satStartTime,staff.satEndTime)
                DataAccess().addStaffSlots(businessId,staff.userId,5,workingSlotNumbers, workingSlotStartTimes,'Y')
                DataAccess().addStaffSlots(businessId, staff.userId, 5,  nonWorkingSlotNumbers, nonWorkingSlotStartTimes, 'N')

                workingSlotNumbers, workingSlotStartTimes, nonWorkingSlotNumbers, nonWorkingSlotStartTimes=BookingUtils().convertWorkingHoursToStaffSlotSetup(staff.sunStartTime,staff.sunEndTime)
                DataAccess().addStaffSlots(businessId,staff.userId, 6, workingSlotNumbers, workingSlotStartTimes,'Y')
                DataAccess().addStaffSlots(businessId, staff.userId, 6,  nonWorkingSlotNumbers, nonWorkingSlotStartTimes, 'N')

        if (business.businessSettings!=None and business.businessSettings.preBookingWindow!=None and business.staff!=None):
            self.addAvailabilityForNewBusiness(businessId,business.businessSettings.preBookingWindow,business.staff)

        # Holidays concept has been repalced by enhanced Leaves concept
        # if (business.holidays!=None):
        #     holidaysDates=[]
        #     for holiday in business.holidays:
        #         holidaysDates.append(holiday[1])
        #
        #     DataAccess().addBusinessHolidays(businessId,holidaysDates, 'A')

            #  Update staff unavailability and ticketing availability tables
            # for holiday in business.holidays:
            #     if (business.staff!=None):
            #         for staff in business.staff:
            #             # BookingUtils().markUnavailability(business.businessMain.businessId,staff.userId,'H',None,None,holiday,'Y')
            #             DataAccess().markUnavailability(businessId,staff.userId,'H',None,None,holiday[1] )
            #             # markUnavailability(self, businessId, userIdOfStaff, slotStatus, minSlotNumber, maxSlotNumber,
            #             #                    actionDate, bookingNumber=None):
            #     if(business.businessSettings!=None):
            #         lastBookingDate= date.today() + timedelta(days=int(business.businessSettings.preBookingWindow))
            #         if(holiday[1] <= lastBookingDate):
            #
            #             if (business.businessServices!=None and business.businessServices[0].ifTicketBasedService=='Y'):
            #                 Tickets().markBusinessUnavailableForOneDay(business.businessServices, holiday[1])

        # Remove the unapproved data from db
        DataAccess().cleanUnapprovedBusinessData(businessId)
        return True



    def addAvailabilityForNewBusiness(self, businessId, bookingWindow, staffMembers):

        print(type(bookingWindow))
        DataAccess().removeAllAvailableSlots(businessId, date.today())
        for day in range(0, int(bookingWindow)+1):
            # Commented the two lines of code and replaced by following line that is more efficient
            # dateOfDay = (date.today() + timedelta(days=day)).isoformat()
            # dayOfWeek = datetime.strptime(dateOfDay, config.applicationUIDateFormat).weekday()
            dateOfDay = date.today() + timedelta(days=day)
            dayOfWeek = dateOfDay.weekday()
            for staffMember in staffMembers:
                oneDaySlots=DataAccess().getStaffSlotsSetup(staffMember.userId, businessId, dayOfWeek)
                bookedSlots = DataAccess().getBookedDatesAndSlots(businessId, dateOfDay, staffMember.userId)
                
                workingSlotNumbers=[]
                for slot in oneDaySlots:
                    if (slot[2]=='Y' and slot not in bookedSlots):
                        workingSlotNumbers.append(slot[0])
                DataAccess().addOneDayAvailabilityForUser(businessId, staffMember.userId, dateOfDay, workingSlotNumbers)



class BusinessSetup:


    # def addBusinessPictures(self, businessId, fileMain, otherFiles):
    #     mainImageName=businessId+_MainImage.jpg
    #     businessId=DataAccess().addMainImageLocation()
    #     DataAccess().signupOwner(businessMain.ownerEmailId, password)
    #     return businessId

    def getBusinessSlotsRange(self, businessId):
        response = DataAccess().getBusinessHours(businessId, 'U')
        if (response != None):
            return response
        else:
            return DataAccess().getBusinessHours(businessId, 'A')


    def addServiceCategory(self, name) :

        response={}
        serviceCategories = DataAccess().getServiceCategories(None)
        print(serviceCategories)
        if (name in serviceCategories):
            response["responseType"] = 'errors'
            response["errors"] = [{"field": "Service Category", "message": "A service with this name already exists"}]
            return response
        DataAccess().addServiceCategory(name)
        serviceCategories.append(name)
        response["responseType"] = "data"
        response["data"] = serviceCategories
        return response

    def changeStatus(self, businessId):

        business = DataAccess().getBusiness(businessId, 'A')

        response = {}
   
        DataAccess().setStatus(businessId, 'NEW')
        response["responseType"] = 'success'
        response["success"] = [{"message": "The business "+business.businessMain.businessName+ " Status has been successfully updated to NEW "}]

        return response


    def deleteBusiness(self, businessId):

        business = DataAccess().getBusiness(businessId, 'U')
        
        DataAccess().cleanUnapprovedBusinessData(businessId)

        response = {}
        response["responseType"] = 'success'
        response["success"] = [{"message": "The business "+business.businessMain.businessName+ " deleted Sucessfully "}]

        return response


    def enabledBusiness(self, businessId):

        business = DataAccess().getBusiness(businessId, 'A')

        response = {}
   
        DataAccess().setStatus(businessId, 'APPROVED')
        response["responseType"] = 'success'
        response["success"] = [{"message": "The business "+business.businessMain.businessName+ " has been enabled successfully"}]

        return response


    def disabledBusiness(self, businessId):

        business = DataAccess().getBusiness(businessId, 'A')
        response = {}
        DataAccess().setStatus(businessId, 'DISABLED')
        response["responseType"] = 'success'
        response["success"] = [{"message": "The business "+business.businessMain.businessName+ " has been disabled successfully"}]
        return response


    def addBusinessMainFields(self, businessMain, password):

        response={}
        errors = []
        businessByName=DataAccess().getBusinessMainFields( None,businessName=businessMain.businessName, storageType='U')
        if(businessByName!=None):
            errors.append({"field": "Business Name", "message": "A business with this name already exists"})
        # user=DataAccess().checkEmailExists(businessMain.ownerEmailId)
        # userId = DataAccess().checkEmailExists(businessMain.ownerEmailId)
        # if (len(user)>0):
        #     errors.append({"field": "email", "message": "Email already exists"})
        # if (len(errors)!=0):
        #     response["responseType"] = 'errors'
        #     response["errors"] = errors
        #     return response

        businessIdNew = DataAccess().generateBusinessId('U')
        businessIdApproved = DataAccess().generateBusinessId('A')
        businessId = {True: businessIdNew, False: businessIdApproved}[businessIdNew > businessIdApproved]
        businessMain.businessId=businessId
        print(vars(businessMain))

        DataAccess().addBusinessMainFields(businessMain, 'U')
        print('b4 creating staff instance')

        staff = Staff(businessId, None, businessMain.ownerFirstname, businessMain.ownerLastname, businessMain.ownerEmailId,
                      businessMain.ownerPhone , None, '08:00', '17:00','08:00', '17:00','08:00', '17:00','08:00', '17:00','08:00',
                      '17:00','08:00', '17:00','00:00', '00:00', 'MANAGER','Y')

        DataAccess().signupOwner(businessMain.ownerEmailId, password, businessId)
        response=BusinessSetup().addBusinessStaff(staff,'OWNER')
        if (response["responseType"]==errors):
            return response

        userId = DataAccess().getUserId(businessMain.ownerEmailId)[0]
        quesIdsAnsPairs=[[0,businessMain.ownerPhone]]
        print('before adding sec que for owner')
        print("businessMain.ownerEmailId:{}, userId:{}, quesIdsAnsPairs:{}".format(businessMain.ownerEmailId, userId, quesIdsAnsPairs))
        DataAccess(). addSecurityQuestions(businessMain.ownerEmailId, userId, quesIdsAnsPairs)

        response["responseType"] = 'data'
        response["data"]=businessId
        return response


    # def addBusinessHolidays(self,businessId, holidays, userRole):
    #     DataAccess().deleteBusinessHolidays(businessId, 'U')
    #     DataAccess().addBusinessHolidays(businessId, holidays,'U')
    #     return True


    def updateBusinessMainFields(self, businessMainFields):
        approvedConn = DataAccess().checkBusinessExistsinApprovedConn(businessMainFields.businessId)
        isedited = DataAccess().checkBusinessIsEdited(businessMainFields.businessId)
        # For editing a business, set status of an approved conn as edited in Unapproved conn.
        if (approvedConn and not(isedited)):
            DataAccess().cloneApprovedBusinessData(businessMainFields.businessId)
            return DataAccess().updateBusinessMainFields(businessMainFields, 'U')
        else:
            return DataAccess().updateBusinessMainFields(businessMainFields, 'U')

      #  DataAccess().addBusinessMainFields(businessMainFields, 'U')
        return True

    def addBusinessAddress(self, businessAddress , userRole):
        approvedConn = DataAccess().checkBusinessExistsinApprovedConn(businessAddress.businessId)
        # For editing a business, set status of an approved conn as edited in Unapproved conn.
        isedited = DataAccess().checkBusinessIsEdited(businessAddress.businessId)
        if (approvedConn and not(isedited)):
            DataAccess().cloneApprovedBusinessData(businessAddress.businessId)
        # if (approvedConn):
        #     DataAccess().addBusinessAddress(businessAddress, 'A')
        # else:
        DataAccess().addBusinessAddress(businessAddress, 'U')
       # return True



    def addBusinessExtraInfo(self, businessExtraInfo, userRole):
        approvedConn = DataAccess().checkBusinessExistsinApprovedConn(businessExtraInfo.businessId)
        # For editing a business, set status of an approved conn as edited in Unapproved conn.
        isedited = DataAccess().checkBusinessIsEdited(businessExtraInfo.businessId)
        if (approvedConn and not(isedited)):
            DataAccess().cloneApprovedBusinessData(businessExtraInfo.businessId)
        url=businessExtraInfo.websiteUrl
        if (url != None):
            if (url.startswith('http://') or url.startswith('https://')):
                pass
            else:
                businessExtraInfo.websiteUrl='http://'+businessExtraInfo.websiteUrl
        DataAccess().addBusinessExtraInfo(businessExtraInfo,'U')
        return True



    def addBusinessSettings(self, businessSettings, userRole):
        approvedConn = DataAccess().checkBusinessExistsinApprovedConn(businessSettings.businessId)
        isedited = DataAccess().checkBusinessIsEdited(businessSettings.businessId)
        # For editing a business, set status of an approved conn as edited in Unapproved conn.
        if (approvedConn and not(isedited)):
            DataAccess().cloneApprovedBusinessData(businessSettings.businessId)
        DataAccess().addBusinessSettings(businessSettings,'U')
        return True



    def addBusinessHours(self, businessHours, userRole):
        approvedConn = DataAccess().checkBusinessExistsinApprovedConn(businessHours.businessId)
        # For editing a business, set status of an approved conn as edited in Unapproved conn.
        isedited = DataAccess().checkBusinessIsEdited(businessHours.businessId)
        if (approvedConn and not(isedited)):
            DataAccess().cloneApprovedBusinessData(businessHours.businessId)
        DataAccess().addBusinessHours(businessHours,'U')
        return True



    def addBusinessService(self, businessService, userRole):

        approvedConn = DataAccess().checkBusinessExistsinApprovedConn(businessService.businessId)
        # For editing a business, set status of an approved conn as edited in Unapproved conn.
        isedited = DataAccess().checkBusinessIsEdited(businessService.businessId)
        if (approvedConn and not(isedited)):
            DataAccess().cloneApprovedBusinessData(businessService.businessId)

        businessService.duration=0
        durationSplit=businessService.subslotsCount.split(';')
        for parts in durationSplit :
            businessService.duration=businessService.duration+int(parts.strip())

        DataAccess().addBusinessService(businessService,'U')
        return True



    def addBusinessStaff(self, staff, userRole):

        approvedConn = DataAccess().checkBusinessExistsinApprovedConn(staff.businessId)
        # For editing a business, set status of an approved conn as edited in Unapproved conn.
        isedited = DataAccess().checkBusinessIsEdited(staff.businessId)
        if (approvedConn and not(isedited)):
            DataAccess().cloneApprovedBusinessData(staff.businessId)

        response = {}

        # if (userRole=='OWNER'):
            # print('b4 adding user')
        user=DataAccess().checkEmailExists(staff.emailId)
        print(staff.businessId)
        print(user)
        if(len(user)>0 and int(user[0][1]) != int(staff.businessId)):
            response["responseType"] = 'errors'
            response["errors"] = [{"field":"email","message":"Email already exists"}]
            return response
        staffRole=None
        if(len(user)>0 and int(user[0][1]) == int(staff.businessId)):
            staffRole=DataAccess().getUserDetails(None, staff.emailId)[2]
            print('role is=',staffRole)
        if (staff.isOwner=='Y' or staffRole=='OWNER'):
            print('setting isOwner to Y')
            staff.isOwner='Y'
        else:
            
            DataAccess().addUser(staff.emailId, staff.empRole, None, staff.businessId)
        # print('user is:', staff.emailId)
        userId = DataAccess().getUserId(staff.emailId)[0]
        # print('userId is:', userId)
        staff.userId=userId

        DataAccess().addStaff(staff,'U')
        response["responseType"] = 'success'
        response["success"] = [{ "message": "Staff memeber data saved successfully. You could add another staff member; or else the setup is now complete."}]
        return response

    def changeStaffBusinessHours(self, businessHours):
        DataAccess().changeStaffBusinessHours(businessHours)


    def deleteBusinessStaff(self,businessId, staffUserId, userRole):

        # staffRole=DataAccess().getUserDetails( staffUserId, None)[2]
        # print(staffRole)
        response={}
        # if ('OWNER' in staffRole):
        #     print('b4 setting respons  to error')
        #     response["responseType"] = 'errors'
        #     response["errors"] = [{"field":"email","message":"Cannot delete the business owner"}]
        #     return response

        DataAccess().deleteBusinessStaffMember(businessId, staffUserId,'U')
        response["responseType"] = 'data'
        response["data"] = True

        return response



    def deleteBusinessService(self,businessId, serviceName, userRole):
        DataAccess().deleteBusinessService(businessId, serviceName,'U')
        return True



    def getBusinessMainFields(self, businessId, situation):
        if (situation=='System'):
            return DataAccess().getBusinessMainFields(businessId, None, 'A')
        elif (situation=='User'):
            response= DataAccess().getBusinessMainFields(businessId,None, 'U')
            if (response!=None):
                return response
            else:
                return DataAccess().getBusinessMainFields(businessId, None, 'A')



    def getBusinessAddress(self, businessId, situation):
        if (situation=='System'):
            return DataAccess().getBusinessAddress(businessId,'A')
        elif (situation=='User'):
            response= DataAccess().getBusinessAddress(businessId, 'U')
            if (response!=None):
                return response
            else:
                return DataAccess().getBusinessAddress(businessId, 'A')



    def getBusinessExtraInfo(self, businessId, situation):
        if (situation=='System'):
            return DataAccess().getBusinessExtraInfo(businessId,'A')
        elif (situation=='User'):
            response= DataAccess().getBusinessExtraInfo(businessId, 'U')
            if (response!=None):
                return response
            else:
                return DataAccess().getBusinessExtraInfo(businessId, 'A')



    def getBusinessSettings(self, businessId, situation):
        if (situation=='System'):
            return DataAccess().getBusinessSettings(businessId,'A')
        elif (situation=='User'):
            response= DataAccess().getBusinessSettings(businessId, 'U')
            if (response!=None ):
                return response
            else:
                return DataAccess().getBusinessSettings(businessId, 'A')



    def getBusinessHours(self, businessId, situation):
        if (situation=='System'):
            return DataAccess().getBusinessHours(businessId,'A')
        elif (situation=='User'):
            response= DataAccess().getBusinessHours(businessId, 'U')
            if (response!=None ):
                return response
            else:
                return DataAccess().getBusinessHours(businessId, 'A')



    def getWeekdayWiseWorkingSlots(self, businessId, situation):

        businessHours =None
        if (situation=='System'):
            businessHours=DataAccess().getBusinessHours(businessId,'A')
        elif (situation=='User'):
            businessHours=DataAccess().getBusinessHours(businessId,'U')
            if (businessHours==None ):
                businessHours= DataAccess().getBusinessHours(businessId, 'A')

        if (businessHours==None):
            return None

        workingHoursSlotsDict={}
        workingHoursSlotsDict['mondaySlots'] = AppUtils().getSlots(businessHours.mondayHours, 30)
        print(workingHoursSlotsDict['mondaySlots'])
        workingHoursSlotsDict['tuesdaySlots'] = AppUtils().getSlots(businessHours.tuesdayHours, 30)
        workingHoursSlotsDict['wednesdaySlots'] = AppUtils().getSlots(businessHours.wednesdayHours, 30)
        workingHoursSlotsDict['thursdaySlots'] = AppUtils().getSlots(businessHours.thursdayHours, 30)
        workingHoursSlotsDict['fridaySlots'] = AppUtils().getSlots(businessHours.fridayHours, 30)
        workingHoursSlotsDict['saturdaySlots'] = AppUtils().getSlots(businessHours.saturdayHours, 30)
        workingHoursSlotsDict['sundaySlots'] = AppUtils().getSlots(businessHours.sundayHours, 30)

        return workingHoursSlotsDict



    def getBusinessServices(self, businessId, situation):

        if (situation=='System'):
            return DataAccess().getBusinessServices(businessId,'A')
        elif (situation=='User'):
            response= DataAccess().getBusinessServices(businessId, 'U')
            if (response!=None and len(response)!=0):
                return response
            else:
                return DataAccess().getBusinessServices(businessId, 'A')



    def getBusinessStaff(self, businessId, situation):
        if (situation=='System'):
            return DataAccess().getStaff(businessId,'A')
        elif (situation=='User'):
            response= DataAccess().getStaff(businessId, 'U')
            if (response!=None and len(response)!=0):
                return response
            else:
                return DataAccess().getStaff(businessId, 'A')



    def getBusinessStaffDetails(self, staffUserId):

        member=DataAccess().getStaffDeatils(staffUserId)
        print(vars(member))
        serviceSkills=member.services
        servicesDetails=[]
        if(serviceSkills!=None):
            skills=serviceSkills.split(';')
            # for skill in skills:
            #     oneService={}
            #     serviceDefinition=BookingUtils().getBusinessServiceDefinition(member.businessId,skill.strip())
            #     price='R'+str(serviceDefinition.price)
            #     duration=str(serviceDefinition.duration)+'mins'
            #     skillStr=skill+'('+price+', '+duration+')'
            #     oneService["name"]= skill.strip()
            #     oneService["nameStr"]=skillStr

                # servicesDetails.append(skillStr)
                # servicesDetails.append(oneService)
                # member.services=servicesDetails

            for skill in skills:
                print('skill=',skill)
                serviceDefinition=BookingUtils().getBusinessServiceDefinition(member.businessId,skill.strip())
                price='R'+str(serviceDefinition.price)
                duration=str(serviceDefinition.duration)+'mins'
                skillStr=skill+'('+price+', '+duration+')'
                servicesDetails.append(skillStr)
                member.services=servicesDetails

        return member


        # return DataAccess().getStaffDeatils(staffUserId)

    def getBusinessesList(self, situation):

        result=[]
        if (situation=='System'):
            result= DataAccess().getBusinessesList('NEW','A')
        elif (situation=='User'):
            response= DataAccess().getBusinessesList('NEW','U')
            if (response!=None and len(response)!=0):
                result=response
            else:
                result= DataAccess().getBusinessesList('NEW','A')

        businessesList=[]
        for row in result :
            print('in result loop')
            oneRow={}
            oneRow["businessId"]=row[0]
            oneRow["owner"]=AppUtils().getFullName(row[1],row[2])
            oneRow["phone"]=row[3]
            oneRow["businessName"]=row[4]

            address= ''
            if (row[5]!=None):
                address=address+ ' '+row[5]
            if (row[6]!=None):
                address=address+ ' '+row[6]
            if (row[7]!=None):
                address=address+ ' '+row[7]
            # if (row[8]!=None):
            #     address=address+ ' '+row[8]
            oneRow["address"]=address
            # oneRow["address"] = row[5] + ' ' + row[6] + ' ' + row[7] + ' ' + row[8]
            businessesList.append(oneRow)
        return businessesList


    def getApprovedBusinessesList(self, situation):

        result=[]
        if (situation=='System'):
            result= DataAccess().getBusinessesList('APPROVED','A')
        elif (situation=='User'):
            response= DataAccess().getBusinessesList('APPROVED','U')
            if (response!=None and len(response)!=0):
                result=response
            else:
                result= DataAccess().getBusinessesList('APPROVED','A')

        approvedBusinessesList=[]
        for row in result :
            print('in result loop')
            oneRow={}
            oneRow["businessId"]=row[0]
            oneRow["owner"]=AppUtils().getFullName(row[1],row[2])
            oneRow["phone"]=row[3]
            oneRow["businessName"]=row[4]

            address= ''
            if (row[5]!=None):
                address=address+ ' '+row[5]
            if (row[6]!=None):
                address=address+ ' '+row[6]
            if (row[7]!=None):
                address=address+ ' '+row[7]
            # if (row[8]!=None):
            #     address=address+ ' '+row[8]
            oneRow["address"]=address
            # oneRow["address"] = row[5] + ' ' + row[6] + ' ' + row[7] + ' ' + row[8]

            approvedBusinessesList.append(oneRow)

        return approvedBusinessesList


    def getEditedBusinessesList(self, situation):

        result=[]
        if (situation=='System'):
            result= DataAccess().editedBusinessesList('EDITED','A')
        elif (situation=='User'):
            response= DataAccess().editedBusinessesList('EDITED','U')
            if (response!=None and len(response)!=0):
                result=response
            else:
                result= DataAccess().editedBusinessesList('EDITED','A')

        editedBusinessesList=[]
        for row in result :
            print('in result loop')
            oneRow={}
            oneRow["businessId"]=row[0]
            oneRow["owner"]=AppUtils().getFullName(row[1],row[2])
            oneRow["phone"]=row[3]
            oneRow["businessName"]=row[4]

            address= ''
            if (row[5]!=None):
                address=address+ ' '+row[5]
            if (row[6]!=None):
                address=address+ ' '+row[6]
            if (row[7]!=None):
                address=address+ ' '+row[7]
            # if (row[8]!=None):
            #     address=address+ ' '+row[8]
            oneRow["address"]=address
            # oneRow["address"] = row[5] + ' ' + row[6] + ' ' + row[7] + ' ' + row[8]

            editedBusinessesList.append(oneRow)

        return editedBusinessesList


    def getDisabledBusinessesList(self, situation):

        result=[]
        if (situation=='System'):
            result= DataAccess().getBusinessesList('DISABLED','A')
        elif (situation=='User'):
            response= DataAccess().getBusinessesList('DISABLED','U')
            if (response!=None and len(response)!=0):
                result=response
            else:
                result= DataAccess().getBusinessesList('DISABLED','A')

        disableBusinessesList=[]
        for row in result :
            print('in result loop')
            oneRow={}
            oneRow["businessId"]=row[0]
            oneRow["owner"]=AppUtils().getFullName(row[1],row[2])
            oneRow["phone"]=row[3]
            oneRow["businessName"]=row[4]

            address= ''
            if (row[5]!=None):
                address=address+ ' '+row[5]
            if (row[6]!=None):
                address=address+ ' '+row[6]
            if (row[7]!=None):
                address=address+ ' '+row[7]
            # if (row[8]!=None):
            #     address=address+ ' '+row[8]
            oneRow["address"]=address
            # oneRow["address"] = row[5] + ' ' + row[6] + ' ' + row[7] + ' ' + row[8]

            disableBusinessesList.append(oneRow)

        return disableBusinessesList

    # def getBusinessHolidays(self, businessId, situation):
    #     if (situation=='System'):
    #         return DataAccess().getBusinessHolidays(businessId,'A')
    #     elif (situation=='User'):
    #         response= DataAccess().getBusinessHolidays(businessId, 'U')
    #         if (response!=None and len(response)!=0):
    #             return response
    #         else:
    #             return DataAccess().getBusinessHolidays(businessId, 'A')
    #
    #
