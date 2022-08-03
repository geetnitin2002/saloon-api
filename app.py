#!/usr/bin/env python
import os
import json

from flask import Flask, make_response, abort, request, jsonify, g, url_for
# from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
import base64
import boto3
import sys
from model import *
from users import Login
from businessSetup import BusinessReviewAndSetup, BusinessSetup
from apputils import AppUtils
from search import Search
from ticketing import Tickets
from booking import BookingCore, BookingUtils
from notifications import *
from dbAccess import DataAccess
import config
import threading
from io import StringIO

from flask_cors import CORS
# from werkzeug.middleware.proxy_fix import ProxyFix

# added by Nawaz
from azure.identity import DefaultAzureCredential

# Import the client object from the Azure library
from azure.storage.blob import BlobClient
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import ContainerClient



app = Flask(__name__)
CORS(app, support_credentials=True)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024


@app.route('/')
def hello_world():
   cont = 'Hello'
   return 'Hello'
#    ical = '''BEGIN:VCALENDAR
# VERSION:2.0
# PRODID:-//hacksw/handcal//NONSGML v1.0//EN
# BEGIN:VEVENT
# UID:uid2@example.com
# DTSTAMP:19970714T170000Z
# ORGANIZER;CN=John Doe:MAILTO:john.doe@example.com
# DTSTART:20200714T170000Z
# DTEND:20200715T035959Z
# SUMMARY:Bastille Day Party
# GEO:48.85299;2.36885
# END:VEVENT
# END:VCALENDAR'''
#    return app.response_class(ical, content_type='text/calendar',mimetype='text/calendar')



def initiateEmailBatch ():
   EmailBatch().executeBatches()

def initiateTicketAvailabilityBatch ():
   Tickets().executeBatches()

def initiateAvailabilityBatch ():
   BookingCore().executeBatches()

emailThread=threading.Thread(target=initiateEmailBatch)
emailThread.start()

availabilityThread=threading.Thread(target=initiateAvailabilityBatch)
availabilityThread.start()

ticketAvailabilityThread=threading.Thread(target=initiateTicketAvailabilityBatch)
# ticketAvailabilityThread.start()

# app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
auth = HTTPBasicAuth()


class TokenManager:

   def generateAndStoreToken(self, userId):
      # s = Serializer('secret', expires_in=3600)
      # print(config.jsonSerializerSecret)
      s = Serializer(config.jsonSerializerSecret, expires_in=int(config.tokenExpiryDurationSecs))
      return s.dumps({'userId': userId})



   def loadAndVerifyToken(self, token):
      token=token.encode('ascii')
      # s = Serializer('secret')
      s = Serializer(config.jsonSerializerSecret)

      data = ''
      try:
         data = s.loads(token)
         print(data)
      except SignatureExpired:
         print('expired token')
         return False
      except BadSignature:
         print('bad token')
         return False

      return True


# class User():
#    username = ''
#    password_hash = ''
#
#    def hash_password(self, password):
#       self.password_hash = pwd_context.encrypt(password)
#
#    def verify_password(self, password):
#       return pwd_context.verify(password, self.password_hash)
#
#    def generate_auth_token(self, expiration=600):
#       s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
#       return s.dumps({'id': '666'})
#
#    @staticmethod
#    def verify_auth_token(token):
#       s = Serializer(app.config['SECRET_KEY'])
#       try:
#          data = s.loads(token)
#       except SignatureExpired:
#          return None  # valid token, but expired
#       except BadSignature:
#          return None  # invalid token
#       user = User().getUserDetails()
#       return user
#
#
# @auth.verify_password
# def verify_password(username_or_token, password):
#     print('in verify  password method')
#     # first try to authenticate by token
#     user = User.verify_auth_token(username_or_token)
#     if not user:
#         # try to authenticate with username/password
#         user = User().verifyPassword(username,password)
#         if not user or not user.verify_password(password):
#             return False
#     g.user = user
#     return True
#
#
# @app.route('/token')
# @auth.login_required
# def get_auth_token():
#     token = g.user.generate_auth_token(600)
#     return jsonify({'token': token.decode('ascii'), 'duration': 600})
#



@auth.verify_password
def verifyPassword(token, password):


   print('in verify password method')
   print(token)
   print(password)
   # return TokenManager().loadAndVerifyToken(token)
   return True


def findImage(imageName): 
    blob_client = ContainerClient.from_connection_string(config.storage_account_conn_str, container_name= config.container_name) #, blob_name='Bid_1190_Image_Main.png')
    if (blob_client.get_blob_client(imageName).exists()):	
        return str(base64.b64encode(blob_client.download_blob(imageName).readall()).decode('utf-8'))	
    else:	
        return ""	
    # return base64.b64encode(blob_client.download_blob(imageName).readall()) # 'Bid_1000_Image2.png').readall()
    # return block_blob_service.get_blob_to_bytes(
    #         containerName, 
    #         input_folder + '/' + imageName, 
    #         max_connections=1).content; 

@app.route('/email/<id>')
def hello_world1(id):
   # ical = '''BEGIN:VCALENDAR
   # VERSION:2.0
   # PRODID:-//hacksw/handcal//NONSGML v1.0//EN
   # BEGIN:VEVENT
   # UID:uid1@example.com
   # DTSTAMP:19970714T170000Z
   # ORGANIZER;CN=John Doe:MAILTO:john.doe@example.com
   # DTSTART:20200714T170000Z
   # DTEND:20200715T035959Z
   # SUMMARY:Bastille Day Party
   # GEO:48.85299;2.36885
   # END:VEVENT
   # END:VCALENDAR'''
   # return Response(ical, mimetype='text/calendar')
   # ICS to Apple
   #calendarBytes = EmailBatch().getCalendarBytes('12/12/2020 12:00', '15', 'kheradenilam2019@gmail.com', 'adyatantech.mail@gmail.com')
   # partCal = MIMEBase("application", "octet-stream")
   # partCal.set_payload(calendarBytes)

   # # Encode file in ASCII characters to send by email
   # encoders.encode_base64(partCal)

   # # Add header as key/value pair to attachment part
   # partCal.add_header(
   #    "Content-Disposition",
   #    "inline; filename= booking.ics",
   # )

   emailMessage = EmailUtil().getEmailMessageInfo(id)
   calendarBytes = EmailBatch().getCalendarBytes(emailMessage.appointmentDateTime, emailMessage.serviceDuration, emailMessage.fromAddress, emailMessage.subject, emailMessage.location)

   response = app.response_class(calendarBytes, mimetype='text/calendar', )
   response.headers.set('Content-Disposition', 'inline', filename='booking.ics')
   return response


@app.route("/business/<businessId>/<filename>", methods=['GET'])
def getBusinessImages(businessId, filename):

   print('in get image')
   image = findImage(filename + '.png')
   return app.response_class(image, content_type='image/png')

@app.route("/business/<businessId>/images", methods=['GET'])
def getBusinessImagesNames(businessId):

   print('in get image')
   # image = findImage(filename + '.png')
   response={}
   response["responseType"]='data'
   response["data"]= {	
      # "Main": findImage("Bid_" + businessId + "_Image_Main.png"), 	
      "Main": { "name": "Bid_" + businessId + "_Image_Main.png", "url": findImage("Bid_" + businessId + "_Image_Main.png") },
      # "Image1": findImage("Bid_" + businessId + "_Image1.png"), 	
      # "Image2" : findImage("Bid_" + businessId + "_Image2.png"),	
      # "Image3" : findImage("Bid_" + businessId + "_Image3.png"),	
      # "Image4" : findImage("Bid_" + businessId + "_Image4.png")	
      "Child": [	
         # findImage("Bid_" + businessId + "_Image1.png"), 	
         # findImage("Bid_" + businessId + "_Image2.png"), 	
         # findImage("Bid_" + businessId + "_Image3.png"),	
         # findImage("Bid_" + businessId + "_Image4.png")	
         { "name": "Bid_" + businessId + "_Image1.png", "url": findImage("Bid_" + businessId + "_Image1.png") }, 	
         { "name": "Bid_" + businessId + "_Image2.png", "url": findImage("Bid_" + businessId + "_Image2.png") }, 	
         { "name": "Bid_" + businessId + "_Image3.png", "url": findImage("Bid_" + businessId + "_Image3.png") },	
         { "name": "Bid_" + businessId + "_Image4.png", "url": findImage("Bid_" + businessId + "_Image4.png") }
      ]
   }
   return app.response_class(json.dumps(response), content_type='application/json')

@app.route("/business/<businessId>/delete", methods=['POST'])
def deleteBusinessImages(businessId):

   print('in delete')
   s3_resource = ''
   content = request.get_json()
   storage_url = config.storage_blob_url
   fileMain =None
   try:
      filename = content["Image"]
      blob_client = ContainerClient.from_connection_string(config.storage_account_conn_str, container_name= config.container_name) #, blob_name=filename)
      blob_client.delete_blob(filename)
   except:
      print("Oops!", sys.exc_info()[0], "occurred getting mainImage")
   response={}
   response["responseType"]='data'
   response["data"]={"Deleted": True}
   return app.response_class(json.dumps(response), content_type='application/json')

