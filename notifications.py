from string import Template
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime,date,timedelta
import time
from connection import EmailConnection
import pytz
import config
import urllib.parse
from dbAccess import DataAccess
from model import BusinessAddress
# import json
# import os
# os.environ['PYTHONIOENCODING'] = 'utf-8'

class MailServerConnection:

    def __init__(self,emailServerHostname, emailServerPort, username, password):

        self.emailServerHostname=emailServerHostname
        self.emailServerPort=emailServerPort
        self.username=username
        self.password=password

class EmailTemplate:

    def __init__(self, temlplateName=None, subjectText=None, bodyText=None,  bodyHtml=None):
        self.temlplateName=temlplateName
        self.subjectText=subjectText
        self.bodyText=bodyText
        self.bodyHtml=bodyHtml

class EmailMessage:

    def __init__(self, fromAddress=None, toAddresses=None, replyToAddress=None, ccAddresses=None, bccAddresses=None, subject=None, body=None, bodyHtml=None, appointmentDateTime=None, serviceDuration=None, location=None, status=None):
        self.fromAddress=fromAddress
        self.toAddresses=toAddresses
        self.replyToAddress=replyToAddress
        self.ccAddresses=ccAddresses
        self.bccAddresses=bccAddresses
        self.subject=subject
        self.body=body
        self.bodyHtml=bodyHtml
        self.appointmentDateTime=appointmentDateTime
        self.serviceDuration=serviceDuration
        self.location = location
        self.Status = status

class EmailMiscellaneous:

    def __init__(self, disclaimer=None, replyToAddress=None, batchCycleInterval=None, emailProcessingInterval=None, mailserverHostname=None, mailserverPort=None, username=None, password=None, fromAddress=None, unSubscribeText=None, platformEmail=None ):

        self.disclaimer=disclaimer
        self.replyToAddress=replyToAddress
        self.batchCycleInterval=batchCycleInterval
        self.emailProcessingInterval=emailProcessingInterval
        self.mailserverHostname=mailserverHostname
        self.mailserverPort=mailserverPort
        self.username=username
        self.password=password
        self.unSubscribeText=unSubscribeText
        self.fromAddress=fromAddress
        self.platformEmail=platformEmail

