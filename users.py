# from src.dbAccess import DataAccess
from dbAccess import DataAccess
from businessSetup import BusinessSetup

class Login:

    def verifyEmail(self, email):

        user = DataAccess().checkEmailExists(email)
        print('userId')
        print(user)
        print('userId')
        response={}
        if(len(user)==0):
            response["responseType"] = 'errors'
            response["errors"] = [{"field": "Email", "message": "We do not have an account with this email"}]
        else:
            response["responseType"] = 'data'
            response["data"]=user[0][0]

        return response


    def login(self, email, password):

        res = DataAccess().login(email, password)

        response={}
        errorMessages = []

        if(res==None or len(res)==0):
            response["responseType"] = 'errors'
            errorMessages.append({"field": "Email/Password", "message": "An approved account with this email and password combination does not exist"})
            response["errors"]=errorMessages
        else:
            response["responseType"] = 'data'
            roles=res[0][1].split(";")
            print('roles= ',roles)
            businessId=res[0][2]
            ifTicketBasedBusiness = None
            ifBusinessApproved=None
            if (businessId!=None):
                services=BusinessSetup().getBusinessServices(businessId,'User')
                if (services!=None and len(services)>0):
                    ifTicketBasedBusiness =services[0].ifTicketBasedService

            response["data"]={"userId":res[0][0],"roles":roles,"businessId":res[0][2],"role":roles[0],"ifTicketBasedBusiness":ifTicketBasedBusiness}
            # response["data"] = {"userId": res[0][0], "roles": roles, "businessId": res[0][2]}
        return response



    def signup(self, email,password):

        user = DataAccess().getUserId(email)

        response = {}
        if (user == None):
            response["responseType"] = 'errors'
            response["errors"] = [{"field": "Email", "message": "This email does not exist in the system"}]
            return response
        else:
            userId, passwordOld,status=user

            if (status != 'APPROVED'):
                response["responseType"] = 'errors'
                response["errors"] = [{"field": "Email", "message": "This account is not approved."}]
                return response

            if (passwordOld != None):
                response["responseType"] = 'errors'
                response["errors"] = [{"field": "Email", "message": "An account with this email already exists"}]
                return response

            DataAccess().signup(email, password)
            userId=DataAccess().getUserId(email)[0]
            response["responseType"] = 'data'
            response["data"] =userId

        return response



    def changePassword(self, email, oldPassword, newPassword):
        updatedRowsCount = DataAccess().changePassword(email, oldPassword, newPassword)
        response={}
        if(updatedRowsCount==0):
            response["responseType"] = 'errors'
            response["errors"] = [{"field": "Old Password", "message": "The old password  entered is incorrect"}]
        else:
            response["responseType"] = 'success'
            response["success"] = [{"message": "Password has been changed successfully"}]
        return response



    def resetPassword(self, email,newPassword):
        res = DataAccess().resetPassword(email, newPassword)
        return res



    def  addSecurityQuestions(self, email, userId, quesIdsAnsPairs):
        print('in users add sec ques    ',quesIdsAnsPairs)
        quesSet=set()
        for onePair in quesIdsAnsPairs:
            quesSet.add(onePair[0])
        response={}
        if (len(quesSet) < len(quesIdsAnsPairs) ):
            response["responseType"] = 'errors'
            response["errors"] = [{"field": "Questions", "message": "The question cannot be repeated"}]
        else:
            DataAccess().addSecurityQuestions(email, userId, quesIdsAnsPairs)
            response["responseType"] = 'success'
            response["success"] = [{"message": "Your security questions and responses have been setup."}]
        return response



    def  verifySecurityResponses(self, userId, quesIdsAnsPairs):
        res = DataAccess().verifySecurityQuestionsResponse(userId, quesIdsAnsPairs)
        response={}
        if(res):
            response["responseType"]='data'
            response["data"]=True
        else:
            response["responseType"] = 'errors'
            response["errors"]=[{"field":"Security Question Response","message":"The response to questions is not correct"}]
        return response


    def  getSecurityQuestions(self):
        res = DataAccess().getSecurityQuestions()
        return res



    def  getUserSecurityQuestions(self, email):
        res = DataAccess().getUserSecurityQuestions(email)
        return res