@app.route("/business/<businessId>/upload", methods=['POST'])
def uploadBusinessImages(businessId):

   print('in upload')

   # s3_resource=boto3.resource('s3', aws_access_key_id=config.awsAaccessKeyId,
   #  aws_secret_access_key= config.awsSecretAccessKey, region_name=config.awsRegionName)
   s3_resource = ''

   # # Retrieve the IDs and secret to use in the JSON dictionary
   # os.environ["AZURE_SUBSCRIPTION_ID"] = 
   # os.environ["AZURE_TENANT_ID"]
   # os.environ["AZURE_CLIENT_ID"]
   # os.environ["AZURE_CLIENT_SECRET"]

   # credential = DefaultAzureCredential()

   # Retrieve the storage blob service URL, which is of the form
   # https://pythonazurestorage12345.blob.core.windows.net/
   storage_url = config.storage_blob_url

   files = request.files.to_dict()
   files.pop('mainImage', None)
   values = list(files.values())
   files.clear()
   emptySlots = []
   images = getBusinessImagesNames(businessId).json['data']['Child']
   ind = 1
   for imageName in images:
      if (imageName['url'] == ""):
         emptySlots.append('otherImage' + str(ind))
      ind += 1
   
   ind = 0
   for slot in emptySlots:
      if (len(values) == ind):
         break
      files[slot] = values[ind]
      ind += 1



   fileMain =None
   try:
      fileMain = request.files['mainImage']
   except:
      print("Oops!", sys.exc_info()[0], "occurred getting mainImage")

   # Create the client object using the storage URL and the credential
   # blob_client = BlobClient(storage_url, container_name="businessimages", blob_name=fileMain.filename, credential=credential)

   # # Working one - Nawaz
   # blob_client = BlobClient.from_connection_string(config.storage_account_conn_str, container_name= config.container_name, blob_name=fileMain.filename)
   # fileData = fileMain.stream.read()
   # blob_client.upload_blob(fileData)

   # # Create the BlobServiceClient object which will be used to create a container client
   # blob_service_client = BlobServiceClient.from_connection_string("DefaultEndpointsProtocol=https;AccountName=bookingwebsitedev;AccountKey=kfVb0R6BEkw46Nn+9PoFl0feJZWWJp8HKN9VDvMMV8e+utvKTslLkuX0VlbwV+/p/0fq12b6BEunGccTu0ffpA==;EndpointSuffix=core.windows.net")

   # blob_service_client.create_blob_from_stream("businessimages", fileMain.filename, fileMain)

   # # Open a local file and upload its contents to Blob Storage
   # with open("./" + fileMain.filename , "rb") as data:
   #    blob_client.upload_blob(data)

   # print('mainImage=',fileMain.filename)
   if (fileMain!=None and fileMain.filename!=''):
      # fileMain.save(os.path.join(config.localFileUoploadDirectory, fileMain.filename))
      # s3_resource.Object(config.s3Bucket, 'Bid_'+businessId+'_Image_Main.png').upload_file(
      #    Filename=config.localFileUoploadDirectory+'/'+fileMain.filename)
      filename = 'Bid_'+businessId+'_Image_Main.png'
      blob_client = BlobClient.from_connection_string(config.storage_account_conn_str, container_name= config.container_name, blob_name=filename)
      fileData = fileMain.stream.read()
      blob_client.upload_blob(fileData, overwrite=True)
   otherImage1=None
   try:
      # otherImage1 = request.files['otherImage1']
      otherImage1 = files['otherImage1']
   except :
      print("Oops!", sys.exc_info()[0], "occurred getting otherImage1.")
   if (otherImage1!=None and otherImage1.filename!=''):
      print('otherImage1=', otherImage1.filename)
      # otherImage1.save(os.path.join(config.localFileUoploadDirectory, otherImage1.filename))
      # s3_resource.Object(config.s3Bucket, 'Bid_' + businessId + '_Image1.png').upload_file(
      #    Filename=config.localFileUoploadDirectory + '/' + otherImage1.filename)
      filename = 'Bid_' + businessId + '_Image1.png'
      blob_client = BlobClient.from_connection_string(config.storage_account_conn_str, container_name= config.container_name, blob_name=filename)
      fileData = otherImage1.stream.read()
      blob_client.upload_blob(fileData, overwrite=True)

   otherImage2=None
   try:
      # otherImage2 = request.files['otherImage2']
      otherImage2 = files['otherImage2']
   except :
      print("Oops!", sys.exc_info()[0], "occurred getting otherImage2.")
   if (otherImage2!=None and otherImage2.filename!=''):
      print('otherImage2=', otherImage2.filename)
      # otherImage2.save(os.path.join(config.localFileUoploadDirectory, otherImage2.filename))
      # s3_resource.Object(config.s3Bucket, 'Bid_'+businessId+'_Image2.png').upload_file(
      #    Filename=config.localFileUoploadDirectory+'/'+otherImage2.filename)
      filename = 'Bid_'+businessId+'_Image2.png'
      blob_client = BlobClient.from_connection_string(config.storage_account_conn_str, container_name= config.container_name, blob_name=filename)
      fileData = otherImage2.stream.read()
      blob_client.upload_blob(fileData, overwrite=True)

   otherImage3=None
   try:
      # otherImage3 = request.files['otherImage3']
      otherImage3 = files['otherImage3']
   except :
      print("Oops!", sys.exc_info()[0], "occurred getting otherImage3.")
   if (otherImage3!=None and otherImage3.filename!=''):
      print('otherImage3=', otherImage3.filename)
      # otherImage3.save(os.path.join(config.localFileUoploadDirectory, otherImage3.filename))
      # s3_resource.Object(config.s3Bucket, 'Bid_'+businessId+'_Image3.png').upload_file(
      #    Filename=config.localFileUoploadDirectory+'/'+otherImage3.filename)
      filename = 'Bid_'+businessId+'_Image3.png'
      blob_client = BlobClient.from_connection_string(config.storage_account_conn_str, container_name= config.container_name, blob_name=filename)
      fileData = otherImage3.stream.read()
      blob_client.upload_blob(fileData, overwrite=True)

   otherImage4=None
   try:
      # otherImage4 = request.files['otherImage4']
      otherImage4 = files['otherImage4']
   except :
      print("Oops!", sys.exc_info()[0], "occurred getting otherImage4.")
   if (otherImage4!=None and otherImage4.filename!=''):
      print('otherImage4=', otherImage4.filename)
      # otherImage4.save(os.path.join(config.localFileUoploadDirectory, otherImage4.filename))
      # s3_resource.Object(config.s3Bucket, 'Bid_' + businessId + '_Image4.png').upload_file(
      #    Filename=config.localFileUoploadDirectory + '/' + otherImage4.filename)
      filename = 'Bid_' + businessId + '_Image4.png'
      blob_client = BlobClient.from_connection_string(config.storage_account_conn_str, container_name= config.container_name, blob_name=filename)
      fileData = otherImage4.stream.read()
      blob_client.upload_blob(fileData, overwrite=True)

   # i=0
   # for file in files:
   #    file.save(os.path.join(config.localFileUoploadDirectory, file.filename))
   #    print(os.path.join(config.localFileUoploadDirectory, file.filename))
   #    s3_resource.Object(config.s3Bucket, 'Bid_'+businessId+'_Image'+str(i)+'.png').\
   #       upload_file(Filename=config.localFileUoploadDirectory+'/' + file.filename)
   #    print('Bid_'+businessId+'_Image'+str(i)+'.png')



   response={}
   response["responseType"]='data'
   response["data"]={"uploaded": True}
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/business/<businessId>/skilledStaff", methods=['POST'])
@auth.login_required
def getSkilledStaff(businessId):

   content = request.get_json()
   print(content)
   services=content["services"]

   skilledStaffMembers = []
   if (len(services)==1):
      skilledStaffMembers=DataAccess().getSkilledStaff(businessId, services[0], None)
   elif(len(services)==2):
      skilledStaffMembers = DataAccess().getSkilledStaff(businessId, services[0], services[1])

   skilledStaff=[]
   for row in skilledStaffMembers:
      oneStaffMemberDict={}
      oneStaffMemberDict['userId']=row[3]
      oneStaffMemberDict['staffName']=AppUtils().getFullName(row[0],row[1])
      skilledStaff.append(oneStaffMemberDict)

   response={}
   response["responseType"]='data'
   response["data"]=skilledStaff
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/business/<businessId>/permittedServiceKinds", methods=['POST'])
@auth.login_required
def getPermittedServiceKinds(businessId):

   content = request.get_json()
   print(content)
   serviceName=content["service"]

   permissions={}
   permissions["RSPermitted"]=True
   permissions["TRSPermitted"]=False
   permissions["PSSPermitted"]=False
   permissions["PDSPermitted"]=False
   countServices=len(BusinessSetup().getBusinessServices(businessId,'System'))
   countStaff = len(BusinessSetup().getBusinessStaff(businessId, 'System'))

   if (BookingUtils().getBusinessServiceDefinition(businessId, serviceName).ifDoubleTimeService=='N'):

      if (countServices ==1 and countStaff>=2):
         permissions["PSSPermitted"] = True

      elif (countServices >=2 and countStaff==1):
         permissions["TRSPermitted"] = True

      elif (countServices >= 2 and countStaff >= 2):
         permissions["PSSPermitted"] = True
         permissions["TRSPermitted"] = True
         permissions["PDSPermitted"] = True

   response={}
   response["responseType"]='data'
   response["data"]=permissions
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/search", methods=['POST'])
def searchBasedOnCriteria():

   content = request.get_json()
   print(content)

   searchDict=content
   location =None
   if (searchDict["location"]!=None):
      locationParts=searchDict["location"].split(', ')
      location=(locationParts[1], locationParts[0])
   searcResultsDict=Search().searchByCriteria(searchDict["serviceCategory"], searchDict["businessName"], location)

   response={}
   response["responseType"]='data'
   response["data"]=searcResultsDict
   return app.response_class(json.dumps(response), content_type='application/json')

