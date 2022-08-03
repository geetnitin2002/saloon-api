from datetime import datetime, date
from datetime import timedelta
# from src.dbAccess import DataAccess
# from src.apputils import AppUtils
from apputils import AppUtils
from dbAccess import DataAccess
import json
import re
import config
from notifications import AppEmail
import time
import pytz

class BookingUtils:

    def checkForBookingsClash(self, email, appointmentDate, clockTimeRange):

        timeAndDuration = clockTimeRange.split(';')
        startSlotNumber=AppUtils().convertClockTimeToSlotNumber(timeAndDuration[0])
        slotsCount = int(timeAndDuration[1]) // int(config.gSingleTimeslotDuration)
        endSlotNumber=startSlotNumber -1 + slotsCount
        bookings=DataAccess().getUsersBookingsOnAday(email, appointmentDate)
        for booking in bookings:
            slots=booking[1].split('-')
            if(self.checkOverlapp(startSlotNumber,endSlotNumber, int(slots[0]),int(slots[1]) ) ):
                return False, booking[0], booking[2], booking[3], booking[4], booking[5]

        return True, None, None, None, None, None


    # TODO - may need a change, appointmentTime may not be possible to come from UI
    def checkForTicketBookingsClash(self, email, appointmentDate, appointmentTime):

        bookingSlotRange=AppUtils.convertClockTimeRangeToSlotsRange(appointmentTime)
        bookings=DataAccess().getUsersTicketBookingsOnAday(email, appointmentDate)
        for booking in bookings:
            startSlotNumber=int(booking[2])
            serviceDuration=self.getBusinessServiceDefinition(booking[1],booking[6])
            endSlotNumber=startSlotNumber - 1 + (serviceDuration//int(config.gSingleTimeslotDuration))

            if(self.checkOverlapp(bookingSlotRange['startSlotNumber'],bookingSlotRange['endSlotNumber'], startSlotNumber, endSlotNumber)):
                return False, booking[0], booking[3], booking[4], booking[5], booking[6]

        return True, None, None, None, None, None


    def checkOverlapp(self, startSlotNumber, endSlotNumber, startSlotNUmer2, endSlotNumber2):

        if (startSlotNumber > endSlotNumber2):
            return False
        if (endSlotNumber < startSlotNUmer2):
            return False

        return True


    def getBusinessAddressForDisplay(self, businessId, style='Continuous'):
        businessAddress = DataAccess().getBusinessAddress(businessId)
        address=''
        if (businessAddress!=None):
            googleMapsLink=businessAddress.googleMapsUrl
            if (style=='Continuous'):
                address = businessAddress.addressLine1
                if (businessAddress.addressLine2!=None):
                    address = address + ', '+businessAddress.addressLine2
                if (businessAddress.cityLocation!=None):
                    address = address + ', ' + businessAddress.cityLocation
                if (businessAddress.city!=None):
                    address = address + ', ' + businessAddress.city
                if (businessAddress.postalCode!=None):
                    address = address + ', ' + businessAddress.postalCode
                if (businessAddress.latitude!=None or businessAddress.longitude!=None):
                    address = address + ', ' + '('+ str(businessAddress.latitude)
                if (businessAddress.latitude!=None or businessAddress.longitude!=None):
                    address = address + ', ' + str(businessAddress.longitude) + ')'
                # if (businessAddress.province!=None):
                #     address = address + ', ' + businessAddress.province
            # address = address + ', ' + businessAddress.city + ' ' + businessAddress.postalCode + ', ' + businessAddress.province
            return address, googleMapsLink

        if (style=='Short'):
            pass
        if (style=='LineByLine'):
            pass


    def applyBookingIntervalToAvailableSlots(self, dateOfDay, businessId, availableServiceSlotsList):

        # Commented code below and replaced by code that follows. Use oython date
        # if (dateOfDay == datetime.today().strftime(config.applicationUIDateFormat)):
        if (dateOfDay == date.today()):
            runningSlot = AppUtils().getTheRunningSlot()
            # bookingIntervalSlotCount = int(
            #     (DataAccess().getBusinessSettings(businessId, 'A').bookingInterval)) // 15 + 1
            bookingIntervalSlotCount = int(
                (DataAccess().getBusinessSettings(businessId, 'A').bookingInterval)) // int(config.gSingleTimeslotDuration) + 1
            minSlotForBookingToday = runningSlot + bookingIntervalSlotCount
            print('availableServiceSlotsList=',availableServiceSlotsList)
            print('minSlotForBookingToday',minSlotForBookingToday)
            availableServiceSlotsList = AppUtils().getHigherElementsInSortedList(availableServiceSlotsList, minSlotForBookingToday)

        return availableServiceSlotsList


    def getBusinessWorkingSlotsRange(self, businessId):

        businessHours=DataAccess().getBusinessHours(businessId,'A')
        workingHoursSlotsList=[]
        if (businessHours!=None):
            mondaySlots = AppUtils().getSlots(businessHours.mondayHours, 30)
            tuesadySlots = AppUtils().getSlots(businessHours.tuesdayHours, 30)
            wednesdaySlots = AppUtils().getSlots(businessHours.wednesdayHours, 30)
            thursdaySlots = AppUtils().getSlots(businessHours.thursdayHours, 30)
            fridaySlots = AppUtils().getSlots(businessHours.fridayHours, 30)
            saturdaySlots = AppUtils().getSlots(businessHours.saturdayHours, 30)
            sundaySlots = AppUtils().getSlots(businessHours.sundayHours, 30)

            workingHoursSlotsList =list(set(mondaySlots) | set(tuesadySlots) | set(wednesdaySlots) | set(thursdaySlots) | set(fridaySlots) | set(saturdaySlots) | set(sundaySlots) )
            if('00:00' in workingHoursSlotsList):
                workingHoursSlotsList.remove('00:00')
            workingHoursSlotsList.sort()
        return workingHoursSlotsList


    # def getUIDisplayWeeks2(self, businessId):
    #
    #     bookingWindow=DataAccess().getBusinessSettings(businessId,'A').preBookingWindow
    #     print('bookingWindow=',bookingWindow)
    #     nearestMondayDate, daysToMonday=AppUtils().getNearestMonday()
    #     lastDayDate=date.today()+timedelta(days=bookingWindow)
    #     print('lastDayDate=',lastDayDate)
    #     weeks=[]
    #     weekOneStartDate=date.today()
    #     weekOneEndDate =''
    #
    #     if (daysToMonday > bookingWindow):
    #         weekOneEndDate=date.today()+timedelta(days=bookingWindow)
    #     else:
    #         if(daysToMonday==0):
    #             weekOneEndDate = date.today() + timedelta(days=6)  # sunday
    #         else:
    #             weekOneEndDate = date.today() + timedelta(days=(daysToMonday-1)) #sunday
    #     weeks.append(AppUtils().convertDatesToWeekFormat(weekOneStartDate,weekOneEndDate))
    #
    #     if (daysToMonday > bookingWindow):
    #         return weeks
    #
    #     if(daysToMonday==0):
    #         previousMondayDate=nearestMondayDate
    #     else:
    #         previousMondayDate = nearestMondayDate - timedelta(days=7)
    #
    #     i=0
    #     while i <= bookingWindow:
    #
    #         mondayDate = previousMondayDate+timedelta(days=7)
    #         if (mondayDate > lastDayDate):
    #             break;
    #
    #         previousMondayDate=mondayDate
    #         weekEndDate=''
    #         sundayDate=mondayDate+timedelta(days=6)
    #
    #         if(sundayDate>lastDayDate):
    #             weekEndDate =lastDayDate
    #         else:
    #             weekEndDate = sundayDate
    #
    #         i=i+7                                                #jump by 7 days
    #         print('iteration : ',i)
    #
    #         weeks.append(AppUtils().convertDatesToWeekFormat(mondayDate, weekEndDate))
    #
    #     return weeks


    def getWeeksInDateRange(self, startDate, endDate):

        weeks = []
        weekendDate = startDate - timedelta(days=startDate.weekday()) + timedelta(days=6)
        if (weekendDate > endDate):
            weekendDate=endDate
        weeks.append((startDate, weekendDate))

        while (weekendDate < endDate):
            weekStartDate = weekendDate + timedelta(days=1)
            weekendDate = weekendDate + timedelta(days=7)
            if (weekendDate < endDate):
                weeks.append((weekStartDate, weekendDate))
            else:
                weeks.append((weekStartDate, endDate))

        return weeks



    def getUIDisplayWeeksInDateRange(self, startDate, endDate):

        weeksInUIFormat = []
        weekendDate = startDate - timedelta(days=startDate.weekday()) + timedelta(days=6)
        # print(weekendDate)
        if (weekendDate > endDate):
            weekendDate=endDate
        weeksInUIFormat.append(AppUtils().convertDatesToWeekFormat(startDate, weekendDate))

        while (weekendDate < endDate):
            weekStartDate = weekendDate + timedelta(days=1)
            weekendDate = weekendDate + timedelta(days=7)
            if (weekendDate < endDate):
                weeksInUIFormat.append(AppUtils().convertDatesToWeekFormat(weekStartDate, weekendDate))
            else:
                weeksInUIFormat.append(AppUtils().convertDatesToWeekFormat(weekStartDate, endDate))

        return weeksInUIFormat



    def getUIDisplayWeeks(self, businessId):

        bookingWindow=DataAccess().getBusinessSettings(businessId,'A').preBookingWindow
        # startDate=date.today()
        dt = date.today() # datetime.strptime(date.today(), '%d/%b/%Y')
        startDate = dt - timedelta(days=dt.weekday())
        return self.getUIDisplayWeeksInDateRange(startDate, startDate + timedelta(days=bookingWindow))



    def getDateRangeFromUIWeekDisplay(self, uiDateString):
        print('in method getDateRangeFromUIWeekDisplay')
        # 04/02/2019(Monday)  to  10/02/2019(Sunday)
        parts = uiDateString.split('(')
        startDate = parts[0].strip()
        endDate = (parts[1].split('to'))[1].strip()
        return (startDate, endDate)



    # Convert the free slots of each member into availablity based on service duration.
    def getUnionAvailabilityOfStaff(self, sortedSlotsOfStaffMembers, slotCount):

        print('in getUnionAvailabilityOfStaff')
        print(sortedSlotsOfStaffMembers)
        print(slotCount)
        # serviceDefinition=BookingUtils().getBusinessServiceDefinition(businessId, serviceName)
        listOfSortedFreeSlots=[]
        for sortedSlotsOfStaffMember in sortedSlotsOfStaffMembers:
            # print('key=',key)
            # print('value=',sortedSlotsOfStaffMembers[key])
            # consectiveChunks=AppUtils().getConsecutiveChunks(sortedSlotsOfStaffMembers[key], slotCount)
            consectiveChunks = AppUtils().getConsecutiveChunks(sortedSlotsOfStaffMember, slotCount)
            print(consectiveChunks)
            listOfSortedFreeSlots.append(consectiveChunks)

        unionFreeSlots=set([])
        for freeSlots in listOfSortedFreeSlots:
            unionFreeSlots=unionFreeSlots | set(freeSlots)

        return  sorted(list(unionFreeSlots))


    def getUnionAvailabilityOfStaffForDTS(self, sortedSlotsOfStaffMembers):

        print('in getUnionAvailabilityOfStaff')
        print(sortedSlotsOfStaffMembers)
        # serviceDefinition=BookingUtils().getBusinessServiceDefinition(businessId, serviceName)
        listOfSortedFreeSlots = sortedSlotsOfStaffMembers
        # for sortedSlotsOfStaffMember in sortedSlotsOfStaffMembers:
        #     # print('key=',key)
        #     # print('value=',sortedSlotsOfStaffMembers[key])
        #     # consectiveChunks=AppUtils().getConsecutiveChunks(sortedSlotsOfStaffMembers[key], slotCount)
        #     consectiveChunks = AppUtils().getConsecutiveChunks(sortedSlotsOfStaffMember, slotCount)
        #     print(consectiveChunks)
        #     listOfSortedFreeSlots.append(consectiveChunks)

        unionFreeSlots=set([])
        for sortedFreeSlots in listOfSortedFreeSlots:
            #for freeSlots in sortedFreeSlots:
            unionFreeSlots=unionFreeSlots | set(sortedFreeSlots)

        return  sorted(list(unionFreeSlots))


    # input is sorted list of free slots
    # returns the slots that are available to perform the service over the service duration
    # def generateAvailableSlotsForService(self, sortedFreeSlots, serviceDuration):
    #     slotAvailableForService=[]
    #     for i in range(len(sortedFreeSlots) - serviceDuration+1):
    #         if(AppUtils().isRangeConsecutive(sortedFreeSlots[i:i+serviceDuration])):
    #             slotAvailableForService.append(sortedFreeSlots[i])
    #
    #     return slotAvailableForService



    # can give one or two service as input
    # if slot date is none, it will return timeband availability for the slot rane over the booking window period starting today
    # if slot range is None, it will return the one day availability for the slot date
    # if slot date and slot range are both present in input, it will return availability for the slot range on the slot date only
    def getAvailabilityOfSkilledStaffUtility (self, businessId, services, slotDate, slotRange):

        if (slotDate==None):
            bookingWindow=DataAccess().getBusinessSettings(businessId,'A').preBookingWindow
            # Replaced below lines by foll lines to use python date
            # startDate = date.today().isoformat()
            # endDate = (date.today() + timedelta(days=bookingWindow)).isoformat()
            startDate = date.today()
            endDate = date.today() + timedelta(days=bookingWindow)

            if (len(services) == 1):
                return DataAccess().getAvailabilityOfSkilledStaff(businessId, services[0], None, None, startDate, endDate,
                                                                  slotRange)
            if (len(services) == 2):
                return DataAccess().getAvailabilityOfSkilledStaff(businessId, services[0], services[1], None, startDate,
                                                                  endDate, slotRange)

        elif (slotRange==None):
            if (len(services) == 1):
                return DataAccess().getAvailabilityOfSkilledStaff(businessId, services[0], None, slotDate, None, None, None)
            if (len(services) == 2):
                return DataAccess().getAvailabilityOfSkilledStaff(businessId, services[0], services[1], slotDate, None, None, None)
        else:
            if (len(services) == 1):
                return DataAccess().getAvailabilityOfSkilledStaff(businessId, services[0], None, slotDate, None, None, slotRange)
            if (len(services) == 2):
                return DataAccess().getAvailabilityOfSkilledStaff(businessId, services[0], services[1], slotDate, None, None, slotRange)



    def getAvailabilityOfStaffUtility (self, userIdOfStaff, businessId, slotDate, slotRange):

        if (slotDate==None):
            bookingWindow=DataAccess().getBusinessSettings(businessId,'A').preBookingWindow
            # Replaced next 2 commented lines by code after that. Use python date
            # startDate = date.today().isoformat()
            # endDate = (date.today() + timedelta(days=bookingWindow)).isoformat()
            startDate = date.today()
            endDate = startDate + timedelta(days=bookingWindow)

            return DataAccess().getAvailabilityOfStaff(businessId, userIdOfStaff, None, startDate, endDate, slotRange)

        elif (slotRange==None):
            print('elif (slotRange==None):')
            print('userid is=',userIdOfStaff)
            # print(DataAccess().getAvailabilityOfStaff(businessId, userIdOfStaff, slotDate, None, None, None))
            return DataAccess().getAvailabilityOfStaff(businessId, userIdOfStaff, slotDate, None, None, None)

        elif(slotDate!=None and slotRange!=None):
            return DataAccess().getAvailabilityOfStaff(businessId, userIdOfStaff, slotDate, None, None, slotRange)



    def convertWorkingHoursToStaffSlotSetup(self, startTime, endTime):

        print(startTime)
        print(endTime)
        minWorkingSlot = AppUtils().convertClockTimeToSlotNumber(startTime)
        maxWorkingSlot = AppUtils().convertClockTimeToSlotNumber(endTime) - 1
        workingSlotNumbers = []
        workingSlotStartTimes = []

        slotRange= maxWorkingSlot - minWorkingSlot + 1
        for i in range(slotRange):
            workingSlotNumbers.append(minWorkingSlot + i)
            workingSlotStartTimes.append(AppUtils().convertSlotNumberToClockTime(minWorkingSlot + i))

        nonWorkingSlotNumbers = []
        nonWorkingSlotStartTimes = []
        for i in range(1, minWorkingSlot):
            nonWorkingSlotNumbers.append(i)
            nonWorkingSlotStartTimes.append(AppUtils().convertSlotNumberToClockTime(i))
        for i in range(maxWorkingSlot + 1, 97):
            nonWorkingSlotNumbers.append(i)
            nonWorkingSlotStartTimes.append(AppUtils().convertSlotNumberToClockTime(i))

        return workingSlotNumbers, workingSlotStartTimes, nonWorkingSlotNumbers, nonWorkingSlotStartTimes



    def getBusinessServiceDefinition(self, businessId, serviceName):
        services = DataAccess().getBusinessServices(businessId,'A')
        for service in services:
            print(serviceName)
            print(service.name)
            if (serviceName == service.name):
                return service



    def getLeaves(self, businessId):

        leaves = DataAccess().getLeavesRecords(businessId)
        print(*leaves, sep='\n')
        leavesList=[]
        for leave in leaves:
            leaveRecord = {}
            # leaveRecord["businessId"]=leave[0]
            leaveRecord["staffUserId"]=leave[1]
            leaveRecord["leaveNumber"]=leave[2]
            leaveRecord["startDate"]=leave[3]
            leaveRecord["startTime"]=leave[4]
            leaveRecord["endDate"]=leave[5]
            leaveRecord["endTime"]=leave[6]
            leaveRecord["ifAllStaff"]=leave[7]
            leaveRecord["parentLeaveNumber"]=leave[8]
            leaveRecord["status"]=leave[9]
            leaveRecord["cancelButtonVisibility"] = False
            if (leave[9]=='NEW'):
                leaveRecord["cancelButtonVisibility"]=True
            # leaveRecord["businessId"]=leave[0]
            # print(leaveRecord)
            leavesList.append(leaveRecord)

        return leavesList


    def getFutureLeaves(self, businessId):
        leaves = DataAccess().getFutureLeaves(businessId)
        print(*leaves, sep='\n')
        leavesList=[]
        for leave in leaves:
            leaveRecord = {}
            # leaveRecord["businessId"]=leave[0]
            leaveRecord["name"]=leave[0]
            leaveRecord["start"]=leave[1]
            leaveRecord["end"]=leave[2]
            leaveRecord["leaveNumber"]=leave[3]
            # leaveRecord["startDate"]=leave[3]
            # leaveRecord["startTime"]=leave[4]
            # leaveRecord["endDate"]=leave[5]
            # leaveRecord["endTime"]=leave[6]
            # leaveRecord["ifAllStaff"]=leave[7]
            leaveRecord["parentLeaveNumber"]=leave[4]
            # print(leaveRecord)
            leavesList.append(leaveRecord)
        return leavesList


    def getBusinessStaffDetails(self, businessId, userIdOfStaff):
        staffMembers = DataAccess().getStaff(businessId,'A')

        for member in staffMembers:
            # x='>'+str(member.userId)+'<'
            # y='>'+str(userIdOfStaff)+'<'
            # print('user Id of staff=',x)
            # print('user Id to check for=', y)
            if (str(userIdOfStaff) == str(member.userId)):
                serviceSkills=member.services
                servicesDetails=[]
                if(serviceSkills!=None):
                    print('skilled')
                    skills=serviceSkills.split(';')
                    print(skills)
                    for skill in skills:

                        serviceDefinition=BookingUtils().getBusinessServiceDefinition(businessId,skill.strip())
                        price='R'+str(serviceDefinition.price)
                        duration=str(serviceDefinition.duration)+'mins'
                        skillStr=price+', '+duration
                        print(skillStr)
                        servicesDetails.append(skillStr)
                        print(servicesDetails)
                        member.services=servicesDetails
                        print(member)

                print('staff found ',member)
                return member
        # print('not found')
        return None


    # Replaced by new table use for availability
    # def markUnavailability( self, businessId, userIdOfStaff, slotStatus, slotNumberRange, clockTimeRange, actionDate, fullDay ):
    #
    #     minSlotNumber =1
    #     maxSlotNumber =1
    #     if (fullDay=='Y'):
    #         maxSlotNumber =96
    #     elif(slotNumberRange!=None):
    #         parts = slotNumberRange.split('-')
    #         minSlotNumber = parts[0].strip()
    #         maxSlotNumber = parts[1].strip()
    #     elif (clockTimeRange!=None):
    #         slots = AppUtils().convertClockTimeRangeToSlotsRange(clockTimeRange)
    #         print(clockTimeRange)
    #         print(slots)
    #         minSlotNumber=slots["startSlotNumber"]
    #         maxSlotNumber=slots["endSlotNumber"]
    #
    #     dayOfWeek = datetime.strptime(actionDate, '%Y-%m-%d').weekday()
    #
    #     DataAccess().markUnavailability(businessId,userIdOfStaff,slotStatus,minSlotNumber,maxSlotNumber,actionDate,dayOfWeek)



    def generateBookingNumber(self, businessId, actionDate, ifTicket='N'):
        sequenceValue =None
        if(ifTicket=='N'):
            sequenceValue=str(DataAccess().getMaxBookingId()).zfill(8)
        else:
            sequenceValue = str(DataAccess().getTicketBookingId()).zfill(8)

        bookingNumber= str(businessId) +'-' + actionDate.strftime('%Y%m%d') + '-' + sequenceValue
        return bookingNumber



    def generateLeaveNumber(self, businessId, staffUserId=None):

        sequenceValue=str(DataAccess().getMaxLeaveId()).zfill(8)
        leaveNumber= str(businessId) + '-' + sequenceValue

        if (staffUserId != None):
            leaveNumber=leaveNumber+'-'+str(staffUserId)
        return leaveNumber



    # def getCompletelyAvailableDay(self, businessId):
    #     timebands=self.getTimeBands(businessId, None)
    #     timebandsDict = {}
    #     for timeband in timebands:
    #         timebandsDict[timeband]='N'
    #     return timebandsDict



    # def getCombinedUnavailabilityByServices(self,  businessId, unavailability, serviceDuration1, serviceDuration2):
    #     serviceDuration=serviceDuration1+serviceDuration2
    #     return self.getTimebandsUnavailability (businessId, unavailability, serviceDuration)



    # def getCombinedUnavailabilityByStaffs(self, businessId, unavailabilityStaff1, unavailabilityStaff2, serviceDuration):
    #
    #     unavailabilityList1=[]
    #     for unavailabilitySlotNumber in unavailabilityStaff1:
    #         unavailabilityList1.append(unavailabilitySlotNumber)
    #
    #     unavailabilityList2=[]
    #     for unavailabilitySlotNumber in unavailabilityStaff2:
    #         unavailabilityList2.append(unavailabilitySlotNumber)
    #
    #     combinedUnavailability = sorted(list(set(unavailabilityList1) | set(unavailabilityList2)))
    #     return self.getTimebandsUnavailability (  businessId, combinedUnavailability, serviceDuration)



    # def getCombinedUnavailabilityByStaffsAndServices(self,  businessId, unavailabilityStaff1, unavailabilityStaff2, serviceDuration1, serviceDuration2):
    #     serviceDuration=''
    #     if(serviceDuration1 >= serviceDuration2):
    #         serviceDuration=serviceDuration1
    #     else:
    #         serviceDuration=serviceDuration2
    #     return self.getCombinedUnavailabilityByStaffs( businessId, unavailabilityStaff1, unavailabilityStaff2, serviceDuration)


    # def getTimebandsUnavailability (self, businessId, unavailability, serviceDuration):
    #
    #     timebands=self.getTimeBands(businessId, None)
    #     timebandsDict = {}
    #     if (self.ifTimebandUnavailability (timebands[0], unavailability, serviceDuration)):
    #         for timeband in timebands:
    #             timebandsDict[timeband]='Y'
    #         return timebandsDict
    #     else:
    #         # del timebands[0]
    #         for timeband in timebands:
    #             if (self.ifTimebandUnavailability(timeband, unavailability, serviceDuration)):
    #                 timebandsDict[timeband] = 'Y'
    #             else:
    #                 timebandsDict[timeband] = 'N'
    #
    #     return timebandsDict


    # def ifTimebandUnavailability (self, timeband, unavailabilityList, serviceDuration):
    #
    #     print('in if timeband unava')
    #     print(unavailabilityList)
    #     slotRange=AppUtils().convertClockTimeRangeToSlotsRange(timeband)
    #
    #     # serviceSlotsCoverageCount=serviceDuration//15
    #     serviceSlotsCoverageCount = serviceDuration // int(config.gSingleTimeslotDuration)
    #     print('serviceSlotsCoverageCount=',serviceSlotsCoverageCount)
    #     print(slotRange)
    #     bandSize=slotRange["endSlotNumber"] - slotRange["startSlotNumber"]
    #     if(bandSize < serviceSlotsCoverageCount) :
    #         print('band size smaller tan service duration')
    #         return True
    #
    #     if (slotRange["endSlotNumber"] < unavailabilityList[0] ):
    #         print('smalles unavaiable slt bigger than time band upper range' )
    #         return False
    #
    #     if (slotRange["startSlotNumber"] > unavailabilityList[len(unavailabilityList)-1] ):
    #         print('largest unavaiable slt smaller than time band lower range')
    #         return False
    #
    #     for i in range(len(unavailabilityList)-1):
    #         print('iteration=  ',i)
    #         print(slotRange["startSlotNumber"])
    #         print(slotRange["endSlotNumber"])
    #
    #
    #         if (slotRange["startSlotNumber"] <= unavailabilityList[i] and slotRange["endSlotNumber"] >= unavailabilityList[
    #             i]):
    #                 print('slot num in time band   - ',unavailabilityList[i])
    #                 if (unavailabilityList[i] + serviceSlotsCoverageCount < unavailabilityList[i+1]):
    #                     return False
    #
    #     if (slotRange["startSlotNumber"] <= unavailabilityList[len(unavailabilityList)-1] and slotRange["endSlotNumber"] >= unavailabilityList[len(unavailabilityList)-1 ]):
    #             print('slot num in time band   - ',unavailabilityList[len(unavailabilityList)-1 ])
    #             if (unavailabilityList[len(unavailabilityList)-1] + serviceSlotsCoverageCount < slotRange["endSlotNumber"]+1):
    #                 return False
    #
    #     return True



    # def applyTimebandToUnAvailability(self, timeband, unavailability, serviceDuration):
    #
    #     timebandUnavailability=[]
    #     slotRange=AppUtils().convertClockTimeRangeToSlotsRange(timeband)
    #     print(slotRange)
    #
    #     for unavailabileSlot in unavailability:
    #         print('unavailabileSlot=',unavailabileSlot)
    #         print(unavailabileSlot[3])
    #         # print(unavailabileSlot[0])
    #         if (unavailabileSlot[3] >= slotRange["startSlotNumber"] and unavailabileSlot[3] <= slotRange["endSlotNumber"]):
    #             print('in timeband, unavailable slot=',unavailabileSlot)
    #             timebandUnavailability.append(unavailabileSlot)
    #         else:
    #             print("out of timeband")
    #
    #     return timebandUnavailability



    # def getTimeBands(self, businessId, numOfBands):
    #     if(numOfBands==None):
    #         numOfBands=4
    #
    #     minSlot, maxSlot = DataAccess().getSlotRange(businessId)
    #     range = maxSlot - minSlot
    #     bandSize = range // numOfBands
    #     timeBands = []
    #     timeBands.append( AppUtils().convertSlotNumberToClockTime(minSlot) + ' - ' + AppUtils().convertSlotNumberToClockTime(maxSlot))
    #     timeBands.append( AppUtils().convertSlotNumberToClockTime(minSlot) + ' - ' + AppUtils().convertSlotNumberToClockTime(minSlot + bandSize))
    #     timeBands.append( AppUtils().convertSlotNumberToClockTime(minSlot + bandSize + 1) + ' - ' + AppUtils().convertSlotNumberToClockTime(minSlot + 2 * bandSize))
    #     timeBands.append( AppUtils().convertSlotNumberToClockTime(minSlot + 2 * bandSize + 1) + ' - ' + AppUtils().convertSlotNumberToClockTime(minSlot + 3 * bandSize))
    #     timeBands.append( AppUtils().convertSlotNumberToClockTime(minSlot + 3 * bandSize + 1) + ' - ' + AppUtils().convertSlotNumberToClockTime(maxSlot))
    #
    #     return timeBands



    # TODO - should be replaced by the method below that allows multiple leaves for multiple staff
    def markStaffOnLeave(self, businessId, staffUserIds):
        # Replaced by code below itto use python date
        # leaveDate = datetime.today().strftime(config.applicationUIDateFormat)
        leaveDate = date.today()
        print('leaveDate=',leaveDate)
        for staffUserId in staffUserIds:
            DataAccess().markUnavailability(businessId,staffUserId,'L',1,96,leaveDate)

        return True



    def markStaffMembersOnLeaves(self, businessId, staffUserIds=[], ifAllStaff='N', ifFullDayLeaves='N', startDate=None, startTime=None, endDate=None, endTime=None):

        print(startDate)
        print(endDate)

        if(ifFullDayLeaves=='Y'):
            startTime = None
            endTime = None


        if(ifAllStaff=='Y'):
            staffUserIds=[]
            print('in if all staff')
            staff=DataAccess().getStaff(businessId,'A')
            for staffMember in staff:
                staffUserIds.append(staffMember.userId)

        parentLeaveNumber = BookingUtils().generateLeaveNumber(businessId)
        print('parentLeaveNumber=',parentLeaveNumber)
        print(staffUserIds)
        for staffUserId  in staffUserIds:
            leaveNumber = BookingUtils().generateLeaveNumber(businessId, staffUserId)
            # startDate, startTime, endDate, endTime,
            DataAccess().createLeaveRecord(businessId, staffUserId, leaveNumber, startDate, startTime, endDate, endTime, ifFullDayLeaves, parentLeaveNumber)

        startSlotNumber = 1
        endSlotNumber = 96

        # if(ifAllStaff == 'Y'):
        #     staffMembers=DataAccess().getStaff(businessId)
        #     for staffMember in staffMembers:
        #         staffUserIds.append(staffMember.userId)

        leaveDates = AppUtils().getDatesBetween(startDate, endDate, 'BOTH')
        print(leaveDates)

        if(ifFullDayLeaves=='Y'):
            print('applying full day leave')
            self.applyLeaveforStaffMembers(businessId, staffUserIds, 1, 96, leaveDates, parentLeaveNumber)
        else:
            if (startDate==endDate):
                print('in startDate==endDate')

                startSlotNumber=AppUtils().convertClockTimeToSlotNumber(startTime)
                endSlotNumber = AppUtils().convertClockTimeToSlotNumber(endTime)

                self.applyLeaveforStaffMembers(businessId, staffUserIds, startSlotNumber, endSlotNumber, [startDate], parentLeaveNumber)
            else:
                print('in else of, startDate==endDate')

                startSlotNumber=AppUtils().convertClockTimeToSlotNumber(startTime)
                self.applyLeaveforStaffMembers(businessId, staffUserIds, startSlotNumber, 96, [startDate], parentLeaveNumber)

                endSlotNumber = AppUtils().convertClockTimeToSlotNumber(endTime)
                self.applyLeaveforStaffMembers(businessId, staffUserIds, 1, endSlotNumber-1, [endDate], parentLeaveNumber)

                leaveDates = AppUtils().getDatesBetween(startDate, endDate, 'NEITHER')
                self.applyLeaveforStaffMembers(businessId, staffUserIds, 1, 96, leaveDates, parentLeaveNumber)

        return True



    def applyLeaveforStaffMembers(self, businessId, staffUserIds, startSlotNumber, endSlotNumber, leaveDates, parentLeaveNumber):

        for staffUserId in staffUserIds:
            print('looping for userid=',staffUserId)
            for leaveDate in leaveDates:
                print('marking unavailability for date=', leaveDate)
                DataAccess().markUnavailability(businessId, staffUserId, 'L', startSlotNumber, endSlotNumber, leaveDate, None, parentLeaveNumber)








































class BookingCore:

    def getReassignemntData(self, businessId, bookingNumber):

        bookingDetails=DataAccess().getBookingDetails(businessId, bookingNumber)
        print(bookingDetails)

        service1Name=bookingDetails[3]
        userIdOfStaff1=DataAccess().getUserId(bookingDetails[10])[0]
        service2Name = bookingDetails[12]
        staff2OnBooking=bookingDetails[9]
        slotDate=bookingDetails[8]
        service1SkilledStaffMembers=None
        service2SkilledStaffMembers=None
        reassignmentDataList = []
        reassignmentData={}

        # PDS
        if (service2Name != None and staff2OnBooking != None):
            reassignmentData['serviceName'] = service1Name
            service1SkilledStaffMembers = DataAccess().getSkilledStaff(businessId, service1Name, None)
            service2SkilledStaffMembers = DataAccess().getSkilledStaff(businessId, service2Name, None)
        # TRS
        elif(service2Name != None and staff2OnBooking == None):
            reassignmentData['serviceName'] = service1Name+', '+service2Name
            service1SkilledStaffMembers = DataAccess().getSkilledStaff(businessId, service1Name, service2Name)
        # PSS
        elif (service2Name == None and staff2OnBooking != None):
            print('in PSS reassignemnt data collection')
            service2Name=service1Name
            reassignmentData['serviceName'] = service1Name
            service1SkilledStaffMembers = DataAccess().getSkilledStaff(businessId, service1Name, None)
            service2SkilledStaffMembers = service1SkilledStaffMembers
        # RS
        elif (service2Name == None and staff2OnBooking == None):
            reassignmentData['serviceName'] = service1Name
            service1SkilledStaffMembers = DataAccess().getSkilledStaff(businessId, service1Name, None)

        slotsOfStaff1InABooking = DataAccess().getSlotsByBookingNumber(bookingNumber, userIdOfStaff1)
        reassignmentData['minSlot'] = slotsOfStaff1InABooking[0]
        reassignmentData['maxSlot'] = slotsOfStaff1InABooking[-1]

        staff1=BookingUtils().getBusinessStaffDetails(businessId, userIdOfStaff1)
        staff1Name=AppUtils().getFullName(staff1.firstname,staff1.lastname)
        service1SelectedMembers=[{'userId':userIdOfStaff1, 'name':staff1Name}]
        print('service1SelectedMembers=',service1SelectedMembers)
        for member in service1SkilledStaffMembers:
            if (self.isPersonAvailableOnSlots (businessId, slotDate, slotsOfStaff1InABooking, member[3])):
                service1SelectedMembers.append({'userId':member[3], 'name':AppUtils().getFullName(member[0],member[1])})
        print('service1SelectedMembers=', service1SelectedMembers)
        reassignmentData['staffList'] = service1SelectedMembers
        reassignmentDataList.append(reassignmentData)
        print('reassignmentDataList=',reassignmentDataList)
        if (service2SkilledStaffMembers!=None):
            reassignmentData2={}
            reassignmentData2['serviceName'] = service2Name
            userIdOfStaff2=DataAccess().getUserId(bookingDetails[11])[0]
            slotsOfStaff2InABooking = DataAccess().getSlotsByBookingNumber(bookingNumber, userIdOfStaff2)
            reassignmentData2['minSlot'] = slotsOfStaff2InABooking[0]
            reassignmentData2['maxSlot'] = slotsOfStaff2InABooking[-1]

            staff2 = BookingUtils().getBusinessStaffDetails(businessId, userIdOfStaff2)
            staff2Name = AppUtils().getFullName(staff2.firstname,staff2.lastname)

            service2SelectedMembers =[{'userId':userIdOfStaff2, 'name':staff2Name}]
            print('service2SelectedMembers=', service2SelectedMembers)
            for member in service2SkilledStaffMembers:
                if (self.isPersonAvailableOnSlots (businessId, slotDate, slotsOfStaff2InABooking, member[3])):
                    service2SelectedMembers.append({'userId':member[3], 'name':AppUtils().getFullName(member[0],member[1])})
            print('service2SelectedMembers=', service2SelectedMembers)
            print('service1SelectedMembers=', service1SelectedMembers)
            reassignmentData2['staffList'] = service2SelectedMembers
            print(reassignmentData2)
            reassignmentDataList.append(reassignmentData2)
            print('reassignmentDataList=',reassignmentDataList)

        return reassignmentDataList



    def isPersonAvailableOnSlots (self, businessId, slotDate, referenceSlots, userIdOfStaff):

        freeSlots=BookingCore().getOnedayAvailabilityOfStaff(businessId, userIdOfStaff, slotDate)
        print('referenceSlots=  ', referenceSlots)
        return all(elem in freeSlots for elem in referenceSlots)



    def applyReassignment(self, bookingNumber, businessId,  appointmentDate, service1, userIdOfStaff1, minSlotNumber1, maxSlotNumber1, service2, userIdOfStaff2, minSlotNumber2, maxSlotNumber2 ):

        DataAccess().markAvailabilityOnBooking(businessId,bookingNumber)

        DataAccess().markUnavailability(businessId, userIdOfStaff1, 'B', minSlotNumber1, maxSlotNumber1, appointmentDate, bookingNumber)
        if (userIdOfStaff2 != None):
            DataAccess().markUnavailability(businessId, userIdOfStaff2, 'B', minSlotNumber2, maxSlotNumber2, appointmentDate, bookingNumber)

        staff1=BookingUtils().getBusinessStaffDetails(businessId,int(userIdOfStaff1))
        # userId, firstname, lastname, emailId
        staff1Name=AppUtils().getFullName(staff1.firstname,staff1.lastname)
        if (userIdOfStaff2 != None):
            staff2 = BookingUtils().getBusinessStaffDetails(businessId, int(userIdOfStaff2))
            staff2Name = AppUtils().getFullName(staff2.firstname, staff2.lastname)
            DataAccess().reAssignBooking(businessId, bookingNumber, staff1Name, staff2Name, staff1.emailId, staff2.emailId)
        else :
            DataAccess().reAssignBooking(businessId, bookingNumber, staff1Name, None, staff1.emailId, None)



    # def getMostAvailableStaffMemberOnADay(self, businessId, staffUserId, service, service2, singleDate, countOfAvailableMembers ):
    #
    #     availabiityRankedMembersOnADay=DataAccess().getAnotherMostAvailableStaffMember (businessId, staffUserId, singleDate)
    #     skilledStaff=DataAccess().getSkilledStaff(businessId, service, service2)
    #     print('freeMemberOrdered = ',availabiityRankedMembersOnADay)
    #     otherSkilledStaff=[]
    #     for staffMember in skilledStaff:
    #         if(staffMember[3] != staffUserId):
    #             otherSkilledStaff.append(staffMember[3])
    #     print('other staff=',otherSkilledStaff)
    #     staffAvailableTheWholeDaySet= set(otherSkilledStaff).difference(availabiityRankedMembersOnADay)
    #     staffAvailableTheWholeDay=list(staffAvailableTheWholeDaySet)
    #     print('staffAvailableTheWholeDay= ', staffAvailableTheWholeDay)
    #     lenStaffAvailableTheWholeDay = len(staffAvailableTheWholeDay)
    #
    #     if (lenStaffAvailableTheWholeDay >= countOfAvailableMembers):
    #         return staffAvailableTheWholeDay[:countOfAvailableMembers]
    #
    #     availabiityRankedSkilledMembersOnADay=list(set(availabiityRankedMembersOnADay).intersection(otherSkilledStaff))
    #     print('availabiityRankedSkilledMembersOnADay=',availabiityRankedSkilledMembersOnADay)
    #     staffAvailableTheWholeDay.extend(availabiityRankedSkilledMembersOnADay)
    #     return staffAvailableTheWholeDay[:countOfAvailableMembers]



    # def getStaffMemberAvailabilityOnADay2(self, userIdOfStaff, businessId, date, serviceName):
    #     if (BookingUtils().checkIfHoliday(businessId, date)):
    #         return None
    #     availbleSlotsAndHours = DataAccess().getAvailabilityOfStaff(businessId,serviceName,None,date,None,None,None)
    #     return availbleSlotsAndHours


        # Replace by use of new table for availability
    # def getStaffMemberAvailabilityOnADay(self, userIdOfStaff, businessId, date, serviceName):
    #     if (BookingUtils().checkIfHoliday(businessId, date)):
    #         return None
    #
    #     workingSlotsAndHours = self.getWorkingSlotsAndHours(userIdOfStaff, businessId, date)
    #     # print('workingSlotsAndHours \n*********************\n')
    #     # print(*workingSlotsAndHours, sep="\n")
    #     # print('\n*********************\n')
    #     unavailableSlots = DataAccess().getUnavailabilityOfStaffMember(userIdOfStaff, businessId, date)
    #     # print('unavailableSlots=\n*********************\n', )
    #     # print(*unavailableSlots, sep="\n")
    #     # print('\n*********************\n')
    #
    #     availbleSlotsAndHours = self.deductUnavailibilityFromWorkTime(workingSlotsAndHours, unavailableSlots)
    #     # print('availbleSlotsAndHours \n*********************\n')
    #     # print(*availbleSlotsAndHours, sep="\n")
    #     service = BookingUtils().getBusinessServiceDefinition(businessId, serviceName)
    #
    #     availableServiceSlots = self.generateSlotsByServiceDuration(availbleSlotsAndHours, service.subslotsCount)
    #     # print('Slots availbale for booking=\n*********************\n')
    #     # print(*availableServiceSlots, sep="\n")
    #     # print('\n*********************\n')
    #
    #     if (date == datetime.today().strftime("%Y-%m-%d")):
    #         clockTime = datetime.now().strftime("%H%M")
    #         availableServiceSlots = self.restOfDayWindow(availableServiceSlots, clockTime)
    #         # print('slots by service duration today=\n', availableServiceSlots)
    #
    #     print(availableServiceSlots)
    #     return availableServiceSlots

    # def getStaffMemberAvailabilityOnADayTRS(self, userIdOfStaff, businessId, date, serviceName1, serviceName2):
    #
    #     if (BookingUtils().checkIfHoliday(businessId, date)):
    #         return None
    #
    #     workingSlotsAndHours = self.getWorkingSlotsAndHours(userIdOfStaff, businessId, date)
    #     unavailableSlots = DataAccess().getUnavailabilityOfStaffMember(userIdOfStaff, businessId, date)
    #
    #     availbleSlotsAndHours = self.deductUnavailibilityFromWorkTime(workingSlotsAndHours, unavailableSlots)
    #     print('availbleSlotsAndHours in the day= \n', availbleSlotsAndHours)
    #     # availbleSlotsAndHoursInWindow = self.getWithinBusinessDayWindow(businessId, availbleSlotsAndHours, date)
    #     # print('available within business window \n', availbleSlotsAndHours)
    #     service1 = BookingUtils().getBusinessServiceDefinition(businessId, serviceName1)
    #     service2 = BookingUtils().getBusinessServiceDefinition(businessId, serviceName2)
    #
    #     availableServiceSlots = self.generateSlotsByServiceDuration(availbleSlotsAndHours,
    #                                                                 (service1.subslotsCount + service2.subslotsCount))
    #     if (date == datetime.today().strftime("%Y-%m-%d")):
    #         clockTime = datetime.now().strftime("%H%M")
    #         availableServiceSlots = self.restOfDayWindow(availableServiceSlots, clockTime)
    #
    #     return availableServiceSlots



    # def getStaffMemberPairAvailabilityForSameService(self, userIdOfStaff1, userIdOfStaff2, businessId, dateOfDay, serviceName):
    #
    #     staff1Availability = self.getStaffMemberAvailabilityOnADay(userIdOfStaff1, businessId, dateOfDay, serviceName)
    #     staff2Availability = self.getStaffMemberAvailabilityOnADay(userIdOfStaff2, businessId, dateOfDay, serviceName)
    #
    #     commonAvailability = []
    #     for staff1Slot in staff1Availability:
    #         for staff2Slot in staff2Availability:
    #             if (staff1Slot[0] == staff2Slot[0]):
    #                 commonAvailability.append(staff1Slot)
    #
    #     return commonAvailability



    # def getStaffMemberPairAvailabilityForDifferentServices(self, userIdOfStaff1, userIdOfStaff2, businessId, date,
    #                                                        serviceName1, serviceName2):
    #
    #     staff1Availability = self.getStaffMemberAvailabilityOnADay(userIdOfStaff1, businessId, date, serviceName1)
    #     staff2Availability = self.getStaffMemberAvailabilityOnADay(userIdOfStaff2, businessId, date, serviceName2)
    #     slotCount1 = self.getBusinessDefinition(serviceName1).subslotsCount
    #     slotCount2 = self.getBusinessDefinition(serviceName2).subslotsCount
    #
    #     if (slotCount1 > slotCount2):
    #         longer = slotCount1
    #         shorter = slotCount2
    #         longerAvailability = staff1Availability
    #         shorterAvailability = staff2Availability
    #     else:
    #         longer = slotCount2
    #         shorter = slotCount1
    #         longerAvailability = staff2Availability
    #         shorterAvailability = staff1Availability
    #
    #     slotCountDiff = longer - shorter
    #     commonAvailability = []
    #     for longerSlot in longerAvailability:
    #         for shorterSlot in shorterAvailability:
    #             if ((longerSlot[0] <= shorterSlot[0]) and (shorterSlot[0] - longerSlot[0] <= slotCountDiff)):
    #                 commonAvailability.append(longerSlot)
    #     return commonAvailability



    # def restOfDayWindow(self, availableServiceSlots, clockTime):
    #     slotNumber = AppUtils().convertClockTimeToSlotNumber(clockTime)
    #     availableServiceSlots = [availbleSlot for availbleSlot in availableServiceSlots if
    #                              (availbleSlot[0] >= slotNumber + 1)]
    #     return availableServiceSlots



    # def deductUnavailibilityFromWorkTime(self, workingSlotsAndHours, unavailableSlots):
    #     for unavailableSlot in unavailableSlots:
    #         self.markUnavailable(unavailableSlot, workingSlotsAndHours)
    #     return workingSlotsAndHours



    # def markUnavailable(self, unavailableSlot, workingSlotsAndHours):
    #     for idx, workingSlot in enumerate(workingSlotsAndHours):
    #         if (unavailableSlot[3] == workingSlot[0]):
    #             workingSlot[2] = 'N'



    # def getWorkingSlotsAndHours(self, userIdOfStaff, businessId, date):
    #     dayOfWeek = datetime.strptime(date, '%Y-%m-%d').weekday()
    #     return DataAccess().getStaffSlotsSetup(userIdOfStaff, businessId, int(dayOfWeek))



    # def generateSlotsByServiceDuration(self, availbleSlotsAndHoursInWindow, slotCount):
    #
    #     print('slotCount=', slotCount)
    #     availableSlotsbyService = []
    #     if (len(slotCount) == 1):
    #         print(availbleSlotsAndHoursInWindow)
    #
    #     for idx, avalaibleSlot in enumerate(availbleSlotsAndHoursInWindow):
    #         if (idx + len(slotCount) <= len(availbleSlotsAndHoursInWindow)):
    #             flag = True
    #             counter = 0
    #             while (counter < len(slotCount)):
    #                 if (availbleSlotsAndHoursInWindow[idx + counter][2] == 'N'):
    #                     flag = False
    #                     break;
    #                 counter = counter + 1
    #             if (flag == True):
    #                 availableSlotsbyService.append(availbleSlotsAndHoursInWindow[idx])
    #
    #     return availableSlotsbyService



    # def getTimebandAvailabilityInBookingWindow(self, ifPartnerService, businessId, services, minSlot, maxSlot, userIdOfStaff):
    #
    #     print('in getTimebandAvailabilityInBookingWindow')
    #     bookingWindow=DataAccess().getBusinessSettings(businessId,'A')
    #
    #     availabilityDict={}
    #     for oneday in range(len(bookingWindow)):
    #
    #         availabilityDate = (date.today() + timedelta(days=oneday)).isoformat()
    #         print('calculating availability for date=')
    #         print(availabilityDate)
    #         oneDayAvailabiityForService,serviceDuration = self.getOnedayAvailabilityForUIDisplay(ifPartnerService, businessId, services, availabilityDate, userIdOfStaff)
    #         #  slice to the range of slots
    #         availabiityForServiceInSlotRangeOnADay=list(x for x in oneDayAvailabiityForService if minSlot <= x <= maxSlot)
    #         availabilityDict[availabilityDate]=availabiityForServiceInSlotRangeOnADay



    # def getOnedayTimebandAvailability(self, ifPartnerService, businessId, services, availabilityDateStr, minSlot, maxSlot, userIdOfStaff):
    #
    #     # availabilityDate = (date.today() + timedelta(days=oneday)).isoformat()
    #
    #     oneDayAvailabiityForService,serviceDuration = self.getOnedayAvailabilityForUIDisplay(ifPartnerService, businessId, services,
    #                                                                          availabilityDateStr, userIdOfStaff)
    #     #  slice to the range of slots
    #     availabiityForServiceInSlotRangeOnADay = list(x for x in oneDayAvailabiityForService if minSlot <= x <= maxSlot)
    #     slotsInClockTime=[]
    #     for slot in availabiityForServiceInSlotRangeOnADay:
    #         slotsInClockTime.append(AppUtils().convertSlotNumberToClockTime(slot))
    #     return slotsInClockTime



    # def getDateRangeToConsiderForAvailability2(self, uiDateString, businessId):
    #
    #     print('in method getDateRangeToConsiderForAvailability')
    #     startDateStr, endDateStr=BookingUtils().getDateRangeFromUIWeekDisplay(uiDateString)
    #     bookingWindow=DataAccess().getBusinessSettings(businessId,'A').preBookingWindow
    #     todayDate=date.today()
    #     startDate=datetime.strptime(startDateStr, "%Y-%m-%d").date()
    #     daysToSunday = 6 - date.today().weekday()
    #     if(todayDate==startDate):
    #         print('if(todayDate==startDate):')
    #         daysRange=bookingWindow
    #         if (daysRange>(daysToSunday+28)):
    #             print('if (daysRange>(daysToSunday+28)):')
    #             daysRange = (daysToSunday + 28)
    #         lastDate=todayDate+timedelta(days=daysRange)
    #         return (datetime.strftime(todayDate, "%Y-%m-%d"),datetime.strftime(lastDate, "%Y-%m-%d"))
    #     else:
    #         print('else to if(todayDate==startDate):')
    #         prevMondayToSelection=startDate-timedelta(days=7)
    #         if (prevMondayToSelection < todayDate):
    #             print('if (prevMondayToSelection < todayDate):')
    #             daysRange = bookingWindow
    #             if (daysRange > (daysToSunday + 28)):
    #                 print('if (daysRange > (daysToSunday + 28)):')
    #                 daysRange = (daysToSunday + 28)
    #             lastDate = todayDate + timedelta(days=daysRange)
    #             return (datetime.strftime(todayDate, "%Y-%m-%d"), datetime.strftime(lastDate, "%Y-%m-%d"))
    #         else:
    #             print('in else to if (prevMondayToSelection < todayDate):')
    #             daysRange=bookingWindow
    #             if (bookingWindow>35):
    #                 print('if (bookingWindow>35):')
    #                 daysRange=35
    #             lastDate = prevMondayToSelection + timedelta(days=daysRange)
    #             if(todayDate+timedelta(days=bookingWindow) > lastDate ):
    #                 print('if(todayDate+timedelta(days=bookingWindow) > lastDate ):')
    #                 lastDate = todayDate+timedelta(days=bookingWindow)
    #
    #             return(datetime.strftime(prevMondayToSelection, "%Y-%m-%d"),datetime.strftime(lastDate, "%Y-%m-%d"))



    def getDateRangeToConsiderForAvailability(self, uiDateString, businessId):

        print('in method getDateRangeToConsiderForAvailability')
        print(uiDateString)
        # Commented the code below and replaced with the line that follows
        startDateStr, endDateStr=BookingUtils().getDateRangeFromUIWeekDisplay(uiDateString)
        print(type(startDateStr))
        print(startDateStr)
        bookingWindow=DataAccess().getBusinessSettings(businessId,'A').preBookingWindow
        print('bookingWindow=',bookingWindow)
        todayDate=date.today()
        print(datetime.strptime(startDateStr, config.applicationUIDateFormat))
        startDate=datetime.strptime(startDateStr, config.applicationUIDateFormat).date()

        if(todayDate + timedelta(days=7) < startDate):
             startDate=startDate-timedelta(days=7)
        elif(todayDate <= startDate):
             startDate=todayDate

        availabilityWindow=int(config.availabilityWindow)
        if (bookingWindow < availabilityWindow):
            availabilityWindow=bookingWindow

        endDate = startDate + timedelta(days=availabilityWindow)
        # Commented the code below and replaced with the line that follows
        # return(datetime.strftime(startDate, config.applicationUIDateFormat),datetime.strftime(endDate, config.applicationUIDateFormat))
        return (startDate, endDate)



    def getAvailabilityForUI(self, ifPartnerService, businessId, services, uiDateString, clockTimeFrom, clockTimeTo, userIdOfStaff):

        print('in method getAvailabilityForUI')
        print('uiDateString=',uiDateString)

        startDate,endDate=self.getDateRangeToConsiderForAvailability(uiDateString, businessId)
        # startDate=datetime.strptime(startDateStr, config.applicationUIDateFormat)
        # endDate=datetime.strptime(endDateStr, config.applicationUIDateFormat)
        weeksInUIFormat=BookingUtils().getUIDisplayWeeksInDateRange(startDate,endDate)
        print('weeksInUIFormat=',weeksInUIFormat)
        weeks=BookingUtils().getWeeksInDateRange(startDate,endDate)
        print('weeks=',weeks)
        minSlot = AppUtils().convertClockTimeToSlotNumber(clockTimeFrom)
        print('in getAvailabilityForUI, minSlot=',minSlot)
        maxSlot= AppUtils().convertClockTimeToSlotNumber(clockTimeTo)
        print('in getAvailabilityForUI, maxSlot=', maxSlot)
        allWeeks=[]

        weekOrder=0
        # weekOrderDict={}
        # weekStringDict={}
        # weekDaysDict = {}
        for i in range(len(weeks)):
            oneWeekDict = {}
            oneWeekDict["weekOrder"]=weekOrder
            weekOrder=weekOrder+1
            oneWeekDict["weekString"]=weeksInUIFormat[i]
            weekdays = [weeks[i][0] + timedelta(days=x) for x in range((weeks[i][1] - weeks[i][0]).days + 1)]
            weekdaysStr=[]
            for weekday in weekdays:
                weekdaysStr.append(datetime.strftime(weekday, config.applicationUIDateFormat))
            oneWeekDict["weekDays"]=weekdaysStr
            allWeeks.append(oneWeekDict)

        availability=self.getAvailabilityInDateAndSlotsRange(ifPartnerService, businessId, services, startDate, endDate, minSlot, maxSlot, userIdOfStaff)
        responseDict={}
        responseDict["weeks"]=allWeeks
        responseDict["availableTimeslots"] = availability
        serviceDuration=availability['serviceDuration']
        print('serviceDuration=',serviceDuration)
        del availability['serviceDuration']
        responseDict["businessName"] = DataAccess().getBusinessMainFields(businessId).businessName
        responseDict["availableTimeslots"] = availability
        responseDict["serviceDuration"] = serviceDuration

        return responseDict



    def getAvailabilityInDateAndSlotsRange(self, ifPartnerService, businessId, services, startDate,endDate, minSlot, maxSlot, userIdOfStaff):

        print('in method getAvailabilityInDateAndSlotsRange')
        print('ifPartnerService:{}, businessId:{}, services:{}, startDate:{},endDate:{}, minSlot:{}, maxSlot:{}, userIdOfStaff:{}'.format(ifPartnerService, businessId, services, startDate,endDate, minSlot, maxSlot, userIdOfStaff))
        # countOfDays = AppUtils().daysBetweenIsoDates(endDate, startDate)
        countOfDays = (endDate - startDate).days + 1
        availabiityDict={}
        # dates = []
        for dayCounter in range(countOfDays):
            # availabilityDateStr = (datetime.strptime(startDate, config.applicationUIDateFormat) + timedelta(days=dayCounter)).date().isoformat()
            availabilityDate = startDate + timedelta(days=dayCounter)
            oneDayAvailabiityForService, serviceDuration = self.getOnedayAvailabilityForUIDisplay(ifPartnerService, businessId, services, availabilityDate, userIdOfStaff, minSlot, maxSlot)
            if (availabilityDate < date.today()):
                oneDayAvailabiityForService = []
            # print()
            # print('serviceDuration=', serviceDuration)
            #  slice to the range of slots
            availabiityForServiceInSlotRangeOnADay = list(x for x in oneDayAvailabiityForService if minSlot <= x <= maxSlot)
            print('availabiityForServiceInSlotRangeOnADay=', availabiityForServiceInSlotRangeOnADay)

            availabiityForServiceByClockTime=[]

            for slotNumber in availabiityForServiceInSlotRangeOnADay:
                clockTime=AppUtils().convertSlotNumberToClockTime(slotNumber)
                availabiityForServiceByClockTime.append(clockTime)
            # dates.append(availabilityDate)

            rowsize = 8
            chunks = [availabiityForServiceByClockTime[i * rowsize:(i + 1) * rowsize] for i in
                      range((len(availabiityForServiceByClockTime) + rowsize - 1) // rowsize)]

            rowDictList = []
            for index, row in enumerate(chunks):
                print("row : ",row)
                row.sort()
                print("sorted row : ", row)
                rowDict = {}
                rowDict['rownum'] = index
                rowDict['slots'] = row
                rowDictList.append(rowDict)

            availabiityDict[availabilityDate.strftime(config.applicationUIDateFormat)] = rowDictList
            availabiityDict['serviceDuration'] = serviceDuration

        return availabiityDict



    def getOnedayAvailabilityForUIDisplay(self, ifPartnerService, businessId, services, appointmentDate, userIdOfStaff, minSlot, maxSlot):

        print('in method getOnedayAvailabilityForUIDisplay')
        print('ifPartnerService:{}, businessId:{}, services:{}, appointmentDate:{}, userIdOfStaff:{}, minSlot:{}, maxSlot:{}'.format(ifPartnerService, businessId, services, appointmentDate, userIdOfStaff, minSlot, maxSlot))
        serviceType=BookingCore().determineTypeOfService(businessId, services, ifPartnerService)
        serviceDuration=0
        print('serviceType=',serviceType)
        availability=[]
        if (serviceType == 'PSS'):
            print('apply partner same service logic')
            availability = self.getAvailabilityForBookingPageDisplayPSS(userIdOfStaff, businessId, appointmentDate, services[0], minSlot, maxSlot)
            serviceDuration=BookingUtils().getBusinessServiceDefinition(businessId,services[0]).duration
            # serviceDuration =len(serviceDuration)*gSingleTimeslotDuration
        elif (serviceType == 'PDS'):
            print('apply partner different service logic')
            availability=self.getAvailabilityForBookingPageDisplayPDS(userIdOfStaff,businessId,appointmentDate,services[0],services[1], minSlot, maxSlot)
            print('one day PDS availability')
            print(*availability, sep='\n')
            serviceDuration1=BookingUtils().getBusinessServiceDefinition(businessId, services[0]).duration
            serviceDuration2 = BookingUtils().getBusinessServiceDefinition(businessId, services[1]).duration
            if (serviceDuration1 >= serviceDuration2):
                serviceDuration=serviceDuration1
            else :
                serviceDuration=serviceDuration2
        elif (serviceType == 'TRS'):
            print('apply two regulr services logic')
            availability= self.getAvailabilityForBookingPageDisplayTRS(userIdOfStaff, businessId, appointmentDate, services[0], services[1], minSlot, maxSlot)
            serviceDuration1=BookingUtils().getBusinessServiceDefinition(businessId, services[0]).duration
            serviceDuration2 = BookingUtils().getBusinessServiceDefinition(businessId, services[1]).duration
            # serviceDuration=int(serviceDuration1)+int(serviceDuration2)
            serviceDuration = serviceDuration1 + serviceDuration2
        elif (serviceType == 'RS'):
            print('apply regular service logic')
            availability= self.getAvailabilityForBookingPageDisplayRS(userIdOfStaff, businessId, appointmentDate, services[0], minSlot, maxSlot)
            print('in getAvailabilityForBookingPageDisplay, type of date is=',type(appointmentDate))
            serviceDuration=BookingUtils().getBusinessServiceDefinition(businessId, services[0]).duration
            print('in RS, serviceDuration=', serviceDuration)

        elif (serviceType == 'DTS'):
            print('apply double time service logic')
            #availability= self.getAvailabilityForBookingPageDisplayRS(userIdOfStaff, businessId, appointmentDate, services[0], minSlot, maxSlot)
            availability= self.getAvailabilityForBookingPageDisplayDTS(userIdOfStaff, businessId, appointmentDate, services[0], minSlot, maxSlot)
            print('in getAvailabilityForBookingPageDisplay, type of date is=',type(appointmentDate))
            serviceDuration=BookingUtils().getBusinessServiceDefinition(businessId, services[0]).duration

        return availability, serviceDuration

    def getAvailabilityForBookingPageDisplayDTS(self, userIdOfStaff, businessId, dateOfDay, serviceName, minSlot, maxSlot):
        print('in getAvailabilityForBookingPageDisplayDTS def')

        service = BookingUtils().getBusinessServiceDefinition(businessId, serviceName)
         
        availableServiceSlotsList=[]

        if (int(userIdOfStaff)==0):
            print('in if jun15')
            skilledStaffMembers=DataAccess().getSkilledStaff(businessId,serviceName,None)
            print('skilledStaffMembers=',skilledStaffMembers)
            # availableServiceSlotsSet=set([])
            sortedFreeSlotsOfAllStaffMembers=[]
            for member in skilledStaffMembers:
                print(member[3])
                sortedFreeSlotsOfOneStaffMember = self.getOnedayAvailabilityOfStaffOfDTS(businessId, member[3], dateOfDay, 'DTS', service, serviceName)
                sortedFreeSlotsOfAllStaffMembers.append(sortedFreeSlotsOfOneStaffMember)
            # availableServiceSlotsList=BookingUtils().getUnionAvailabilityOfStaff(sortedFreeSlotsOfAllStaffMembers, service.duration//15)
            print('sortedFreeSlotsOfAllStaffMembers=',sortedFreeSlotsOfAllStaffMembers)
            if (skilledStaffMembers!=None and len(skilledStaffMembers) > 0):
                availableServiceSlotsList = BookingUtils().getUnionAvailabilityOfStaffForDTS(sortedFreeSlotsOfAllStaffMembers)
               # availableServiceSlotsList = BookingUtils().getUnionAvailabilityOfStaff(sortedFreeSlotsOfAllStaffMembers,
                #                                                                   service.duration // int(config.gSingleTimeslotDuration))
            # print('availableServiceSlotsList=', availableServiceSlotsList)
        else:
            print('in else jun15')
            sortedFreeSlotsOfStaffMember=self.getOnedayAvailabilityOfStaffOfDTS(businessId, userIdOfStaff, dateOfDay, 'DTS', service, serviceName)
            print('sortedFreeSlotsOfStaffMember=',sortedFreeSlotsOfStaffMember)
            # availableServiceSlotsList=AppUtils().getConsecutiveChunks(sortedFreeSlotsOfStaffMember, service.duration//15)
            availableServiceSlotsList = sortedFreeSlotsOfStaffMember
            #AppUtils().getConsecutiveChunks(sortedFreeSlotsOfStaffMember,ervice.duration // int(config.gSingleTimeslotDuration))
        print('availableServiceSlotsList=',availableServiceSlotsList)

        print('after if else jun15')
        if (len(availableServiceSlotsList)>0):
            availableServiceSlotsList=BookingUtils().applyBookingIntervalToAvailableSlots(dateOfDay,businessId,availableServiceSlotsList)
        return availableServiceSlotsList



    def getAvailabilityForBookingPageDisplayRS(self, userIdOfStaff, businessId, dateOfDay, serviceName, minSlot, maxSlot):

        service = BookingUtils().getBusinessServiceDefinition(businessId, serviceName)
        availableServiceSlotsList=[]

        if (int(userIdOfStaff)==0):
            print('in if jun15')
            skilledStaffMembers=DataAccess().getSkilledStaff(businessId,serviceName,None)
            print('skilledStaffMembers=',skilledStaffMembers)
            # availableServiceSlotsSet=set([])
            sortedFreeSlotsOfAllStaffMembers=[]
            for member in skilledStaffMembers:
                print(member[3])
                sortedFreeSlotsOfOneStaffMember = self.getOnedayAvailabilityOfStaff(businessId, member[3], dateOfDay)
                sortedFreeSlotsOfAllStaffMembers.append(sortedFreeSlotsOfOneStaffMember)
            # availableServiceSlotsList=BookingUtils().getUnionAvailabilityOfStaff(sortedFreeSlotsOfAllStaffMembers, service.duration//15)
            print('sortedFreeSlotsOfAllStaffMembers=',sortedFreeSlotsOfAllStaffMembers)
            if (skilledStaffMembers!=None and len(skilledStaffMembers) > 0):
                availableServiceSlotsList = BookingUtils().getUnionAvailabilityOfStaff(sortedFreeSlotsOfAllStaffMembers,
                                                                                   service.duration // int(config.gSingleTimeslotDuration))
            # print('availableServiceSlotsList=', availableServiceSlotsList)
        else:
            print('in else jun15')
            sortedFreeSlotsOfStaffMember=self.getOnedayAvailabilityOfStaff(businessId, userIdOfStaff, dateOfDay)
            print('sortedFreeSlotsOfStaffMember=',sortedFreeSlotsOfStaffMember)
            # availableServiceSlotsList=AppUtils().getConsecutiveChunks(sortedFreeSlotsOfStaffMember, service.duration//15)
            availableServiceSlotsList = AppUtils().getConsecutiveChunks(sortedFreeSlotsOfStaffMember,
                                                                        service.duration // int(config.gSingleTimeslotDuration))
        print('availableServiceSlotsList=',availableServiceSlotsList)

        print('after if else jun15')
        if (len(availableServiceSlotsList)>0):
            availableServiceSlotsList=BookingUtils().applyBookingIntervalToAvailableSlots(dateOfDay,businessId,availableServiceSlotsList)
        # if (dateOfDay == datetime.today().strftime("%Y-%m-%d")):
        #     runningSlot=AppUtils().getTheRunningSlot()
        #     # bookingIntervalSlotCount=int((DataAccess().getBusinessSettings(businessId,'A').bookingInterval))//15 +1
        #     bookingIntervalSlotCount = int(
        #         (DataAccess().getBusinessSettings(businessId, 'A').bookingInterval)) // int(config.gSingleTimeslotDuration) + 1
        #
        #     minSlotForBookingToday=runningSlot+bookingIntervalSlotCount
        #
        #     availableServiceSlotsList =AppUtils().getHigherElementsInSortedList(availableServiceSlotsList, minSlotForBookingToday)

        return availableServiceSlotsList

    def getSomething(self,userIdOfStaff, businessId, duration, serviceName, dateOfDay):

        availableServiceSlotsList=[]
        if (int(userIdOfStaff)==0):
            skilledStaffMembers=DataAccess().getSkilledStaff(businessId,serviceName,None)
            print(*skilledStaffMembers, sep='\n')
            sortedFreeSlotsOfAllStaffMembers=[]
            for member in skilledStaffMembers:
                sortedFreeSlotsOfOneStaffMember = self.getOnedayAvailabilityOfStaff(businessId, member[3], dateOfDay)
                sortedFreeSlotsOfAllStaffMembers.append(sortedFreeSlotsOfOneStaffMember)
            print(sortedFreeSlotsOfAllStaffMembers)
            # availableServiceSlotsList=BookingUtils().getUnionAvailabilityOfStaff(sortedFreeSlotsOfAllStaffMembers,  (service1.duration//15+ service2.duration//15) )
            availableServiceSlotsList = BookingUtils().getUnionAvailabilityOfStaff(sortedFreeSlotsOfAllStaffMembers, (
                        duration// int(config.gSingleTimeslotDuration) ))
            print('availableServiceSlotsList= \n',availableServiceSlotsList)
            # int(config.gSingleTimeslotDuration)
        else:
            sortedFreeSlotsOfStaffMember=self.getOnedayAvailabilityOfStaff(businessId, userIdOfStaff, dateOfDay)
            # availableServiceSlotsList=AppUtils().getConsecutiveChunks(sortedFreeSlotsOfStaffMember, (service1.duration//15+ service2.duration//15) )
            availableServiceSlotsList = AppUtils().getConsecutiveChunks(sortedFreeSlotsOfStaffMember, (
                        duration // int(config.gSingleTimeslotDuration)))

        availableServiceSlotsList=BookingUtils().applyBookingIntervalToAvailableSlots(dateOfDay,businessId,availableServiceSlotsList)

        return availableServiceSlotsList


    def getAvailabilityForBookingPageDisplayTRS(self, userIdOfStaff, businessId, dateOfDay, serviceName1, serviceName2, minSlot, maxSlot):

        print('in getAvailabilityForBookingPageDisplayTRS')
        print('userIdOfStaff:{}, businessId:{}, dateOfDay:{}, serviceName1:{}, serviceName2:{}, minSlot:{}, maxSlot:{}'.format(userIdOfStaff, businessId, dateOfDay, serviceName1, serviceName2, minSlot, maxSlot))
        service1 = BookingUtils().getBusinessServiceDefinition(businessId, serviceName1)
        service2 = BookingUtils().getBusinessServiceDefinition(businessId, serviceName2)

        serviceA_UnitedSlots = self.getSomething(userIdOfStaff, businessId, service1.duration, service1.name, dateOfDay)
        serviceC_UnitedSlots = self.getSomething(userIdOfStaff, businessId, service2.duration, service2.name, dateOfDay)    

        finalSlotsList = []
        for everyslot in serviceA_UnitedSlots:
            if ((everyslot + (service1.duration // int(config.gSingleTimeslotDuration))) in serviceC_UnitedSlots):
                finalSlotsList.append(everyslot)

        print("finalSlotsList : "+ str(finalSlotsList))
        return finalSlotsList


    # def getAvailabilityForBookingPageDisplayTRS(self, userIdOfStaff, businessId, dateOfDay, serviceName1, serviceName2, minSlot, maxSlot):

    #     print('in getAvailabilityForBookingPageDisplayTRS')
    #     print('userIdOfStaff:{}, businessId:{}, dateOfDay:{}, serviceName1:{}, serviceName2:{}, minSlot:{}, maxSlot:{}'.format(userIdOfStaff, businessId, dateOfDay, serviceName1, serviceName2, minSlot, maxSlot))
    #     service1 = BookingUtils().getBusinessServiceDefinition(businessId, serviceName1)
    #     service2 = BookingUtils().getBusinessServiceDefinition(businessId, serviceName2)

    #     serviceA_UnitedSlots = getSomething(service1)
    #     serviceC_UnitedSlots = getSomething(service2)     

    #     finalSlotsList = []
    #     for everyslot in serviceA_UnitedSlots:
    #         if ((everyslot + service1Duration) in serviceC_UnitedSlots):
    #             finalSlotsList.append(everyslot)

    #     print("finalSlotsList : "+ str(finalSlotsList))

    #     availableServiceSlotsList=[]
    #     if (int(userIdOfStaff)==0):
    #         skilledStaffMembers=DataAccess().getSkilledStaff(businessId,serviceName1,serviceName2)
    #         print(*skilledStaffMembers, sep='\n')
    #         sortedFreeSlotsOfAllStaffMembers=[]
    #         for member in skilledStaffMembers:
    #             sortedFreeSlotsOfOneStaffMember = self.getOnedayAvailabilityOfStaff(businessId, member[3], dateOfDay)
    #             sortedFreeSlotsOfAllStaffMembers.append(sortedFreeSlotsOfOneStaffMember)
    #         print(sortedFreeSlotsOfAllStaffMembers)
    #         # availableServiceSlotsList=BookingUtils().getUnionAvailabilityOfStaff(sortedFreeSlotsOfAllStaffMembers,  (service1.duration//15+ service2.duration//15) )
    #         availableServiceSlotsList = BookingUtils().getUnionAvailabilityOfStaff(sortedFreeSlotsOfAllStaffMembers, (
    #                     service1.duration // int(config.gSingleTimeslotDuration) + service2.duration // int(config.gSingleTimeslotDuration)))
    #         print('availableServiceSlotsList= \n',availableServiceSlotsList)
    #         # int(config.gSingleTimeslotDuration)
    #     else:
    #         sortedFreeSlotsOfStaffMember=self.getOnedayAvailabilityOfStaff(businessId, userIdOfStaff, dateOfDay)
    #         # availableServiceSlotsList=AppUtils().getConsecutiveChunks(sortedFreeSlotsOfStaffMember, (service1.duration//15+ service2.duration//15) )
    #         availableServiceSlotsList = AppUtils().getConsecutiveChunks(sortedFreeSlotsOfStaffMember, (
    #                     service1.duration // int(config.gSingleTimeslotDuration) + service2.duration // int(config.gSingleTimeslotDuration)))

    #     availableServiceSlotsList=BookingUtils().applyBookingIntervalToAvailableSlots(dateOfDay,businessId,availableServiceSlotsList)

    #     return availableServiceSlotsList



    def getAvailabilityForBookingPageDisplayPSS(self, userIdOfStaff1,  businessId, dateOfDay, serviceName, minSlot, maxSlot):

        service = BookingUtils().getBusinessServiceDefinition(businessId, serviceName)
        skilledStaffMembers = DataAccess().getSkilledStaff(businessId, serviceName, None)
        availableServiceSlotsList = []
        if (len(skilledStaffMembers)==1):
            return availableServiceSlotsList
        if (int(userIdOfStaff1)!=0):
            availableServiceSlotsList=self.getCombinedAvailability(businessId, dateOfDay, service, service, skilledStaffMembers, userIdOfStaff1, minSlot, maxSlot)
        else:
            availabilityOptions=[]
            for member in skilledStaffMembers:
                availableServiceSlotsList = self.getCombinedAvailability(businessId, dateOfDay, service, service, skilledStaffMembers, member[3], minSlot, maxSlot)
                availabilityOptions.append(availableServiceSlotsList)
            # Choose the longest among the service slot lists

            if (len(availabilityOptions)>0):
                max_len = max([len(x) for x in availabilityOptions])
                maxAvailability = [x for x in availabilityOptions if len(x) == max_len][0]
                availableServiceSlotsList=maxAvailability

        availableServiceSlotsList=BookingUtils().applyBookingIntervalToAvailableSlots(dateOfDay,businessId,availableServiceSlotsList)
        return availableServiceSlotsList



    def getCombinedAvailability(self, businessId, dateOfDay, service, serviceOfRest, skilledStaffMembers, userIdOfStaff, minSlot, maxSlot):
        print('skilled members')
        print(*skilledStaffMembers, sep='\n')
        print('selected user= ',userIdOfStaff)
        # print(*bookings, sep='\n')
        availableServiceSlotsSet = set([])
        sortedFreeSlotsOfAllStaffMembers = []
        for member in skilledStaffMembers:
            print(member)
            print(member[3])
            if (member[3] != userIdOfStaff):
                print('check user= ', member[3])
                # sortedFreeSlotsOfOneStaffMember = self.getOnedayAvailabilityOfStaff(businessId, member[3], dateOfDay)
                slotRange={}
                slotRange["startSlotNumber"]=minSlot
                slotRange["endSlotNumber"]=maxSlot
                sortedFreeSlotsOfOneStaffMember = self.getSlotRangeAvailabilityOfStaff(businessId, member[3], dateOfDay, slotRange)
                sortedFreeSlotsOfAllStaffMembers.append(sortedFreeSlotsOfOneStaffMember)

        print('after looping')
        print(sortedFreeSlotsOfAllStaffMembers)
        availableServiceSlotsList = BookingUtils().getUnionAvailabilityOfStaff(sortedFreeSlotsOfAllStaffMembers,
                                                                               serviceOfRest.duration // int(config.gSingleTimeslotDuration))
        print(availableServiceSlotsList)
        sortedFreeSlotsOfUser = self.getOnedayAvailabilityOfStaff(businessId, userIdOfStaff, dateOfDay)
        print(sortedFreeSlotsOfUser)
        availableServiceSlotsUser = AppUtils().getConsecutiveChunks(sortedFreeSlotsOfUser,  service.duration//int(config.gSingleTimeslotDuration))
        print(availableServiceSlotsUser)
        if (len(skilledStaffMembers) == 1):
            availableServiceSlotsSet = set(availableServiceSlotsUser)
        else:
            availableServiceSlotsSet = set(availableServiceSlotsList) & set(availableServiceSlotsUser)  
        # availableServiceSlotsSet = set(availableServiceSlotsList) & set(availableServiceSlotsUser)
        # availableServiceSlotsSet = set(availableServiceSlotsList) | set(availableServiceSlotsUser)
        print(availableServiceSlotsSet)
        return list(availableServiceSlotsSet)



    def getAvailabilityForBookingPageDisplayPDS(self, userIdOfStaff1,  businessId, dateOfDay, serviceName1, serviceName2, minSlot, maxSlot):

        service1 = BookingUtils().getBusinessServiceDefinition(businessId, serviceName1)
        service1SkilledStaffMembers = DataAccess().getSkilledStaff(businessId, serviceName1, None)
        service1SkilledStaffMembersIds = [x[3] for x in service1SkilledStaffMembers]

        service2 = BookingUtils().getBusinessServiceDefinition(businessId, serviceName2)
        service2SkilledStaffMembers = DataAccess().getSkilledStaff(businessId, serviceName2, None)
        service2SkilledStaffMembersIds = [x[3] for x in service2SkilledStaffMembers]
        availableServiceSlotsList = []
        if (int(userIdOfStaff1)!=0):
            print('user id is not 0')
            availableServiceSlotsList = self.getCombinedAvailability(businessId, dateOfDay, service1, service2, service2SkilledStaffMembers, userIdOfStaff1, minSlot, maxSlot)
        if (int(userIdOfStaff1)==0):
            print('user id is 0')
            slotRange = {}
            slotRange["startSlotNumber"] = minSlot
            slotRange["endSlotNumber"] = maxSlot


            maxAvailableSlots = ('0', [])
            for staffUserId in service1SkilledStaffMembersIds:

                availableSlots = self.getCombinedAvailability(businessId, dateOfDay, service1, service2, service2SkilledStaffMembers,
                                             staffUserId, minSlot, maxSlot)
                print('availableSlots=', availableSlots)
                if (len(availableSlots) > len(maxAvailableSlots[1])):
                    maxAvailableSlots = (staffUserId, availableSlots)

            for staffUserId in service2SkilledStaffMembersIds:
                availableSlots = self.getCombinedAvailability(businessId, dateOfDay, service2, service1, service1SkilledStaffMembers,
                                             staffUserId, minSlot, maxSlot)
                print('availableSlots=', availableSlots)
                if (len(availableSlots) > len(maxAvailableSlots[1])):
                    maxAvailableSlots = (staffUserId, availableSlots)

            availableServiceSlotsList = maxAvailableSlots[1]

        availableServiceSlotsList=BookingUtils().applyBookingIntervalToAvailableSlots(dateOfDay,businessId,availableServiceSlotsList)

        return availableServiceSlotsList


    # def bookRS(self, businessId, businessName, serviceName, clockTimeRange, appointmentDate,
    #                             userIdOfStaff, customerEmail, customerName):
    #
    #     if (userIdOfStaff==0):
    #         userIdOfStaff = BookingCore().getMostAvailableStaffMemberOnADay(businessId, 0, serviceName, None,
    #                                                                       appointmentDate, 1)[0]
    #
    #     bookingNumber = BookingUtils().generateBookingNumber(businessId, appointmentDate)
    #     BookingUtils().markUnavailability(businessId, userIdOfStaff, 'B', None, clockTimeRange, appointmentDate, 'N',bookingNumber)
    #
    #
    #     staff=BookingUtils().getBusinessStaffDetails(businessId,userIdOfStaff)
    #     slotsRange=AppUtils().convertClockTimeRangeToSlotsRange(clockTimeRange)
    #     print(slotsRange)
    #     slotsRangeStr=str(slotsRange["startSlotNumber"])+' - '+str(slotsRange["endSlotNumber"])
    #     dayOfWeek = datetime.strptime(appointmentDate, '%Y-%m-%d').weekday()
    #     DataAccess().makeBooking(businessId, customerEmail, bookingNumber, serviceName, AppUtils().getFullName(staff.firstname,staff.lastname),None, slotsRangeStr, clockTimeRange, customerName, appointmentDate, None, staff.emailId, None, dayOfWeek, serviceName,businessName)
    #     # NotificationsCore().sendBookingEmail(businessName, bookerEmail, serviceName, staffMemberName, additionalEmail,
    #     #                                      serviceClockTimeRange, bookerName, appointmentDate)
    #
    #     return bookingNumber



    # def bookTRS(self, businessId, businessName, service1Name, service2Name, clockTimeRange, appointmentDate,
    #                             userIdOfStaff, customerEmail, customerName):
    #     if (userIdOfStaff==0):
    #         userIdOfStaff = BookingCore().getMostAvailableStaffMemberOnADay(businessId, 0, service1Name,service2Name, None,
    #                                                                       appointmentDate, 1)[0]
    #
    #     BookingUtils().markUnavailability(businessId, userIdOfStaff, 'B', None, clockTimeRange, appointmentDate, 'N')
    #
    #     bookingNumber=BookingUtils().generateBookingNumber(businessId, appointmentDate)
    #     staff=BookingUtils().getBusinessStaffDetails(businessId,userIdOfStaff)
    #     print('staff=',staff)
    #     slotsRange=AppUtils().convertClockTimeRangeToSlotsRange(clockTimeRange)
    #     dayOfWeek = datetime.strptime(appointmentDate, '%Y-%m-%d').weekday()
    #     DataAccess().makeBooking(businessId, customerEmail, bookingNumber, service1Name, AppUtils().getFullName(staff.firstname,staff.lastname), None, slotsRange,
    #                              clockTimeRange, customerName, appointmentDate, None, staff.emailId, None, dayOfWeek, service2Name, businessName)
    #     # NotificationsCore().sendBookingEmail(businessName, bookerEmail, serviceName, staffMemberName, additionalEmail,
    #     #                                      serviceClockTimeRange, bookerName, appointmentDate)
    #
    #     return bookingNumber



    # def bookPSS(self, businessId, businessName, serviceName, clockTimeRange, appointmentDate,
    #                             userIdOfStaff1, customerEmail, customerName, partnerEmail ):
    #     if (userIdOfStaff1==0):
    #         userIdOfStaff1 = BookingCore().getMostAvailableStaffMemberOnADay(businessId, 0, serviceName,None, None,
    #                                                                       appointmentDate, 1)[0]
    #     userIdOfStaff2 = BookingCore().getMostAvailableStaffMemberOnADay(businessId, userIdOfStaff1, serviceName,None, None,
    #                                                                       appointmentDate, 1)[0]
    #
    #     BookingUtils().markUnavailability(businessId, userIdOfStaff1, 'B', None, clockTimeRange, appointmentDate, 'N')
    #     BookingUtils().markUnavailability(businessId, userIdOfStaff2, 'B', None, clockTimeRange, appointmentDate, 'N')
    #
    #     bookingNumber=BookingUtils().generateBookingNumber(businessId, appointmentDate)
    #     staff1=BookingUtils().getBusinessStaffDetails(businessId,userIdOfStaff1)
    #     staff2 = BookingUtils().getBusinessStaffDetails(businessId, userIdOfStaff2)
    #     slotsRange = AppUtils().convertClockTimeRangeToSlotsRange(clockTimeRange)
    #     dayOfWeek = datetime.strptime(appointmentDate, '%Y-%m-%d').weekday()
    #     DataAccess().makeBooking(businessId, customerEmail, bookingNumber, serviceName, AppUtils().getFullName(staff1.firstname,staff1.lastname),partnerEmail, slotsRange,
    #                              clockTimeRange, customerName, appointmentDate, AppUtils().getFullName(staff2.firstname,staff2.lastname), staff1.emailId, staff2.emailId, dayOfWeek, serviceName, businessName)
    #
    #     # NotificationsCore().sendBookingEmail(businessName, bookerEmail, serviceName, staffMemberName, additionalEmail,
    #     #                                      serviceClockTimeRange, bookerName, appointmentDate)
    #
    #     return bookingNumber



    # def bookPDS(self, businessId, businessName, service1Name, service2Name,clockTimeRange, appointmentDate,
    #                             userIdOfStaff1, customerEmail, customerName, partnerEmail ):
    #     if (userIdOfStaff1==0):
    #         userIdOfStaff1 = BookingCore().getMostAvailableStaffMemberOnADay(businessId, 0, service1Name,None, None,
    #                                                                       appointmentDate, 1)[0]
    #     userIdOfStaff2 = BookingCore().getMostAvailableStaffMemberOnADay(businessId, userIdOfStaff1, service2Name, None, None,
    #                                                                       appointmentDate, 1)[0]
    #
    #     # Get dustaion based on services and not the clock time on UI
    #     duration1=len(BookingUtils().getBusinessServiceDefinition(businessId,service1Name).subslotsCount)
    #     duration2=len(BookingUtils().getBusinessServiceDefinition(businessId,service2Name).subslotsCount)
    #     slotsRange = AppUtils().convertClockTimeRangeToSlotsRange(clockTimeRange)
    #     minSlot=slotsRange["startSlotNumber"]
    #     maxSlot = slotsRange["endSlotNumber"]
    #     if (duration1 > duration2):
    #         BookingUtils().markUnavailability(businessId, userIdOfStaff1, 'B', None, clockTimeRange, appointmentDate, 'N')
    #
    #         unavailbility2=DataAccess().getUnavailabilityOfStaffMember(userIdOfStaff2,businessId,appointmentDate)
    #         if (len(unavailbility2)==0):
    #             s2Range=minSlot+ ' - '+minSlot+duration2
    #             BookingUtils().markUnavailability(businessId, userIdOfStaff2, 'B', s2Range, None, appointmentDate,'N')
    #         else:
    #             startSlotAvailability2=minSlot
    #             for unavailableSlot in unavailbility2:
    #                 if (unavailableSlot >= minSlot):
    #                     if(unavailableSlot <=maxSlot):
    #                         startSlotAvailability2=startSlotAvailability2+1
    #                     elif (startSlotAvailability2+duration2 <= maxSlot):
    #                         break
    #             slot2Range=startSlotAvailability2+' - '+maxSlot
    #             BookingUtils().markUnavailability(businessId, userIdOfStaff2, 'B', slot2Range, None, appointmentDate,
    #                                               'N')
    #     else:
    #         BookingUtils().markUnavailability(businessId, userIdOfStaff2, 'B', None, clockTimeRange, appointmentDate, 'N')
    #
    #         unavailbility1 = DataAccess().getUnavailabilityOfStaffMember(userIdOfStaff1, businessId, appointmentDate)
    #         if (len(unavailbility1) == 0):
    #             s1Range = minSlot + ' - ' + minSlot + duration1
    #             BookingUtils().markUnavailability(businessId, userIdOfStaff1, 'B', s1Range, None, appointmentDate, 'N')
    #         else:
    #             startSlotAvailability1 = minSlot
    #             for unavailableSlot in unavailbility1:
    #                 if (unavailableSlot >= minSlot):
    #                     if (unavailableSlot <= maxSlot):
    #                         startSlotAvailability1 = startSlotAvailability1 + 1
    #                     elif (startSlotAvailability1 + duration2 <= maxSlot):
    #                         break
    #             slot1Range = startSlotAvailability1 + ' - ' + maxSlot
    #             BookingUtils().markUnavailability(businessId, userIdOfStaff1, 'B', slot1Range, None, appointmentDate,'N')
    #
    #     bookingNumber=BookingUtils().generateBookingNumber(businessId, appointmentDate)
    #     staff1=BookingUtils().getBusinessStaffDetails(businessId,userIdOfStaff1)
    #     staff2 = BookingUtils().getBusinessStaffDetails(businessId, userIdOfStaff2)
    #
    #     dayOfWeek = datetime.strptime(appointmentDate, '%Y-%m-%d').weekday()
    #     DataAccess().makeBooking(businessId, customerEmail, bookingNumber, service1Name, AppUtils().getFullName(staff1.firstname,staff1.lastname), partnerEmail, slotsRange,
    #                              clockTimeRange, customerName, appointmentDate, AppUtils().getFullName(staff2.firstname,staff2.lastname), staff1.emailId, staff2.emailId, dayOfWeek, service2Name, businessName)
    #
    #     # NotificationsCore().sendBookingEmail(businessName, bookerEmail, serviceName, staffMemberName, additionalEmail,
    #     #                                      serviceClockTimeRange, bookerName, appointmentDate)
    #
    #     return bookingNumber



    # def bookDTS(self, businessId, businessName, serviceName, clockTimeRange, appointmentDate,
    #                             userIdOfStaff, customerEmail, customerName ):
    #     if (userIdOfStaff==0):
    #         userIdOfStaff = BookingCore().getMostAvailableStaffMemberOnADay(businessId, 0, serviceName,None, None,
    #                                                                       appointmentDate, 1)[0]
    #
    #     slotsRange = AppUtils().convertClockTimeRangeToSlotsRange(clockTimeRange)
    #     subSlots=BookingUtils().getBusinessServiceDefinition(businessId,serviceName).subslotsCount
    #     occupiedSlots=re.split("F+", subSlots)
    #     occupiedSlotsRange1=slotsRange["startSlotNumber"]+ ' - '+slotsRange["startSlotNumber"]+len(occupiedSlots[0])
    #     occupiedSlotsRange2 = slotsRange["endSlotNumber"] - len(occupiedSlots[1])+' - ' +slotsRange["endSlotNumber"]
    #
    #     # duration2=len(BookingUtils().getBusinessServiceDefinition(businessId, serviceName).subslotsCount)
    #
    #     BookingUtils().markUnavailability(businessId, userIdOfStaff, 'B', occupiedSlotsRange1, None, appointmentDate, 'N')
    #     BookingUtils().markUnavailability(businessId, userIdOfStaff, 'B', occupiedSlotsRange2, None, appointmentDate, 'N')
    #
    #     bookingNumber=BookingUtils().generateBookingNumber(businessId, appointmentDate)
    #     staff=BookingUtils().getBusinessStaffDetails(businessId,userIdOfStaff)
    #
    #     dayOfWeek = datetime.strptime(appointmentDate, '%Y-%m-%d').weekday()
    #     DataAccess().makeBooking(businessId, customerEmail, bookingNumber, serviceName, AppUtils().getFullName(staff.firstname,staff.lastname), None, slotsRange,
    #                              clockTimeRange, customerName, appointmentDate, None, staff.emailId, None, dayOfWeek, None, businessName)
    #
    #     # NotificationsCore().sendBookingEmail(businessName, bookerEmail, serviceName, staffMemberName, additionalEmail,
    #     #                                      serviceClockTimeRange, bookerName, appointmentDate)
    #
    #     return bookingNumber



    # def bookRSNew(self, businessId, businessName, serviceName, clockTimeRange, appointmentDate, userIdOfStaff, customerEmail, customerName,bookerComment):
    #
    #     slotsRange = AppUtils().convertClockTimeRangeToSlotsRange(clockTimeRange)
    #
    #     if (userIdOfStaff==0):
    #         slotsCount=slotsRange["endSlotNumber"] - slotsRange["startSlotNumber"]
    #
    #         result=DataAccess().getStaffMembersForBooking(businessId,serviceName,None, appointmentDate,slotsRange,None)
    #         shortlistedUsers=[]
    #         for oneUser in result:
    #             if(oneUser[1]>=slotsCount):
    #                 shortlistedUsers.append(oneUser[0])
    #         print(shortlistedUsers)
    #
    #         if (len(shortlistedUsers) ==1 ):
    #             userIdOfStaff=shortlistedUsers[0]
    #         else:
    #             staffRankedByAvailabiity = DataAccess().rankStaffMembersByAvailabilityOnADay(businessId, appointmentDate, shortlistedUsers)
    #             userIdOfStaff = staffRankedByAvailabiity[0]
    #
    #     bookingNumber = BookingUtils().generateBookingNumber(businessId, appointmentDate)

        # print('bookingNumber=',bookingNumber)
        #
        # DataAccess().markUnavailability(businessId,userIdOfStaff,'B', slotsRange["startSlotNumber"], slotsRange["endSlotNumber"],appointmentDate,bookingNumber)
        #
        # staff=BookingUtils().getBusinessStaffDetails(businessId,userIdOfStaff)
        # slotsRangeStr=str(slotsRange["startSlotNumber"])+' - '+str(slotsRange["endSlotNumber"])
        # dayOfWeek = datetime.strptime(appointmentDate, '%Y-%m-%d').weekday()
        # DataAccess().makeBooking(businessId, customerEmail, bookingNumber, serviceName, AppUtils().getFullName(staff.firstname,staff.lastname), None, slotsRangeStr,
        #                          clockTimeRange, customerName, appointmentDate, None, staff.emailId, None, dayOfWeek, None,businessName,bookerComment)


        # NotificationsCore().sendBookingEmail(businessName, bookerEmail, serviceName, staffMemberName, additionalEmail,
        #                                      serviceClockTimeRange, bookerName, appointmentDate)


        # return bookingNumber


    # def bookTRSNew(self, businessId, businessName, service1Name, service2Name, clockTimeRange, appointmentDate,
    #                             userIdOfStaff, customerEmail, customerName,bookerComment):
    #     slotsRange = AppUtils().convertClockTimeRangeToSlotsRange(clockTimeRange)
    #     if (userIdOfStaff==0):
    #         slotsCount=slotsRange["endSlotNumber"] - slotsRange["startSlotNumber"]
    #         result=DataAccess().getStaffMembersForBooking(businessId,service1Name,service2Name, appointmentDate,slotsRange,None)
    #         shortlistedUsers=[]
    #         for oneUser in result:
    #             if(oneUser[1]>=slotsCount):
    #                 shortlistedUsers.append(oneUser[0])
    #         print(shortlistedUsers)
    #
    #         if (len(shortlistedUsers) ==1 ):
    #             userIdOfStaff=shortlistedUsers[0]
    #         else:
    #             staffRankedByAvailabiity = DataAccess().rankStaffMembersByAvailabilityOnADay(businessId, appointmentDate, shortlistedUsers)
    #             userIdOfStaff = staffRankedByAvailabiity[0]
    #
    #     bookingNumber = BookingUtils().generateBookingNumber(businessId, appointmentDate)
    #     # BookingUtils().markUnavailability(businessId, userIdOfStaff, 'B', None, clockTimeRange, appointmentDate, 'N',bookingNumber)
    #     DataAccess().markUnavailability(businessId,userIdOfStaff,'B', slotsRange["startSlotNumber"], slotsRange["endSlotNumber"],appointmentDate,bookingNumber)
    #
    #
    #     staff=BookingUtils().getBusinessStaffDetails(businessId,userIdOfStaff)
    #     print('staff=',staff)
    #     slotsRange=AppUtils().convertClockTimeRangeToSlotsRange(clockTimeRange)
    #     print('slotsRange=',slotsRange)
    #     slotsRangeStr = str(slotsRange["startSlotNumber"]) + ' - ' + str(slotsRange["endSlotNumber"])
    #     dayOfWeek = datetime.strptime(appointmentDate, '%Y-%m-%d').weekday()
    #     DataAccess().makeBooking(businessId, customerEmail, bookingNumber, service1Name, AppUtils().getFullName(staff.firstname,staff.lastname), None, slotsRangeStr,
    #                              clockTimeRange, customerName, appointmentDate, None, staff.emailId, None, dayOfWeek, service2Name, businessName,bookerComment)
        # NotificationsCore().sendBookingEmail(businessName, bookerEmail, serviceName, staffMemberName, additionalEmail,
        #                                      serviceClockTimeRange, bookerName, appointmentDate)

        # return bookingNumber



    # def bookPSSNew(self, businessId, businessName, serviceName, clockTimeRange, appointmentDate,
    #                             userIdOfStaff1, customerEmail, customerName, partnerEmail,bookerComment ):
    #
    #     slotsRange = AppUtils().convertClockTimeRangeToSlotsRange(clockTimeRange)
    #
    #     slotsCount = slotsRange["endSlotNumber"] - slotsRange["startSlotNumber"] + 1
    #     result=[]
    #     if (userIdOfStaff1!=0):
    #         result=DataAccess().getStaffMembersForBooking(businessId,serviceName,None, appointmentDate,slotsRange,userIdOfStaff1)
    #         print('result=',result)
    #     elif (userIdOfStaff1 == 0):
    #         result=DataAccess().getStaffMembersForBooking(businessId,serviceName,None, appointmentDate,slotsRange,None)
    #     print('after if result=', result)
    #     shortlistedUsers=[]
    #     for oneUser in result:
    #         if(oneUser[1]>=slotsCount):
    #             shortlistedUsers.append(oneUser[0])
    #     print(shortlistedUsers)
    #     userIdOfStaff2=''
    #     if (userIdOfStaff1!=0):
    #         if (len(shortlistedUsers) ==1 ):
    #             userIdOfStaff2=shortlistedUsers[0]
    #             print('in if-> if, user id is: ',userIdOfStaff2)
    #         else:
    #             staffRankedByAvailabiity = DataAccess().rankStaffMembersByAvailabilityOnADay(businessId, appointmentDate, shortlistedUsers)
    #             userIdOfStaff2 = staffRankedByAvailabiity[0][0]
    #             print('in if-> else, user id is: ', userIdOfStaff2)
    #     elif (userIdOfStaff1 == 0):
    #         if (len(shortlistedUsers) ==2 ):
    #             userIdOfStaff1 = shortlistedUsers[0]
    #             userIdOfStaff2=shortlistedUsers[1]
    #             print('in elif ->if, user id is: ', userIdOfStaff2)
    #         else:
    #             staffRankedByAvailabiity = DataAccess().rankStaffMembersByAvailabilityOnADay(businessId, appointmentDate, shortlistedUsers)
    #             userIdOfStaff1=staffRankedByAvailabiity[0][0]
    #             userIdOfStaff2 = staffRankedByAvailabiity[1][0]
    #             print('in elif->else, user id is: ', userIdOfStaff2)
    #
    #     bookingNumber = BookingUtils().generateBookingNumber(businessId, appointmentDate)
    #     DataAccess().markUnavailability(businessId, userIdOfStaff1, 'B', slotsRange["startSlotNumber"], slotsRange["endSlotNumber"], appointmentDate, bookingNumber)
    #     DataAccess().markUnavailability(businessId, userIdOfStaff2, 'B', slotsRange["startSlotNumber"],slotsRange["endSlotNumber"], appointmentDate, bookingNumber)
    #
    #     staff1=BookingUtils().getBusinessStaffDetails(businessId,userIdOfStaff1)
    #     staff2 = BookingUtils().getBusinessStaffDetails(businessId, userIdOfStaff2)
    #     # slotsRange = AppUtils().convertClockTimeRangeToSlotsRange(clockTimeRange)
    #     dayOfWeek = datetime.strptime(appointmentDate, '%Y-%m-%d').weekday()
    #     slotsRangeStr = str(slotsRange["startSlotNumber"]) + ' - ' + str(slotsRange["endSlotNumber"])
    #
    #
    #     DataAccess().makeBooking(businessId, customerEmail, bookingNumber, serviceName, AppUtils().getFullName(staff1.firstname,staff1.lastname),partnerEmail, slotsRangeStr,
    #                              clockTimeRange, customerName, appointmentDate, AppUtils().getFullName(staff2.firstname,staff2.lastname), staff1.emailId, staff2.emailId, dayOfWeek, serviceName, businessName,bookerComment)
    #
    #     # NotificationsCore().sendBookingEmail(businessName, bookerEmail, serviceName, staffMemberName, additionalEmail,
    #     #                                      serviceClockTimeRange, bookerName, appointmentDate)
    #
    #     return bookingNumber



    # def bookPDSNew(self, businessId, businessName, service1Name, service2Name,clockTimeRange, appointmentDate,
    #                             userIdOfStaff1, customerEmail, customerName, partnerEmail,bookerComment ):
    #
    #     print('in bookPDSNew, service2Name=', service2Name)
    #     slotsRange = AppUtils().convertClockTimeRangeToSlotsRange(clockTimeRange)
    #     slotsCount = slotsRange["endSlotNumber"] - slotsRange["startSlotNumber"] +1
    #     userIdOfStaff2 = ''
    #     if (userIdOfStaff1!=0):
    #         result = []
    #         result=DataAccess().getStaffMembersForBooking(businessId,service2Name,None, appointmentDate,slotsRange,userIdOfStaff1)
    #         if (len(result)==1):
    #             userIdOfStaff2 =result[0][0]
    #         else:
    #             shortlistedUsers=[]
    #             for oneUser in result:
    #                 if(oneUser[1]>=slotsCount):
    #                     shortlistedUsers.append(oneUser[0])
    #             print(shortlistedUsers)
    #             if (len(shortlistedUsers) == 1):
    #                 userIdOfStaff2 = shortlistedUsers[0]
    #             else:
    #                 staffRankedByAvailabiity = DataAccess().rankStaffMembersByAvailabilityOnADay(businessId, appointmentDate, shortlistedUsers)
    #                 userIdOfStaff2 = staffRankedByAvailabiity[0][0]
    #
    #     if (userIdOfStaff1==0):
    #         result1=DataAccess().getStaffMembersForBooking(businessId,service1Name,None, appointmentDate,slotsRange,None)
    #         result2 = DataAccess().getStaffMembersForBooking(businessId, service2Name, None, appointmentDate,slotsRange, None)
    #         if ( len(result1)==1 and len(result2)==1):
    #             userIdOfStaff1 =result1[0][0]
    #             userIdOfStaff2 = result2[0][0]
    #
    #         elif ( len(result1)==1 and len(result2)!=1):
    #             userIdOfStaff1 =result1[0][0]
    #             shortlistedUsers2=[]
    #             for oneUser in result2:
    #                 if(oneUser[1]>=slotsCount):
    #                     shortlistedUsers2.append(oneUser[0])
    #             print(shortlistedUsers2)
    #             if (len(shortlistedUsers2) == 1):
    #                 userIdOfStaff2 = shortlistedUsers2[0]
    #             else:
    #                 staffRankedByAvailabiity2 = DataAccess().rankStaffMembersByAvailabilityOnADay(businessId, appointmentDate, shortlistedUsers2)
    #                 userIdOfStaff2 = staffRankedByAvailabiity2[0][0]
    #                 if(userIdOfStaff1==userIdOfStaff2):
    #                     userIdOfStaff2 = staffRankedByAvailabiity2[1][0]
    #
    #         elif ( len(result1)!=1 and len(result2)==1):
    #             userIdOfStaff2 =result2[0][0]
    #             shortlistedUsers1=[]
    #             for oneUser in result1:
    #                 if(oneUser[1]>=slotsCount):
    #                     shortlistedUsers1.append(oneUser[0])
    #             print(shortlistedUsers1)
    #             if (len(shortlistedUsers1) == 1):
    #                 userIdOfStaff1 = shortlistedUsers1[0]
    #             else:
    #                 staffRankedByAvailabiity1 = DataAccess().rankStaffMembersByAvailabilityOnADay(businessId, appointmentDate, shortlistedUsers1)
    #                 userIdOfStaff1 = staffRankedByAvailabiity1[0][0]
    #                 if(userIdOfStaff1==userIdOfStaff2):
    #                     userIdOfStaff1 = staffRankedByAvailabiity1[1][0]
    #
    #         elif ( len(result1)!=1 and len(result2)!=1):
    #             shortlistedUsers1=[]
    #             for oneUser in result1:
    #                 if(oneUser[1]>=slotsCount):
    #                     shortlistedUsers1.append(oneUser[0])
    #             print(shortlistedUsers1)
    #             staffRankedByAvailabiity1 = DataAccess().rankStaffMembersByAvailabilityOnADay(businessId, appointmentDate, shortlistedUsers1)
    #             userIdOfStaff1Top2 = [staffRankedByAvailabiity1[0][0], staffRankedByAvailabiity1[1][0]]
    #
    #             shortlistedUsers2=[]
    #             for oneUser in result2:
    #                 if(oneUser[1]>=slotsCount):
    #                     shortlistedUsers2.append(oneUser[0])
    #             print(shortlistedUsers2)
    #             staffRankedByAvailabiity2 = DataAccess().rankStaffMembersByAvailabilityOnADay(businessId, appointmentDate, shortlistedUsers2)
    #             userIdOfStaff2Top2 = [staffRankedByAvailabiity2[0][0], staffRankedByAvailabiity2[1][0]]
    #
    #             userIds=AppUtils().getOneEachButDifferentElements( userIdOfStaff1Top2, userIdOfStaff2Top2)
    #             userIdOfStaff1=userIds[0]
    #             userIdOfStaff2 = userIds[1]



        # Get duration based on services and not the clock time on UI

        # duration1=(BookingUtils().getBusinessServiceDefinition(businessId,service1Name).duration) // 15
        # duration2=(BookingUtils().getBusinessServiceDefinition(businessId,service2Name).duration) // 15
        # duration1=(BookingUtils().getBusinessServiceDefinition(businessId,service1Name).duration) // int(config.gSingleTimeslotDuration)
        # duration2=(BookingUtils().getBusinessServiceDefinition(businessId,service2Name).duration) // int(config.gSingleTimeslotDuration)
        # # slotsRange = AppUtils().convertClockTimeRangeToSlotsRange(clockTimeRange)
        # minSlot=slotsRange["startSlotNumber"]
        # maxSlot = slotsRange["endSlotNumber"]
        # bookingNumber=BookingUtils().generateBookingNumber(businessId, appointmentDate)
        # print('userIdOfStaff1=', userIdOfStaff1)
        # print('userIdOfStaff2=',userIdOfStaff2)
        # if (duration1 > duration2):
        #     DataAccess().markUnavailability(businessId,userIdOfStaff1,'B',minSlot,maxSlot,appointmentDate,bookingNumber)
        #     # 1.Get sorted list of freeslots of 2nd staff in the duration of 1st service.
        #     # 2. Check the consecutive slots for duration1.
        #     # 3. Choose the 1st from list
        #     freeSlotsService2=self.getSlotRangeAvailabilityOfStaff(businessId,userIdOfStaff2,appointmentDate,slotsRange)
        #     print('freeSlotsService2=',freeSlotsService2)
        #     consecutiveChunksForService2=AppUtils().getConsecutiveChunks(freeSlotsService2,duration2)
        #     print('consecutiveChunksForService2=', consecutiveChunksForService2)
        #     DataAccess().markUnavailability(businessId,userIdOfStaff2,'B',consecutiveChunksForService2[0],consecutiveChunksForService2[0]+(duration2-1),appointmentDate,bookingNumber)
        # else:
        #     DataAccess().markUnavailability(businessId,userIdOfStaff2,'B',minSlot,maxSlot,appointmentDate,bookingNumber)
        #     freeSlotsService1=self.getSlotRangeAvailabilityOfStaff(businessId,userIdOfStaff1,appointmentDate,slotsRange)
        #     print('freeSlotsService1=', freeSlotsService1)
        #     consecutiveChunksForService1=AppUtils().getConsecutiveChunks(freeSlotsService1,duration1)
        #     print('consecutiveChunksForService1=', consecutiveChunksForService1)
        #     DataAccess().markUnavailability(businessId,userIdOfStaff1,'B',consecutiveChunksForService1[0],consecutiveChunksForService1[0]+(duration1-1),appointmentDate,bookingNumber)
        #
        # staff1=BookingUtils().getBusinessStaffDetails(businessId,userIdOfStaff1)
        # staff2 = BookingUtils().getBusinessStaffDetails(businessId, userIdOfStaff2)
        #
        # dayOfWeek = datetime.strptime(appointmentDate, '%Y-%m-%d').weekday()
        # slotsRangeStr = str(slotsRange["startSlotNumber"]) + ' - ' + str(slotsRange["endSlotNumber"])
        # print('b4 calling make booking, service2Name=', service2Name)
        # DataAccess().makeBooking(businessId, customerEmail, bookingNumber, service1Name, AppUtils().getFullName(staff1.firstname,staff1.lastname), partnerEmail, slotsRangeStr,
        #                          clockTimeRange, customerName, appointmentDate, AppUtils().getFullName(staff2.firstname,staff2.lastname), staff1.emailId, staff2.emailId, dayOfWeek, service2Name, businessName,bookerComment)
        #
        # # NotificationsCore().sendBookingEmail(businessName, bookerEmail, serviceName, staffMemberName, additionalEmail,
        # #                                      serviceClockTimeRange, bookerName, appointmentDate)
        #
        # return bookingNumber



    def bookRSNew2(self, businessId, businessName, serviceName, clockTimeRange, appointmentDate, userIdOfStaff, bookerEmail, bookerName,bookerComment):

        print('businessId:{}, businessName:{}, serviceName:{}, clockTimeRange:{}, appointmentDate:{}, userIdOfStaff:{}, bookerEmail:{}, bookerName:{},bookerComment:{}'.format(businessId, businessName, serviceName, clockTimeRange, appointmentDate, userIdOfStaff, bookerEmail, bookerName,bookerComment))
        slotsRange = AppUtils().convertClockTimeRangeToSlotsRange(clockTimeRange)

        if (userIdOfStaff==0):

            result=DataAccess().getStaffMembersForBookingNew2(businessId, serviceName, None, appointmentDate, slotsRange, None)
            bookedUsers = [number[0] for number in result if (number[1] != 'Y')]
            availableUsers = [number[0] for number in result if number[1] == 'Y']
            shortlistedUsers=list(set(availableUsers) - set(bookedUsers))

            if (len(shortlistedUsers) ==1 ):
                userIdOfStaff=shortlistedUsers[0]
            else:
                staffRankedByAvailabiity = DataAccess().rankStaffMembersByAvailabilityOnADay(businessId, appointmentDate, shortlistedUsers)
                #userIdOfStaff = staffRankedByAvailabiity
                userIdOfStaff = staffRankedByAvailabiity[0][0]

        bookingNumber = BookingUtils().generateBookingNumber(businessId, appointmentDate)

        print('bookingNumber=',bookingNumber)

        DataAccess().markUnavailability(businessId,userIdOfStaff,'B', slotsRange["startSlotNumber"], slotsRange["endSlotNumber"],appointmentDate, bookingNumber)

        staff=BookingUtils().getBusinessStaffDetails(businessId,userIdOfStaff)
        slotsRangeStr=str(slotsRange["startSlotNumber"])+' - '+str(slotsRange["endSlotNumber"])
        # Commented the code below and replaced with the code that follows. Use python date
        # dayOfWeek = datetime.strptime(appointmentDate, config.applicationUIDateFormat).weekday()
        dayOfWeek = appointmentDate.weekday()
        staffMemberName=AppUtils().getFullName(staff.firstname, staff.lastname)

        # DataAccess().makeBooking(businessId, bookerEmail, bookingNumber, serviceName, staffMemberName, None, slotsRangeStr,
        #                          clockTimeRange, bookerName, appointmentDate, None, staff.emailId, None, dayOfWeek, None,businessName,bookerComment)

        serviceDefinition = BookingUtils().getBusinessServiceDefinition(businessId,serviceName)
        serviceDuration = serviceDefinition.duration
        price=serviceDefinition.price

        DataAccess().makeBooking(businessId, bookerEmail, bookingNumber, serviceName, staffMemberName, None, slotsRangeStr,
                                 clockTimeRange, bookerName, appointmentDate, None, staff.emailId, None, dayOfWeek, None,businessName,bookerComment, price, None)

        appointmentStartTime=clockTimeRange[:5]
        # address=BookingUtils().getBusinessAddressForDisplay(businessId,'Continuous')
        address, googleMapsUrl = BookingUtils().getBusinessAddressForDisplay(businessId, 'Continuous')
        conatctPhone = None
        extraInfo=DataAccess().getBusinessExtraInfo(businessId)
        if (extraInfo!=None):
            conatctPhone = extraInfo.contactPhone

        ifStaffNotifiedFutureBookingsSetting=DataAccess().getBusinessSettings(businessId).ifStaffNotifiedFutureBookings
        ifDisplayPhoneOnBookingSetting=DataAccess().getBusinessSettings(businessId).displayPhoneOnBooking
        AppEmail().sendBookingEmail(businessId, businessName, bookingNumber, 'RS',serviceDuration, serviceName, bookerName, staffMemberName, bookerEmail,
                                            staff.emailId, appointmentDate, appointmentStartTime , None, None,None,None,None, address,price,conatctPhone, ifStaffNotifiedFutureBookingsSetting, ifDisplayPhoneOnBookingSetting, googleMapsUrl)

        return bookingNumber

    def getStaffForServiceOnGivenSlot(self, userIdOfStaff,businessId, businessName, serviceName, appointmentDate, slotsRange):
        if (userIdOfStaff==0):
            result=DataAccess().getStaffMembersForBookingNew2(businessId, serviceName, None, appointmentDate, slotsRange, None)
            bookedUsers = [number[0] for number in result if (number[1] != 'Y')]
            availableUsers = [number[0] for number in result if number[1] == 'Y']
            shortlistedUsers=list(set(availableUsers) - set(bookedUsers))

            print('shortlistedUsers')
            print(shortlistedUsers)
            if (len(shortlistedUsers) ==1 ):
                userIdOfStaff=shortlistedUsers[0]
            else:
                staffRankedByAvailabiity = DataAccess().rankStaffMembersByAvailabilityOnADay(businessId, appointmentDate, shortlistedUsers)
                userIdOfStaff = staffRankedByAvailabiity[0][0]

        return userIdOfStaff


    def bookTRSNew2(self, businessId, businessName, service1Name, service2Name, clockTimeRange, appointmentDate,
                                userIdOfStaff, bookerEmail, bookerName,bookerComment):
        slotsRange = AppUtils().convertClockTimeRangeToSlotsRange(clockTimeRange)

        service1Definition = BookingUtils().getBusinessServiceDefinition(businessId,service1Name)
        service1DurationInSlots = service1Definition.duration // int(config.gSingleTimeslotDuration)
        slot1Range = { "startSlotNumber" : slotsRange["startSlotNumber"], "endSlotNumber": slotsRange["startSlotNumber"] + service1DurationInSlots - 1 }
        slot2Range = { "startSlotNumber" : slotsRange["startSlotNumber"] + service1DurationInSlots, "endSlotNumber": slotsRange["endSlotNumber"] }


        userIdOfStaff1 = self.getStaffForServiceOnGivenSlot(userIdOfStaff, businessId, businessName, service1Name, appointmentDate, slot1Range)
        userIdOfStaff2 = self.getStaffForServiceOnGivenSlot(userIdOfStaff, businessId, businessName, service2Name, appointmentDate, slot2Range)

        bookingNumber = BookingUtils().generateBookingNumber(businessId, appointmentDate)
        # DataAccess().markUnavailability(businessId,userIdOfStaff,'B', slotsRange["startSlotNumber"], slotsRange["endSlotNumber"],appointmentDate,bookingNumber)
        DataAccess().markUnavailability(businessId,userIdOfStaff1,'B', slot1Range["startSlotNumber"], slot1Range["endSlotNumber"],appointmentDate,bookingNumber)
        DataAccess().markUnavailability(businessId,userIdOfStaff2,'B', slot2Range["startSlotNumber"], slot2Range["endSlotNumber"],appointmentDate,bookingNumber)

        staff1=BookingUtils().getBusinessStaffDetails(businessId,userIdOfStaff1)
        staff2=BookingUtils().getBusinessStaffDetails(businessId,userIdOfStaff2)
        print('staff1 = ',staff1)
        print('staff2 = ',staff2)

        slotsRange=AppUtils().convertClockTimeRangeToSlotsRange(clockTimeRange)
        print('slotsRange=',slotsRange)
        slotsRangeStr = str(slotsRange["startSlotNumber"]) + ' - ' + str(slotsRange["endSlotNumber"])
        # Commented the code below and replaced with the code that follows. Use python date
        # dayOfWeek = datetime.strptime(appointmentDate, config.applicationUIDateFormat).weekday()
        dayOfWeek = appointmentDate.weekday()
        staff1MemberName=AppUtils().getFullName(staff1.firstname,staff1.lastname)
        staff2MemberName=AppUtils().getFullName(staff2.firstname,staff2.lastname)

        # DataAccess().makeBooking(businessId, bookerEmail, bookingNumber, service1Name, staffMemberName, None, slotsRangeStr,
        #                          clockTimeRange, bookerName, appointmentDate, None, staff.emailId, None, dayOfWeek, service2Name, businessName,bookerComment)

        # serviceName=service1Name+', '+service2Name
        service1Definition = BookingUtils().getBusinessServiceDefinition(businessId,service1Name)
        service2Definition = BookingUtils().getBusinessServiceDefinition(businessId,service2Name)
        serviceDuration=service1Definition.duration+service2Definition.duration

        DataAccess().makeBooking(businessId, bookerEmail, bookingNumber, service1Name, staff1MemberName, None, slotsRangeStr,
                                 clockTimeRange, bookerName, appointmentDate, staff2MemberName, staff1.emailId, staff2.emailId, dayOfWeek, service2Name, businessName,bookerComment, service1Definition.price, service2Definition.price)

        appointmentStartTime=clockTimeRange[:5]
        # address = BookingUtils().getBusinessAddressForDisplay(businessId, 'Continuous')
        address, googleMapsUrl = BookingUtils().getBusinessAddressForDisplay(businessId, 'Continuous')
        # price=service1Definition.price+service2Definition.price
        price = str(service1Definition.price) +';'+ str(service2Definition.price)
        
        conatctPhone = None
        extraInfo = DataAccess().getBusinessExtraInfo(businessId)
        if (extraInfo != None):
            conatctPhone = extraInfo.contactPhone

        ifStaffNotifiedFutureBookingsSetting=DataAccess().getBusinessSettings(businessId).ifStaffNotifiedFutureBookings
        ifDisplayPhoneOnBookingSetting=DataAccess().getBusinessSettings(businessId).displayPhoneOnBooking

        AppEmail().sendBookingEmail(businessId, businessName, bookingNumber, 'TRS',serviceDuration, service1Name, bookerName, staff1MemberName, bookerEmail,
                                            staff1.emailId, appointmentDate, appointmentStartTime , service2Name, staff2MemberName, staff2.emailId,None,None,address,price,conatctPhone, ifStaffNotifiedFutureBookingsSetting, ifDisplayPhoneOnBookingSetting, googleMapsUrl)

        return bookingNumber

    # def bookTRSNew2(self, businessId, businessName, service1Name, service2Name, clockTimeRange, appointmentDate,
    #                             userIdOfStaff, bookerEmail, bookerName,bookerComment):
    #     slotsRange = AppUtils().convertClockTimeRangeToSlotsRange(clockTimeRange)
    #     if (userIdOfStaff==0):
    #         result=DataAccess().getStaffMembersForBookingNew2(businessId, service1Name, service2Name, appointmentDate, slotsRange, None)
    #         bookedUsers = [number[0] for number in result if (number[1] != 'Y')]
    #         availableUsers = [number[0] for number in result if number[1] == 'Y']
    #         shortlistedUsers=list(set(availableUsers) - set(bookedUsers))

    #         print('shortlistedUsers')
    #         print(shortlistedUsers)
    #         if (len(shortlistedUsers) ==1 ):
    #             userIdOfStaff=shortlistedUsers[0]
    #         else:
    #             staffRankedByAvailabiity = DataAccess().rankStaffMembersByAvailabilityOnADay(businessId, appointmentDate, shortlistedUsers)
    #             userIdOfStaff = staffRankedByAvailabiity[0][0]

    #     bookingNumber = BookingUtils().generateBookingNumber(businessId, appointmentDate)
    #     DataAccess().markUnavailability(businessId,userIdOfStaff,'B', slotsRange["startSlotNumber"], slotsRange["endSlotNumber"],appointmentDate,bookingNumber)


    #     staff=BookingUtils().getBusinessStaffDetails(businessId,userIdOfStaff)
    #     print('staff=',staff)
    #     slotsRange=AppUtils().convertClockTimeRangeToSlotsRange(clockTimeRange)
    #     print('slotsRange=',slotsRange)
    #     slotsRangeStr = str(slotsRange["startSlotNumber"]) + ' - ' + str(slotsRange["endSlotNumber"])
    #     # Commented the code below and replaced with the code that follows. Use python date
    #     # dayOfWeek = datetime.strptime(appointmentDate, config.applicationUIDateFormat).weekday()
    #     dayOfWeek = appointmentDate.weekday()
    #     staffMemberName=AppUtils().getFullName(staff.firstname,staff.lastname)

    #     # DataAccess().makeBooking(businessId, bookerEmail, bookingNumber, service1Name, staffMemberName, None, slotsRangeStr,
    #     #                          clockTimeRange, bookerName, appointmentDate, None, staff.emailId, None, dayOfWeek, service2Name, businessName,bookerComment)

    #     # serviceName=service1Name+', '+service2Name
    #     service1Definition = BookingUtils().getBusinessServiceDefinition(businessId,service1Name)
    #     service2Definition = BookingUtils().getBusinessServiceDefinition(businessId,service2Name)
    #     serviceDuration=service1Definition.duration+service2Definition.duration

    #     DataAccess().makeBooking(businessId, bookerEmail, bookingNumber, service1Name, staffMemberName, None, slotsRangeStr,
    #                              clockTimeRange, bookerName, appointmentDate, None, staff.emailId, None, dayOfWeek, service2Name, businessName,bookerComment, service1Definition.price, service2Definition.price)

    #     appointmentStartTime=clockTimeRange[:5]
    #     # address = BookingUtils().getBusinessAddressForDisplay(businessId, 'Continuous')
    #     address, googleMapsUrl = BookingUtils().getBusinessAddressForDisplay(businessId, 'Continuous')
    #     price=service1Definition.price+service2Definition.price
    #     conatctPhone = None
    #     extraInfo = DataAccess().getBusinessExtraInfo(businessId)
    #     if (extraInfo != None):
    #         conatctPhone = extraInfo.contactPhone

    #     ifStaffNotifiedFutureBookingsSetting=DataAccess().getBusinessSettings(businessId).ifStaffNotifiedFutureBookings
    #     ifDisplayPhoneOnBookingSetting=DataAccess().getBusinessSettings(businessId).displayPhoneOnBooking

    #     AppEmail().sendBookingEmail(businessId, businessName, bookingNumber, 'TRS',serviceDuration, service1Name, bookerName, staffMemberName, bookerEmail,
    #                                         staff.emailId, appointmentDate, appointmentStartTime , service2Name, None,None,None,None,address,price,conatctPhone, ifStaffNotifiedFutureBookingsSetting, ifDisplayPhoneOnBookingSetting, googleMapsUrl)


    #     return bookingNumber



    def bookPSSNew2(self, businessId, businessName, serviceName, clockTimeRange, appointmentDate,
                                userIdOfStaff1, bookerEmail, bookerName, partnerEmail,bookerComment ):

        slotsRange = AppUtils().convertClockTimeRangeToSlotsRange(clockTimeRange)

        # result=[]
        result = DataAccess().getStaffMembersForBookingNew2(businessId, serviceName, None, appointmentDate, slotsRange,
                                                            userIdOfStaff1)
        bookedUsers = [number[0] for number in result if (number[1] != 'Y')]
        availableUsers = [number[0] for number in result if number[1] == 'Y']
        shortlistedUsers = list(set(availableUsers) - set(bookedUsers))

        userIdOfStaff2=0
        if (userIdOfStaff1!=0):
            if (len(shortlistedUsers) ==1 ):
                userIdOfStaff2=shortlistedUsers[0]
                print('in if-> if, user id is: ',userIdOfStaff2)
            else:
                staffRankedByAvailabiity = DataAccess().rankStaffMembersByAvailabilityOnADay(businessId, appointmentDate, shortlistedUsers)
                userIdOfStaff2 = staffRankedByAvailabiity[0][0]
                print('in if-> else, user id is: ', userIdOfStaff2)
        else:
            if (len(shortlistedUsers) ==2 ):
                userIdOfStaff1=shortlistedUsers[0]
                userIdOfStaff2 = shortlistedUsers[1]
                print('in if-> if, user id is: ',userIdOfStaff2)
            else:
                staffRankedByAvailabiity = DataAccess().rankStaffMembersByAvailabilityOnADay(businessId, appointmentDate, shortlistedUsers)
                userIdOfStaff1 = staffRankedByAvailabiity[0][0]
                userIdOfStaff2 = staffRankedByAvailabiity[1][0]
                print('in if-> else, user id is: ', userIdOfStaff2)

        bookingNumber = BookingUtils().generateBookingNumber(businessId, appointmentDate)
        DataAccess().markUnavailability(businessId, userIdOfStaff1, 'B', slotsRange["startSlotNumber"], slotsRange["endSlotNumber"], appointmentDate, bookingNumber)
        DataAccess().markUnavailability(businessId, userIdOfStaff2, 'B', slotsRange["startSlotNumber"],slotsRange["endSlotNumber"], appointmentDate, bookingNumber)

        staff1=BookingUtils().getBusinessStaffDetails(businessId,userIdOfStaff1)
        staff2 = BookingUtils().getBusinessStaffDetails(businessId, userIdOfStaff2)
        # slotsRange = AppUtils().convertClockTimeRangeToSlotsRange(clockTimeRange)
        # Commented the code below and replaced with the code that follows. Use python date
        # dayOfWeek = datetime.strptime(appointmentDate, config.applicationUIDateFormat).weekday()
        dayOfWeek = appointmentDate.weekday()
        slotsRangeStr = str(slotsRange["startSlotNumber"]) + ' - ' + str(slotsRange["endSlotNumber"])

        staffMember1Name=AppUtils().getFullName(staff1.firstname,staff1.lastname)
        staffMember2Name=AppUtils().getFullName(staff2.firstname, staff2.lastname)
        # DataAccess().makeBooking(businessId, bookerEmail, bookingNumber, serviceName,staffMember1Name ,partnerEmail, slotsRangeStr,
        #                          clockTimeRange, bookerName, appointmentDate, staffMember2Name, staff1.emailId, staff2.emailId, dayOfWeek, serviceName, businessName,bookerComment)

        # staffMemberName= staffMember1Name+', '+ staffMember2Name
        serviceDefinition=BookingUtils().getBusinessServiceDefinition(businessId,serviceName)
        serviceDuration=serviceDefinition.duration
        appointmentStartTime=clockTimeRange[:5]
        address, googleMapsUrl=BookingUtils().getBusinessAddressForDisplay(businessId,'Continuous')
        price=int(serviceDefinition.price)+int(serviceDefinition.price)

        DataAccess().makeBooking(businessId, bookerEmail, bookingNumber, serviceName,staffMember1Name ,partnerEmail, slotsRangeStr,
                                 clockTimeRange, bookerName, appointmentDate, staffMember2Name, staff1.emailId, staff2.emailId, dayOfWeek, serviceName, businessName,bookerComment, price, price)
        conatctPhone = None
        extraInfo = DataAccess().getBusinessExtraInfo(businessId)
        if (extraInfo != None):
            conatctPhone = extraInfo.contactPhone

        print('email=',bookerEmail)

        ifStaffNotifiedFutureBookingsSetting=DataAccess().getBusinessSettings(businessId).ifStaffNotifiedFutureBookings
        ifDisplayPhoneOnBookingSetting=DataAccess().getBusinessSettings(businessId).displayPhoneOnBooking

        AppEmail().sendBookingEmail(businessId, businessName, bookingNumber, 'PSS',serviceDuration, serviceName, bookerName, staffMember1Name, bookerEmail,
                                            staff1.emailId, appointmentDate, appointmentStartTime , None, staffMember2Name,staff2.emailId,None,partnerEmail,address, price,conatctPhone, ifStaffNotifiedFutureBookingsSetting, ifDisplayPhoneOnBookingSetting,googleMapsUrl)


        return bookingNumber



    def bookPDSNew2(self, businessId, businessName, service1Name, service2Name,clockTimeRange, appointmentDate,
                                userIdOfStaff1, bookerEmail, bookerName, partnerEmail,bookerComment ):

        print('in bookPDSNew, service2Name=', service2Name)
        slotsRange = AppUtils().convertClockTimeRangeToSlotsRange(clockTimeRange)

        result=[]
        userIdOfStaff2=0
        if (userIdOfStaff1!=0):
            result = DataAccess().getStaffMembersForBookingNew2(businessId, service2Name, None, appointmentDate,
                                                                slotsRange, userIdOfStaff1)
            bookedUsers = [number[0] for number in result if (number[1] != 'Y')]
            availableUsers = [number[0] for number in result if number[1] == 'Y']
            shortlistedUsers = list(set(availableUsers) - set(bookedUsers))
            if (len(shortlistedUsers) ==1 ):
                userIdOfStaff2=shortlistedUsers[0]
                print('in if-> if, user id is: ',userIdOfStaff2)
            else:
                staffRankedByAvailabiity = DataAccess().rankStaffMembersByAvailabilityOnADay(businessId, appointmentDate, shortlistedUsers)
                userIdOfStaff2 = staffRankedByAvailabiity[0][0]
                print('in if-> else, user id is: ', userIdOfStaff2)

        else:
            resultS1 = DataAccess().getStaffMembersForBookingNew2(businessId, service1Name, None, appointmentDate,
                                                                slotsRange, None)
            bookedUsersS1 = [number[0] for number in resultS1 if (number[1] != 'Y')]
            availableUsersS1 = [number[0] for number in resultS1 if number[1] == 'Y']
            shortlistedUsersS1 = list(set(availableUsersS1) - set(bookedUsersS1))

            resultS2 = DataAccess().getStaffMembersForBookingNew2(businessId, service2Name, None, appointmentDate,
                                                                slotsRange, None)
            bookedUsersS2 = [number[0] for number in resultS2 if (number[1] != 'Y')]
            availableUsersS2 = [number[0] for number in resultS2 if number[1] == 'Y']
            shortlistedUsersS2 = list(set(availableUsersS2) - set(bookedUsersS2))

            userIdOfStaff1,userIdOfStaff2 = AppUtils().getOneEachButDifferentElements(shortlistedUsersS1[:2], shortlistedUsersS2[:2])


        # Get duration based on services and not the clock time on UI
        # duration1Slots=(BookingUtils().getBusinessServiceDefinition(businessId,service1Name).duration) // 15
        # duration2Slots=(BookingUtils().getBusinessServiceDefinition(businessId,service2Name).duration) // 15
        service1Definition=BookingUtils().getBusinessServiceDefinition(businessId, service1Name)
        duration1Slots=service1Definition.duration // int(config.gSingleTimeslotDuration)
        service2Definition=BookingUtils().getBusinessServiceDefinition(businessId, service2Name)
        duration2Slots=service2Definition.duration // int(config.gSingleTimeslotDuration)
        minSlot=slotsRange["startSlotNumber"]
        maxSlot = slotsRange["endSlotNumber"]
        bookingNumber=BookingUtils().generateBookingNumber(businessId, appointmentDate)
        print('userIdOfStaff1=', userIdOfStaff1)
        print('userIdOfStaff2=',userIdOfStaff2)
        if (duration1Slots > duration2Slots):
            DataAccess().markUnavailability(businessId,userIdOfStaff1,'B',minSlot,maxSlot,appointmentDate,bookingNumber)
            # 1.Get sorted list of freeslots of 2nd staff in the duration of 1st service.
            # 2. Check the consecutive slots for duration1Slots.
            # 3. Choose the 1st from list
            freeSlotsService2=self.getSlotRangeAvailabilityOfStaff(businessId,userIdOfStaff2,appointmentDate,slotsRange)
            print('freeSlotsService2=',freeSlotsService2)
            consecutiveChunksForService2=AppUtils().getConsecutiveChunks(freeSlotsService2,duration2Slots)
            print('consecutiveChunksForService2=', consecutiveChunksForService2)
            DataAccess().markUnavailability(businessId,userIdOfStaff2,'B',consecutiveChunksForService2[0],consecutiveChunksForService2[0]+(duration2Slots-1),appointmentDate,bookingNumber)
        else:
            DataAccess().markUnavailability(businessId,userIdOfStaff2,'B',minSlot,maxSlot,appointmentDate,bookingNumber)
            freeSlotsService1=self.getSlotRangeAvailabilityOfStaff(businessId,userIdOfStaff1,appointmentDate,slotsRange)
            print('freeSlotsService1=', freeSlotsService1)
            consecutiveChunksForService1=AppUtils().getConsecutiveChunks(freeSlotsService1,duration1Slots)
            print('consecutiveChunksForService1=', consecutiveChunksForService1)
            DataAccess().markUnavailability(businessId,userIdOfStaff1,'B',consecutiveChunksForService1[0],consecutiveChunksForService1[0]+(duration1Slots-1),appointmentDate,bookingNumber)

        staff1=BookingUtils().getBusinessStaffDetails(businessId,userIdOfStaff1)
        staff2 = BookingUtils().getBusinessStaffDetails(businessId, userIdOfStaff2)

        # Commented the code below and replaced with the code that follows. Use python date
        # dayOfWeek = datetime.strptime(appointmentDate, config.applicationUIDateFormat).weekday()
        dayOfWeek = appointmentDate.weekday()
        slotsRangeStr = str(slotsRange["startSlotNumber"]) + ' - ' + str(slotsRange["endSlotNumber"])
        print('b4 calling make booking, service2Name=', service2Name)
        # DataAccess().makeBooking(businessId, bookerEmail, bookingNumber, service1Name, AppUtils().getFullName(staff1.firstname,staff1.lastname), partnerEmail, slotsRangeStr,
        #                          clockTimeRange, bookerName, appointmentDate, AppUtils().getFullName(staff2.firstname,staff2.lastname), staff1.emailId, staff2.emailId, dayOfWeek, service2Name, businessName,bookerComment)

        serviceDuration = {True: service1Definition.duration, False: service2Definition.duration}[service1Definition.duration > service2Definition.duration]
        appointmentStartTime = clockTimeRange[:5]
        address, googleMapsUrl=BookingUtils().getBusinessAddressForDisplay(businessId,'Continuous')
        # price=int(service1Definition.price)+int(service2Definition.price)
        price = str(service1Definition.price) +';'+ str(service2Definition.price)

        DataAccess().makeBooking(businessId, bookerEmail, bookingNumber, service1Name, AppUtils().getFullName(staff1.firstname,staff1.lastname), partnerEmail, slotsRangeStr,
                                 clockTimeRange, bookerName, appointmentDate, AppUtils().getFullName(staff2.firstname,staff2.lastname), staff1.emailId, staff2.emailId, dayOfWeek, service2Name, businessName,bookerComment,service1Definition.price,service2Definition.price)

        conatctPhone = None
        extraInfo = DataAccess().getBusinessExtraInfo(businessId)
        if (extraInfo != None):
            conatctPhone = extraInfo.contactPhone

        staffMember1Name=AppUtils().getFullName(staff1.firstname,staff1.lastname)
        staffMember2Name=AppUtils().getFullName(staff2.firstname, staff2.lastname)

        ifStaffNotifiedFutureBookingsSetting=DataAccess().getBusinessSettings(businessId).ifStaffNotifiedFutureBookings
        ifDisplayPhoneOnBookingSetting=DataAccess().getBusinessSettings(businessId).displayPhoneOnBooking

        AppEmail().sendBookingEmail(businessId, businessName, bookingNumber, 'PDS',serviceDuration, service1Name, bookerName, staffMember1Name, bookerEmail,
                                            staff1.emailId, appointmentDate, appointmentStartTime , service2Name, staffMember2Name,staff2.emailId,None,partnerEmail, address, price,conatctPhone, ifStaffNotifiedFutureBookingsSetting, ifDisplayPhoneOnBookingSetting,googleMapsUrl)


        return bookingNumber



    def bookDTSNew2(self, businessId, businessName, serviceName, clockTimeRange, appointmentDate, userIdOfStaff, bookerEmail, bookerName, bookerComment):

        print('businessId:{}, businessName:{}, serviceName:{}, clockTimeRange:{}, appointmentDate:{}, userIdOfStaff:{}, bookerEmail:{}, bookerName:{},bookerComment:{}'.format(businessId, businessName, serviceName, clockTimeRange, appointmentDate, userIdOfStaff, bookerEmail, bookerName,bookerComment))
        slotsRange = AppUtils().convertClockTimeRangeToSlotsRange(clockTimeRange)

        if (userIdOfStaff==0):

            result=DataAccess().getStaffMembersForBookingNew2(businessId, serviceName, None, appointmentDate, slotsRange, None)
            bookedUsers = [number[0] for number in result if (number[1] != 'Y')]
            availableUsers = [number[0] for number in result if number[1] == 'Y']
            shortlistedUsers=list(set(availableUsers) - set(bookedUsers))

            if (len(shortlistedUsers) ==1 ):
                userIdOfStaff=shortlistedUsers[0]
            else:               
                staffRankedByAvailabiity = DataAccess().rankStaffMembersByAvailabilityOnADay(businessId, appointmentDate, shortlistedUsers)
                userIdOfStaff = staffRankedByAvailabiity[0][0]

        bookingNumber = BookingUtils().generateBookingNumber(businessId, appointmentDate)

        print('bookingNumber=',bookingNumber)
        serviceDefinition = BookingUtils().getBusinessServiceDefinition(businessId, serviceName)
        subSlotsStr=serviceDefinition.subslotsCount
        subSlots=subSlotsStr.split(';')
        initialSlots=int(subSlots[0].strip())//int(config.gSingleTimeslotDuration)
        remainingSlots = int(subSlots[2].strip())//int(config.gSingleTimeslotDuration)

        DataAccess().markUnavailability(businessId, userIdOfStaff,'B', slotsRange["startSlotNumber"], slotsRange["startSlotNumber"]+initialSlots-1,appointmentDate,bookingNumber)
        DataAccess().markUnavailability(businessId, userIdOfStaff, 'B',slotsRange["endSlotNumber"]-remainingSlots+1, slotsRange["endSlotNumber"], appointmentDate, bookingNumber)

        staff=BookingUtils().getBusinessStaffDetails(businessId, userIdOfStaff)
        slotsRangeStr=str(slotsRange["startSlotNumber"])+' - '+str(slotsRange["endSlotNumber"])
        # Commented the code below and replaced with the code that follows. Use python date
        # dayOfWeek = datetime.strptime(appointmentDate, config.applicationUIDateFormat).weekday()
        dayOfWeek = appointmentDate.weekday()
        staffMemberName=AppUtils().getFullName(staff.firstname, staff.lastname)
        # DataAccess().makeBooking(businessId, bookerEmail, bookingNumber, serviceName, staffMemberName, None, slotsRangeStr,
        #                          clockTimeRange, bookerName, appointmentDate, None, staff.emailId, None, dayOfWeek, None,businessName,bookerComment)

        serviceDuration = serviceDefinition.duration
        price=serviceDefinition.price
        appointmentStartTime=clockTimeRange[:5]
        address, googleMapsUrl=BookingUtils().getBusinessAddressForDisplay(businessId,'Continuous')

        DataAccess().makeBooking(businessId, bookerEmail, bookingNumber, serviceName, staffMemberName, None, slotsRangeStr,
                                 clockTimeRange, bookerName, appointmentDate, None, staff.emailId, None, dayOfWeek, None,businessName,bookerComment, price, None)

        conatctPhone = None
        extraInfo = DataAccess().getBusinessExtraInfo(businessId)
        if (extraInfo != None):
            conatctPhone = extraInfo.contactPhone

        ifStaffNotifiedFutureBookingsSetting=DataAccess().getBusinessSettings(businessId).ifStaffNotifiedFutureBookings
        ifDisplayPhoneOnBookingSetting=DataAccess().getBusinessSettings(businessId).displayPhoneOnBooking
        AppEmail().sendBookingEmail(businessId, businessName, bookingNumber, 'DTS',serviceDuration, serviceName, bookerName, staffMemberName, bookerEmail,
                                            staff.emailId, appointmentDate, appointmentStartTime , None, None,None,None,None, address,price,conatctPhone, ifStaffNotifiedFutureBookingsSetting, ifDisplayPhoneOnBookingSetting,googleMapsUrl)

        return bookingNumber



    def getEmployeeBookings(self, businessId, userIdOfStaff, startDate, endDate):

        bookings=DataAccess().getStaffBookings(userIdOfStaff,startDate,endDate)
        bookingsDictList = []
        for booking in bookings:
            bookingDict = {}
            bookingDict["appointmentDate"] = datetime.strftime(booking[0], config.applicationUIDateFormat)
            # bookingDict["appointmentDate"] = booking[0]
            bookingDict["service1Name"] = booking[1]
            bookingDict["service2Name"] = booking[2]
            bookingDict["slotClockTime"] = booking[3]
            bookingDict["bookerName"] = booking[4]
            bookingDict["bookerComments"] = booking[5]
            bookingDict["bookingNumber"] = booking[6]
            bookingDict["status"] = booking[7]

            bookingDict["noShowButtonVisibility"] = True
            if(booking[7]!='OPEN' or booking[0] >= datetime.today().date()):
                bookingDict["noShowButtonVisibility"] = False

            bookingsDictList.append(bookingDict)
        return bookingsDictList



    def getBookings(self, businessId, userIdOfStaff, startDate, endDate, serviceName, loggedInUserId):

        if (userIdOfStaff!=None and userIdOfStaff !=0):
            staffEmail= DataAccess().getUserDetails(userIdOfStaff, None )[0]
        else:
            staffEmail =None
        loggedInUserEmail = DataAccess().getUserDetails(loggedInUserId, None)[0]
        # print('loggedInUserEmail=',loggedInUserEmail)

        # print('serviceName=',serviceName)
        # print('selected staff email=', staffEmail)
        bookings=DataAccess().getBusinessBookings(businessId, startDate, endDate, staffEmail, serviceName)
        # print('count of bookings=',len(bookings))
        bookingsDictList=[]
        for booking in bookings:
            bookingDict={}
            bookingDict["appointmentDate"] = datetime.strftime(booking[0], config.applicationUIDateFormat)
            bookingDict["service1Name"] = booking[1]
            bookingDict["service2Name"]=booking[2]
            bookingDict["slotClockTime"] = booking[3]
            bookingDict["bookerName"]=booking[4]
            bookingDict["bookerComments"] = booking[5]
            bookingDict["staff1Name"] = booking[6]
            bookingDict["staff2Name"] = booking[7]
            bookingDict["bookingNumber"] = booking[8]
            bookingDict['status']=booking[11]
            bookingDict['price1']=booking[12]
            bookingDict['price2']=booking[13]

            bookedStaffEmail=booking[9]
            bookedStaff2Email = booking[10]
            # print(bookedStaffEmail)
            # print(bookedStaff2Email)

            bookingDict["noShowButtonVisibility"] = False
            bookingDict["cancelButtonVisibility"] = False
            bookingDict["reassignButtonVisibility"] = False

            # if(booking[11] !='OPEN'):
            #     bookingDict["noShowButtonVisibility"] = False
            #     bookingDict["cancelButtonVisibility"] = False
            #     bookingDict["reassignButtonVisibility"] = False

            if(booking[11] =='OPEN'):
                if (booking[0] < datetime.today().date() ):
                    if (loggedInUserEmail == bookedStaffEmail or (bookedStaff2Email!=None and bookedStaff2Email==loggedInUserEmail) and booking[11] =='OPEN'):
                        bookingDict["noShowButtonVisibility"] = True
                else:
                    bookingDict["cancelButtonVisibility"] = True
                    bookingDict["reassignButtonVisibility"] = True


            # else:
            #     bookingDict["noShowButtonVisibility"] = False
            #     if (booking[0] < datetime.today().date() ):
            #         bookingDict["cancelButtonVisibility"] = False
            #         bookingDict["reassignButtonVisibility"] = False
            #         if (loggedInUserEmail == bookedStaffEmail or (bookedStaff2Email!=None and bookedStaff2Email==loggedInUserEmail) ):
            #             bookingDict["noShowButtonVisibility"] = True
            #     else:
            #         bookingDict["cancelButtonVisibility"] = True
            #         bookingDict["reassignButtonVisibility"] = True

            bookingsDictList.append(bookingDict)

        bookingsAndAvailabilityDict={}
        bookingsAndAvailabilityDict["bookingsList"]=bookingsDictList
        availabilityDictList=[]
        staffMembers =[]
        if (userIdOfStaff==None):
            staffMembers=DataAccess().getStaff(businessId, 'A')
        else:
            staffMember=BookingUtils().getBusinessStaffDetails(businessId, userIdOfStaff)
            staffMembers.append(staffMember)

        # print(staffMembers)
        for member in staffMembers:
            onedayAvailability=BookingCore().getOnedayAvailabilityOfStaff(businessId, member.userId, startDate)
            # print(onedayAvailability)
            slotsInClockTime=[]
            for slot in onedayAvailability:
                slotsInClockTime.append(AppUtils().convertSlotNumberToClockTime(slot))
            availabilityDict = {}
            availabilityDict['userId']=member.userId
            availabilityDict['fullName'] = AppUtils().getFullName(member.firstname, member.lastname)

            availabilityDict['availableSlots'] =slotsInClockTime
            availabilityDictList.append(availabilityDict)

        bookingsAndAvailabilityDict["staffAvailablity"] = availabilityDictList

        return bookingsAndAvailabilityDict



    # clockTimeRange format 1130;45, user selected timeslot and duration of service
    # def setBookingDetails(self, ifPartnerService, businessId, businessName, services, clockTimeRange, appointmentDate,
    #                       userIdOfStaff, customerEmail, partnerEmail, customerName, bookerComment):
    #     serviceType=BookingCore().determineTypeOfService(businessId, services, ifPartnerService)
    #
    #     # clockTimeRange format 1130;45
    #     timeAndDuration = clockTimeRange.split(';')
    #     print(timeAndDuration)
    #     slotNumTemp=AppUtils().convertClockTimeToSlotNumber(timeAndDuration[0])
    #     # serviceSlotsTemp=int(timeAndDuration[1])//15
    #     serviceSlotsTemp = int(timeAndDuration[1]) // int(config.gSingleTimeslotDuration)
    #     clockEndTime=AppUtils().convertSlotNumberToClockTime(slotNumTemp+serviceSlotsTemp)
    #     clockTimeRange= timeAndDuration[0]+ ' - '+ clockEndTime
    #
    #     if (serviceType == 'PSS'):
    #         print('apply partner same service logic')
    #         return self.bookPSSNew(businessId, businessName, services[0], clockTimeRange, appointmentDate,
    #                      userIdOfStaff, customerEmail, customerName, partnerEmail,bookerComment)
    #     elif (serviceType == 'PDS'):
    #         print('apply partner different service logic')
    #         print('in pds, services')
    #         print(services)
    #         return self.bookPDSNew(businessId, businessName, services[0], services[1], clockTimeRange, appointmentDate, userIdOfStaff, customerEmail, customerName, partnerEmail,bookerComment)
    #     elif (serviceType == 'TRS'):
    #         print('apply two regulr services logic')
    #         return self.bookTRSNew(businessId, businessName, services[0], services[1], clockTimeRange, appointmentDate, userIdOfStaff, customerEmail, customerName,bookerComment)
    #
    #     elif (serviceType == 'RS'):
    #         print('apply regular service logic')
    #         return self.bookRSNew(businessId, businessName, services[0], clockTimeRange, appointmentDate, userIdOfStaff, customerEmail, customerName,bookerComment)
    #     elif (serviceType == 'DTS'):
    #         print('apply double time service logic')
    #         return self.bookDTSNew(businessId, businessName, services[0], clockTimeRange, appointmentDate, userIdOfStaff, customerEmail, customerName,bookerComment)
    #
        # BookingUtils().markUnavailability(businessId, userIdOfStaff, 'B', None, clockTimeRange, appointmentDate, 'N')

        # DataAccess().makeBooking(businessId, bookerEmail, serviceName, staffMemberName, additionalEmail,
        #                          serviceSlotsRange, serviceClockTimeRange, bookerName, appointmentDate)
        # NotificationsCore().sendBookingEmail(businessName, bookerEmail, serviceName, staffMemberName, additionalEmail,
        #                                      serviceClockTimeRange, bookerName, appointmentDate)




    def determineTypeOfService(self, businessId, services, ifPartnerService):

        serviceDetails = BookingUtils().getBusinessServiceDefinition(businessId, services[0])
        print('serviceDetails=', vars(serviceDetails))
        if (len(services) == 2):
            if (ifPartnerService == 'Y'):
                    print('partner different service')
                    return 'PDS'
            else:
                print('Two regular services')
                return 'TRS'
        elif (len(services) == 1):
            if (serviceDetails.ifDoubleTimeService == 'N' and serviceDetails.ifTicketBasedService == 'N'):
                if (ifPartnerService == 'Y'):
                    print('partner same service')
                    return 'PSS'
                else:
                    print('regular service')
                    return 'RS'
            elif (serviceDetails.ifDoubleTimeService == 'Y'):
                print('double time service')
                return 'DTS'
            elif (serviceDetails.ifTicketBasedService == 'Y'):
                print('ticket based service')
                return 'TS'


    # def getDatewiseAvailability(self, businessId, staffMember, services, ifPartnerService):
    #
    #     serviceType = self.determineTypeOfService(businessId, services, ifPartnerService)
    #     bookingWindow=DataAccess().getBusinessSettings(businessId,'A').preBookingWindow
    #     if (serviceType == 'PSS'):
    #         print('apply partner same service logic')
    #         return self.getDatewiseUnAvailabilityForServicePSS(businessId, staffMember, services[0], bookingWindow)
    #     elif (serviceType == 'PDS'):
    #         print('apply partner different service logic')
    #         return self.getDatewiseUnAvailabilityForServicePDS(businessId, staffMember, services[0], services[1], bookingWindow)
    #     elif (serviceType == 'TRS'):
    #         print('apply two regulr services logic')
    #         return self.getDatewiseUnAvailabilityForServicesTRS(businessId, staffMember, services[0], services[1], bookingWindow)
    #     elif (serviceType == 'RS'):
    #         print('apply regular service logic')
    #         return self.getDatewiseUnAvailabilityForServiceRS(businessId, staffMember, services[0], bookingWindow)
    #     elif (serviceType == 'DTS'):
    #         print('apply double time service logic')
        # elif (serviceType == 'TS'):
        #     print('apply ticket service logic')
        #     self.getAvailabilityTS



    # def getDatewiseUnAvailabilityForServiceRS (self, businessId, staffUserId, serviceName, bookingWindow ):
    #     serviceDefinition=BookingUtils().getBusinessServiceDefinition( businessId, serviceName)
    #     # serviceDuration=len(serviceDefinition.subslotsCount)*15
    #     serviceDuration = len(serviceDefinition.subslotsCount) * int(config.gSingleTimeslotDuration)
    #     return self.getDatewiseUnAvailabilityRS(businessId, staffUserId,serviceName, serviceDuration, bookingWindow)


    # def getDatewiseUnAvailabilityRS (self, businessId, staffUserId, serviceName, serviceDuration, bookingWindow ):
    #
    #     unavailabilityDict={}
    #     for oneday in range(1, bookingWindow):
    #         availabilityDate = (date.today() + timedelta(days=oneday)).isoformat()
    #         print(availabilityDate)
    #
    #         if(staffUserId==0):
    #             staffUserId=BookingCore().getMostAvailableStaffMemberOnADay(businessId, staffUserId, serviceName,None,
    #                                                         availabilityDate, 1)[0]
    #         oneDayUnavailability=DataAccess().getUnavailabilityOfStaffMember(staffUserId,businessId,availabilityDate)
    #         print(oneDayUnavailability)
    #
    #         if(len(oneDayUnavailability)==0):
    #             unavailabilityDict[availabilityDate]=BookingUtils().getCompletelyAvailableDay(businessId)
    #         else:
    #             unavailableSlotsList=[]
    #             for slot in oneDayUnavailability :
    #                 unavailableSlotsList.append(slot[3])
    #             print(unavailableSlotsList)
    #
    #             oneDayUnavailabilityByTimeband=BookingUtils().getTimebandsUnavailability(businessId, unavailableSlotsList, serviceDuration)
    #             unavailabilityDict[availabilityDate] = oneDayUnavailabilityByTimeband
    #
    #     print(unavailabilityDict)
    #     return unavailabilityDict


    # def getDatewiseUnAvailabilityForServicesTRS(self, businessId, staffUserId, serviceName1, serviceName2, bookingWindow):
    #
    #     serviceDefinition=BookingUtils()().getBusinessServiceDefinition( businessId, serviceName1,serviceName2)
    #     # int(config.gSingleTimeslotDuration)
    #     # serviceDuration1=len(serviceDefinition.subslotsCount)*15
    #     # serviceDefinition2=BookingUtils()().getBusinessServiceDefinition( businessId, serviceName1,serviceName2)
    #     # serviceDuration2=len(serviceDefinition2.subslotsCount)*15
    #     serviceDuration1=len(serviceDefinition.subslotsCount)*int(config.gSingleTimeslotDuration)
    #     serviceDefinition2=BookingUtils()().getBusinessServiceDefinition( businessId, serviceName1,serviceName2)
    #     serviceDuration2=len(serviceDefinition2.subslotsCount)*int(config.gSingleTimeslotDuration)
    #     print('serviceDuration=',serviceDuration1)
    #     print('serviceDuration2=', serviceDuration2)
    #     return self.getDatewiseUnAvailabilityTRS(businessId, staffUserId, serviceName1,serviceName2, serviceDuration1,serviceDuration2, bookingWindow)

    # def getDatewiseUnAvailabilityTRS (self, businessId, staffUserId, serviceName1,serviceName2, serviceDuration1, serviceDuration2, bookingWindow ):
    #
    #     unavailabilityDict={}
    #     for oneday in range(1, bookingWindow):
    #         availabilityDate = (date.today() + timedelta(days=oneday)).isoformat()
    #         print(availabilityDate)
    #
    #         if(staffUserId==0):
    #             staffUserId=BookingCore().getMostAvailableStaffMemberOnADay(businessId, 0, serviceName1,serviceName2, availabilityDate, 1)[0]
    #
    #         oneDayUnavailability=DataAccess().getUnavailabilityOfStaffMember(staffUserId,businessId,availabilityDate)
    #         print(oneDayUnavailability)
    #
    #         if(len(oneDayUnavailability)==0):
    #             unavailabilityDict[availabilityDate]=BookingUtils().getCompletelyAvailableDay(businessId)
    #         else:
    #             unavailableSlotsList=[]
    #             for slot in oneDayUnavailability :
    #                 unavailableSlotsList.append(slot[3])
    #             print(unavailableSlotsList)
    #
    #             oneDayUnavailabilityByTimeband=BookingUtils().getCombinedUnavailabilityByServices(businessId, unavailableSlotsList,serviceDuration1, serviceDuration2)
    #             unavailabilityDict[availabilityDate] = oneDayUnavailabilityByTimeband
    #
    #     print(unavailabilityDict)
    #     return unavailabilityDict

    # def getDatewiseUnAvailabilityForServicePSS (self, businessId, staffUserId, serviceName, bookingWindow ):
    #
    #     serviceDefinition=BookingUtils()().getBusinessServiceDefinition( businessId, serviceName)
    #
    #     # serviceDuration=len(serviceDefinition.subslotsCount)*15
    #     serviceDuration = len(serviceDefinition.subslotsCount) * int(config.gSingleTimeslotDuration)
    #     print('serviceDuration=',serviceDuration)
    #     return self.getDatewiseUnAvailabilityPSS(businessId, staffUserId,serviceName, serviceDuration, bookingWindow)



    # def getDatewiseUnAvailabilityPSS (self, businessId, staffUserId, serviceName, serviceDuration, bookingWindow ):
    #
    #     unavailabilityDict={}
    #     for oneday in range(1, bookingWindow):
    #         availabilityDate = (date.today() + timedelta(days=oneday)).isoformat()
    #         print(availabilityDate)
    #         if (staffUserId==0):
    #             staffUserId=BookingCore().getMostAvailableStaffMemberOnADay(businessId, 0, serviceName,None,
    #                                                         availabilityDate, 1)[0]
    #         availableStaffUserId=BookingCore().getMostAvailableStaffMemberOnADay(businessId, staffUserId, serviceName,None,
    #                                                         availabilityDate, 1)[0]
    #         oneDayUnavailabilityStaff1=DataAccess().getUnavailabilityOfStaffMember(staffUserId, businessId, availabilityDate)
    #         oneDayUnavailabilityStaff2 = DataAccess().getUnavailabilityOfStaffMember(availableStaffUserId, businessId,
    #                                                                            availabilityDate)
    #         print(oneDayUnavailabilityStaff1)
    #         print(oneDayUnavailabilityStaff2)
    #
    #         unavailableSlotsListStaff2 = []
    #         unavailableSlotsListStaff1 = []
    #
    #         for slot in oneDayUnavailabilityStaff1:
    #             unavailableSlotsListStaff1.append(slot[3])
    #         for slot in oneDayUnavailabilityStaff2:
    #             unavailableSlotsListStaff2.append(slot[3])
    #
    #         if(len(oneDayUnavailabilityStaff1)==0 and len(oneDayUnavailabilityStaff2)==0 ):
    #             unavailabilityDict[availabilityDate] =BookingUtils().getCompletelyAvailableDay(businessId)
    #         elif(len(oneDayUnavailabilityStaff1)==0 and len(oneDayUnavailabilityStaff2)!=0 ):
    #             unavailabilityDict[availabilityDate]=BookingUtils().getTimebandsUnavailability(businessId,unavailableSlotsListStaff2,serviceDuration)
    #         elif (len(oneDayUnavailabilityStaff1)!=0 and len(oneDayUnavailabilityStaff2)==0 ):
    #             unavailabilityDict[availabilityDate] = BookingUtils().getTimebandsUnavailability(businessId,unavailableSlotsListStaff1,serviceDuration)
    #         else:
    #             oneDayUnavailabilityByTimeband=BookingUtils().getCombinedUnavailabilityByStaffs(businessId,unavailableSlotsListStaff1,unavailableSlotsListStaff2,serviceDuration)
    #             unavailabilityDict[availabilityDate] = oneDayUnavailabilityByTimeband
    #
    #     print(unavailabilityDict)
    #     return unavailabilityDict



    # def getDatewiseUnAvailabilityForServicePDS (self, businessId, staffUserId, serviceName1, serviceName2, bookingWindow ):

        # serviceDefinition=BookingUtils()().getBusinessServiceDefinition( businessId, serviceName1,serviceName2)
        # serviceDuration1=len(serviceDefinition.subslotsCount)*15
        # serviceDefinition2=BookingUtils()().getBusinessServiceDefinition( businessId, serviceName1,serviceName2)
        # serviceDuration2=len(serviceDefinition2.subslotsCount)*15

        # serviceDefinition=BookingUtils()().getBusinessServiceDefinition( businessId, serviceName1,serviceName2)
        # serviceDuration1=len(serviceDefinition.subslotsCount)*int(config.gSingleTimeslotDuration)
        # serviceDefinition2=BookingUtils()().getBusinessServiceDefinition( businessId, serviceName1,serviceName2)
        # serviceDuration2=len(serviceDefinition2.subslotsCount)*int(config.gSingleTimeslotDuration)
        #
        # print('serviceDuration=',serviceDuration1)
        # print('serviceDuration2=', serviceDuration2)
        # return self.getDatewiseUnAvailabilityPDS(businessId, staffUserId, serviceName1,serviceName2, serviceDuration1,serviceDuration2, bookingWindow)



    # def getDatewiseUnAvailabilityPDS (self, businessId, staffUserId, serviceName1, serviceName2, serviceDuration1, serviceDuration2, bookingWindow ):
    #
    #     unavailabilityDict={}
    #     for oneday in range(1, bookingWindow):
    #         availabilityDate = (date.today() + timedelta(days=oneday)).isoformat()
    #         print(availabilityDate)
    #         if (staffUserId==0):
    #             staffUserId=BookingCore().getMostAvailableStaffMemberOnADay(businessId, 0, serviceName1,None,
    #                                                         availabilityDate, 1)[0]
    #
    #         availableStaffUserId=BookingCore().getMostAvailableStaffMemberOnADay(businessId, staffUserId, serviceName2,None,
    #                                                         availabilityDate,1)[0]
    #         print('availableStaffUserId=',availableStaffUserId)
    #         oneDayUnavailabilityStaff1=DataAccess().getUnavailabilityOfStaffMember(staffUserId, businessId, availabilityDate)
    #         oneDayUnavailabilityStaff2 = DataAccess().getUnavailabilityOfStaffMember(availableStaffUserId, businessId,
    #                                                                            availabilityDate)
    #         print(oneDayUnavailabilityStaff1)
    #         print(oneDayUnavailabilityStaff2)
    #
    #         unavailableSlotsListStaff2 = []
    #         unavailableSlotsListStaff1 = []
    #
    #         for slot in oneDayUnavailabilityStaff1:
    #             unavailableSlotsListStaff1.append(slot[3])
    #         for slot in oneDayUnavailabilityStaff2:
    #             unavailableSlotsListStaff2.append(slot[3])
    #
    #         if(len(oneDayUnavailabilityStaff1)==0 and len(oneDayUnavailabilityStaff2)==0 ):
    #             unavailabilityDict[availabilityDate] =BookingUtils().getCompletelyAvailableDay(businessId)
    #         elif(len(oneDayUnavailabilityStaff1)==0 and len(oneDayUnavailabilityStaff2)!=0 ):
    #             unavailabilityDict[availabilityDate]=BookingUtils().getTimebandsUnavailability(businessId,unavailableSlotsListStaff2,serviceDuration2)
    #         elif (len(oneDayUnavailabilityStaff1)!=0 and len(oneDayUnavailabilityStaff2)==0 ):
    #             unavailabilityDict[availabilityDate] = BookingUtils().getTimebandsUnavailability(businessId,unavailableSlotsListStaff1,serviceDuration1)
    #         else:
    #             oneDayUnavailabilityByTimeband=BookingUtils().getCombinedUnavailabilityByStaffsAndServices(businessId,unavailableSlotsListStaff1,unavailableSlotsListStaff2,serviceDuration1,serviceDuration2)
    #             unavailabilityDict[availabilityDate] = oneDayUnavailabilityByTimeband
    #
    #     print(unavailabilityDict)
    #     return unavailabilityDict



    # timeband availability for the slot range over the booking window period starting today,
    # def getTimebandAvailabilityOfSkilledStaff(self, businessId, services, slotRange):
    #     return BookingUtils().getAvailabilityOfSkilledStaffUtility(businessId, services, None, slotRange)
    #
    #
    #
    # # availability for the slot range on the slot date
    # def getSlotRangeAvailabilityOfSkilledStaff (self, businessId, services, slotDate, slotRange):
    #     return BookingUtils().getAvailabilityOfSkilledStaffUtility(businessId, services, slotDate, slotRange)
    #
    #
    #
    # #  one day availability for the slot date
    # def getOnedayAvailabilityOfSkilledStaff (self, businessId, services, slotDate):
    #     return BookingUtils().getAvailabilityOfSkilledStaffUtility(businessId, services, slotDate, None)
    #
    #
    #
    #
    # # timeband availability for the slot range over the booking window period starting today,
    # def getTimebandAvailabilityOfStaff(self, businessId, userIdOfStaff, slotRange):
    #     return BookingUtils().getAvailabilityOfStaffUtility(businessId, userIdOfStaff, None, slotRange)



    # availability for the slot range on the slot date
    def getSlotRangeAvailabilityOfStaff (self, businessId, userIdOfStaff, slotDate, slotRange):
        return BookingUtils().getAvailabilityOfStaffUtility(userIdOfStaff, businessId, slotDate, slotRange)



    #  one day availability for the slot date
    def getOnedayAvailabilityOfStaff (self, businessId, userIdOfStaff, slotDate):
        print('getOnedayAvailabilityOfStaff')
        return BookingUtils().getAvailabilityOfStaffUtility(userIdOfStaff, businessId, slotDate, None)


    def getOnedayAvailabilityOfStaffOfDTS (self, businessId, userIdOfStaff, slotDate, serviceType, services, serviceName):
        print('getOnedayAvailabilityOfStaff')
        if (serviceType == 'DTS'):
            a = BookingUtils().getAvailabilityOfStaffUtility(userIdOfStaff, businessId, slotDate, None)

            serviceDefinition = BookingUtils().getBusinessServiceDefinition(businessId, serviceName)
            subSlotsStr=serviceDefinition.subslotsCount
            subSlots=subSlotsStr.split(';')
            initialSlots=int(subSlots[0].strip())//int(config.gSingleTimeslotDuration)
            breakSlots = int(subSlots[1].strip())//int(config.gSingleTimeslotDuration)
            remainingSlots = int(subSlots[2].strip())//int(config.gSingleTimeslotDuration)

            diff = initialSlots + breakSlots
            initialChunkList = AppUtils().getConsecutiveChunks(a, initialSlots)
            remainingChunkList = AppUtils().getConsecutiveChunks(a, remainingSlots)
            finalList= []

            for j in initialChunkList:
                num = j+diff
                if( num in remainingChunkList):
                    finalList.append(j)

            return finalList

        else:
            return BookingUtils().getAvailabilityOfStaffUtility(userIdOfStaff, businessId, slotDate, None)



    # partner availability is intersection of two satff availability...may need to change
    # def getPSSAvailability(self, staff1Availability, staff2Availability):
    #     return list(set(staff1Availability) & set(staff2Availability))



    # If one staff member is selected by user, then the availability is selected staff member intersection
    # with combined availabilityof other service staff members

    # If no staff is selected, one of the possible approaches has to be chosen.
    #
    # Approach I: It picks the most available staff on the service of longer duration.
    # It then intersects it with combined availability of rest of staff members for the other service

    # Approach II:
    # 1. for all staff for first service, get combined of the rest.Pick max of these.Call it maxS1
    # 2. for the staff for second service, get combined of the rest.Pick max of these.Call it maxs2
    # 3. Pick the bigger of  maxS1, maxS2.

    # def getPDSAvailablity (self):
    #     pass



    def executeBatches(self):

        while(True):
            time.sleep(24*60*64)
            self.executeOneBatch()



    def executeOneBatch(self):

        print('in execute one batch')
        approvedBusinesses = DataAccess().getBusinessesList('APPROVED','A')
        print(*approvedBusinesses, sep='\n')
        regularBusinesses=[]
        for business in approvedBusinesses:
            if(DataAccess().getBusinessServices(business[0])[0].ifTicketBasedService=='N'):
                regularBusinesses.append(business[0])
        print(regularBusinesses)
        for businessId in regularBusinesses:
            self.addAdditionalDayAvaialabilityAtEndOfBookingWindow(businessId)



    def addAdditionalDayAvaialabilityAtEndOfBookingWindow(self, businessId):
        # businesses=DataAccess().getAllBusinesses()
        # for business in businesses:
        staffMembers=DataAccess().getStaff(businessId,'A')
        for staffMember in staffMembers:
            self.addAvailabilityOnLastDayOfBookingWindow(business.businessId, staffMember)



    def addAvailabilityOnLastDayOfBookingWindow(self, businessId, staffMember):

        bookingWindow=int(DataAccess().getBusinessSettings(businessId,'A').preBookingWindow)
        dateOfDay = date.today() + timedelta(days=bookingWindow)
        # dayOfWeek = datetime.strptime(dateOfDay, config.applicationUIDateFormat).weekday()
        dayOfWeek = dateOfDay.weekday()
        oneDaySlots = DataAccess().getStaffSlotsSetup(staffMember.userId, businessId, dayOfWeek)
        workingSlotNumbers = []
        for slot in oneDaySlots:
            if (slot[2] == 'Y'):
                workingSlotNumbers.append(slot.slotNumber)

        DataAccess().addOneDayAvailabilityForUser(businessId, staffMember.userId, dateOfDay, workingSlotNumbers)



    def markNoShowOnBooking(self, businessId, bookingNumber):

        noShowMarkedOn = datetime.utcnow().astimezone(pytz.timezone("Africa/Johannesburg")).strftime(config.applicationDBDateTimeFormat)
        DataAccess().updateBookingStatus(businessId, bookingNumber, 'NOSHOW', noShowMarkedOn)
        bookingDetails=DataAccess().getBookingDetails(businessId, bookingNumber)
        staffUserId=DataAccess().getUserId(bookingDetails[10])[0]
        print('staffUserId=  ',staffUserId)
        DataAccess().markAvailability(businessId, staffUserId, 'Y', None, None, bookingDetails[8], bookingNumber)
        if(bookingDetails[11]!=None):
            staff2UserId = DataAccess().getUserId(bookingDetails[10])[0]
            DataAccess().markAvailability(businessId, staff2UserId, 'Y', None, None, bookingDetails[8], bookingNumber)

        bookingDetails=DataAccess().getBookingDetails(businessId, bookingNumber)

        service1Name=bookingDetails[3]
        service2Name = bookingDetails[12]
        staffMember1Name=bookingDetails[4]
        staffMember2Name = bookingDetails[9]
        serviceType=None
        slotsCount=int(bookingDetails[15][-2:]) - int(bookingDetails[15][:2])
        serviceDuration=(slotsCount+1)*2
        appointmentDate= bookingDetails[8]
        appointmentStartTime=bookingDetails[14][:5]
        # address = BookingUtils().getBusinessAddressForDisplay(businessId, 'Continuous')
        address, googleMapsUrl = BookingUtils().getBusinessAddressForDisplay(businessId, 'Continuous')
        price = 0
        conatctPhone = None
        extraInfo=DataAccess().getBusinessExtraInfo(businessId)
        if (extraInfo!=None):
            conatctPhone = extraInfo.contactPhone


        print(service1Name)
        print(service2Name)
        print(staffMember1Name)
        print(staffMember2Name)
        if (service2Name!=None and service1Name!=service2Name and staffMember2Name!=None and staffMember1Name !=staffMember2Name):
            serviceType='PDS'
            print('PDS service')
            service1Definition = BookingUtils().getBusinessServiceDefinition(businessId, service1Name)
            service2Definition = BookingUtils().getBusinessServiceDefinition(businessId, service2Name)
            price = int(service1Definition.price) + int(service2Definition.price)

        elif(staffMember2Name!=None and staffMember1Name != staffMember2Name and service2Name!=None and service1Name==service2Name ):
            serviceType='PSS'
            print('PSS service')
            service1Definition = BookingUtils().getBusinessServiceDefinition(businessId, service1Name)
            price = int(service1Definition.price) + int(service1Definition.price)

        elif(service2Name!=None and service1Name!=service2Name and staffMember2Name==None):
            serviceType='TRS'
            print('TRS service')
            service1Definition = BookingUtils().getBusinessServiceDefinition(businessId, service1Name)
            service2Definition = BookingUtils().getBusinessServiceDefinition(businessId, service2Name)
            price = int(service1Definition.price) + int(service2Definition.price)

        elif (service2Name == None and  staffMember2Name == None):
            serviceType='RS'
            print('RS service')
            service1Definition = BookingUtils().getBusinessServiceDefinition(businessId, service1Name)
            price = int(service1Definition.price)


        noShowEmailSetting=DataAccess().getBusinessSettings(businessId).notifyNoShowToCustomer
        if(noShowEmailSetting == 'Y'):
            AppEmail().sendNoShowEmail(businessId, bookingDetails[13], bookingDetails[2], serviceType, str(serviceDuration), service1Name, bookingDetails[7], staffMember1Name, bookingDetails[1],
                                            bookingDetails[10], appointmentDate, appointmentStartTime , service2Name, staffMember2Name,bookingDetails[11],None,bookingDetails[5],
                                            address, str(price),conatctPhone)

        return True



    def cancelBooking(self, businessId, bookingNumber, cancelReason):

        cancellationDateTime = datetime.utcnow().astimezone(pytz.timezone("Africa/Johannesburg")).strftime(config.applicationDBDateTimeFormat)
        DataAccess().updateBookingStatus(businessId, bookingNumber, 'CANCELLED', cancellationDateTime, cancelReason)
        bookingDetails=DataAccess().getBookingDetails(businessId, bookingNumber)
        staffUserId=DataAccess().getUserId(bookingDetails[10])[0]
        print('staffUserId=  ',staffUserId)
        DataAccess().markAvailability(businessId, staffUserId, 'Y', None, None, bookingDetails[8], bookingNumber)
        if(bookingDetails[11]!=None):
            staff2UserId = DataAccess().getUserId(bookingDetails[10])[0]
            DataAccess().markAvailability(businessId, staff2UserId, 'Y', None, None, bookingDetails[8], bookingNumber)

        # bookingDetails=DataAccess().getBookingDetails(businessId, bookingNumber)

        service1Name=bookingDetails[3]
        service2Name = bookingDetails[12]
        staffMember1Name=bookingDetails[4]
        staffMember2Name = bookingDetails[9]
        serviceType=None
        slotsCount=int(bookingDetails[15][-2:]) - int(bookingDetails[15][:2])
        serviceDuration=(slotsCount+1)*2
        appointmentDate= bookingDetails[8]
        appointmentStartTime=bookingDetails[14][:5]
        # address = BookingUtils().getBusinessAddressForDisplay(businessId, 'Continuous')
        address, googleMapsUrl = BookingUtils().getBusinessAddressForDisplay(businessId, 'Continuous')
        price = 0
        conatctPhone = None
        extraInfo=DataAccess().getBusinessExtraInfo(businessId)
        if (extraInfo!=None):
            conatctPhone = extraInfo.contactPhone


        if (service2Name!=None and service1Name!=service2Name and staffMember2Name!=None and staffMember1Name !=staffMember2Name):
            serviceType='PDS'
            print('PDS service')
            service1Definition = BookingUtils().getBusinessServiceDefinition(businessId, service1Name)
            service2Definition = BookingUtils().getBusinessServiceDefinition(businessId, service2Name)
            price = int(service1Definition.price) + int(service2Definition.price)

        elif(staffMember2Name!=None and staffMember1Name != staffMember2Name and service2Name!=None and service1Name==service2Name ):
            serviceType='PSS'
            print('PSS service')
            service1Definition = BookingUtils().getBusinessServiceDefinition(businessId, service1Name)
            price = int(service1Definition.price) + int(service1Definition.price)

        elif(service2Name!=None and service1Name!=service2Name and staffMember2Name==None):
            serviceType='TRS'
            print('TRS service')
            service1Definition = BookingUtils().getBusinessServiceDefinition(businessId, service1Name)
            service2Definition = BookingUtils().getBusinessServiceDefinition(businessId, service2Name)
            price = int(service1Definition.price) + int(service2Definition.price)

        elif (service2Name == None and  staffMember2Name == None):
            serviceType='RS'
            print('RS service')
            service1Definition = BookingUtils().getBusinessServiceDefinition(businessId, service1Name)
            price = int(service1Definition.price)


        AppEmail().sendCancellationEmail(businessId, bookingDetails[13], bookingDetails[2], serviceType, str(serviceDuration), service1Name, bookingDetails[7], staffMember1Name, bookingDetails[1],
                                            bookingDetails[10], appointmentDate, appointmentStartTime , service2Name, staffMember2Name,bookingDetails[11],None,bookingDetails[5],
                                            address, str(price),conatctPhone)

        return bookingNumber



    def cancelLeaves(self, businessId, parentLeaveNumber, leaveNumber=None):

        DataAccess().updateLeavesRecordsStatus(businessId, 'CANCELLED', parentLeaveNumber, leaveNumber)
        leaves=DataAccess().getLeavesRecords(businessId, parentLeaveNumber, leaveNumber)

        for leave in leaves:
            staffUserId=leave[1]
            print('staffUserId=  ',staffUserId)
            print(leave)
            # businessId, userIdOfStaff, slotStatus, minSlotNumber, maxSlotNumber, actionDate, bookingNumber, parentLeaveNumber
            DataAccess().markAvailability(businessId, staffUserId, 'Y', None, None, None, None,leave[8])

        return parentLeaveNumber, leaveNumber



    # clockTimeRange format 1130;45, user selected timeslot and duration of service
    def setBookingDetailsNew2(self, ifPartnerService, businessId, businessName, services, clockTimeRange, appointmentDate,
                          userIdOfStaff, customerEmail, partnerEmail, customerName, bookerComment):
        serviceType=BookingCore().determineTypeOfService(businessId, services, ifPartnerService)

        # clockTimeRange format 1130;45
        timeAndDuration = clockTimeRange.split(';')
        print(timeAndDuration)
        slotNumTemp=AppUtils().convertClockTimeToSlotNumber(timeAndDuration[0])

        # serviceSlotsTemp=int(timeAndDuration[1])//15
        serviceSlotsTemp = int(timeAndDuration[1]) // int(config.gSingleTimeslotDuration)
        clockEndTime=AppUtils().convertSlotNumberToClockTime(slotNumTemp+serviceSlotsTemp)
        clockTimeRange= timeAndDuration[0]+ ' - '+ clockEndTime

        if (serviceType == 'PSS'):
            print('apply partner same service logic')
            print('email=',customerEmail)
            return self.bookPSSNew2(businessId, businessName, services[0], clockTimeRange, appointmentDate,
                         userIdOfStaff, customerEmail, customerName, partnerEmail,bookerComment)

        elif (serviceType == 'PDS'):
            print('apply partner different service logic')
            print('in pds, services')
            print(services)
            return self.bookPDSNew2(businessId, businessName, services[0], services[1], clockTimeRange, appointmentDate, userIdOfStaff, customerEmail, customerName, partnerEmail,bookerComment)
        elif (serviceType == 'TRS'):
            print('apply two regulr services logic')
            return self.bookTRSNew2(businessId, businessName, services[0], services[1], clockTimeRange, appointmentDate, userIdOfStaff, customerEmail, customerName,bookerComment)
        elif (serviceType == 'RS'):
            print('apply regular service logic')
            return self.bookRSNew2(businessId, businessName, services[0], clockTimeRange, appointmentDate, userIdOfStaff, customerEmail, customerName,bookerComment)
        elif (serviceType == 'DTS'):
            print('apply double time service logic')
            return self.bookDTSNew2(businessId, businessName, services[0], clockTimeRange, appointmentDate, userIdOfStaff, customerEmail, customerName,bookerComment)



# BookingUtils().markUnavailability(businessId, userIdOfStaff, 'B', None, clockTimeRange, appointmentDate, 'N')

# DataAccess().makeBooking(businessId, bookerEmail, serviceName, staffMemberName, additionalEmail,
#                          serviceSlotsRange, serviceClockTimeRange, bookerName, appointmentDate)
# NotificationsCore().sendBookingEmail(businessName, bookerEmail, serviceName, staffMemberName, additionalEmail,
#                                      serviceClockTimeRange, bookerName, appointmentDate)

# print(BookingCore().getAvailabilityOfSkilledSatff(34,['Boys Haircut'],'2020-02-22',{"startSlotNumber":45, "endSlotNumber":53}))

# BookingCore().getAvailability(34, [1003], ['Ladies Haircut'], 'N', '1100 - 1700', None)
# BookingCore().getMostAvailableStaffMemberDatewise(34, 1003, 'staff4@bid34.com', 'Boys Haircut', 20 )

# print(BookingCore().getMostAvailableStaffMemberOnADay(34, 1003, 'Boys Haircut', '2019-12-30' ))

# print(NewBookingCore().getDatewiseUnAvailabilityPSS (34, 1003, 'Boys Haircut', 30, 2 ))

# NewBookingCore().getDatewiseUnAvailabilityPDS (34, 1003, 'Boys Haircut', 'Mens Haircut', 90, 120, 3 )
# NewBookingCore().getDatewiseUnAvailabilityRS (34, 1003, 'Boys Haircut', 30, 2 )
# o=NewBookingCore().getDatewiseUnAvailabilityTRS (34, 1003,'Mens Haircut', 'Boys Haircut', 90, 30, 4 )
#
# print(json.dumps(o))
# bands=BookingUtils().getTimeBands(34,4)
# print(bands)

# print(BookingCore().getMostAvailableStaffMemberOnADay( 34, 1003, 'Boys Haircut', 'Mens Haircut', '2019-12-31', 2 ))

# print(json.dumps(BookingUtils().getServiceCategoriesAndBusinesses()))

# print(BookingUtils().getServicesCategoriesByTopCategorries())

# print(json.dumps(NewBookingCore().getDatewiseUnAvailabilityForServiceRS(34,1003,'Boys Haircut',10)))


# BookingCore().bookRS(34,'BName','Boys Haircut','1200 - 1300','2020-01-11',1003,'custEmail@ddd.hhh','Cust Name')

# BookingUtils().getBusinessStaffDetails(34,1003)

# BookingCore().getAvailabilityForBookingPageDisplayRS(1003, 34, '2020-01-14', 'Boys Haircut')
# BookingCore().getAvailabilityForBookingPageDisplayPSS(1003,34,'2020-01-14','Boys Haircut')

# BookingCore().getStaffMemberAvailabilityOnADay(1003, 34, '2020-01-14', 'Boys Haircut')

# o=BookingCore().getAvailabilityForUI('N', 34, ['Mens Haircut'], '2020-02-10(Monday)   to 2020-02-16(Sunday)', '1200', '1400', 1003)
# print(json.dumps(o))

# o=BookingCore().getBookings(34,0,'2020-01-14','2020-01-16',None,'Manager')
# print(json.dumps(o))

# o=BookingUtils().getUIDisplayWeeks(34)
# print(*o, sep='\n')


# print(json.dumps(BookingCore().getReassignemntData( 34, '34-20200206-00000241')))

# BookingCore().applyReassignment( '34-20200206-00000241', 34,  '2020-02-06', 'Boys Haircut', 1002, 55, 57, None, None, None, None )