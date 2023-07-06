### I think this should maybe keep track of the departure split? Maybe?
### Definitely should be able to poll the number of departures i think

import time
import json
from DataCollector import DataCollector

currentSplit = {
    "N":["NOONE","NOTWO","PENCL","VARNM","PADGT","SMKEY","WEONE","WETWO","POUNC","KAJIN","NASSA","CUTTN"],
    "C":["EAONE","EATWO","PLMMR","JACCC","PHIIL","GAIRY","SOONE","SOTWO","VRSTY","SMLTZ","BANNG","HAALO"],
    "S":[],
}

normalSplit = {
    "NOONE":"N", "NOTWO":"N", "PENCL":"N", "VARNM":"N", "PADGT":"N", "SMKEY":"N",
    "WEONE":"N", "WETWO":"N", "POUNC":"N", "KAJIN":"N", "NASSA":"N", "CUTTN":"N",
    "EAONE":"C", "EATWO":"C", "PLMMR":"C", "JACCC":"C", "PHIIL":"C", "GAIRY":"C",
    "SOONE":"C", "SOTWO":"C", "VRSTY":"C", "SMLTZ":"C", "BANNG":"C", "HAALO":"C"
    }

gateFixes = {
    "EAONE":["EAONE", "PLMMR", "JACCC"],
    "EATWO":["EATWO", "PHIIL", "GAIRY"],
    "SOONE":["SOONE", "VRSTY", "SMLTZ"],
    "SOTWO":["SOTWO", "BANNG", "HAALO"],
    "WEONE":["WEONE", "POUNC", "KAJIN"],
    "WETWO":["WETWO", "NASSA", "CUTTN"],
    "NOONE":["NOONE", "PENCL", "VARNM"],
    "NOTWO":["NOTWO", "PADGT", "SMKEY"]
}

depCodes = {
    "E1":"EAONE",
    "E3":"PLMMR",
    "E5":"JACCC",
    "E2":"EATWO",
    "E4":"PHIIL",
    "E6":"GAIRY",
    "W1":"WEONE",
    "W3":"POUNC",
    "W5":"KAJIN",
    "W2":"WETWO",
    "W4":"NASSA",
    "W6":"CUTTN",
    "N1":"NOONE",
    "N3":"PENCL",
    "N5":"VARNM",
    "N2":"NOTWO",
    "N4":"PADGT",
    "N6":"SMKEY",
    "S1":"SOONE",
    "S3":"SMLTZ",
    "S5":"VRSTY",
    "S2":"SOTWO",
    "S4":"BANNG",
    "S6":"HAALO"
}


#COMMAND STRUCTURE IS ALL or DEPARTURE NORTH/CENTER/SOUTH

class AirspaceManagement:
    def __init__(self, control_area) -> None:
        self.currentSplit = currentSplit
        self.gateFixes = gateFixes
        self.normalSplit = normalSplit
        self.controlArea = control_area
        self.FTD = False
        self.datacollector = DataCollector
    
    def getSplit(self) -> str:
        time.sleep(.5)
        while(True):
            splitPosition = input("Enter ARMT command: ")
            
            splitPosition = self.formatCommand(splitPosition)

            if splitPosition[:3] == "ftd":
                try:
                    self.FTD = bool(int(input("Do you want to activate the 3rd runway? Reply '1' for yes or '0' for no.")))
                    if self.FTD == False:
                        self.amendSplit("normal")
                except:
                    continue

            if splitPosition[:3] == "all":
                self.amendSplit(splitPosition)

            if splitPosition.upper()[:5] in self.normalSplit:
                print("yea it'll work")
                self.amendSplit(splitPosition)
            elif splitPosition[:6] == "normal":
                self.amendSplit("normal")
            elif splitPosition == "countproposals":
                self.countProposals
            elif splitPosition == "worstqueue":
                self.worstQueue

    def amendSplit(self, input):
        input = input.replace(" ","")
        engToCode1 = {"north":"N","center":"C","south":"S"}
        try:
            if input[:3] == "all":
                newCode = engToCode1[input[3:]]
                print("change the split!!")
                self.currentSplit = {"N":[],"C":[],"S":[]}
                for i in self.normalSplit:
                    self.currentSplit[newCode].append(i)
                print(self.currentSplit)
                print(len(self.currentSplit[newCode]))
            elif input == "normal":
                print("normal split, coming up!")
                self.currentSplit = {"N":[],"C":[],"S":[]}
                for i in self.normalSplit:
                    self.currentSplit[self.normalSplit[i]].append(i)
                print(self.currentSplit)
            else:
                newCode = engToCode1[input[5:]]
                input = input.upper()
                print(f"change the split!! moving {input[:5]} to the {newCode}")
                if input[:5] in self.gateFixes:
                    for x in self.gateFixes[input[:5]]:
                        for i in self.currentSplit:
                            if x in self.currentSplit[i]:
                                self.currentSplit[i].remove(x)
                        self.currentSplit[newCode].append(x)
                else:
                    for i in self.currentSplit:
                        if input[:5] in self.currentSplit[i]:
                            self.currentSplit[i].remove(input[:5])
                    self.currentSplit[newCode].append(input[:5])
                print(self.currentSplit)
            
        except:
            print("huh?")
    
    def countProposals(self):
        aircraft = {}
        json_File = self.datacollector.get_json()
        for i in json_File:
            print(i)
        connected_pilots = json_File['pilots']
        for i in range(len(connected_pilots)):
            # pilot at index i information
            current_pilot = connected_pilots[i]
            lat_long_tuple = (current_pilot['latitude'], current_pilot['longitude'])
            pilot_departure_airport = current_pilot['flight_plan']['departure']
            try:
                if pilot_departure_airport is "KATL" and DataCollector.in_geographical_region_wip(self.controlArea, pilot_departure_airport, lat_long_tuple):
                    aircraft[current_pilot['callsign']] = current_pilot['flight_plan']['route']
            except:
                continue

        print(aircraft)

        
    def worstQueue(self):
        print("lick me")

                    
    def formatCommand(self, splitPosition):
        splitPosition = splitPosition.lower()
        if splitPosition[-1] in ["n","c","s"]:
            elongator = {"n":"north","c":"center","s":"south"}
            splitPosition = f'{splitPosition[:-1]}{elongator[splitPosition[-1]]}'

        if self.FTD is False:
            splitPosition = splitPosition.replace("south","center")

        splitPosition = splitPosition.replace(" ","")
        print(splitPosition[1])
        if splitPosition[1].isnumeric():
            splitPosition = splitPosition.replace(splitPosition[:2],depCodes[splitPosition.upper()[:2]]).lower()
        return splitPosition
            