class Business:

    def __init__(self, businessMain, businessExtraInfo, businessHours, businessSettings, businessServices, businessAddress, staffMembers):

        self.businessMain=businessMain
        self.businessExtraInfo=businessExtraInfo
        self.businessHours=businessHours
        self.businessSettings=businessSettings
        self.businessServices=businessServices
        self.businessAddress=businessAddress
        self.staff=staffMembers


class BusinessSettings:

    def __init__(self, businessId, displayPhoneOnBooking, notifyNoShowToCustomer, bookingInterval, preBookingWindow, ifStaffNotifiedFutureBookings):

        self.businessId = businessId
        self.displayPhoneOnBooking=displayPhoneOnBooking
        self.notifyNoShowToCustomer=notifyNoShowToCustomer
        self.bookingInterval=bookingInterval
        self.preBookingWindow=preBookingWindow
        self.ifStaffNotifiedFutureBookings=ifStaffNotifiedFutureBookings

class  BusinessExtraInfo():

    def __init__(self, businessId, websiteUrl, writeup, filepath, slotsize,  contactPhone):
        self.businessId=businessId
        self.websiteUrl = websiteUrl
        self.writeup = writeup
        self.filepath = filepath
        self.slotsize=slotsize
        self.contactPhone=contactPhone

class BusinessAddress :
    def __init__(self, businessId, addressLine1, addressLine2 ,  cityLocation, city, googleMapsUrl, postalCode, latitude, longitude ):

        self.businessId = businessId
        self.addressLine1=addressLine1
        self.addressLine2=addressLine2
        self.cityLocation=cityLocation
        self.city=city
        self.googleMapsUrl =googleMapsUrl
        self.postalCode=postalCode
        self.latitude=latitude
        self.longitude=longitude


class BusinessMain:

    def __init__(self, businessId, ownerFirstname, ownerLastname, ownerEmailId, ownerPhone, businessName, status):

        self.businessId = businessId
        self.ownerFirstname=ownerFirstname
        self.ownerLastname=ownerLastname
        self.ownerEmailId=ownerEmailId
        self.ownerPhone=ownerPhone
        self.businessName=businessName
        self.status=status

class BusinessHours:

    def __init__(self, businessId, mondayHours, tuesdayHours, wednesdayHours, thursdayHours,  fridayHours,saturdayHours,sundayHours):

        self.businessId = businessId
        self.mondayHours=mondayHours
        self.tuesdayHours=tuesdayHours
        self.wednesdayHours=wednesdayHours
        self.thursdayHours=thursdayHours
        self.fridayHours=fridayHours
        self.saturdayHours=saturdayHours
        self.sundayHours=sundayHours

class BusinessService:

    def __init__(self,businessId, name, subslotsCount, ifDoubleTimeService='N', price='1', currency='RAND',  ifTicketBasedService='N', totalTicketCount=0,
                 maxTicketsSoldPerBooking=0,category=None,topCategory=None, duration=0, description=None):
        self.businessId = businessId
        self.name=name
        self.subslotsCount=subslotsCount
        self.price=price
        self.currency=currency
        self.category=category
        self.topCategory=topCategory
        self.ifDoubleTimeService=ifDoubleTimeService
        self.ifTicketBasedService=ifTicketBasedService
        self.totalTicketCount=totalTicketCount
        self.maxTicketsSoldPerBooking=maxTicketsSoldPerBooking
        self.duration=duration
        self.description=description

class Staff:

    def __init__(self,businessId, userId, firstname, lastname, emailId, phone, services, monStartTime,monEndTime, tuesStartTime, tuesEndTime,
                 wedStartTime, wedEndTime, thursStartTime, thursEndTime, friStartTime, friEndTime, satStartTime, satEndTime,
                 sunStartTime, sunEndTime, empRole,isOwner='N'):
        # businessId, None, content['firstName'], content['lastName'],
        # content['email'], content['phone'], content['serviceSkills'],
        # content['startTimeMon'], content['endTimeMon'],
        # content['startTimeTues'], content['endTimeTues'],
        # content['startTimeWed'], content['endTimeWed'],
        # content['startTimeThurs'], content['endTimeThurs'],
        # content['startTimeFri'], content['endTimeFri'],
        # content['startTimeSat'], content['endTimeSat'],
        # content['startTimeSun'], content['endTimeSun'],
        # content['staffRole'])

        self.businessId = businessId
        self.userId=userId
        self.firstname=firstname
        self.lastname=lastname
        self.emailId=emailId
        self.phone=phone
        self.services=services
        self.monStartTime=monStartTime
        self.monEndTime = monEndTime
        self.tuesStartTime=tuesStartTime
        self.tuesEndTime = tuesEndTime
        self.wedStartTime=wedStartTime
        self.wedEndTime = wedEndTime
        self.thursStartTime=thursStartTime
        self.thursEndTime = thursEndTime
        self.friStartTime=friStartTime
        self.friEndTime = friEndTime
        self.satStartTime=satStartTime
        self.satEndTime = satEndTime
        self.sunStartTime=sunStartTime
        self.sunEndTime = sunEndTime
        self.empRole=empRole
        self.isOwner=isOwner
