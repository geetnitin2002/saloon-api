import configparser
import os

config = configparser.ConfigParser()

# config.read('/Users/atularora/PycharmProjects/bookings-serveice/src/bookings-config.ini')
# config.read('/home/ubuntu/bookings/src/bookings-config.ini')
config.read((os.path.join(os.path.dirname(__file__), '', 'bookings-config.ini')))
# config.sections()
sections=config.sections()
print(sections)
# for section in sections:
#     print(config.items(section))

# AWS
awsAaccessKeyId=config['AWS']['aws_access_key_id']
awsSecretAccessKey=config['AWS']['aws_secret_access_key']
awsRegionName=config['AWS']['aws_region_name']
s3Bucket=config['AWS']['s3-bucket']
localFileUoploadDirectory=config['AWS']['local_file_upload_directory']

# TOKEN
jsonSerializerSecret=config['TOKEN']['json-serializer-secret']
tokenExpiryDurationSecs=config['TOKEN']['token-expiry-duration-secs']

# MESSAGES
loginFailedMessage=config['MESSAGES']['unsuccessful-login']

# APPLICATION
baseUrl=config['APPLICATION']['base-url']
baseAppUrl=config['APPLICATION']['base-app-url']
gSingleTimeslotDuration=config['APPLICATION']['gSingleTimeslotDuration']
# # duration of an atomic slot
# gSingleTimeslotDuration=15

# # no of days for which availability ois to be shown to the user
# availabilityWindow=35

# applicationUIDateFormat='%d/%m/%Y'
# applicationDBDateFormat='%Y-%m-%d'
# applicationUITimeFormat='%H:%M'
# applicationDBTimeFormat=''
# applicationDBDateTimeFormat=''
# applicationUIDateTimeFormat=''

# duration of an atomic slot
# gSingleTimeslotDuration=config['APPLICATION']['gSingleTimeslotDuration']

# no of days for which availability ois to be shown to the user
availabilityWindow=config['APPLICATION']['availabilityWindow']

applicationUIDateFormat=config['APPLICATION']['applicationUIDateFormat']
applicationDBDateFormat=config['APPLICATION']['applicationDBDateFormat']
applicationUITimeFormat=config['APPLICATION']['applicationUITimeFormat']
applicationDBTimeFormat=config['APPLICATION']['applicationDBTimeFormat']
applicationDBDateTimeFormat=config['APPLICATION']['applicationDBDateTimeFormat']
applicationUIDateTimeFormat=config['APPLICATION']['applicationUIDateTimeFormat']

# AZURE
storage_blob_url = config['AZURE']['storage_blob_url']
storage_account_conn_str = config['AZURE']['storage_account_conn_str'].strip('\'')
container_name = config['AZURE']['container_name']
api_base_url = config['AZURE']['api_base_url']
logo_url = config['AZURE']['logo_url']
googleCalendarButtonImg = config['AZURE']['googleCalendarButtonImg']
appleCalendarButtonImg = config['AZURE']['appleCalendarButtonImg']