class AppEmail:

    def sendTicketBookingEmail(self, businessId, numberOfTickets, businessName, bookingNumber, serviceDuration,serviceName, bookerName,
                         bookerEmail,appointmentDate, appointmentStartTime, businessAddress, price, businessContactPhone=None, businessAddressGoogleLink=None ):

        print('in sendTicketBookingEmail')
        # subjectText=''
        # body=''
        # bodyHtml =''
        valuesDict = {}

        emailMiscellaneousItems=EmailData().getEmailMiscellaneousItems()
        print(emailMiscellaneousItems)

        valuesDict["numberOfTickets"] = numberOfTickets
        valuesDict["businessId"] = businessId
        valuesDict["businessName"] = businessName
        valuesDict["bookingNumber"] = bookingNumber
        valuesDict["serviceDuration"] = str(serviceDuration)+'mins'
        print(appointmentDate)

        valuesDict["appointmentDate"] = appointmentDate.strftime('%b-%d')
        valuesDict["appointmentStartTime"] = appointmentStartTime
        valuesDict["businessAddress"] = businessAddress
        valuesDict["businessAddressGoogleLink"] = businessAddressGoogleLink

        totalPrice=int(price) * int(numberOfTickets)
        valuesDict["totalPrice"] = 'R'+str(totalPrice)+' ('+str(price)+' x '+str(numberOfTickets)+')'
        valuesDict["contactPhone"] = businessContactPhone
        valuesDict["bookerName"] = bookerName
        # valuesDict["bookerEmail"] = bookerEmail
        # valuesDict["staff1Name"] = staff1Name
        # valuesDict["staff1Email"] = staff1Email
        valuesDict["disclaimer"] = emailMiscellaneousItems.disclaimer

        bccAddressList = [emailMiscellaneousItems.platformEmail]

        templateName='TicketConfirmation'
        valuesDict["serviceName"] = serviceName
        toAddressList=[bookerEmail]
        ccAddressList=[]

        print(valuesDict)
        subjectText, bodyText, bodyHtml=self.getEmailMessageBodyAndSubject(templateName, valuesDict)
        print(subjectText)
        print(bodyText)
        print(bodyHtml)

        local = pytz.timezone("Africa/Johannesburg")
        # appointmentStartTime = '14:30'
        appointemntDateTime = appointmentDate.strftime(config.applicationUIDateFormat) + ' ' + appointmentStartTime
        print(appointmentStartTime)
        print(appointemntDateTime)
        naive = datetime.strptime(appointemntDateTime, config.applicationUIDateFormat+' '+ config.applicationUITimeFormat)
        # local_dt = local.localize(naive, is_dst=None)
        local_dt = local.localize(naive)
        utc_dt = local_dt.astimezone(pytz.utc)
        print('utc_dt')
        print(utc_dt)
        appointemntDateTimeUTC = datetime.strftime(utc_dt, config.applicationUIDateFormat+' '+ config.applicationUITimeFormat)
        # appointemntDateTimeUTC = utc_dt

        print(appointemntDateTimeUTC)
        print('toAddresslist=',toAddressList)
        self.storeEmailItems(subjectText, bodyText, bodyHtml, toAddressList, ccAddressList, bccAddressList,bookingNumber, appointemntDateTimeUTC, serviceDuration)

        return True

    def sendTicketCancellationEmail(self, businessId, bookingNumber, bookerName, bookerEmail, businessName,serviceName,appointmentDate,appointmentStartTime,serviceDuration):

        print('in sendTicketCancellationEmail')
        # subjectText=''
        # body=''
        # bodyHtml =''
        valuesDict = {}

        emailMiscellaneousItems=EmailData().getEmailMiscellaneousItems()
        print(emailMiscellaneousItems)

        valuesDict["businessName"] = businessName
        valuesDict["businessId"] = businessId
        valuesDict["bookingNumber"] = bookingNumber
        valuesDict["serviceDuration"] = serviceDuration
        print(appointmentDate)
        # appointmentDate=datetime.strptime(appointmentDate, '%Y-%m-%d').strftime('%b-%d')
        # print(appointmentDate)
        valuesDict["appointmentDate"] = appointmentDate.strftime('%b-%d')
        valuesDict["appointmentStartTime"] = appointmentStartTime
        valuesDict["bookerName"] = bookerName
        valuesDict["disclaimer"] = emailMiscellaneousItems.disclaimer

        bccAddressList = [emailMiscellaneousItems.platformEmail]

        templateName='TicketCancellation'
        valuesDict["serviceName"] = serviceName
        toAddressList=[bookerEmail]
        ccAddressList=[]

        subjectText, bodyText, bodyHtml=self.getEmailMessageBodyAndSubject(templateName, valuesDict)
        print(subjectText)
        print(bodyText)
        print(bodyHtml)

        local = pytz.timezone("Africa/Johannesburg")
        # appointmentDate = '2020-01-30'
        # appointmentStartTime = '1430'
        appointemntDateTime = appointmentDate.strftime(config.applicationUIDateFormat) + ' ' + appointmentStartTime
        print(appointmentStartTime)
        print(appointemntDateTime)
        naive = datetime.strptime(appointemntDateTime, config.applicationUIDateFormat+' '+ config.applicationUITimeFormat)
        # local_dt = local.localize(naive, is_dst=None)
        local_dt = local.localize(naive)
        utc_dt = local_dt.astimezone(pytz.utc)
        print('utc_dt')
        print(utc_dt)
        appointemntDateTimeUTC = datetime.strftime(utc_dt, config.applicationUIDateFormat+' '+ config.applicationUITimeFormat)
        # appointemntDateTimeUTC = utc_dt

        print(appointemntDateTimeUTC)
        print('toAddresslist=',toAddressList)
        self.storeEmailItems(subjectText, bodyText, bodyHtml, toAddressList, ccAddressList, bccAddressList,bookingNumber, appointemntDateTimeUTC, serviceDuration)
        return True



    def sendBookingEmail(self, businessId, businessName, bookingNumber, serviceType, serviceDuration,service1Name, bookerName, staff1Name,
                         bookerEmail, staff1Email, appointmentDate, appointmentStartTime, service2Name=None, staff2Name=None,
                         staff2Email=None, partnerName=None, partnerEmail=None, businessAddress=None, totalPrice='0', businessContactPhone=None, ifStaffNotifiedFutureBookingsSetting='N', ifDisplayPhoneOnBookingSetting='N', businessAddressGoogleLink=None ):

        print('in sendBookingEmail')
        # subjectText=''
        # body=''
        # bodyHtml =''
        valuesDict = {}

        emailMiscellaneousItems=EmailData().getEmailMiscellaneousItems()
        print(emailMiscellaneousItems)

        valuesDict["businessName"] = businessName
        valuesDict["businessId"] = businessId
        valuesDict["bookingNumber"] = bookingNumber
        # valuesDict["serviceDuration"] = str(serviceDuration)+'mins'
        valuesDict["serviceDuration"] = str(serviceDuration)+' minutes'
        print(appointmentDate)
        # appointmentDate=datetime.strptime(appointmentDate, '%Y-%m-%d').strftime('%b-%d')
        # print(appointmentDate)
        datetimeDuration = timedelta(minutes = serviceDuration)
        appointmentEndTime = appointmentDate + datetimeDuration
        print(appointmentEndTime)
        # valuesDict["appointmentDate"] = appointmentDate.strftime('%b-%d')
        valuesDict["appointmentDate"] = appointmentDate.strftime('%e %B %Y')
        valuesDict["appointmentStartTime"] = appointmentStartTime
        
        local = pytz.timezone("Africa/Johannesburg")
        # appointmentDate = '2020-01-30'
        # appointmentStartTime = '1430'
        appointemntDateTime = appointmentDate.strftime(config.applicationUIDateFormat) + ' ' + appointmentStartTime
        print(appointmentStartTime)
        print(appointemntDateTime)
        naive = datetime.strptime(appointemntDateTime, config.applicationUIDateFormat+' '+ config.applicationUITimeFormat)
        # local_dt = local.localize(naive, is_dst=None)
        local_dt = local.localize(naive)
        utc_dt = local_dt.astimezone(pytz.utc)
        print('utc_dt')
        print(utc_dt)
        appointemntDateTimeUTC = datetime.strftime(utc_dt, config.applicationUIDateFormat+' '+ config.applicationUITimeFormat)

        #Images
        valuesDict["logoURL"] = config.logo_url
        valuesDict["googleCalendarButtonImg"] = config.googleCalendarButtonImg
        valuesDict["appleCalendarButtonImg"] = config.appleCalendarButtonImg

        valuesDict["businessAddress"] = businessAddress
        valuesDict["businessAddressGoogleLink"] = businessAddressGoogleLink
        valuesDict["totalPrice"] = 'R'+str(totalPrice)
        valuesDict["contactPhone"] =''
        if(ifDisplayPhoneOnBookingSetting=='Y'):
            # valuesDict["contactPhone"] = ('Contact Phone:  '+ ('' if businessContactPhone == None else businessContactPhone))
            valuesDict["contactPhone"] = (('' if businessContactPhone == None else ('<a href=\'tel:+27' + businessContactPhone[1 : len(businessContactPhone)] + '\'>' + businessContactPhone + '</a>')))
        valuesDict["bookerName"] = bookerName
        # valuesDict["bookerEmail"] = bookerEmail
        valuesDict["staff1Name"] = staff1Name
        # valuesDict["staff1Email"] = staff1Email
        valuesDict["disclaimer"] = emailMiscellaneousItems.disclaimer


        # bccAddressList = [emailMiscellaneousItems.platformEmail]
        bccAddressList = []
        ccAddressList = []
        todaysBooking = (appointmentDate == datetime.today().date())
        ifCCToSTaff = False
        # if (ifStaffNotifiedFutureBookingsSetting == 'Y' or todaysBooking):
        # if (ifStaffNotifiedFutureBookingsSetting == 'Y' or (
        #         ifStaffNotifiedFutureBookingsSetting == 'N' and todaysBooking)):
        if (ifStaffNotifiedFutureBookingsSetting == 'Y' or todaysBooking):
            ifCCToSTaff = True
        
        apiURL = config.api_base_url

        templateName=None
        if (serviceType=='RS'):
            print('in serviceType==RS')
            templateName='RSBookingConfirmation'
            valuesDict["serviceName"] = service1Name
            # google Calendar
            valuesDict["googleCalendar"] = "https://calendar.google.com/calendar/r/eventedit?text=" + valuesDict["serviceName"] + " with " + valuesDict["staff1Name"] + "&dates=" + utc_dt.strftime('%Y%m%dT%H%M%SZ') + "/" + (utc_dt + datetimeDuration).strftime('%Y%m%dT%H%M%SZ') + "&location=" + businessAddress
            valuesDict["appleCalendar"] = apiURL + "email/" + bookingNumber
            toAddressList=[bookerEmail]
            if(ifCCToSTaff):
                # ccAddressList=[staff1Email]
                bccAddressList.append(staff1Email)

        elif (serviceType=='TRS'):
            templateName = 'TRSBookingConfirmation'
            valuesDict["service1Name"] = service1Name
            valuesDict["service2Name"] = service2Name
            valuesDict["staff2Name"] = staff2Name
            valuesDict["price1"] = 'R'+totalPrice.split(';')[0]
            valuesDict["price2"] = 'R'+totalPrice.split(';')[1]
            # valuesDict["serviceName"] = service1Name+', '+service2Name
            # google Calendar valuesDict["googleCalendar"] = "https://calendar.google.com/calendar/r/eventedit?text=" + valuesDict["service1Name"] + " with " + valuesDict["staff1Name"] + " and " + valuesDict["service2Name"] + " with " + valuesDict["staff2Name"] + "&dates=" + utc_dt.strftime('%Y%m%dT%H%M%SZ') + "/" + (utc_dt + datetimeDuration).strftime('%Y%m%dT%H%M%SZ') + "&location=" + businessAddress
            valuesDict["googleCalendar"] = "https://calendar.google.com/calendar/r/eventedit?text=" + valuesDict["service1Name"] + " with " + valuesDict["staff1Name"] + " and " + valuesDict["service2Name"] + " with " + valuesDict["staff2Name"] + "&dates=" + utc_dt.strftime('%Y%m%dT%H%M%SZ') + "/" + (utc_dt + datetimeDuration).strftime('%Y%m%dT%H%M%SZ') + "&location=" + businessAddress
                     
            # valuesDict["googleCalendar"] = "https://calendar.google.com/calendar/r/eventedit?text=" + valuesDict["serviceName"] + " with " + valuesDict["staff1Name"] + "&dates=" + utc_dt.strftime('%Y%m%dT%H%M%SZ') + "/" + (utc_dt + datetimeDuration).strftime('%Y%m%dT%H%M%SZ') + "&location=" + businessAddress
            valuesDict["appleCalendar"] = apiURL + "email/" + bookingNumber
            toAddressList=[bookerEmail]
            if (ifCCToSTaff):
                # ccAddressList=[staff1Email]
                bccAddressList.append(staff1Email)
                bccAddressList.append(staff2Email)

        elif (serviceType == 'PSS'):
            templateName = 'PSSBookingConfirmation'
            valuesDict["serviceName"] = service1Name
            valuesDict["staff2Name"] = staff2Name
            # valuesDict["staff2Email"] = staff2Email
            # $serviceName with $staff1Name and $staff2Name
            valuesDict["partnerName"] = partnerName
            # valuesDict["partnerEmail"] = partnerEmail

            # google Calendar
            valuesDict["googleCalendar"] = "https://calendar.google.com/calendar/r/eventedit?text=" + valuesDict["serviceName"] + " with " + valuesDict["staff1Name"] + " and " + valuesDict["staff2Name"] + "&dates=" + utc_dt.strftime('%Y%m%dT%H%M%SZ') + "/" + (utc_dt + datetimeDuration).strftime('%Y%m%dT%H%M%SZ') + "&location=" + businessAddress
            valuesDict["appleCalendar"] = apiURL + "email/" + bookingNumber

            toAddressList=[bookerEmail,partnerEmail]
            if(ifCCToSTaff):
                # ccAddressList=[staff1Email,staff2Email]
                bccAddressList.append(staff1Email)
                bccAddressList.append(staff2Email)

        elif (serviceType == 'PDS'):

            templateName = 'PDSBookingConfirmation'
            valuesDict["service1Name"] = service1Name
            valuesDict["service2Name"] = service2Name
            valuesDict["staff2Name"] = staff2Name
            # valuesDict["staff2Email"] = staff2Email
            valuesDict["partnerName"] = partnerName
            # valuesDict["partnerEmail"] = partnerEmail
            valuesDict["price1"] = 'R'+totalPrice.split(';')[0]
            valuesDict["price2"] = 'R'+totalPrice.split(';')[1]

            # google Calendar
            valuesDict["googleCalendar"] = "https://calendar.google.com/calendar/r/eventedit?text=" + valuesDict["service1Name"] + " with " + valuesDict["staff1Name"] + " and " + valuesDict["service2Name"] + " with " + valuesDict["staff2Name"] + "&dates=" + utc_dt.strftime('%Y%m%dT%H%M%SZ') + "/" + (utc_dt + datetimeDuration).strftime('%Y%m%dT%H%M%SZ') + "&location=" + businessAddress
            valuesDict["appleCalendar"] = apiURL + "email/" + bookingNumber

            toAddressList=[bookerEmail,partnerEmail]
            if(ifCCToSTaff):
                # ccAddressList=[staff1Email,staff2Email]
                bccAddressList.append(staff1Email)
                bccAddressList.append(staff2Email)

        elif (serviceType == 'DTS'):
            templateName = 'DTSBookingConfirmation'
            valuesDict["serviceName"] = service1Name
            # google Calendar
            valuesDict["googleCalendar"] = "https://calendar.google.com/calendar/r/eventedit?text=" + valuesDict["serviceName"] + " with " + valuesDict["staff1Name"] + "&dates=" + utc_dt.strftime('%Y%m%dT%H%M%SZ') + "/" + (utc_dt + datetimeDuration).strftime('%Y%m%dT%H%M%SZ') + "&location=" + businessAddress
            valuesDict["appleCalendar"] = apiURL + "email/" + bookingNumber
            toAddressList=[bookerEmail]
            if(ifCCToSTaff):
                # ccAddressList=staff1Email
                bccAddressList.append(staff1Email)

        subjectText, bodyText, bodyHtml=self.getEmailMessageBodyAndSubject(templateName, valuesDict)
        print(subjectText)
        print(bodyText)
        print(bodyHtml)

        local = pytz.timezone("Africa/Johannesburg")
        # appointmentDate = '2020-01-30'
        # appointmentStartTime = '1430'
        appointemntDateTime = appointmentDate.strftime(config.applicationUIDateFormat) + ' ' + appointmentStartTime
        print(appointmentStartTime)
        print(appointemntDateTime)
        naive = datetime.strptime(appointemntDateTime, config.applicationUIDateFormat+' '+ config.applicationUITimeFormat)
        # local_dt = local.localize(naive, is_dst=None)
        local_dt = local.localize(naive)
        utc_dt = local_dt.astimezone(pytz.utc)
        print('utc_dt')
        print(utc_dt)
        appointemntDateTimeUTC = datetime.strftime(utc_dt, config.applicationUIDateFormat+' '+ config.applicationUITimeFormat)
        # appointemntDateTimeUTC = utc_dt

        print(appointemntDateTimeUTC)
        print('toAddresslist=',toAddressList)
        self.storeEmailItems(subjectText, bodyText, bodyHtml, toAddressList, ccAddressList, bccAddressList,bookingNumber, appointemntDateTimeUTC, serviceDuration)
        return True




    def sendCancellationEmail(self, businessId, businessName, bookingNumber, serviceType, serviceDuration, service1Name, bookerName, staff1Name,
                         bookerEmail, staff1Email, appointmentDate, appointmentStartTime, service2Name=None, staff2Name=None,
                         staff2Email=None, partnerName=None, partnerEmail=None, businessAddress=None, totalPrice='1', businessContactPhone=None ):

        print('in sendCancellationEmail')
        # subjectText=''
        # body=''
        # bodyHtml =''
        valuesDict = {}

        emailMiscellaneousItems=EmailData().getEmailMiscellaneousItems()
        print(emailMiscellaneousItems)

        valuesDict["businessName"] = businessName
        valuesDict["businessId"] = businessId

        #Images
        valuesDict["logoURL"] = config.logo_url

        valuesDict["bookingNumber"] = bookingNumber
        valuesDict["serviceDuration"] = serviceDuration
        print(appointmentDate)
        # appointmentDate=datetime.strptime(appointmentDate, '%Y-%m-%d').strftime('%b-%d')
        print(appointmentDate)
        print(type(appointmentDate))
        valuesDict["appointmentDate"] = appointmentDate.strftime('%b-%d')
        valuesDict["appointmentStartTime"] = appointmentStartTime
        # valuesDict["businessAddress"] = businessAddress
        # valuesDict["totalPrice"] = totalPrice
        valuesDict["contactPhone"] = businessContactPhone
        valuesDict["bookerName"] = bookerName
        # valuesDict["bookerEmail"] = bookerEmail
        valuesDict["staff1Name"] = staff1Name
        # valuesDict["staff1Email"] = staff1Email
        valuesDict["disclaimer"] = emailMiscellaneousItems.disclaimer

        ccAddressList = []
        # bccAddressList = [emailMiscellaneousItems.platformEmail]

        templateName='BookingCancellation'
        if (serviceType=='RS'):
            print('in serviceType==RS')
            # templateName='RSBookingCancellation'
            valuesDict["serviceName"] = service1Name
            toAddressList=[bookerEmail]
            bccAddressList=[staff1Email]

        elif (serviceType=='TRS'):
            # templateName = 'TRSBookingCancellation'
            valuesDict["serviceName"] = service1Name+', '+service2Name
            toAddressList=[bookerEmail]
            bccAddressList=[staff1Email]

        elif (serviceType == 'PSS'):
            # templateName = 'PSSBookingCancellation'
            valuesDict["serviceName"] = service1Name
            valuesDict["staff2Name"] = staff2Name
            # valuesDict["staff2Email"] = staff2Email
            valuesDict["partnerName"] = partnerName
            # valuesDict["partnerEmail"] = partnerEmail
            toAddressList=[bookerEmail,partnerEmail]
            bccAddressList=[staff1Email,staff2Email]

        elif (serviceType == 'PDS'):
            # templateName = 'PDSBookingCancellation'
            valuesDict["serviceName"] = service1Name+', '+service2Name
            valuesDict["staff2Name"] = staff2Name
            # valuesDict["staff2Email"] = staff2Email
            valuesDict["partnerName"] = partnerName
            # valuesDict["partnerEmail"] = partnerEmail
            toAddressList=[bookerEmail,partnerEmail]
            bccAddressList=[staff1Email,staff2Email]

        elif (serviceType == 'DTS'):
            # templateName = 'DTSBookingCancellation'
            valuesDict["serviceName"] = service1Name
            toAddressList=[bookerEmail]
            bccAddressList=staff1Email

        subjectText, bodyText, bodyHtml=self.getEmailMessageBodyAndSubject(templateName, valuesDict)
        print(subjectText)
        print(bodyText)
        print(bodyHtml)

        local = pytz.timezone("Africa/Johannesburg")
        # appointmentDate = '2020-01-30'
        # appointmentStartTime = '1430'
        appointemntDateTime = appointmentDate.strftime(config.applicationUIDateFormat) + ' ' + appointmentStartTime
        print(appointmentStartTime)
        print(appointemntDateTime)
        naive = datetime.strptime(appointemntDateTime, config.applicationUIDateFormat+' '+ config.applicationUITimeFormat)
        # local_dt = local.localize(naive, is_dst=None)
        local_dt = local.localize(naive)
        utc_dt = local_dt.astimezone(pytz.utc)
        print('utc_dt')
        print(utc_dt)
        appointemntDateTimeUTC = datetime.strftime(utc_dt, config.applicationUIDateFormat+' '+ config.applicationUITimeFormat)
        # appointemntDateTimeUTC = utc_dt

        print(appointemntDateTimeUTC)
        print('toAddresslist=',toAddressList)
        self.storeEmailItems(subjectText, bodyText, bodyHtml, toAddressList, ccAddressList, bccAddressList,bookingNumber, appointemntDateTimeUTC, serviceDuration)

        return True



    def sendNoShowEmail(self, businessId, businessName, bookingNumber, serviceType, serviceDuration, service1Name, bookerName, staff1Name,
                         bookerEmail, staff1Email, appointmentDate, appointmentStartTime, service2Name=None, staff2Name=None,
                         staff2Email=None, partnerName=None, partnerEmail=None, businessAddress=None, totalPrice='1', businessContactPhone=None ):

        print('in send NoShow Email')
        print(serviceType)
        valuesDict = {}

        emailMiscellaneousItems=EmailData().getEmailMiscellaneousItems()
        print(emailMiscellaneousItems)

        valuesDict["businessName"] = businessName
        valuesDict["businessId"] = businessId

        #Images
        valuesDict["logoURL"] = config.logo_url

        valuesDict["bookingNumber"] = bookingNumber
        valuesDict["serviceDuration"] = serviceDuration
        print(appointmentDate)
        # appointmentDate=datetime.strptime(appointmentDate, '%Y-%m-%d').strftime('%b-%d')
        print(appointmentDate)
        print(type(appointmentDate))
        valuesDict["appointmentDate"] = appointmentDate.strftime('%b-%d')
        valuesDict["appointmentStartTime"] = appointmentStartTime
        # valuesDict["businessAddress"] = businessAddress
        # valuesDict["totalPrice"] = totalPrice
        valuesDict["contactPhone"] = businessContactPhone
        valuesDict["bookerName"] = bookerName
        # valuesDict["bookerEmail"] = bookerEmail
        valuesDict["staff1Name"] = staff1Name
        # valuesDict["staff1Email"] = staff1Email
        valuesDict["disclaimer"] = emailMiscellaneousItems.disclaimer

        ccAddressList = []
        # bccAddressList = [emailMiscellaneousItems.platformEmail]

        templateName='NoShowEmail'
        if (serviceType=='RS' or serviceType=='DTS'):
            print('in serviceType==RS or DTS')
            valuesDict["serviceName"] = service1Name
            toAddressList=[bookerEmail]
            bccAddressList=[staff1Email]

        elif (serviceType=='TRS'):
            valuesDict["serviceName"] = service1Name+', '+service2Name
            toAddressList=[bookerEmail]
            bccAddressList=[staff1Email]

        elif (serviceType == 'PSS'):
            valuesDict["serviceName"] = service1Name
            valuesDict["staff2Name"] = staff2Name
            # valuesDict["staff2Email"] = staff2Email
            valuesDict["partnerName"] = partnerName
            # valuesDict["partnerEmail"] = partnerEmail
            toAddressList=[bookerEmail,partnerEmail]
            bccAddressList=[staff1Email,staff2Email]

        elif (serviceType == 'PDS'):
            valuesDict["serviceName"] = service1Name+', '+service2Name
            valuesDict["staff2Name"] = staff2Name
            # valuesDict["staff2Email"] = staff2Email
            valuesDict["partnerName"] = partnerName
            # valuesDict["partnerEmail"] = partnerEmail
            toAddressList=[bookerEmail,partnerEmail]
            bccAddressList=[staff1Email,staff2Email]

        # elif (serviceType == 'DTS'):
        #     valuesDict["serviceName"] = service1Name
        #     toAddressList=[bookerEmail]
        #     ccAddressList=staff1Email

        subjectText, bodyText, bodyHtml=self.getEmailMessageBodyAndSubject(templateName, valuesDict)
        print(subjectText)
        print(bodyText)
        print(bodyHtml)

        local = pytz.timezone("Africa/Johannesburg")
        # appointmentDate = '2020-01-30'
        # appointmentStartTime = '1430'
        appointemntDateTime = appointmentDate.strftime(config.applicationUIDateFormat) + ' ' + appointmentStartTime
        print(appointmentStartTime)
        print(appointemntDateTime)
        naive = datetime.strptime(appointemntDateTime, config.applicationUIDateFormat+' '+ config.applicationUITimeFormat)
        # local_dt = local.localize(naive, is_dst=None)
        local_dt = local.localize(naive)
        utc_dt = local_dt.astimezone(pytz.utc)
        print('utc_dt')
        print(utc_dt)
        appointemntDateTimeUTC = datetime.strftime(utc_dt, config.applicationUIDateFormat+' '+ config.applicationUITimeFormat)
        # appointemntDateTimeUTC = utc_dt

        print(appointemntDateTimeUTC)
        print('toAddresslist=',toAddressList)
        self.storeEmailItems(subjectText, bodyText, bodyHtml, toAddressList, ccAddressList, bccAddressList,bookingNumber, appointemntDateTimeUTC, serviceDuration)

        return True



    def getEmailMessageBodyAndSubject(self, templateName, valuesDict):

        print('in getEmailMessageBodyAndSubject. template is   ', templateName)
        print(valuesDict)
        bodyText = ''
        subjectText=''
        bodyHtml=''

        templateData=EmailData().getTemplate(templateName)
        # print(templateData.subjectText)
        # print(templateData.bodyText)
        # print(templateData.bodyHtml)
        # sys.exit(0)
        subjectTemplate = Template(templateData.subjectText)
        bodyTemplate = Template(templateData.bodyText)
        bodyHtmlTemplate = Template(templateData.bodyHtml)

        if (templateName=='RSBookingConfirmation'):

            print('in temlplateName==RSBookingConfirmation')
            print('businessName=',valuesDict['businessName'])
            print('appointmentDate=', valuesDict['appointmentDate'])
            subjectText= subjectTemplate.substitute(businessName=valuesDict['businessName'], appointmentDate=valuesDict['appointmentDate'])
            print('subjectText=',subjectText)
            cancellationBaseUrl = config.baseUrl + '/cancel-view/' + valuesDict['businessId']
            bookingParams={}
            bookingParams['bkNbr']= valuesDict['bookingNumber']
            bookingParams['type']= 'regular'
            bookingParams['appointment']= valuesDict['appointmentDate'] + ' ' + valuesDict['appointmentStartTime']

            # Customer Name and Service
            bookingParams['customer']= valuesDict['bookerName']
            bookingParams['service']= valuesDict['serviceName']
            queryString = urllib.parse.urlencode(bookingParams)
            cancelLink = cancellationBaseUrl + '/?'+ queryString
            print(cancelLink)

            bodyText= bodyTemplate.substitute(businessName=valuesDict["businessName"],bookingNumber=valuesDict["bookingNumber"],
                      serviceDuration=valuesDict["serviceDuration"], appointmentDate=valuesDict["appointmentDate"],appointmentStartTime=valuesDict["appointmentStartTime"],
                      bookerName=valuesDict["bookerName"], staff1Name=valuesDict["staff1Name"], disclaimer=valuesDict["disclaimer"], serviceName=valuesDict["serviceName"],
                        businessAddress=valuesDict["businessAddress"],contactPhone=valuesDict["contactPhone"],totalPrice=valuesDict["totalPrice"],cancelLink=cancelLink, businessAddressGoogleLink=valuesDict["businessAddressGoogleLink"])
            print('bodyText=', bodyText)

            bodyHtml = bodyHtmlTemplate.substitute(businessName=valuesDict["businessName"],bookingNumber=valuesDict["bookingNumber"],
                      serviceDuration=valuesDict["serviceDuration"], appointmentDate=valuesDict["appointmentDate"],appointmentStartTime=valuesDict["appointmentStartTime"],
                      bookerName=valuesDict["bookerName"], staff1Name=valuesDict["staff1Name"], disclaimer=valuesDict["disclaimer"], serviceName=valuesDict["serviceName"],
                        businessAddress=valuesDict["businessAddress"],contactPhone=valuesDict["contactPhone"],totalPrice=valuesDict["totalPrice"],cancelLink=cancelLink, businessAddressGoogleLink=valuesDict["businessAddressGoogleLink"], googleCalendarLink = valuesDict["googleCalendar"], appleCalendarLink = valuesDict["appleCalendar"],
                        logoURL = valuesDict["logoURL"], googleCalendarButtonImg = valuesDict["googleCalendarButtonImg"], appleCalendarButtonImg = valuesDict["appleCalendarButtonImg"])
            print('bodyHtml=', bodyHtml)

        if (templateName=='TRSBookingConfirmation'):

            print('in temlplateName==TRSBookingConfirmation')
            subjectText= subjectTemplate.substitute(businessName=valuesDict['businessName'], appointmentDate=valuesDict['appointmentDate'])
            print('subjectText=',subjectText)
            cancellationBaseUrl = config.baseUrl + '/cancel-view/' + valuesDict['businessId']
            bookingParams={}
            bookingParams['bkNbr']= valuesDict['bookingNumber']
            bookingParams['type']= 'regular'
            bookingParams['appointment']= valuesDict['appointmentDate'] + ' ' + valuesDict['appointmentStartTime']
            
            # Customer Name and Service
            bookingParams['customer']= valuesDict['bookerName']
            bookingParams['service']= valuesDict['service1Name'] + ', ' + valuesDict['service2Name']
            queryString = urllib.parse.urlencode(bookingParams)
            cancelLink = cancellationBaseUrl + '/?'+ queryString
            print(cancelLink)

            bodyText= bodyTemplate.substitute(businessName=valuesDict["businessName"],bookingNumber=valuesDict["bookingNumber"],
                      serviceDuration=valuesDict["serviceDuration"], appointmentDate=valuesDict["appointmentDate"],appointmentStartTime=valuesDict["appointmentStartTime"],
                      bookerName=valuesDict["bookerName"], staff1Name=valuesDict["staff1Name"], disclaimer=valuesDict["disclaimer"], serviceName=valuesDict["service1Name"],
                        businessAddress=valuesDict["businessAddress"],contactPhone=valuesDict["contactPhone"],totalPrice=valuesDict["totalPrice"],cancelLink=cancelLink, businessAddressGoogleLink=valuesDict["businessAddressGoogleLink"])
            print('bodyText=', bodyText)

            # bodyHtml = bodyHtmlTemplate.substitute(businessName=valuesDict["businessName"],bookingNumber=valuesDict["bookingNumber"],
            #           serviceDuration=valuesDict["serviceDuration"], appointmentDate=valuesDict["appointmentDate"],appointmentStartTime=valuesDict["appointmentStartTime"],
            #           bookerName=valuesDict["bookerName"], staff1Name=valuesDict["staff1Name"], disclaimer=valuesDict["disclaimer"], serviceName=valuesDict["serviceName"],
            #             businessAddress=valuesDict["businessAddress"],contactPhone=valuesDict["contactPhone"],totalPrice=valuesDict["totalPrice"],cancelLink=cancelLink, businessAddressGoogleLink=valuesDict["businessAddressGoogleLink"], googleCalendarLink = valuesDict["googleCalendar"], appleCalendarLink = valuesDict["appleCalendar"],
            #             logoURL = valuesDict["logoURL"], googleCalendarButtonImg = valuesDict["googleCalendarButtonImg"], appleCalendarButtonImg = valuesDict["appleCalendarButtonImg"])
            # print('bodyHtml=', bodyHtml)
            bodyHtml = bodyHtmlTemplate.substitute(businessName=valuesDict["businessName"],bookingNumber=valuesDict["bookingNumber"],
                      serviceDuration=valuesDict["serviceDuration"], appointmentDate=valuesDict["appointmentDate"],appointmentStartTime=valuesDict["appointmentStartTime"],
                      bookerName=valuesDict["bookerName"],staff1Name=valuesDict["staff1Name"],  disclaimer=valuesDict["disclaimer"], service1Name=valuesDict["service1Name"],service2Name=valuesDict["service2Name"],
                      staff2Name=valuesDict["staff2Name"],
                        businessAddress=valuesDict["businessAddress"],contactPhone=valuesDict["contactPhone"],price1=valuesDict["price1"],price2=valuesDict["price2"],cancelLink=cancelLink, businessAddressGoogleLink=valuesDict["businessAddressGoogleLink"], googleCalendarLink = valuesDict["googleCalendar"], appleCalendarLink = valuesDict["appleCalendar"],
                        logoURL = valuesDict["logoURL"], googleCalendarButtonImg = valuesDict["googleCalendarButtonImg"], appleCalendarButtonImg = valuesDict["appleCalendarButtonImg"])



        if (templateName=='PSSBookingConfirmation'):

            subjectText= subjectTemplate.substitute(businessName=valuesDict['businessName'], appointmentDate=valuesDict['appointmentDate'])
            cancellationBaseUrl = config.baseUrl + '/cancel-view/' + valuesDict['businessId']
            bookingParams={}
            bookingParams['bkNbr']= valuesDict['bookingNumber']
            bookingParams['type']= 'regular'
            bookingParams['appointment']= valuesDict['appointmentDate'] + ' ' + valuesDict['appointmentStartTime']
            
            # Customer Name and Service
            bookingParams['customer']= valuesDict['bookerName']
            bookingParams['service']= valuesDict['serviceName']
            queryString = urllib.parse.urlencode(bookingParams)
            cancelLink = cancellationBaseUrl + '/?'+ queryString
            print(cancelLink)

            bodyText= bodyTemplate.substitute(businessName=valuesDict["businessName"],bookingNumber=valuesDict["bookingNumber"],
                      serviceDuration=valuesDict["serviceDuration"], appointmentDate=valuesDict["appointmentDate"],appointmentStartTime=valuesDict["appointmentStartTime"],
                      bookerName=valuesDict["bookerName"],staff1Name=valuesDict["staff1Name"],  disclaimer=valuesDict["disclaimer"], serviceName=valuesDict["serviceName"],
                      staff2Name=valuesDict["staff2Name"], partnerName=valuesDict["partnerName"],
                        businessAddress=valuesDict["businessAddress"],contactPhone=valuesDict["contactPhone"],totalPrice=valuesDict["totalPrice"],cancelLink=cancelLink, businessAddressGoogleLink=valuesDict["businessAddressGoogleLink"])

            bodyHtml = bodyHtmlTemplate.substitute(businessName=valuesDict["businessName"],bookingNumber=valuesDict["bookingNumber"],
                      serviceDuration=valuesDict["serviceDuration"], appointmentDate=valuesDict["appointmentDate"],appointmentStartTime=valuesDict["appointmentStartTime"],
                      bookerName=valuesDict["bookerName"],staff1Name=valuesDict["staff1Name"],  disclaimer=valuesDict["disclaimer"], serviceName=valuesDict["serviceName"],
                      staff2Name=valuesDict["staff2Name"], partnerName=valuesDict["partnerName"],
                        businessAddress=valuesDict["businessAddress"],contactPhone=valuesDict["contactPhone"],totalPrice=valuesDict["totalPrice"],cancelLink=cancelLink, businessAddressGoogleLink=valuesDict["businessAddressGoogleLink"], googleCalendarLink = valuesDict["googleCalendar"], appleCalendarLink = valuesDict["appleCalendar"],
                        logoURL = valuesDict["logoURL"], googleCalendarButtonImg = valuesDict["googleCalendarButtonImg"], appleCalendarButtonImg = valuesDict["appleCalendarButtonImg"])

        if (templateName=='PDSBookingConfirmation'):

            subjectText= subjectTemplate.substitute(businessName=valuesDict['businessName'], appointmentDate=valuesDict['appointmentDate'])
            cancellationBaseUrl = config.baseUrl + '/cancel-view/' + valuesDict['businessId']
            bookingParams={}
            bookingParams['bkNbr']= valuesDict['bookingNumber']
            bookingParams['type']= 'regular'
            bookingParams['appointment']= valuesDict['appointmentDate'] + ' ' + valuesDict['appointmentStartTime']
            
            # Customer Name and Service
            bookingParams['customer']= valuesDict['bookerName']
            bookingParams['service']= valuesDict['service1Name'] + ', ' + valuesDict['service2Name']
            queryString = urllib.parse.urlencode(bookingParams)
            cancelLink = cancellationBaseUrl + '/?'+ queryString
            print(cancelLink)

            bodyText= bodyTemplate.substitute(businessName=valuesDict["businessName"],bookingNumber=valuesDict["bookingNumber"],
                      serviceDuration=valuesDict["serviceDuration"], appointmentDate=valuesDict["appointmentDate"],appointmentStartTime=valuesDict["appointmentStartTime"],
                      bookerName=valuesDict["bookerName"],staff1Name=valuesDict["staff1Name"],  disclaimer=valuesDict["disclaimer"], service1Name=valuesDict["service1Name"],service2Name=valuesDict["service2Name"],
                      staff2Name=valuesDict["staff2Name"], partnerName=valuesDict["partnerName"],
                        businessAddress=valuesDict["businessAddress"],contactPhone=valuesDict["contactPhone"],price1=valuesDict["price1"],price2=valuesDict["price2"],cancelLink=cancelLink, businessAddressGoogleLink=valuesDict["businessAddressGoogleLink"])

            bodyHtml = bodyHtmlTemplate.substitute(businessName=valuesDict["businessName"],bookingNumber=valuesDict["bookingNumber"],
                      serviceDuration=valuesDict["serviceDuration"], appointmentDate=valuesDict["appointmentDate"],appointmentStartTime=valuesDict["appointmentStartTime"],
                      bookerName=valuesDict["bookerName"],staff1Name=valuesDict["staff1Name"],  disclaimer=valuesDict["disclaimer"], service1Name=valuesDict["service1Name"],service2Name=valuesDict["service2Name"],
                      staff2Name=valuesDict["staff2Name"], partnerName=valuesDict["partnerName"],
                        businessAddress=valuesDict["businessAddress"],contactPhone=valuesDict["contactPhone"],price1=valuesDict["price1"],price2=valuesDict["price2"],cancelLink=cancelLink, businessAddressGoogleLink=valuesDict["businessAddressGoogleLink"], googleCalendarLink = valuesDict["googleCalendar"], appleCalendarLink = valuesDict["appleCalendar"],
                        logoURL = valuesDict["logoURL"], googleCalendarButtonImg = valuesDict["googleCalendarButtonImg"], appleCalendarButtonImg = valuesDict["appleCalendarButtonImg"])

        if (templateName=='DTSBookingConfirmation'):

            subjectText= subjectTemplate.substitute(businessName=valuesDict['businessName'], appointmentDate=valuesDict['appointmentDate'])
            print('subjectText=',subjectText)
            cancellationBaseUrl = config.baseUrl + '/cancel-view/' + valuesDict['businessId']
            bookingParams={}
            bookingParams['bkNbr']= valuesDict['bookingNumber']
            bookingParams['type']= 'regular'
            bookingParams['appointment']= valuesDict['appointmentDate'] + ' ' + valuesDict['appointmentStartTime']
            
            # Customer Name and Service
            bookingParams['customer']= valuesDict['bookerName']
            bookingParams['service']= valuesDict['serviceName']
            queryString = urllib.parse.urlencode(bookingParams)
            cancelLink = cancellationBaseUrl + '/?'+ queryString

            bodyText= bodyTemplate.substitute(businessName=valuesDict["businessName"],bookingNumber=valuesDict["bookingNumber"],
                      serviceDuration=valuesDict["serviceDuration"], appointmentDate=valuesDict["appointmentDate"],appointmentStartTime=valuesDict["appointmentStartTime"],
                      bookerName=valuesDict["bookerName"], staff1Name=valuesDict["staff1Name"], disclaimer=valuesDict["disclaimer"], serviceName=valuesDict["serviceName"],
                        businessAddress=valuesDict["businessAddress"],contactPhone=valuesDict["contactPhone"],totalPrice=valuesDict["totalPrice"],cancelLink=cancelLink, businessAddressGoogleLink=valuesDict["businessAddressGoogleLink"])
            print('bodyText=', bodyText)

            bodyHtml = bodyHtmlTemplate.substitute(businessName=valuesDict["businessName"],bookingNumber=valuesDict["bookingNumber"],
                      serviceDuration=valuesDict["serviceDuration"], appointmentDate=valuesDict["appointmentDate"],appointmentStartTime=valuesDict["appointmentStartTime"],
                      bookerName=valuesDict["bookerName"], staff1Name=valuesDict["staff1Name"], disclaimer=valuesDict["disclaimer"], serviceName=valuesDict["serviceName"],
                        businessAddress=valuesDict["businessAddress"],contactPhone=valuesDict["contactPhone"],totalPrice=valuesDict["totalPrice"],cancelLink=cancelLink, businessAddressGoogleLink=valuesDict["businessAddressGoogleLink"], googleCalendarLink = valuesDict["googleCalendar"], appleCalendarLink = valuesDict["appleCalendar"],
                        logoURL = valuesDict["logoURL"], googleCalendarButtonImg = valuesDict["googleCalendarButtonImg"], appleCalendarButtonImg = valuesDict["appleCalendarButtonImg"])
            print('bodyHtml=', bodyHtml)

        if (templateName=='BookingCancellation'):

            subjectText= subjectTemplate.substitute(businessName=valuesDict['businessName'])
            print('subjectText=',subjectText)
            newBookingLink = config.baseAppUrl +'/business/'+urllib.parse.quote(valuesDict["businessName"])+'/'+valuesDict["businessId"]
            bodyText= bodyTemplate.substitute(businessName=valuesDict["businessName"],bookingNumber=valuesDict["bookingNumber"],
                      serviceDuration=valuesDict["serviceDuration"], appointmentDate=valuesDict["appointmentDate"],appointmentStartTime=valuesDict["appointmentStartTime"],
                      bookerName=valuesDict["bookerName"], disclaimer=valuesDict["disclaimer"], serviceName=valuesDict["serviceName"],
                        newBookingLink=newBookingLink)
            print('bodyText=', bodyText)

            bodyHtml = bodyHtmlTemplate.substitute(businessName=valuesDict["businessName"],bookingNumber=valuesDict["bookingNumber"],
                      serviceDuration=valuesDict["serviceDuration"], appointmentDate=valuesDict["appointmentDate"],appointmentStartTime=valuesDict["appointmentStartTime"],
                      bookerName=valuesDict["bookerName"], disclaimer=valuesDict["disclaimer"], serviceName=valuesDict["serviceName"],
                        newBookingLink=newBookingLink, staff1Name=valuesDict["staff1Name"], logoURL = valuesDict["logoURL"])
            print('bodyHtml=', bodyHtml)


        if (templateName=='TRSBookingCancellation'):
            pass

        if (templateName=='PSSBookingCancellation'):
            pass

        if (templateName=='PDSBookingCancellation'):
            pass

        if (templateName=='DTSBookingCancellation'):
            pass

        if (templateName=='NoShowEmail'):
            subjectText= subjectTemplate.substitute(businessName=valuesDict['businessName'])
            print('subjectText=',subjectText)
            newBookingLink = config.baseAppUrl + '/business/' + urllib.parse.quote(valuesDict["businessName"]) + '/' + \
                             valuesDict["businessId"]
            bodyText= bodyTemplate.substitute(businessName=valuesDict["businessName"],bookingNumber=valuesDict["bookingNumber"],
                      serviceDuration=valuesDict["serviceDuration"], appointmentDate=valuesDict["appointmentDate"],appointmentStartTime=valuesDict["appointmentStartTime"],
                      bookerName=valuesDict["bookerName"], disclaimer=valuesDict["disclaimer"], serviceName=valuesDict["serviceName"],
                        newBookingLink=newBookingLink)
            print('bodyText=', bodyText)

            bodyHtml = bodyHtmlTemplate.substitute(businessName=valuesDict["businessName"],bookingNumber=valuesDict["bookingNumber"],
                      serviceDuration=valuesDict["serviceDuration"], appointmentDate=valuesDict["appointmentDate"],appointmentStartTime=valuesDict["appointmentStartTime"],
                      bookerName=valuesDict["bookerName"], disclaimer=valuesDict["disclaimer"], serviceName=valuesDict["serviceName"],
                        newBookingLink=newBookingLink, logoURL = valuesDict["logoURL"])
            print('bodyHtml=', bodyHtml)

        if (templateName=='TicketConfirmation'):
            subjectText= subjectTemplate.substitute(businessName=valuesDict['businessName'])
            print('subjectText=',subjectText)
            cancellationBaseUrl = config.baseUrl + '/cancel-view/' + valuesDict['businessId']
            bookingParams={}
            bookingParams['bkNbr']= valuesDict['bookingNumber']
            bookingParams['type']= 'ticket'
            bookingParams['appointment']= valuesDict['appointmentDate'] + ' ' + valuesDict['appointmentStartTime']
            queryString = urllib.parse.urlencode(bookingParams)
            cancelLink = cancellationBaseUrl + '/?'+ queryString
            print(cancelLink)

            print(valuesDict)
            bodyText= bodyTemplate.substitute(numberOfTickets=valuesDict["numberOfTickets"],businessName=valuesDict["businessName"],bookingNumber=valuesDict["bookingNumber"],
                      serviceDuration=valuesDict["serviceDuration"], appointmentDate=valuesDict["appointmentDate"],appointmentStartTime=valuesDict["appointmentStartTime"],
                      bookerName=valuesDict["bookerName"], disclaimer=valuesDict["disclaimer"], serviceName=valuesDict["serviceName"],
                        businessAddress=valuesDict["businessAddress"],contactPhone=valuesDict["contactPhone"],totalPrice=valuesDict["totalPrice"],cancelLink=cancelLink, businessAddressGoogleLink=valuesDict["businessAddressGoogleLink"])
            print('bodyText=', bodyText)

            bodyHtml = bodyHtmlTemplate.substitute(numberOfTickets=valuesDict["numberOfTickets"],businessName=valuesDict["businessName"],bookingNumber=valuesDict["bookingNumber"],
                      serviceDuration=valuesDict["serviceDuration"], appointmentDate=valuesDict["appointmentDate"],appointmentStartTime=valuesDict["appointmentStartTime"],
                      bookerName=valuesDict["bookerName"], disclaimer=valuesDict["disclaimer"], serviceName=valuesDict["serviceName"],
                        businessAddress=valuesDict["businessAddress"],contactPhone=valuesDict["contactPhone"],totalPrice=valuesDict["totalPrice"],cancelLink=cancelLink, businessAddressGoogleLink=valuesDict["businessAddressGoogleLink"])

        if (templateName=='TicketCancellation'):

            subjectText= subjectTemplate.substitute(businessName=valuesDict['businessName'])
            print('subjectText=',subjectText)
            newBookingLink = config.baseUrl + '/business/' + valuesDict["businessId"] + '/details'

            bodyText= bodyTemplate.substitute(businessId=valuesDict["businessId"],businessName=valuesDict["businessName"],
                      bookerName=valuesDict["bookerName"], disclaimer=valuesDict["disclaimer"], newBookingLink=newBookingLink)
            print('bodyText=', bodyText)

            bodyHtml = bodyHtmlTemplate.substitute(businessId=valuesDict["businessId"],businessName=valuesDict["businessName"],
                      bookerName=valuesDict["bookerName"], disclaimer=valuesDict["disclaimer"], newBookingLink=newBookingLink)
            print('bodyHtml=', bodyHtml)

        return subjectText, bodyText, bodyHtml



    def generateEmailReferenceNumber(self):

        sequenceValue=str(EmailData().getEmailMaxId()).zfill(8)
        emailReferenceNumber= date.today().isoformat()+'-'+sequenceValue
        return emailReferenceNumber



    def storeEmailItems(self, subjectText, bodyText, bodyHtml, toAddressList, ccAddressList, bccAddressList, sourceReferenceNumber, appointmentDateTimeUTC, serviceDuration):

        # 1. Store the different parts in email core and email recipient tables
        emailReferenceNumber=self.generateEmailReferenceNumber()
        EmailData().addEmailCore(subjectText, bodyText, bodyHtml, sourceReferenceNumber, emailReferenceNumber, appointmentDateTimeUTC, serviceDuration)

        for email in toAddressList:
            print('email=',email)
            if (email!=None):
                EmailData().addEmailRecipients(emailReferenceNumber, email,'To')
        if (ccAddressList!=None):
            for email in ccAddressList:
                if (email != None):
                    EmailData().addEmailRecipients(emailReferenceNumber, email,'Cc')
        if (bccAddressList != None):
            for email in bccAddressList:
                if (email != None):
                    EmailData().addEmailRecipients(emailReferenceNumber, email,'Bcc')