# @app.route("/business/<businessId>/getAvailability", methods=['POST'])
# def getBusinessAvailablity(businessId):
#
#    print('in get busines availability method')
#
#    content = request.get_json()
#    print(content)
#
#    staffMember=content['userIdOfStaff']
#    services=content['services']
#    ifPartnerService=content['ifPartnerService']
#
#    timeBandedAvailability=BookingCore().getDatewiseAvailability(businessId, staffMember, services, ifPartnerService)
#    response={}
#    response["responseType"]='data'
#    response["data"]=timeBandedAvailability
#    return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/business/<businessId>/getStaffAvailability", methods=['POST'])
def getStaffAvailablity(businessId):

   print('in get staff availability method')

   content = request.get_json()
   print(content)

   userIdOfStaff=content['userIdOfStaff']
   services=content['services']
   if (len(services)==2):
      if('(' in services[1]):
         services[1] = services[1].split('(')[0].strip()
   print(services)

   ifPartnerService=content['ifPartnerService']
   uiDateString=content['uiDateString']
   clockTimeFrom=content['clockTimeFrom']
   clockTimeTo=content['clockTimeTo']

   # timeBandedAvailability=BookingCore().getDatewiseAvailability(businessId, staffMember, services, ifPartnerService)
   staffAvailability=BookingCore().getAvailabilityForUI(ifPartnerService, businessId, services, uiDateString, clockTimeFrom, clockTimeTo, userIdOfStaff)

   response={}
   response["responseType"]='data'
   response["data"]=staffAvailability
   return app.response_class(json.dumps(response), content_type='application/json')



# Not used, should be removed
# @app.route("/business/<businessId>/getOneDayAvailability", methods=['POST'])
# def getOneDayAvailablity(businessId):
#
#    print('in get one day availablity ')
#    content = request.get_json()
#    print(content)
#
#    userIdOfStaff=content['userIdOfStaff']
#    services=content['services']
#    ifPartnerService=content['ifPartnerService']
#    appointmentDate=content['appointmentDate']
#
#    availabileSlots=BookingCore().getOnedayAvailabilityForUIDisplay(ifPartnerService, businessId, services, datetime.strptime(appointmentDate, config.applicationUIDateFormat).date(), userIdOfStaff)
#    response={}
#    response["responseType"]='data'
#    response["data"]=availabileSlots
#    return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/business/<businessId>/booking/<bookingNumber>/getReassignmentData", methods=['POST'])
def getReassignemntData(businessId, bookingNumber):

   print('in get one day availablity ')
   # content = request.get_json()
   # loggedInUserId=content['loggedInUserId']
   # print(content)

   serviceAndStaff=BookingCore().getReassignemntData(businessId, bookingNumber)
   response={}
   response["responseType"]='data'
   response["data"]=serviceAndStaff
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/business/<businessId>/user/bookings", methods=['POST'])
@auth.login_required
def getUserBookings(businessId):

   print('in user bookings ')
   content = request.get_json()
   print(content)

   userIdOfStaff=content['userIdOfStaff']
   startDate=datetime.strptime(content['startDateStr'], config.applicationUIDateFormat).date()
   endDate=datetime.strptime(content['endDateStr'], config.applicationUIDateFormat).date()

   # dict = request.form
   # for key in dict:
   #    print('key:  {}  and   value:   {}'.format(key, dict[key]))
   bookingsDict=BookingCore().getEmployeeBookings(businessId, userIdOfStaff, startDate, endDate)
   response={}
   response["responseType"]='data'
   response["data"]=bookingsDict
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/business/<businessId>/bookings", methods=['POST'])
@auth.login_required
def getBookings(businessId):

   print('in buiness bookings ')
   content = request.get_json()
   print(content)

   searchDate=datetime.strptime('01/01/1970' if content['dateStr'] == None else content['dateStr'], config.applicationUIDateFormat).date()
   fromDate=datetime.strptime('01/01/1970' if content['fromDateStr'] == None else content['fromDateStr'], config.applicationUIDateFormat).date()
   toDate=datetime.strptime('01/01/1970' if content['toDateStr'] == None else content['toDateStr'], config.applicationUIDateFormat).date()
   
   print('after searchdate')
   # endDateStr=content['endDateStr']
   # serviceName=content['serviceName']
   serviceName=None
   selectedUserId=content['selectedUserId']
   loggedInUserId=content['loggedInUserId']
   
   if(serviceName!=None and serviceName.strip()==''):
      serviceName=None
   if(  (selectedUserId!=None) and (selectedUserId.strip()=='' or selectedUserId=='0')):
      selectedUserId=None
   if (selectedUserId==None):
      bookingsDict=BookingCore().getBookings(businessId, None, fromDate, toDate, serviceName,loggedInUserId)
      bookingsDictForStaffAvail=BookingCore().getBookings(businessId, None, searchDate, searchDate, serviceName,loggedInUserId)
   else:
      bookingsDict = BookingCore().getBookings(businessId, int(selectedUserId), fromDate, toDate, serviceName,
                                    loggedInUserId)
      bookingsDictForStaffAvail = BookingCore().getBookings(businessId, int(selectedUserId), searchDate, searchDate, serviceName,
                                    loggedInUserId)
   bookingsDict["staffAvailablity"] = bookingsDictForStaffAvail["staffAvailablity"]
   response={}
   response["responseType"]='data'
   response["data"]=bookingsDict
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/business/<businessId>/booking/<bookingNumber>/applyReassignment", methods=['POST'])
def reAssignServiceBooking(businessId, bookingNumber):

   print('in book service')

   content = request.get_json()
   print(content)

   service1=content['service1']
   minSlotNumber1=content['minSlotNumber1']
   appointmentDate =None
   if (content['appointmentDate']!=None):
      appointmentDate = datetime.strptime(content['appointmentDate'], config.applicationUIDateFormat).date()
   userIdOfStaff1 = content['userIdOfStaff1']
   maxSlotNumber1 = content['maxSlotNumber1']
   service2=content['service2']
   minSlotNumber2=content['minSlotNumber2']
   userIdOfStaff2 = content['userIdOfStaff2']
   maxSlotNumber2 = content['maxSlotNumber2']

   BookingCore().applyReassignment( bookingNumber, businessId,  appointmentDate, service1, userIdOfStaff1, minSlotNumber1, maxSlotNumber1, service2, userIdOfStaff2, minSlotNumber2, maxSlotNumber2 )

   response={}
   response["responseType"]='success'
   response["success"]=[{"message":"The reassignment is applied."}]
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/business/<businessId>/checkBookingForPotentialClash", methods=['POST'])
def checkForBookingsClash(businessId):

   print('in book service')

   content = request.get_json()
   print(content)

   email=content['email']
   appointmentDate=content['appointmentDate']
   clockTimeRange=content['clockTimeRange']
   result=BookingUtils().checkForBookingsClash(email, datetime.strptime(appointmentDate,config.applicationUIDateFormat).date(), clockTimeRange)
   print(result)

   response={}
   print(result[0])

   if (result[0]):
      print('in if')
      response["responseType"] = 'success'
      response["success"] = [{"message": "Their is no booking clashing with this one"}]
   else:
      print('in else')
      print(result[1])
      print(result[2])
      print(result[3])
      print(result[4])
      print(result[5])

      response["responseType"] = 'warning'
      warningDataDict={}
      warningDataDict["bookingNumber"]=result[1]
      warningDataDict["businessName"] = result[2]
      response["warning"]=warningDataDict
      appointmentDateStr=result[3].strftime(config.applicationUIDateFormat)

      # messageString='The booking has a clash with an earlier booking ('+result[1] + ') with business '+result[2]+ ' on '+appointmentDateStr+ ' ' +result[4]+' for '+result[5]
      messageString='This booking conflicts with an existing booking for the same e-mail address '+result[2]+ ' on '+appointmentDateStr+ ' ' +result[4]+' for '+result[5]
      messageDataDict={}
      messageDataDict["message"]=messageString
      messageDataDict["warningData"] = warningDataDict
      response["warning"] = messageDataDict

   print(json.dumps(response))
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/business/<businessId>/bookAppointment", methods=['POST'])
def bookService(businessId):

   print('in book service')

   content = request.get_json()
   print(content)

   services=content['services']
   if (len(services)==2):
      if('(' in services[1]):
         services[1] = services[1].split('(')[0].strip()
   print(services)

   ifPartnerService=content['ifPartnerService']
   businessName=content['businessName']
   clockTimeRange=content['clockTimeRange']
   appointmentDate = content['appointmentDate']
   userIdOfStaff = content['userIdOfStaff']
   customerEmail = content['customerEmail']

   # partnerEmail = content['partnerEmail']
   partnerEmail=None
   # partnerName = content['partnerName']
   partnerName = None
   customerName = content['customerName']
   bookerComment = content['bookerComment']
   print('clockTimeRange=',clockTimeRange)

   bookingNumber=BookingCore().setBookingDetailsNew2( ifPartnerService, businessId, businessName, services, clockTimeRange,
                  datetime.strptime(appointmentDate,config.applicationUIDateFormat).date(),int(userIdOfStaff), customerEmail, partnerEmail, customerName, bookerComment)

   response={}
   response["responseType"]='success'
   # response["success"]=[{"message":"Appointment has been booked. Your booking number is "+bookingNumber}]
   response["success"]=[{"message":"Booking Confirmed"}]
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/business/<businessId>/approve", methods=['POST'])
def approveBusiness(businessId):

   print('in approve business')

   # content = request.get_json()
   # print(content)

   response=BusinessReviewAndSetup().approveBusiness(businessId)
   print(json.dumps(response))
   return app.response_class(json.dumps(response), content_type='application/json')


