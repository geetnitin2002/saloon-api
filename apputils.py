from datetime import datetime,date,timedelta
from collections import defaultdict
from bisect import bisect_left
import config
import pytz

class AppUtils:


    def getDatesBetween(self, startDate, endDate, inclusionFlag='BOTH'):

        inBetweenDates=[]
        inBetweenDaysCount=(endDate - startDate).days+1
        for idx in range (inBetweenDaysCount):
            inBetweenDates.append(startDate+timedelta(days=idx))

        # print(inBetweenDates)
        if (inclusionFlag == 'FIRST'):
            return inBetweenDates[:len(inBetweenDates) - 1]
        elif (inclusionFlag == 'LAST'):
            return inBetweenDates[1:len(inBetweenDates)]
        elif (inclusionFlag == 'NEITHER'):
            return inBetweenDates[1:len(inBetweenDates) -1]
        elif (inclusionFlag == 'BOTH'):
            return inBetweenDates

        return inBetweenDates
    # def daysBetweenIsoDates(self, d1, d2):
    #
    #     d1 = datetime.strptime(d1, config.applicationUIDateFormat)
    #     d2 = datetime.strptime(d2, config.applicationUIDateFormat)
    #     return abs((d2 - d1).days)


    def convertTimeFormatFromUI2DB(self, time):
        pass



    def convertTimeFormatFromDB2UI(self, time):
        pass



    def convertDateFormatFromUI2DB(self, dateStr):
        return datetime.strptime(dateStr, config.applicationUIDateFormat).strftime(config.applicationDBDateFormat)



    def convertDateFormatFromDB2UI(self, dateStr):
        return datetime.strptime(dateStr, config.applicationUIDateFormat).strftime(config.applicationDBDateFormat)



    def getFullName(self, firstName, lastName):
        if(firstName==None):
            return lastName
        elif(lastName == None):
            return firstName
        else:
            return firstName + ' ' + lastName



    # format for time range: [11:00 - 20:00]
    # returns the list if slots in the time range
    def getSlots(self, timeRange, slotDuration):

        startTime = timeRange[:5]
        endTime = timeRange[-5:]

        # timeFormat = '%H%M'
        slots = []
        slotTime = startTime
        slots.append(slotTime)
        # print(slotTime)
        while (slotTime != endTime):
            newSlot = datetime.strptime(slotTime, config.applicationUITimeFormat) + timedelta(minutes=slotDuration)
            slotTime = datetime.strftime(newSlot, config.applicationUITimeFormat)
            # print(slotTime)
            slots.append(slotTime)

        # print(slots)
        return slots



    # def getSlots2(self, hoursRange, slotDuration):
    #
    #     # 1100 - 2000
    #     startHours = int(hoursRange[:2])
    #     startMinutes = int(hoursRange[2:4])
    #     # print('startMinutes = ', startMinutes)
    #     endHours = int(hoursRange[-4:-2])
    #     endMinutes = int(hoursRange[-2:])
    #     hoursDiff = endHours - startHours
    #     minutesDiff = endMinutes - startMinutes
    #     # print('hoursDiff = ', hoursDiff)
    #     # print('minutesDiff = ', minutesDiff)
    #     numericMinutesRange = hoursDiff * 100 + (minutesDiff * 100 // 60)
    #     print('numericMinutesRange =', numericMinutesRange)
    #     numericSlotDuration = slotDuration * 100 // 60
    #     slotsCount = numericMinutesRange // numericSlotDuration
    #     print(slotsCount)
    #
    #     numericStartHours = startHours
    #     numericStartMinutes = startMinutes * 100 // 60
    #     numericStartTime = (numericStartHours * 100) + numericStartMinutes
    #
    #     clockSlots = []
    #     for i in range(slotsCount + 1):
    #         numericTime = numericStartTime + (numericSlotDuration * i)
    #         clockHours = numericTime // 100
    #         clockMinutes = (numericTime % 100) * 60 // 100
    #         clockTime = str(clockHours).zfill(2) + str(clockMinutes).zfill(2)
    #         clockSlots.append(clockTime)
    #
    #     print(clockSlots)
    #     return clockSlots



    def convertDatesToWeekFormat(self, weekStartDate, weekEndDate):
        #     17/1/2019(Friday)  to  19/1/2019(Sunday)
        weekStartDateString = datetime.strftime(weekStartDate, config.applicationUIDateFormat)
        weekEndDateString = datetime.strftime(weekEndDate, config.applicationUIDateFormat)
        weekStartDay = weekStartDate.strftime("%A")
        weekEndDay = weekEndDate.strftime("%A")
        displayWeek = weekStartDateString + ' (' + weekStartDay + ')         to' + '       ' + weekEndDateString + ' (' + weekEndDay + ')'

        return displayWeek

    # def getNearestMonday(self):
    #     dayOfWeek = date.today().weekday()
    #     if (dayOfWeek == 0):
    #         return date.today(), 0
    #     else:
    #         monday = date.today() + timedelta(days=(7 - dayOfWeek))
    #         # print(monday)
    #         return monday, (7 - dayOfWeek)



    def daysBetweenIsoDates(self, d1, d2):

        d1 = datetime.strptime(d1, config.applicationUIDateFormat)
        d2 = datetime.strptime(d2, config.applicationUIDateFormat)
        return abs((d2 - d1).days)



    def getOneEachButDifferentElements(self, list1, list2):
        print(list1,list2)
        # list3 = []
        # s1 = set(list1)
        # s2 = set(list2)
        #
        # if (len(list1) == 1 and len(list2) == 1):
        #     list3 = [list1[0], list2[0]]
        #     return list3
        #
        # if (len(list1) == 2 and len(list2) == 2):
        #     (s2).discard(list1[0])
        #     if (len(s2) == 1):
        #         list3 = [list1[0], s2.pop()]
        #     else:
        #         list3 = [list1[0], list2[0]]
        #     return list3
        #
        # if (len(list1) == 1):
        #     (s2).discard(list1[0])
        #     if (len(s2) == 1):
        #         list3 = [list1[0], s2.pop()]
        #     else:
        #         list3 = [list1[0], list2[0]]
        #     return list3
        #
        # if (len(list2) == 1):
        #     (s1).discard(list2[0])
        #     if (len(s1) == 1):
        #         list3 = [list2[0], s1.pop()]
        #     else:
        #         list3 = [list1[0], list2[0]]
        #     return list3
        #
        # return list3

        if (len(list1) == 1 and len(list2) == 1):
            print(list1[0], list2[0])
            return list1[0], list2[0]

        elif (len(list1) == 1 and len(list2) > 1):
            if list1[0] in list2:
                list2.remove(list1[0])
                print(list1[0], list2[0])
                return list1[0], list2[0]
            else:
                print(list1[0], list2[0])
                return list1[0], list2[0]

        elif (len(list1) > 1 and len(list2) >= 1):
            if list2[0] in list1:
                list1.remove(list2[0])
                print(list1[0], list2[0])
                return list1[0], list2[0]
            else:
                print(list1[0], list2[0])
                return list1[0], list2[0]



    def getHigherElementsInSortedList(self, sortedList, elementToBeFound):

        if (len(sortedList)==0):
            return sortedList

        if (elementToBeFound <= sortedList[0]):
            print('in if')
            return sortedList
        elif (elementToBeFound > sortedList[len(sortedList) - 1]):
            print('in elif')
            return []
        else:
            print('in else')
            i = 0
            for item in sortedList:
                print(item)
                i = i + 1
                if (item >= elementToBeFound):
                    print(i)
                    return sortedList[i - 1:]



    def getTheRunningSlot(self):

        local = pytz.timezone("Africa/Johannesburg")
        clockTime = datetime.now(local).strftime('%H:%M')
        return AppUtils().convertClockTimeToSlotNumber(clockTime)



    def isRangeConsecutive(self, sortedList):
        return sortedList == list(range(min(sortedList), max(sortedList) + 1))



    # input is sorted list of free slots
    # returns the slots that are available to perform the service over the service duration
    def getConsecutiveChunks(self, sortedList, chunkSize):

        if (chunkSize > len(sortedList)):
            return []
        chunkPointers=[]
        # iterations=len(sortedList) - chunkSize + 1
        # if (iterations>0):
        for i in range(len(sortedList) - chunkSize + 1):
            if(self.isRangeConsecutive(sortedList[i:i + chunkSize])):
                chunkPointers.append(sortedList[i])
        return chunkPointers


    def convertClockTimeRangeToSlotsRange(self, clockTimeRange):
        startTime = clockTimeRange[:5]
        endTime = clockTimeRange[-5:]
        slots = {'startSlotNumber': 0, 'endSlotNumber': 0}
        slots['startSlotNumber'] = self.convertClockTimeToSlotNumber(startTime)
        slots['endSlotNumber'] = self.convertClockTimeToSlotNumber(endTime) - 1
        return slots



    def convertSlotsRangeToClockTimeRange(self, slotRange):
        parts = slotRange.split('-')
        slotRangeStart = parts[0].strip()
        slotRangeEnd = parts[1].strip()
        return self.convertSlotNumberToClockTime(int(slotRangeStart)) + ' - ' + self.convertSlotNumberToClockTime(
            int(slotRangeEnd)+1)



    def convertSlotNumberToClockTime(self, slotNumber):
        # time = (slotNumber - 1) * 15;
        time = (slotNumber - 1) * int(config.gSingleTimeslotDuration);
        hour = time // 60;
        minutes = time % 60;
        return str(hour).zfill(2) +':'+ str(minutes).zfill(2);



    def convertClockTimeToSlotNumber(self, clockTime):

        hours = int(clockTime.strip()[:2])
        minutes = int(clockTime.strip()[-2:])
        # slotNumber = (hours * 4) + (minutes // 15) + 1
        slotNumber = (hours * (60//int(config.gSingleTimeslotDuration))) + (minutes // int(config.gSingleTimeslotDuration)) + 1

        return slotNumber



    def convert2ElementsTupleListToDict(self, inList):

        res = defaultdict(list)
        for i, j in inList:
            res[i].append(j)

        return res



    def convertTupleToDict2(self, inList):

        # logic to convert list of tuples to dict , key is business id, value is services list
        resDict={}
        sKeys = set()
        for row in inList:
            if(self.in_or_add(sKeys, row[0])):
                resDict[row[0]]=[row[1]]
            else:
                # print('in else part')
                elements=resDict[row[0]]
                elements.append(row[1])
                resDict[row[0]]=elements
        return resDict



    def in_or_add(self,s, x):
        return not(x in s or s.add(x))



    def getSublist(self, multiElementDict, sublistSize):
        # sublist={}
        # for key in multiElementDict:
        #     tempList=[]
        #     if (len(multiElementDict[key]) <= sublistSize):
        #         return multiElementDict
        #         # sublistSize=len(multiElementDict[key])
        #     for i in range (0, sublistSize):
        #         # print('iteration =',i)
        #         tempList.append(multiElementDict[key][i])
        #     sublist[key]=tempList

        sublist = {}
        for key in multiElementDict:
            print(key)
            tempList = []
            if (len(multiElementDict[key]) <= sublistSize):
                tempList = multiElementDict[key]
            else:
                for i in range(0, sublistSize):
                    tempList.append(multiElementDict[key][i])
            sublist[key] = tempList

        return sublist



    # def getDayOfWeek(self, date):
    #     return datetime.strptime(date, '%Y-%m-%d').weekday()



    # def convertDatabaseDateToStr(self, dBdate):
    #     return datetime.strftime(dBdate, '%Y-%m-%d')



    # def convertPythonDateToDateStr(self, pythonDate):
    #     return datetime.strftime(pythonDate, '%Y-%m-%d')



    # def isFirsDateStringBigger(self, d1, d2):
    #     date1=datetime.strptime(d1, '%Y-%m-%d').date()
    #     date2=datetime.strptime(d2, '%Y-%m-%d').date()
    #     return d1 > d2


    # def convert_to_dict(self, obj):
    @staticmethod
    def convert_to_dict(obj):
        obj_dict = {}
        obj_dict.update(obj.__dict__)
        return obj_dict

        # print(date1)
# print(AppUtils().getDayOfWeek('2020-01-08'))


# print(AppUtils().convertDatabaseDateToStr(dateDB))
# print(AppUtils().convertPythonDateToDateStr(datetime.today()))
# print(AppUtils().isFirsDateStringBigger('2020-02-14','2020-02-14'))