class EmailUtil:

    def getUnprocessedEmails(self, emailMiscellaneousInfo):

        emails=EmailData().getUnprocessedEmailsCore()

        unProcessedEmailsDict={}
        for email in emails:
            emailMessage = EmailMessage()
            print('empty emailMessage=', vars(emailMessage))
            emailMessage.subject = email[0]
            emailMessage.body=email[1]
            emailMessage.bodyHtml=email[5]
            emailMessage.appointmentDateTime = email[6]
            emailMessage.serviceDuration = email[7]
            emailMessage.Status = email[8]
    

            #address
            businessId = email[3].split('-')[0]
            address = DataAccess().getBusinessAddress(businessId)
            if (address != None):
                emailMessage.location = ( ('' if address.addressLine1 == None else address.addressLine1) + ',' + ('' if address.addressLine2 == None else address.addressLine2) + ',' + ('' if address.cityLocation == None else address.cityLocation) + ',' + ('' if address.city == None else address.city) + ',' + ( '' if address.postalCode == None else address.postalCode))
            else:
                emailMessage.location = None

            emailMessage.fromAddress=emailMiscellaneousInfo.fromAddress
            emailMessage.replyToAddress = emailMiscellaneousInfo.replyToAddress
            print('email ref number=',email[4])
            emailMessage.toAddresses=EmailData().getEmailRecepients(email[4],'To')
            emailMessage.ccAddresses = EmailData().getEmailRecepients(email[4], 'CC')
            emailMessage.bccAddresses = EmailData().getEmailRecepients(email[4], 'BCC')

            print('filled emailMessage=', vars(emailMessage))
            unProcessedEmailsDict[email[4]]=emailMessage

        return unProcessedEmailsDict

    def getEmailMessageInfo(self, bookingNumber):
        emailMiscellaneousInfo = EmailData().getEmailMiscellaneousItems()
        email = EmailData().getEmailMessage(bookingNumber)[0]

        emailMessage = EmailMessage()
        print('empty emailMessage=', vars(emailMessage))
        emailMessage.subject = email[0]
        emailMessage.body=email[1]
        emailMessage.bodyHtml=email[5]
        emailMessage.appointmentDateTime = email[6]
        emailMessage.serviceDuration = email[7]

        #address
        businessId = email[3].split('-')[0]
        address = DataAccess().getBusinessAddress(businessId)
        if (address != None):
            # emailMessage.location = address.addressLine1 + ',' + address.addressLine2 + ',' + address.cityLocation + ',' + address.city + ',' + address.postalCode
            emailMessage.location = ( ('' if address.addressLine1 == None else address.addressLine1) + ',' + ('' if address.addressLine2 == None else address.addressLine2) + ',' + ('' if address.cityLocation == None else address.cityLocation) + ',' + ('' if address.city == None else address.city) + ',' + ( '' if address.postalCode == None else address.postalCode))
        else:
            emailMessage.location = None

        emailMessage.fromAddress=emailMiscellaneousInfo.fromAddress
        # emailMessage.replyToAddress = emailMiscellaneousInfo.replyToAddress
        # print('email ref number=',email[4])
        # emailMessage.toAddresses=EmailData().getEmailRecepients(email[4],'To')
        # emailMessage.ccAddresses = EmailData().getEmailRecepients(email[4], 'CC')
        # emailMessage.bccAddresses = EmailData().getEmailRecepients(email[4], 'BCC')

        return emailMessage