@app.route("/business/<businessId>/service/<serviceName>/getTicketsAvailability", methods=['GET'])
def getAvailableTickets(businessId, serviceName):

   print('in getAvailableTickets')
   print(businessId)
   print(serviceName)
   timeBandedAvailability=Tickets().generateBusinessTimeBands(businessId, serviceName)
   # timeBandedAvailability = Tickets().generateBusinessTimeBands(businessId, 'Boating Deluxe')

   response={}
   response["responseType"]='data'
   response["data"]=timeBandedAvailability
   return app.response_class(json.dumps(response), content_type='application/json')


# Temporarily comented as we feel it is not used. Be carefule before deleting
# @app.route("/business/<businessId>/getBusinessSlotsRange", methods=['POST'])
# def getBusinessSlotsRange(businessId):
#
#    print('in getBusinessSlotsRange')
#    print(businessId)
#    slotsRange=BusinessSetup().getBusinessSlotsRange(businessId)
#
#    response={}
#    response["responseType"]='data'
#    response["data"]=slotsRange
#    return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/business/<businessId>/bookTickets", methods=['POST'])
def bookTickets(businessId):

   print('in book Tickets')
   content = request.get_json()
   print(content)

   serviceName=content['serviceName']
   bookerName=content['bookerName']
   bookerEmail=content['bookerEmail']
   countOfTicketsToBook=content['countOfTicketsToBook']
   eventDate = content['eventDate']
   slotStartTime = content['slotStartTime']

   bookingNumber=Tickets().bookTickets(bookerName,bookerEmail,businessId, serviceName, countOfTicketsToBook, datetime.strptime(eventDate,config.applicationUIDateFormat).date(),slotStartTime)
   response={}
   response["responseType"]='success'
   response["success"]=[{"message":"The ticket(s) have been booked. Your booking number is "+bookingNumber}]
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/business/<businessId>/tickets", methods=['POST'])
def getTicketBookings(businessId):

   print('in getTicketBookings ')
   ticketBookings=Tickets().getTicketBookings(businessId)
   response={}
   response["responseType"]='data'
   response["data"]=ticketBookings
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/business/<businessId>/cancelTicket", methods=['POST'])
def cancelTickets(businessId):

   print('in cancel Tickets')
   content = request.get_json()
   print(content)

   bookingNumber=content['bookingNumber']
   cancelReason=content['cancelReason']

   bookingNumber=Tickets().cancelTicket(businessId,bookingNumber,cancelReason)
   response={}
   response["responseType"]='success'
   response["success"]=[{"message":"The ticket for the booking number "+bookingNumber+" has been cancelled."}]
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route('/user/login', methods=["POST"])
def login():
   print('in login')

   # dict = request.form
   # for key in dict:
   #    print('key:  {}  and   value:   {}'.format(key, dict[key]))

   content = request.get_json()
   print(content)

   email=content['email']
   password = content['password']
   response=Login().login(email,password)
   if (response["responseType"]=='data'):
      dataDict=response["data"]
      dataDict["auth-token"]=TokenManager().generateAndStoreToken(dataDict["userId"]).decode('ascii')
      print('encoded token')

      # print('after auth token 33')
      # print(dataDict["auth-token"])
      response["data"]=dataDict
      print(response)

   return app.response_class(json.dumps(response), content_type='application/json')



@app.route('/user/signup', methods=["POST"])
def signup():
   print('in signup')
   content = request.get_json()
   print(content)

   email=content['email']
   password = content['password']
   # dict = request.form
   # for key in dict:
   #    print('key:  {}  and   value:   {}'.format(key, dict[key]))
   response = Login().signup(email, password)

   # response={}
   # response["responseType"]='data'
   # response["data"]=res
   print(json.dumps(response))
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route('/user/changePassword', methods=["POST"])
def changePassword():
   print('in change password')
   content = request.get_json()
   print(content)

   # userId=content['userId']
   email=content['email']
   oldPassword=content['oldPassword']
   newPassword = content['newPassword']
   # dict = request.form
   # for key in dict:
   #    print('key:  {}  and   value:   {}'.format(key, dict[key]))

   response = Login().changePassword(email, oldPassword, newPassword)
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route('/user/resetPassword', methods=["POST"])
def resetPassword():
   print('in reset password')
   content = request.get_json()
   print(content)

   email=content['email']
   newPassword = content['newPassword']
   # dict = request.form
   # for key in dict:
   #    print('key:  {}  and   value:   {}'.format(key, dict[key]))

   res = Login().resetPassword(email, newPassword)
   response={}
   response["responseType"]='success'
   response["success"]=[{"message":"Password has been reset successfully"}]
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route('/verifyEmail', methods=["POST"])
def verifyEmail():
   print('in verify email')
   content = request.get_json()
   print(content)

   email=content['email']
   # dict = request.form
   # for key in dict:
   #    print('key:  {}  and   value:   {}'.format(key, dict[key]))
   response = Login().verifyEmail(email)
   print(response)
   print(json.dumps(response))
   return app.response_class(json.dumps(response), content_type='application/json')


@app.route('/user/<userId>/addSecurityQuestions', methods=["POST"])
def addSecurityQuestions(userId):
   print('in add securty ques ')

   content = request.get_json()
   print(content)
   quesAndIdPairs=content['quesIdAnsPair']
   email = content['email']

   response=Login().addSecurityQuestions(email, userId, quesAndIdPairs)
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route('/securityQuestions', methods=["GET"])
def getSecurityQuestions():
   print('in  get securty ques')
   questions=Login().getSecurityQuestions()
   response={}
   response["responseType"]='data'
   response["data"]=questions
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route('/user/securityQuestions', methods=["POST"])
def getUserSecurityQuestions():
   print('in  get user securty ques')
   content = request.get_json()
   questions=Login().getUserSecurityQuestions(content['email'])
   response={}
   response["responseType"]='data'
   response["data"]=questions
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route('/user/<userId>/verifySecurityResponses', methods=["POST"])
def verifyResponseToSecurityQuestions(userId):

   print('in verify securty responses')

   content = request.get_json()
   print(content)
   quesAndIdPairs=content['quesIdAnsPair']

   # qIdsAnsPairs=request.form.getlist('quesIdAnsPair')
   # quesAndIdPairs=[]
   # for qIdsAnsPair in qIdsAnsPairs:
   #    tuplePair=tuple(qIdsAnsPair.split(':').strip(' '))
   #    quesAndIdPairs.append(tuplePair)

   response=Login().verifySecurityResponses(userId,quesAndIdPairs)
   return app.response_class(json.dumps(response), content_type='application/json')

