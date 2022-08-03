import mysql.connector

class Connection:

    def getConnection(self):

        # print('in getconnection')
        dbconfig = {
            "database": "bookings",
            "user": "root",
            # "password":"password",
            # "password":"Password123@",
            "password":"",
            "host":"localhost"
            # "host":"bookingsapp.mysql.database.azure.com",
            # "user": "adyatan_admin@bookingsapp",
            # "password": "password@123"


            # "host": "13.58.41.185"
            # ,
            # "auth_plugin":"caching_sha2_password"
        }
        # print('\n*************************************************************before dbconfig********************************************************************************************\n')
        # print(dbconfig)
        # print('\n*************************************************************before dbconfig********************************************************************************************\n')

        connectionA = mysql.connector.connect(pool_name="applicationPoolA", pool_size=10, **dbconfig)

        return connectionA


    def getUnapprovedConnection(self):

        dbconfig = {
            "database": "newbookings",
            "user": "root",
            # # "password":"password",
            # # "password":"Password123@",
            "password":"",
            "host":"localhost"
            # # "host": "13.58.41.185"
            # "host":"bookingsapp.mysql.database.azure.com",
            # "user": "adyatan_admin@bookingsapp",
            # "password": "password@123"


        }

        connectionB = mysql.connector.connect(pool_name="applicationPoolU", pool_size=10, **dbconfig)

        # print(connection-old)
        return connectionB


class EmailConnection:

    def getConnection(self):
        # print('in getconnection')

        dbconfig = {
            "database": "bookings",
            "user": "root",
            "password":"",
            # "password":"Password123@",
            "host":"localhost"
            # # "host": "13.58.41.185"
            # "host":"bookingsapp.mysql.database.azure.com",
            # "user": "adyatan_admin@bookingsapp",
            # "password": "password@123"

        }

        # print('\n*************************************************************before dbconfig********************************************************************************************\n')
        # print(dbconfig)
        # print('\n*************************************************************before dbconfig********************************************************************************************\n')
        connection = mysql.connector.connect(pool_name="applicationPoolEmail", pool_size=10, **dbconfig)

        # print(connection-old)
        return connection