class EmailBatch:


    def getCalendarBytes(self, appointemntDateTimeUI, serviceDuration, emailSender, emailSubject, location = None):

        # pass
        from ics import Calendar, Event
        c = Calendar(creator='Lettucebook.co.za')
        e = Event()
        e.name = emailSubject
        dateAndTime=datetime.strptime(appointemntDateTimeUI,config.applicationUIDateFormat+ ' '+config.applicationUITimeFormat)
        appointemntDateTimeUTC = dateAndTime.strftime(config.applicationDBDateFormat + ' ' + config.applicationUITimeFormat)
        print('appointemntDateTimeUTC=',appointemntDateTimeUTC)
        e.begin = appointemntDateTimeUTC
        print('serviceDuration=',serviceDuration)
        # e.duration=serviceDuration
        e.duration = timedelta(minutes=int(serviceDuration))
        e.organizer=emailSender
        e.location = location
        c.events.add(e)
        return bytearray(str(c), encoding ='utf-8')

    # Final email sending method, this will be called from a batch process running every 5 mins
    # def sendEmail(self, subjectText, bodyText, bodyHtml, toAddressList, fromAddress, replyToAddress, emailServerHostname, emailServerPort, username, password, ccAddressList, bccAddressList):
    def sendEmail(self, emailMessage, calendarBytes, mailServerConnection):

        # emailServerHostname, emailServerPort, username, password, fromAddress, replyToAddress, disclaimerText, batchCycleInterval, processingInterval=EmailData().getEmailMiscellaneousItems()
        # (self, fromAddress
         # =None, toAddresses=None, replyToAddress=None, ccAddresses=None, bccAddresses=None, subject=None, body=None, bodyHtml=None, appointmentDateTime=None, serviceDuration=None):
        message = MIMEMultipart("alternative")
        message["Subject"] = emailMessage.subject
        message["From"] = emailMessage.fromAddress
        message["To"] = ", ".join(emailMessage.toAddresses)
        print(message["To"])
        message["Cc"] = ", ".join(emailMessage.ccAddresses)
        # message["Bcc"] = ", ".join(emailMessage.bccAddresses)
        # message.add_header('reply-to', emailMessage.replyToAddress)
        part1 = MIMEText(emailMessage.body, "plain")
        part2 = MIMEText(emailMessage.bodyHtml, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(part1)
        message.attach(part2)

        if (emailMessage.Status != 'NOSHOW'):
            partCal = MIMEBase("application", "octet-stream")
            partCal.set_payload(calendarBytes)

            # Encode file in ASCII characters to send by email
            encoders.encode_base64(partCal)

            # Add header as key/value pair to attachment part
            partCal.add_header(
                "Content-Disposition",
                "attachment; filename= booking.ics",
            )

            # Add attachment to message and convert message to string
            message.attach(partCal)

        # Create secure connection-old with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(mailServerConnection.emailServerHostname, mailServerConnection.emailServerPort, context=context) as server:
            server.login(mailServerConnection.username, mailServerConnection.password)
            print(vars(emailMessage))
            print(emailMessage.toAddresses)
            if (emailMessage.fromAddress!=None and len(emailMessage.toAddresses)>0):
                # server.sendmail(emailMessage.fromAddress, emailMessage.toAddresses, message.as_string())
                server.sendmail(emailMessage.fromAddress, emailMessage.toAddresses + emailMessage.ccAddresses + emailMessage.bccAddresses, message.as_string())

        # context = ssl.create_default_context()
        # with smtplib.SMTP(mailServerConnection.emailServerHostname, mailServerConnection.emailServerPort) as server:
        #     server.starttls(context=context)
        #     server.login(mailServerConnection.username, mailServerConnection.password)
        #     server.sendmail(emailMessage.fromAddress, emailMessage.toAddresses, message.as_string())


    def executeOneBatch(self, emailMessagesBatchDict, processingInterval, mailServerConnection):

        # 1. Send the emails in sequence. Mark each email as 'Processed' as and when it has been sent.
        print(emailMessagesBatchDict)
        # sys.exit(0)
        for emailRefNumber in emailMessagesBatchDict:
            emailMessage=emailMessagesBatchDict[emailRefNumber]
            time.sleep(processingInterval)
            print('in executeOneBatch, for loop   emailMessage=   ')
            print(vars(emailMessage))
            calendarBytes=self.getCalendarBytes(emailMessage.appointmentDateTime, emailMessage.serviceDuration, emailMessage.fromAddress, emailMessage.subject, emailMessage.location)
            self.sendEmail(emailMessage, calendarBytes, mailServerConnection)
            print('after sending email')
            EmailData().updateEmailStatus('PROCESSED', emailRefNumber)



    def executeBatches(self):

        print('in executebatches')
        emailMiscellaneousInfo = EmailData().getEmailMiscellaneousItems()
        print(emailMiscellaneousInfo)

        mailServerConnection = MailServerConnection(emailMiscellaneousInfo.mailserverHostname, emailMiscellaneousInfo.mailserverPort, emailMiscellaneousInfo.username, emailMiscellaneousInfo.password)
        print(vars(mailServerConnection))
        while(True):
            time.sleep(emailMiscellaneousInfo.batchCycleInterval)
            emailMessagesBatchDict=EmailUtil().getUnprocessedEmails(emailMiscellaneousInfo)
            print(emailMessagesBatchDict)
            print('service duration in dict')
            print(emailMessagesBatchDict)

            self.executeOneBatch(emailMessagesBatchDict, emailMiscellaneousInfo.emailProcessingInterval, mailServerConnection)





class EmailData:

    def updateEmailStatus(self, status, emailReferenceNumber):
        bookingsDB =EmailConnection().getConnection()
        cursor = bookingsDB.cursor()

        query="update email_core set status=%s where email_ref_number=%s"

        print(query)

        values = (status, emailReferenceNumber)

        cursor.execute(query, values)
        bookingsDB.commit()
        bookingsDB.close()
        return True


    def getEmailMaxId(self):

        bookingsDB = EmailConnection().getConnection()
        cursor = bookingsDB.cursor()
        query = "select max(id) from email_core"
        print(query)
        cursor.execute(query)
        rows = cursor.fetchall()
        # bookingsDB.close()
        bookingsDB.close()
        if (rows==None or rows[0]==None or rows[0][0]==None):
            return 1000
        return (rows[0][0] + 1)

        # if (rows==None or rows[0]==None):
        #     return 1
        # return (rows[0][0] + 1)



    def getEmailMiscellaneousItems(self):

        bookingsDB = EmailConnection().getConnection()
        cursor = bookingsDB.cursor()
        query = "select disclaimer_text, reply_to, unsubscribe_text, mailserver_host, mailserver_port, username, password, " \
                "batch_cycle_interval, email_processing_interval, from_address, platform_email " \
                "from email_misc "
        print(query)

        cursor.execute(query)
        rows = cursor.fetchall()

        emailMiscellaneousInfo=EmailMiscellaneous()
        emailMiscellaneousInfo.disclaimer = rows[0][0]
        emailMiscellaneousInfo.replyToAddres=rows[0][1]
        emailMiscellaneousInfo.unSubscribeText=rows[0][2]
        emailMiscellaneousInfo.mailserverHostname=rows[0][3]
        emailMiscellaneousInfo.mailserverPort=rows[0][4]
        emailMiscellaneousInfo.username  =rows[0][5]
        emailMiscellaneousInfo.password=rows[0][6]
        emailMiscellaneousInfo.batchCycleInterval=rows[0][7]
        emailMiscellaneousInfo.emailProcessingInterval=rows[0][8]
        emailMiscellaneousInfo.fromAddress=rows[0][9]
        emailMiscellaneousInfo.platformEmail = rows[0][10]

        bookingsDB.close()
        return emailMiscellaneousInfo



    def getUnprocessedEmailsCore(self):

        bookingsDB = EmailConnection().getConnection()
        cursor = bookingsDB.cursor()
        query = "select subject, body, e.status, source_ref_id, email_ref_number, body_html, appointment_datetime, service_duration, b.status " \
                "from email_core e  " \
                "join current_bookings b on e.source_ref_id = b.booking_number " \
                "where e.status='NEW' "
        print(query)

        cursor.execute(query)
        rows = cursor.fetchall()
        print(rows)
        bookingsDB.close()
        return rows



    def getEmailRecepients(self, emailRefNumber, recipientType):

        bookingsDB = EmailConnection().getConnection()
        cursor = bookingsDB.cursor()
        query = "select email " \
                "from email_recipients  " \
                "where email_ref_number=%s and type=%s "
        print(query)
        values=(emailRefNumber,recipientType)
        print(values)
        cursor.execute(query, values)


        rows = cursor.fetchall()
        emails=[]
        for row in rows:
            emails.append(row[0])
        bookingsDB.close()
        return emails




    def addEmailCore(self, subjectText, bodyText, bodyHtml, sourceReferenceNumber,emailReferenceNumber, appointmentDatetimeUTC, serviceDuration):

        bookingsDB =EmailConnection().getConnection()
        cursor = bookingsDB.cursor()

        query="insert into email_core (subject, body, status, source_ref_id, email_ref_number, body_html, appointment_datetime, service_duration) " \
              "values(%s,%s,%s,%s,%s,    %s,%s,%s) "

        print(query)

        values = (subjectText,bodyText,'NEW',sourceReferenceNumber,emailReferenceNumber,bodyHtml, appointmentDatetimeUTC, serviceDuration)

        cursor.execute(query, values)
        bookingsDB.commit()
        bookingsDB.close()

        return True



    def addEmailRecipients(self, emailReferenceNumber, email,recipientType):

        bookingsDB =EmailConnection().getConnection()
        cursor = bookingsDB.cursor()

        query="insert into email_recipients (email, email_ref_number, type) " \
              "values(%s,%s,%s) "

        print(query)

        values = (email,emailReferenceNumber,recipientType)
        print(values)
        cursor.execute(query, values)
        bookingsDB.commit()
        bookingsDB.close()

        return True


    def getTemplate(self, templateName):

        bookingsDB = EmailConnection().getConnection()
        cursor = bookingsDB.cursor()
        query = "select name, subject, body_text, body_html  " \
                "from email_templates  " \
                "where name=%s "
        print(query)
        values=(templateName,)
        cursor.execute(query, values)

        rows = cursor.fetchall()
        emailTemplate=EmailTemplate(rows[0][0],rows[0][1],rows[0][2],rows[0][3])
        bookingsDB.close()
        return emailTemplate

    def getEmailMessage(self, bookingNumber):

        bookingsDB = EmailConnection().getConnection()
        cursor = bookingsDB.cursor()
        query = "select subject, body, status, source_ref_id, email_ref_number, body_html, appointment_datetime, service_duration " \
                "from email_core  " \
                "where source_ref_id='" + bookingNumber + "' "
        print(query)

        cursor.execute(query)
        rows = cursor.fetchall()
        print(rows)
        bookingsDB.close()
        return rows



# AppEmail().sendBookingEmail('EasyCuts', 'B00222', 'RS', '45 mins','Ladies Haircut', 'Katie Perkins', 'Maddy Green',  'atul.a.arora@gmail.com', 'rvkellerman@gmail.com', '2020-01-25','1130 hours' )
# EmailBatch().executeBatches()