@app.route('/business/<businessId>/saveBusiness', methods=["POST"])
def saveCompleteBusinessDetails(businessId):

   print('save complete business details')
   content = request.get_json()
   print(content)

   # dict = request.form
   # for key in dict:
   #    print('key:  {}  and   value:   {}'.format(key, dict[key]))

   businessAdderss=BusinessAddress(businessId, content['addrL1'], content['addrL2'],content['suburb'],
                                   content['city'], content['googleMapsUrl'])


   businessExtraInfo=BusinessExtraInfo(businessId, content['weburl'], content['writeup'],None, config.gSingleTimeslotDuration, content['contactPhone'])

   businessHours=BusinessHours(businessId, content['monHours'], content['tuesHours'],
                                 content['wedHours'], content['thursHours'] , content['friHours'],
                                 content['satHours'], content['sunHours'])

   businessSettings=BusinessSettings(businessId, content['ifPhoneShownOnBookingEmail'],
                                     content['ifNotifyNoShowToBooker'], content['preBookingInterval'],
                                     content['advanceBookingPeriod'] , content['ifStaffNotifiedFutureBookings']  )

   servicesNames=content['name']
   print('servicesNames=   ',servicesNames)
   servicesSlotsDefinitions=content['slotsDefinition']
   servicesIfDoubleTimes=content['ifDoubleTime']
   servicesPrices=content['price']
   servicesCurencies=content['currency']
   servicesIfTicketBased=content['ifTicketBasedService']
   servicesMaxTicketCounts=content['maxTicketCount']
   print('servicesMaxTicketCounts= ', servicesMaxTicketCounts)
   servicesMaxTicketAllowedPerBooking=content['maxTicketsAllowedPerBooking']
   servicesCategories=content['category']
   servicesTopCategories=content['topCategory']

   services=[]
   for idx, serviceName in enumerate(servicesNames):
      # print('iteration= ', idx)
      # print(servicesMaxTicketCounts[idx])
      businessService=BusinessService(businessId, serviceName, servicesSlotsDefinitions[idx],
                              servicesIfDoubleTimes[idx], servicesPrices[idx] , servicesCurencies[idx],
                              servicesIfTicketBased[idx], servicesMaxTicketCounts[idx],
                                servicesMaxTicketAllowedPerBooking[idx], servicesCategories[idx], servicesTopCategories[idx])
      services.append(businessService)

   # holidays=content['holiday']
   # holidaysDates=[]
   # for holiday in holidays:
   #    holidaysDates.append(datetime.strptime(holiday,config.applicationUIDateFormat))


   fNames=content['firstName']
   lNames=content['lastName']
   emails=content['email']
   print('emails=   ',emails)
   phones=content['phone']
   print('phones=   ', phones)
   servicesSkills=content['serviceSkills']
   startTimeMons=content['startTimeMon']
   endTimeMons=content['endTimeMon']
   startTimeTuesdays=content['startTimeTues']
   endTimeTuesdays=content['endTimeTues']
   startTimeWeds=content['startTimeWed']
   endTimeWeds=content['endTimeWed']
   startTimeThursdays=content['startTimeThurs']
   endTimeThurdays=content['endTimeThurs']
   startTimeFris=content['startTimeFri']
   endTimeFris=content['endTimeFri']
   startTimeSats=content['startTimeSat']
   endTimeSats=content['endTimeSat']
   startTimeSuns=content['startTimeSun']
   endTimeSuns=content['endTimeSun']
   staffRoles=content['staffRole']

   staffMembers=[]
   for idx, email in enumerate(emails):
      businessStaff=Staff(businessId, None, fNames[idx], lNames[idx],
                              email, phones[idx] , servicesSkills[idx],
                              startTimeMons[idx], endTimeMons[idx],
                              startTimeTuesdays[idx], endTimeTuesdays[idx],
                              startTimeWeds[idx], endTimeWeds[idx],
                              startTimeThursdays[idx], endTimeThurdays[idx],
                              startTimeFris[idx], endTimeFris[idx],
                              startTimeSats[idx], endTimeSats[idx],
                              startTimeSuns[idx], endTimeSuns[idx],
                              staffRoles[idx])
      staffMembers.append(businessStaff)

   business = Business(None,businessExtraInfo,businessHours,businessSettings,services,businessAdderss,staffMembers)

   res=BusinessReviewAndSetup().saveReviewedBusinessSetup(businessId, business)
   response={}
   response["responseType"]='data'
   response["data"]=res
   # return app.response_class(json.dumps(response), content_type='application/json')



@app.route('/business/addBusinessMain', methods=["POST"])
def addBusinessMainFields():

   print('add business main')

   content = request.get_json()
   print(content)

   businessMainFields=BusinessMain(0, content['firstName'], content['lastName'], content['email'], content['phone'],
                                   content['businessName'],  'NEW')
   password=content['password']

   response=BusinessSetup().addBusinessMainFields(businessMainFields, password)
   response["responseType"] = 'success'
   response["success"] = [{
                             "message": "Staff member added. Add more staff or press Complete Setup to complete the setup."}]

   return app.response_class(json.dumps(response), content_type='application/json')



@app.route('/business/<businessId>/updateBusinessMainFields', methods=["POST"])
def updateBusinessMainFields(businessId):

   print('Update business main')
   content = request.get_json()
   print(content)

   businessMainFields=BusinessMain(businessId, content['firstName'],content['lastName'],content['email'],
                                   content['phone'], content['businessName'], 'NEW')
   res=BusinessSetup().updateBusinessMainFields(businessMainFields)
   response={}
   response["responseType"]='data'
   response["data"]=res
   return app.response_class(json.dumps(response), content_type='application/json')


@app.route('/business/<businessId>/addBusinessAddress', methods=["POST"])
def addBusinessAddress(businessId):

   print('add business address')

   content = request.get_json()
   print(content)

   businessAdderss=BusinessAddress(businessId, content['addressLine1'],content['addressLine2'],content['area'],
                                   content['city'], content['googleMapsUrl'], content['postalCode'], content['latitude'],content['longitude'])
   userRole=content['userRole']

   # dict = request.form
   # for key in dict:
   #    print('key:  {}  and   value:   {}'.format(key, dict[key]))

   res=BusinessSetup().addBusinessAddress(businessAdderss,userRole)
   response={}
   response["responseType"]='data'
   response["data"]=res
   return app.response_class(json.dumps(response), content_type='application/json')


@app.route('/business/<businessId>/addBusinessExtraInfo', methods=["POST"])
def addBusinessExtraInfo(businessId):

   print('add business extra info')

   content = request.get_json()
   print(content)

   businessExtraInfo=BusinessExtraInfo(businessId, content.get('weburl'), content.get('writeup'),None, config.gSingleTimeslotDuration, content.get('contactPhone'))
   userRole = content['userRole']
   # dict = request.form
   # for key in dict:
   #    print('key:  {}  and   value:   {}'.format(key, dict[key]))

   res=BusinessSetup().addBusinessExtraInfo(businessExtraInfo,userRole)
   response={}
   response["responseType"]='data'
   response["data"]=res
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route('/business/<businessId>/addBusinessHours', methods=["POST"])
def addBusinessHours(businessId):

   print('add business hours')

   content = request.get_json()
   print(content)
   businessHours=None
   if(len(content['monHours'])==4  ):
      monHours=content['monHours'][:2]+':'+content['monHours'][-2:]
      tuesHours = content['tuesHours'][:2] + ':' + content['tuesHours'][-2:]
      wedHours = content['wedHours'][:2] + ':' + content['wedHours'][-2:]
      thursHours = content['thursHours'][:2] + ':' + content['thursHours'][-2:]
      friHours = content['friHours'][:2] + ':' + content['friHours'][-2:]
      satHours = content['satHours'][:2] + ':' + content['satHours'][-2:]
      sunHours = content['sunHours'][:2] + ':' + content['sunHours'][-2:]

      businessHours=BusinessHours(businessId, content['monHours'], content['tuesHours'],
                                    content['wedHours'], content['thursHours'] , content['friHours'],
                                       content['satHours'], content['sunHours'])
   else:
      businessHours=BusinessHours(businessId, content['monHours'], content['tuesHours'],
                                    content['wedHours'], content['thursHours'] , content['friHours'],
                                       content['satHours'], content['sunHours'])


   userRole = content['userRole']
   # dict = request.form
   # for key in dict:
   #    print('key:  {}  and   value:   {}'.format(key, dict[key]))

   res=BusinessSetup().addBusinessHours(businessHours,userRole)
   BusinessSetup().changeStaffBusinessHours(businessHours)
   response={}
   response["responseType"]='data'
   response["data"]=res
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route('/business/<businessId>/addBusinessSettings', methods=["POST"])
def addBusinessSettings(businessId):

   print('add business settings')

   content = request.get_json()
   print(content)


   businessSettings=BusinessSettings(businessId, content['ifPhoneShownOnBookingEmail'],
                                     content['ifNotifyNoShowToBooker'], content['preBookingInterval'],
                                     content['advanceBookingPeriod'] , content['ifStaffNotifiedFutureBookings']  )

   userRole = content['userRole']
   # dict = request.form
   # for key in dict:
   #    print('key:  {}  and   value:   {}'.format(key, dict[key]))

   res=BusinessSetup().addBusinessSettings(businessSettings,userRole)
   response={}
   response["responseType"]='data'
   response["data"]=res
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route('/business/<businessId>/addBusinessService', methods=["POST"])
def addBusinessService(businessId):

   print('add business service')

   content = request.get_json()
   print(content)

   price =content["price"] if (content["price"] != None ) else 0
   currency = content['currency'] if (content['currency'] !=None and content["currency"].strip() !='') else 'RAND'
   maxTicketCount = content['maxTicketCount'] if (content['maxTicketCount'] !=None ) else 0
   maxTicketsAllowedPerBooking = content['maxTicketsAllowedPerBooking'] if (content['maxTicketsAllowedPerBooking'] !=None ) else 0

   print('maxTicketCount =',maxTicketCount )

   businessService=BusinessService(businessId, content['name'], content['slotsDefinition'],
                              content['ifDoubleTime'], price , currency,
                              content['ifTicketBasedService'], maxTicketCount,
                              maxTicketsAllowedPerBooking, content['category'], content['topCategory'],0, content['description'])

   # businessId, name, subslotsCount, ifDoubleTimeService = 'N', price = '1', currency = 'RAND', ifTicketBasedService = 'N', totalTicketCount = 0,
   # maxTicketsSoldPerBooking = 0, category = None, topCategory = None, duration = 0, description = None


   print(vars(businessService))

   userRole = content['userRole']

   # dict = request.form
   # for key in dict:
   #    print('key:  {}  and   value:   {}'.format(key, dict[key]))

   res=BusinessSetup().addBusinessService(businessService,userRole)
   response = {}
   if (res==True):
      response["responseType"] = 'success'
      response["success"] = [{"message": " Service details saved successfully "}]
   else :
      response["responseType"] = 'errors'
      response["errors"] = [{"field": "", "message": "Something went wrong"}]

   return app.response_class(json.dumps(response), content_type='application/json')


