from datetime import datetime, date
from datetime import timedelta
# from src.dbAccess import DataAccess
# from src.booking import BookingUtils
# from src.apputils import AppUtils
from dbAccess import DataAccess
from booking import BookingUtils
from apputils import AppUtils
import json
import config
import time
from notifications import *
from model import *

class Tickets:

    def getTicketBookings(self, businessId):

        bookings=DataAccess().getTicketBookingDetails(businessId)

        bookingsDictList=[]
        for booking in bookings:
            bookingDict={}
            bookingDict["eventDate"]=booking[6].strftime(config.applicationUIDateFormat)
            bookingDict["serviceName"] = booking[1]
            bookingDict["slotClockTime"] = booking[7]
            bookingDict["bookerName"]=booking[4]
            bookingDict["bookingNumber"] = booking[5]
            bookingDict["status"]=booking[9]
            bookingDict["ticketsCount"] = booking[2]
            bookingDict["cancelButtonVisibility"] = True
            if(booking[9]=='CANCELLED'):
                bookingDict["cancelButtonVisibility"] = False

            bookingsDictList.append(bookingDict)

        return bookingsDictList



    def cancelTicket(self, businessId, bookingNumber, cancelReason):

        # 1. update booking status to cancelled
        DataAccess().updateTicketBookingStatus(businessId, bookingNumber, 'CANCELLED',cancelReason)

        # 2. Free up used tickets
        bookingDetails=DataAccess().getTicketBookingDetails(businessId, bookingNumber)[0]
        print('bookingDetails=',bookingDetails)

        print(bookingDetails[1])
        print(-1*int(bookingDetails[2]))
        print(bookingDetails[6])
        print(bookingDetails[8])
        DataAccess().updateTicketAvailability(businessId,bookingDetails[1],-1*int(bookingDetails[2]),bookingDetails[6],bookingDetails[8] )

        serviceDuration=BookingUtils().getBusinessServiceDefinition(businessId, bookingDetails[1]).duration
        AppEmail().sendTicketCancellationEmail(businessId, bookingDetails[5],bookingDetails[4], bookingDetails[3], bookingDetails[10], bookingDetails[1], bookingDetails[6],
                                    bookingDetails[7], serviceDuration)
        return bookingNumber



    def getTicketDetails(self, businessId, serviceName):
        ticketDetails=BookingUtils().getBusinessServiceDefinition(businessId, serviceName)
        print(ticketDetails)
        return ticketDetails



    def bookTickets(self, bookerName, bookerEmail, businessId, serviceName, countOfTicketsToBook, eventDate, slotStartTime):

        # 1. Entry in ticket bookings
        bookingNumber = BookingUtils().generateBookingNumber(businessId, eventDate,'Y')
        slotStartNumber=AppUtils().convertClockTimeToSlotNumber(slotStartTime)

        businessName=DataAccess().getBusinessMainFields(businessId).businessName
        contactPhone=DataAccess().getBusinessExtraInfo(businessId).contactPhone

        DataAccess().bookTicket(bookerName, bookerEmail, businessId, serviceName, countOfTicketsToBook, bookingNumber, eventDate, slotStartTime, slotStartNumber,'NEW',businessName)

        # 2. Update availability in tickets_availability
        DataAccess().updateTicketAvailability(businessId, serviceName, countOfTicketsToBook, eventDate, slotStartNumber)
        serviceDefinition = self.getTicketDetails(businessId, serviceName)
        serviceDuration=serviceDefinition.duration
        # address=BookingUtils().getBusinessAddressForDisplay(businessId,'Continuous')
        address, googleMapsUrl = BookingUtils().getBusinessAddressForDisplay(businessId, 'Continuous')
        # totalPrice=int(serviceDefinition.price) *  int(countOfTicketsToBook)
        AppEmail().sendTicketBookingEmail(businessId, countOfTicketsToBook, businessName, bookingNumber, serviceDuration,serviceName, bookerName,
                         bookerEmail,eventDate, slotStartTime, address, serviceDefinition.price, contactPhone, googleMapsUrl )

        return bookingNumber



    def generateBusinessTimeBands(self, businessId, serviceName):
        bookingWindow=DataAccess().getBusinessSettings(businessId,'A').preBookingWindow
        return self.generateTimeBands( businessId, serviceName, bookingWindow)



    def generateTimeBands(self, businessId, serviceName, bookingWindow):

        availabilityDict={}
        maxTicketsAllowedPerBooking=self.getTicketDetails(businessId,serviceName).maxTicketsSoldPerBooking
        for day in range(1, bookingWindow):
            availabilityDate = date.today() + timedelta(days=day)
            print(availabilityDate)
            oneDayAvailability = self.getTicketAvailabilityOnADay(businessId, availabilityDate, serviceName)
            print('one day:   ', oneDayAvailability)

            timeBandsAvailability=self.getOneDayAvailabilityInTimebandFormat(oneDayAvailability,maxTicketsAllowedPerBooking)
            availabilityDict[availabilityDate.strftime(config.applicationUIDateFormat)] = timeBandsAvailability
        return availabilityDict



    def getOneDayAvailabilityInTimebandFormat(self, oneDayAvailability, maxTicketsAllowedPerBooking):
        availabilityInTimebandFormat=[]
        for slotAvailbility in oneDayAvailability:
            oneSlotInTBDict={}
            clockTime=AppUtils().convertSlotNumberToClockTime(slotAvailbility[3])
            # oneSlotInTBDict[clockTime+ ' - '+str(slotAvailbility[4]) ] =slotAvailbility[4]
            ticketsAvailableForBooking=slotAvailbility[4]
            if (ticketsAvailableForBooking > maxTicketsAllowedPerBooking):
                ticketsAvailableForBooking=maxTicketsAllowedPerBooking

            oneSlotInTBDict['timeslot'] =clockTime
            oneSlotInTBDict['ticketAllowed'] = ticketsAvailableForBooking
            availabilityInTimebandFormat.append(oneSlotInTBDict)
        return availabilityInTimebandFormat



    def getTicketAvailabilityOnADay(self, businessId, availabilityDate, serviceName):
        availability=DataAccess().getTicketAvailabilityOnADay(businessId,availabilityDate,serviceName)
        return availability



    def addTicketsForNewBusiness(self, businessId, serviceName, maxAvailability, bookingWindow, businnessHours, slotDuration):

        for day in range(1, bookingWindow+1):
            # Commnted the code below and replaced by the code  that follows. Use python date
            # dateOfDay = (date.today() + timedelta(days=day)).isoformat()
            # dayOfWeek = datetime.strptime(dateOfDay, config.applicationUIDateFormat).weekday()
            dateOfDay = date.today() + timedelta(days=day)
            dayOfWeek = dateOfDay.weekday()
            slotRange=0
            if dayOfWeek ==0:
                slotRange=AppUtils().convertClockTimeRangeToSlotsRange(businnessHours.mondayHours)
            elif dayOfWeek ==1:
                slotRange = AppUtils().convertClockTimeRangeToSlotsRange(businnessHours.tuesdayHours)
            elif dayOfWeek ==2:
                slotRange = AppUtils().convertClockTimeRangeToSlotsRange(businnessHours.wednesdayHours)
            elif dayOfWeek ==3:
                slotRange = AppUtils().convertClockTimeRangeToSlotsRange(businnessHours.thursdayHours)
            elif dayOfWeek ==4:
                slotRange = AppUtils().convertClockTimeRangeToSlotsRange(businnessHours.fridayHours)
            elif dayOfWeek ==5:
                slotRange = AppUtils().convertClockTimeRangeToSlotsRange(businnessHours.saturdayHours)
            elif dayOfWeek ==6:
                slotRange = AppUtils().convertClockTimeRangeToSlotsRange(businnessHours.sundayHours)
            # print('dayOfWeek=',dayOfWeek)
            # print('dateOfDay=', dateOfDay)
            # print('slotRange= ', slotRange)

            serviceSlotsCount=(slotRange["endSlotNumber"] - slotRange["startSlotNumber"])//slotDuration
            # print('serviceSlotsCount= ', serviceSlotsCount)
            slotNumbers=[]
            for i in range (serviceSlotsCount):
                slotNumbers.append((slotRange["startSlotNumber"]+(slotDuration*i)))

            DataAccess().addOneDayTicketAvailability(businessId,serviceName,maxAvailability,dateOfDay,slotNumbers)



    def executeBatches(self):

        while(True):
            time.sleep(24*60*64)
            self.executeOneBatch()



    def executeOneBatch(self):

        print('in execute one batch')
        approvedBusinesses = DataAccess().getBusinessesList('APPROVED','A')
        print(*approvedBusinesses, sep='\n')
        ticketBusinesses=[]
        for business in approvedBusinesses:
            if(DataAccess().getBusinessServices(business[0])[0].ifTicketBasedService=='Y'):
                ticketBusinesses.append(business[0])
        print(ticketBusinesses)
        for businessId in ticketBusinesses:
            self.addAdditionalDayTicketsAtEndOfBookingWindow(businessId)



    def addAdditionalDayTicketsAtEndOfBookingWindow (self, businessId):
        services=DataAccess().getBusinessServices(businessId,'A')
        for service in services:
            self.addTicketsOnLastDayOfBookingWindow(businessId, service)



    def addTicketsOnLastDayOfBookingWindow(self, businessId, service):
        businnessHours=DataAccess().getBusinessHours(businessId,'A')
        # holidays=DataAccess().getBusinessHolidays(businessId,'A')
        bookingWindow=int(DataAccess().getBusinessSettings(businessId,'A').preBookingWindow)
        # Commnted the code below and replaced by the code  that follows. Use python date
        # dateOfDay = (date.today() + timedelta(days=day)).isoformat()
        # dayOfWeek = datetime.strptime(dateOfDay, config.applicationUIDateFormat).weekday()
        dateOfDay = date.today() + timedelta(days=day)
        dayOfWeek = dateOfDay.weekday()
        slotRange=0

        if dayOfWeek ==0:
            slotRange=AppUtils().convertClockTimeRangeToSlotsRange(businnessHours.mondayHours)
        elif dayOfWeek ==1:
            slotRange = AppUtils().convertClockTimeRangeToSlotsRange(businnessHours.tuesdayHours)
        elif dayOfWeek ==2:
            slotRange = AppUtils().convertClockTimeRangeToSlotsRange(businnessHours.wednesdayHours)
        elif dayOfWeek ==3:
            slotRange = AppUtils().convertClockTimeRangeToSlotsRange(businnessHours.thursdayHours)
        elif dayOfWeek ==4:
            slotRange = AppUtils().convertClockTimeRangeToSlotsRange(businnessHours.fridayHours)
        elif dayOfWeek ==5:
            slotRange = AppUtils().convertClockTimeRangeToSlotsRange(businnessHours.saturdayHours)
        elif dayOfWeek ==6:
            slotRange = AppUtils().convertClockTimeRangeToSlotsRange(businnessHours.sundayHours)

        slotDuration=len(service.subslotsCount)
        serviceSlotsCount = (slotRange["endSlotNumber"] - slotRange["startSlotNumber"]) // slotDuration
        slotNumbers = []

        for i in range(serviceSlotsCount):
            slotNumbers.append((slotRange["startSlotNumber"]+(slotDuration*i)))

        DataAccess().addOneDayTicketAvailability(businessId,service.name,service.totalTicketCount,dateOfDay,slotNumbers)

        # for holiday in holidays:
        #     if (dateOfDay ==holiday.date()):
        #         Tickets().markServiceUnavailableForOneDay(service, dateOfDay)



    def markBusinessUnavailableForOneDay(self, businessServices, eventDate):
        for service in businessServices:
            if (service.ifTicketBasedService=='Y'):
                self.markServiceUnavailableForOneDay(service, eventDate)



    def markServiceUnavailableForOneDay(self, businessService, eventDate):
        DataAccess().updateTicketAvailability(businessService.businessId, businessService.name, businessService.totalTicketCount, eventDate, None)


# print(Tickets().getTicketDetails('37', 'Steamer Economy'))
# print(json.dumps(Tickets().generateBusinessTimeBands(37,'Boating Economy')))
# print(json.dumps(Tickets().generateTimeBands(37,'Boating Economy', 7)))

# businessId=37
# bHours=DataAccess().getBusinessHours(businessId,'A')
# businessServices=DataAccess().getBusinessServices(businessId,'A')
# for businessService in businessServices:
#     DataAccess().addBusinessService(businessService,'A')
#     if (businessService.ifTicketBasedService=='Y'):
#         Tickets().addTicketsForNewBusiness(businessId, businessService.name,
#                                            businessService.totalTicketCount, 45,
#                                            bHours, len(businessService.subslotsCount))




# Tickets().addTicketsForNewBusiness( 37, 'Boating Economy', 25, 5, bHours, 6)

# Tickets().bookTickets('Mihika Arora','m@nn.bbb', 37,'Boating Deluxe', 2,'2020-01-10','1300')