# Commented as it will not be required, has been replaced by extended leave concepts
# @app.route('/business/<businessId>/addBusinessHolidays', methods=["POST"])
# def addBusinessHolidays(businessId):
#
#    print('add business holidays')
#
#    content = request.get_json()
#    print(content)
#
#    holidays=content['holiday']
#    userRole = content['userRole']
   # print(holidays)


   # holidaysDates = []
   # for holiday in holidays:
   #    holiday=datetime.strptime(holiday,config.applicationUIDateFormat).date()
   #    holidaysDates.append(holiday)
   #
   # res=BusinessSetup().addBusinessHolidays(businessId, holidaysDates, userRole)
   # response={}
   # response["responseType"]='data'
   # response["data"]=res
   # return app.response_class(json.dumps(response), content_type='application/json')



@app.route('/business/<businessId>/addBusinessStaff', methods=["POST"])
def addBusinessStaff(businessId):

   print('add business staff')

   content = request.get_json()
   print(content)

   isOwner='N'
   serviceSkills=content['serviceSkills']
   print(serviceSkills)
   serviceSkillsStr=''
   if (serviceSkills==None):
      serviceSkillsStr=None
   elif (len(serviceSkills)==0):
      serviceSkillsStr=None
   elif (len(serviceSkills)==1):
      serviceSkillsStr=serviceSkills[0]
   else :
      for skill in serviceSkills:
         if(serviceSkillsStr ==''):
            serviceSkillsStr=skill
         else:
            serviceSkillsStr = serviceSkillsStr+';'+skill
   print(serviceSkillsStr)
   businessStaff=Staff(businessId, None, content['firstName'], content['lastName'],
                              content['email'], content['phone'] , serviceSkillsStr,
                              content['startTimeMon'], content['endTimeMon'],
                              content['startTimeTues'], content['endTimeTues'],
                              content['startTimeWed'], content['endTimeWed'],
                              content['startTimeThurs'], content['endTimeThurs'],
                              content['startTimeFri'], content['endTimeFri'],
                              content['startTimeSat'], content['endTimeSat'],
                              content['startTimeSun'], content['endTimeSun'],
                              content['staffRole'],isOwner)

   print(businessStaff)
   userRole=content['userRole']
   response=BusinessSetup().addBusinessStaff(businessStaff,userRole)
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route('/business/<businessId>/deleteBusinessService', methods=["POST"])
def deleteBusinessService(businessId):

   print('delete business service')

   content = request.get_json()
   print(content)

   serviceName=content['serviceName']
   userRole = content['userRole']

   res=BusinessSetup().deleteBusinessService(businessId, serviceName, userRole)
   response={}
   response["responseType"]='data'
   response["data"]=res
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route('/business/<businessId>/deleteBusinessStaff', methods=["POST"])
def deleteBusinessStaff(businessId):

   print('delete business staff')

   content = request.get_json()
   print(content)

   staffUserId=content['staffUserId']
   userRole = content['userRole']

   response=BusinessSetup().deleteBusinessStaff(businessId,staffUserId,userRole)
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route('/business/<businessId>/cancelBooking', methods=["POST"])
def cancelBooking(businessId):

   print('cancel booking')

   content = request.get_json()
   print(content)

   bookingNumber=content['bookingNumber']
   cancelReason=content['cancelReason'] if 'cancelReason' in content else ''

   # dict = request.form
   # for key in dict:
   #    print('key:  {}  and   value:   {}'.format(key, dict[key]))
   bookingNumber=BookingCore().cancelBooking(businessId,bookingNumber, cancelReason)
   response={}
   response["responseType"]='success'
   response["success"]=[{"message":"The appointment for the booking number "+bookingNumber+" has been cancelled."}]
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route('/business/<businessId>/cancelLeaves', methods=["POST"])
def cancelLeaves(businessId):

   print('cancel leaves')
   content = request.get_json()
   print(content)

   leaveNumber=content['leaveNumber']
   parentLeaveNumber=content['parentLeaveNumber']

   parentLeaveNumberResponse, leaveNumberResponse = BookingCore().cancelLeaves(businessId, parentLeaveNumber, leaveNumber)
   response={}
   response["responseType"]='success'
   response["success"]=[{"message":"The leave has been cancelled"}]
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route('/business/<businessId>/noShow', methods=["POST"])
def markNoShowOnBooking(businessId):

   print('mark no show on booking')

   content = request.get_json()
   print(content)

   bookingNumber=content['bookingNumber']

   # dict = request.form
   # for key in dict:
   #    print('key:  {}  and   value:   {}'.format(key, dict[key]))
   res=BookingCore().markNoShowOnBooking(businessId,bookingNumber)
   response={}
   response["responseType"]='success'
   response["success"]=[{"message":"The appointment for the booking number "+bookingNumber+" is a NO SHOW."}]
   return app.response_class(json.dumps(response), content_type='application/json')



# @app.route('/business/<businessId>/staff/leave', methods=["POST"])
# def markStaffOnLeave(businessId):
#
#    print('mark staff memeber on leave')
#
#    content = request.get_json()
#    print(content)
#
#    staffUserIds=content['staffUserIds']
#
#    # dict = request.form
#    # for key in dict:
#    #    print('key:  {}  and   value:   {}'.format(key, dict[key]))
#    res=BookingUtils().markStaffOnLeave(businessId,staffUserIds)
#    response={}
#    response["responseType"]='success'
#    response["success"]=[{"message":"Leave applied successfully"}]
#    return app.response_class(json.dumps(response), content_type='application/json')



@app.route('/business/<businessId>/staff/leave', methods=["POST"])
def markStaffOnLeave(businessId):

   print('mark staff memeber on leave')

   content = request.get_json()
   print(content)

   staffUserIds=content['staffUserIds']
   # ifAllStaff=content['ifAllStaff']
   # ifFullDayLeaves = content['ifFullDayLeaves']

   # res=BookingUtils().markStaffMembersOnLeaves(businessId,staffUserIds,ifAllStaff, ifFullDayLeaves)

   res = BookingUtils().markStaffOnLeave(businessId, staffUserIds)
   response={}
   response["responseType"]='success'
   response["success"]=[{"message":"Leave applied successfully"}]

   return app.response_class(json.dumps(response), content_type='application/json')



@app.route('/business/<businessId>/leaves', methods=["POST"])
def getBusinessLeaves(businessId):

   print('get staff leaves listing')

   leavesData=[]
   # parentLeaveNumbers=[]
   leaves = BookingUtils().getLeaves(businessId)
   print(leaves)

   # print(json.dumps(leaves))
   # leaveRecord["staffUserId"] = leave[1]
   # leaveRecord["leaveNumber"] = leave[2]
   # leaveRecord["startDate"] = leave[3]
   # leaveRecord["endDate"] = leave[4]
   # leaveRecord["startTime"] = leave[5]
   # leaveRecord["endTime"] = leave[6]
   # leaveRecord["ifAllStaff"] = leave[7]
   # leaveRecord["parentLeaveNumber"] = leave[8]
   # leaveRecord["status"] = leave[9]
   # leaveRecord["cancelButtonVisibility"] = False
   # if (leave[9] == 'NEW'):
   #    leaveRecord["cancelButtonVisibility"] = True


   parentLeaveNumberSet=set()
   for leave in leaves:
      parentLeaveNumberSet.add(leave["parentLeaveNumber"])

   print(parentLeaveNumberSet)
   parentLeaveNumberList=list(parentLeaveNumberSet)
   parentLeaveNumberDictList = []

   for pLN in parentLeaveNumberList:
      parentLeaveNumberDict = {}
      childRecords = []
      for leave in leaves:
         # childRecords=[]
         if (pLN==leave["parentLeaveNumber"]):
            if (leave["startDate"] != None):
               leave["startDate"] = leave["startDate"].strftime(config.applicationUIDateFormat)
            if (leave["endDate"] != None):
               leave["endDate"] = leave["endDate"].strftime(config.applicationUIDateFormat)
            childRecords.append(leave)

      parentLeaveNumberDict["parentLeaveNumber"]=pLN
      parentLeaveNumberDict["childLeaves"] = childRecords
      parentLeaveNumberDictList.append(parentLeaveNumberDict)



         #
         # parentLeaveDict = {}
         #
         # if (leave["startDate"] != None):
         #    leave["startDate"]=leave["startDate"].strftime(config.applicationUIDateFormat)
         # if (leave["endDate"] != None):
         #    leave["endDate"] = leave["endDate"].strftime(config.applicationUIDateFormat)
         #
         # parentLeaveDict["parentLeaveNumber"]=leave["parentLeaveNumber"]
         # parentLeaveDict["leave"] = leave
         # leavesData.append(parentLeaveDict)

   response={}
   response["responseType"]='data'
   response["data"]=parentLeaveNumberDictList

   return app.response_class(json.dumps(response), content_type='application/json')



@app.route('/business/<businessId>/markStaffOnleaves', methods=["POST"])
def markStaffOnLeaves(businessId):

   print('mark staff memeber on leave')

   content = request.get_json()
   print(content)

   ifMarkAllStaffMembers=content['ifMarkAllStaffMembers']
   ifMarkLeaveForFullDay = content['ifMarkLeaveForFullDay']
   staffUserIds=content['staffUserIds']
   response = {}

   if (ifMarkAllStaffMembers=='N' and staffUserIds==None):
      response["responseType"] = 'errors'
      response["errors"] = [{"field": "Staff Members", "message": "Choose atleast one staff member to mark leave for"}]
      return app.response_class(json.dumps(response), content_type='application/json')

   if (staffUserIds==None):
      staffUserIds=[]
   startDate = datetime.strptime(content['startDate'], config.applicationUIDateFormat).date()
   endDate = datetime.strptime(content['endDate'], config.applicationUIDateFormat).date()
   startTime=content['startTime']
   endTime = content['endTime']

   result = BookingUtils().markStaffMembersOnLeaves(businessId, staffUserIds, ifMarkAllStaffMembers, ifMarkLeaveForFullDay, startDate, startTime, endDate,  endTime)

   response["responseType"]='success'
   response["success"]=[{"message":"Leave(s) applied successfully"}]

   return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/business/<businessId>/services", methods=['POST'])
def getBusinessServices(businessId):

   services=BusinessSetup().getBusinessServices(businessId, 'User')
   jSerevices = json.dumps(services, default=AppUtils.convert_to_dict)
   servicesList = json.loads(jSerevices)
   # for key in servicesDict:
   newList=[]
   for service in servicesList:
      service["priceAndDuration"]='R'+str(service["price"])+', '+str(service["duration"])+'mins'
      newList.append(service)
   response={}
   response["responseType"]='data'
   response["data"]=newList
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/business/<businessId>/servicesNames", methods=['GET'])
def getBusinessServicesNames(businessId):

   print('in getBusiness services names')
   services=BusinessSetup().getBusinessServices(businessId, 'User')
   servicesNames=[]
   for service in services:
      servicesNames.append(service.name)
   response={}
   response["responseType"]='data'
   response["data"]=servicesNames
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/business/<businessId>/staff", methods=['POST'])
def getBusinessStaff(businessId):

   staff=BusinessSetup().getBusinessStaff(businessId, 'User')
   for member in staff:
      fullname=AppUtils().getFullName(member.firstname,member.lastname)
      member.firstname=fullname
      member.lastname=fullname


   print(*staff, sep='\n')
   jStaff = json.dumps(staff, default=AppUtils.convert_to_dict)
   print(jStaff)
   staffList = json.loads(jStaff)
   newStaffList=[]
   for oneStaff in staffList:
      oneStaff["allowStaffDeletion"]=True
      if (oneStaff["isOwner"] =='Y'):
         oneStaff["allowStaffDeletion"] = False
      newStaffList.append(oneStaff)
   print(staffList)

   response={}
   response["responseType"]='data'
   response["data"]=newStaffList
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/user/<staffUserId>/staffName", methods=['POST'])
def getStaffMemberDetails(staffUserId):

   print('in get staff memeber details')
   staff=BusinessSetup().getBusinessStaffDetails(staffUserId)
   print(staff)
   staff.firstname=AppUtils().getFullName(staff.firstname, staff.lastname)
   staff.lastname = staff.firstname
   # firstname, lastname
   jStaff = json.dumps(staff, default=AppUtils.convert_to_dict)
   print(jStaff)
   staffDict = json.loads(jStaff)

   response={}
   response["responseType"]='data'
   response["data"]=staffDict
   return app.response_class(json.dumps(response), content_type='application/json')



# Commented as holidays are being replaced by enhanced leave system
# @app.route("/business/<businessId>/holidays", methods=['POST'])
# def getBusinessHolidays(businessId):
#
#    holidays=BusinessSetup().getBusinessHolidays(businessId, 'User')
#
#    holidaysDates=[]
#    for holiday in holidays:
#       holidaysDates.append(holiday[1].strftime(config.applicationUIDateFormat))

   # jHolidays = json.dumps(holidaysDates, default=AppUtils.convert_to_dict)
   # holidaysDict = json.loads(jHolidays)
   # response={}
   # response["responseType"]='data'
   # response["data"]=holidaysDict
   # return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/business/<businessId>/workingHours", methods=['POST'])
def getBusinessHours(businessId):

   workingHours=BusinessSetup().getBusinessHours(businessId, 'User')

   jWorkingHours = json.dumps(workingHours, default=AppUtils.convert_to_dict)
   workingHoursDict = json.loads(jWorkingHours)
   response={}
   response["responseType"]='data'
   response["data"]=workingHoursDict
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/business/<businessId>/weeksRange", methods=['GET'])
def getWeeksRangeForUI(businessId):

   print('in staff display weeks')
   weeks=BookingUtils().getUIDisplayWeeks( businessId)

   response={}
   response["responseType"]='data'
   response["data"]=weeks
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/business/<businessId>/staffWorkingHourSlotsRange", methods=['POST'])
def getWeekdayWiseWorkingSlotsRange(businessId):

   print('in staff working hours slot range')
   workingHoursDict=BusinessSetup().getWeekdayWiseWorkingSlots(businessId, 'User')

   response={}
   response["responseType"]='data'
   response["data"]=workingHoursDict
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/business/<businessId>/businessWorkingHourSlotsRange", methods=['GET'])
def getBuisnessWorkingSlotsRange(businessId):

   print('in business working hours slot range')
   workingHoursList=BookingUtils().getBusinessWorkingSlotsRange(businessId)

   response={}
   response["responseType"]='data'
   response["data"]=workingHoursList
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/business/<businessId>/address", methods=['POST'])
def getBusinessAddress(businessId):

   address=BusinessSetup().getBusinessAddress(businessId, 'User')
   jAdress = json.dumps(address, default=AppUtils.convert_to_dict)
   addressDict = json.loads(jAdress)
   response={}
   response["responseType"]='data'
   response["data"]=addressDict
   return app.response_class(json.dumps(response), content_type='application/json')


@app.route("/business/<businessId>/extraInfo", methods=['POST'])
def getBusinessExtraInfo(businessId):

   extraInfo=BusinessSetup().getBusinessExtraInfo(businessId, 'User')
   jExtraInfo = json.dumps(extraInfo, default=AppUtils.convert_to_dict)
   extraInfoDict = json.loads(jExtraInfo)
   response={}
   response["responseType"]='data'
   response["data"]=extraInfoDict
   return app.response_class(json.dumps(response), content_type='application/json')


@app.route("/business/<businessId>/settings", methods=['POST'])
def getBusinessSettings(businessId):

   settings=BusinessSetup().getBusinessSettings(businessId, 'User')
   jSettings = json.dumps(settings, default=AppUtils.convert_to_dict)
   settingsDict = json.loads(jSettings)
   response={}
   response["responseType"]='data'
   response["data"]=settingsDict
   return app.response_class(json.dumps(response), content_type='application/json')


@app.route("/business/<businessId>/changeStatus", methods=['POST'])
def changeStatus(businessId):

   status=BusinessSetup().changeStatus(businessId)

   response={}
   response["responseType"]='data'
   # response["data"]=jsonBusinesses
   response["data"] = status
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/business/<businessId>/deleteBusiness", methods=['POST'])
def deleteBusiness(businessId):

   status=BusinessSetup().deleteBusiness(businessId)

   response={}
   response["responseType"]='data'
   # response["data"]=jsonBusinesses
   response["data"] = status
   return app.response_class(json.dumps(response), content_type='application/json')


@app.route("/business/<businessId>/enable", methods=['POST'])
def enabledBusiness(businessId):

   status=BusinessSetup().enabledBusiness(businessId)

   response={}
   response["responseType"]='data'
   # response["data"]=jsonBusinesses
   response["data"] = status
   return app.response_class(json.dumps(response), content_type='application/json')


@app.route("/business/<businessId>/disable", methods=['POST'])
def disabledBusiness(businessId):

   status=BusinessSetup().disabledBusiness(businessId)

   response={}
   response["responseType"]='data'
   # response["data"]=jsonBusinesses
   response["data"] = status
   return app.response_class(json.dumps(response), content_type='application/json')


@app.route("/businesses", methods=['GET'])
def getBusinesses():

   businesses=BusinessSetup().getBusinessesList('User')
   print(*businesses, sep='\n')
   # jsonBusinesses=[]
   # for business in businesses :
   #    jMainFields = json.dumps(business, default=AppUtils.convert_to_dict)
   #    mainFields=json.loads(jMainFields)
   #    print(mainFields)
   #    jsonBusinesses.append(mainFields)
   #
   response={}
   response["responseType"]='data'
   # response["data"]=jsonBusinesses
   response["data"] = businesses
   return app.response_class(json.dumps(response), content_type='application/json')


@app.route("/approvedbusinesses", methods=['GET'])
def getapprovedBusinesses():

   businesses=BusinessSetup().getApprovedBusinessesList('System')
   print(*businesses, sep='\n')
   # jsonBusinesses=[]
   # for business in businesses :
   #    jMainFields = json.dumps(business, default=AppUtils.convert_to_dict)
   #    mainFields=json.loads(jMainFields)
   #    print(mainFields)
   #    jsonBusinesses.append(mainFields)
   #
   response={}
   response["responseType"]='data'
   # response["data"]=jsonBusinesses
   response["data"] = businesses
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/editedbusinesses", methods=['GET'])
def geteditedBusinesses():

   businesses=BusinessSetup().getEditedBusinessesList('User')
   print(*businesses, sep='\n')
   response={}
   response["responseType"]='data'
   response["data"] = businesses
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/disabledbusinesses", methods=['GET'])
def getdisabledBusinesses():
   businesses=BusinessSetup().getDisabledBusinessesList('System')
   print(*businesses, sep='\n')
   # jsonBusinesses=[]
   # for business in businesses :
   #    jMainFields = json.dumps(business, default=AppUtils.convert_to_dict)
   #    mainFields=json.loads(jMainFields)
   #    print(mainFields)
   #    jsonBusinesses.append(mainFields)
   #
   response={}
   response["responseType"]='data'
   # response["data"]=jsonBusinesses
   response["data"] = businesses
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/business/<businessId>/mainFields", methods=['POST'])
def getBusinessMainFields(businessId):

   mainFields=BusinessSetup().getBusinessMainFields(businessId, 'User')

   jMainFields = json.dumps(mainFields, default=AppUtils.convert_to_dict)
   mainFieldsDict = json.loads(jMainFields)
   response={}
   response["responseType"]='data'
   response["data"]=mainFieldsDict
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/locations", methods=['GET'])
def getLocations():

   locations=Search().getLocations()

   response={}
   response["responseType"]='data'
   response["data"]=locations
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/serviceCategories", methods=['GET'])
def getAllServiceCategories():

   serviceCategories=Search().getServicesCategoriesByTopCategorries()
   print(serviceCategories)
   response={}
   response["responseType"]='data'
   response["data"]=serviceCategories
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/serviceCategory/<name>", methods=['POST'])
def addServiceCategory(name):

   print('in add service category')
   response=BusinessSetup().addServiceCategory(name)
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route('/deleteServiceCategory/<serviceCategoryName>', methods=["POST"])
def deleteBusinessServiceCategory(serviceCategoryName):

   print('delete business service category')

   res=BusinessReviewAndSetup().deleteBusinessServiceCategory(serviceCategoryName)
   response={}
   response["responseType"]='data'
   response["data"]=res
   return app.response_class(json.dumps(response), content_type='application/json')



@app.route("/serviceCategoriessAndBusinesses", methods=['GET'])
def getAllServicesAndBusinesses():

   servicesAndBusinesses=Search().getServiceCategoriesAndBusinesses()
   print(servicesAndBusinesses)

   response={}
   response["responseType"]='data'
   response["data"]=servicesAndBusinesses
   return app.response_class(json.dumps(response), content_type='application/json')


@app.route("/business/<businessId>/futureLeaves", methods=['POST'])
def getBusinessFutureLeaves(businessId):

   leaves = BookingUtils().getFutureLeaves(businessId)
   print(leaves)

   response={}
   response["responseType"]='data'
   response["data"]=leaves
   return app.response_class(json.dumps(response), content_type='application/json')



# Replace the code below. Temporarily uncommented for troubleshooting and allowed GET
# @app.route("/business/<businessId>", methods=['POST'])
@app.route("/business/<businessId>", methods=['GET', 'POST'])
def getBusiness(businessId):

   content = request.get_json()
   print(content)
   if (content == None ):
      content ={'behavior' : 'User'} 
   elif(content['behavior'] != 'User' and content['behavior'] != 'System'):
      content ={'behavior' : 'User'} 

   print(businessId)
   mainFields=BusinessSetup().getBusinessMainFields(businessId, content['behavior'])
   address=BusinessSetup().getBusinessAddress(businessId,content['behavior'])
   extraInfo=BusinessSetup().getBusinessExtraInfo(businessId, content['behavior'])
   settings=BusinessSetup().getBusinessSettings(businessId, content['behavior'])
   services=BusinessSetup().getBusinessServices(businessId, content['behavior'])
   jSerevices = json.dumps(services, default=AppUtils.convert_to_dict)
   servicesList = json.loads(jSerevices)
   newList = []
   for service in servicesList:
      service["priceAndDuration"]='R'+str(service["price"])+', '+str(service["duration"])+'mins'
      newList.append(service)
   services = newList
   staff=BusinessSetup().getBusinessStaff(businessId, content['behavior'])

   for member in staff:
      fullname=AppUtils().getFullName(member.firstname,member.lastname)
      member.firstname=fullname
      member.lastname=fullname
   print([mem.firstname for mem in staff])
   weeklyWorkingHours=BusinessSetup().getBusinessHours(businessId,'User')
   # holidays=BusinessSetup().getBusinessHolidays(businessId,'User')

   businessAllFieldsDict={}

   jMainFields = json.dumps(mainFields, default=AppUtils.convert_to_dict)
   mainFieldsDict = json.loads(jMainFields)
   businessAllFieldsDict["main"]=mainFieldsDict

   jAddress = json.dumps(address, default=AppUtils.convert_to_dict)
   addressDict = json.loads(jAddress)
   businessAllFieldsDict["address"]=addressDict

   jExtraInfo = json.dumps(extraInfo, default=AppUtils.convert_to_dict)
   extraInfoDict = json.loads(jExtraInfo)
   businessAllFieldsDict["extraInfo"]=extraInfoDict

   jSettings = json.dumps(settings, default=AppUtils.convert_to_dict)
   settingsDict = json.loads(jSettings)
   businessAllFieldsDict["settings"]=settingsDict

   jSerevices = json.dumps(services, default=AppUtils.convert_to_dict)
   servicesDict = json.loads(jSerevices)
   businessAllFieldsDict["services"]=servicesDict

   jStaff = json.dumps(staff, default=AppUtils.convert_to_dict)
   staffDict = json.loads(jStaff)
   businessAllFieldsDict["staff"]=staffDict

   jWorkingHours = json.dumps(weeklyWorkingHours, default=AppUtils.convert_to_dict)
   workingHoursDict = json.loads(jWorkingHours)
   businessAllFieldsDict["workingHours"]=workingHoursDict

   # print('holidays=',holidays)
   # holidaysDates=[]
   # for holiday in holidays:
   #    holidaysDates.append(holiday[1].strftime(config.applicationUIDateFormat))
   #
   # jHolidays = json.dumps(holidaysDates, default=AppUtils.convert_to_dict)
   # holidaysDict = json.loads(jHolidays)
   # businessAllFieldsDict["holidays"]=holidaysDict

   response={}
   response["responseType"]='data'
   response["data"]=businessAllFieldsDict
   return app.response_class(json.dumps(response), content_type='application/json')


@app.route("/report/allBusinessBookings", methods=['POST', 'GET'])
def getBusinessesData():

   import csv
   # data_list = [["SN", "Name", "Contribution"],
   #             [1, "Linus Torvalds", "Linux Kernel"],
   #             [2, "Tim Berners-Lee", "World Wide Web"],
   #             [3, "Guido van Rossum", "Python Programming"]]

   # appointment_date, service1_name, service2_name, slot_clock_time, booker_name, booker_comments, " \
               #  "staff_member, staff_member2, booking_number, staff_email, staff2_email, status " \
               #  ", price1, price2
   # data_header = ["Appointment Date", "Service 1", "Service 2", "Appointment Time", "Booker Name", "Booker Comments", 
   #                "Staff Member 1", "Staff Member 2", "Booking ID", "Staff 1 Email", "Staff 2 Email", "Booking Status", 
   #                "Price of Service 1", "Price of Service 2" ]

   data_header = ["Appointment Date", "Business Name", "Service", "Appointment Time", "Booker Email", "Booker Name", "Booker Comments", 
                  "Staff Member", "Booking ID", "Staff Email", "Booking Status", 
                  "Price of Service", "Cancellation Reason", "Booking Date and Time", "Cancellation Date and Time", "No Show Marked On" ]

   fromDate = request.args.get('fromDate') if request.args.get('fromDate') != None else ''
   toDate = request.args.get('toDate') if request.args.get('toDate') != None else ''

   data_list = DataAccess().getAllBusinessBookings(fromDate, toDate)

   si = StringIO()
   writer = csv.writer(si, delimiter=',')
   writer.writerow(data_header)
   writer.writerows(data_list)
   # with open('./innovators.csv', 'w', newline='') as file:
   # with open('E:/innovators.csv', 'w', newline='') as file:
      # writer = csv.writer(file, delimiter=',')
      # writer.writerow(data_header)
      # writer.writerows(data_list)

   response = make_response(si.getvalue())
   response.headers["Content-Disposition"] = "attachment; filename=All_Bookings.csv"
   response.headers["Content-type"] = "text/csv"
   return response
   
   # response={}
   # response["responseType"]='data'
   # response["data"]='Data written successfully'   
   # return app.response_class(json.dumps(response), content_type='application/json')

@app.route("/report/allBusinessList", methods=['POST', 'GET'])
def getAllBusinessesList():

   import csv
   data_header = ["Business Id", "Business Name", "Owner First Name", "Owner Last Name", "Owner Email Id", "Owner Phone Number", "Business status", "Address Line1", "Address Line2", "Area", "City", "Postal Code"]
   data_list = DataAccess().getAllBusiness()

   si = StringIO()
   writer = csv.writer(si, delimiter=',')
   writer.writerow(data_header)
   writer.writerows(data_list)

   response = make_response(si.getvalue())
   response.headers["Content-Disposition"] = "attachment; filename=All_Businesses.csv"
   response.headers["Content-type"] = "text/csv"
   return response


if __name__ == '__main__':

   # sys.stdout = open('/Users/atularora/temp/booking.logs', 'a')

   # app.run(host='0.0.0.0', ssl_context='adhoc')
   # app.wsgi_app = ProxyFix(app.wsgi_app)
   app.run()

   # loc=['a']
   # app.run(ssl_context='adhoc')
   # EmailBatch().executeBatches()
   # DataAccess().getLocations(5)
   # getBusinessServicesNames(34)