from Printer import Printer
from DataCollector import DataCollector
import time
from EFSTS import Scanner

__author__ = "Simon Heck"

class CallsignRequester:
    control_area = "A80ALL" # Set A80ALL as the control area in case theres some failure, lol.
    def __init__(self, printer: Printer, data_collector: DataCollector, control_area, scanner: Scanner) -> None:
        self.printer = printer
        self.data_collector = data_collector
        self.control_area = control_area
        self.scan = scanner

    def request_callsign_from_user(self) -> str:
        time.sleep(0.5)
        while(True):
            callsign_to_print = input("Enter Callsign: ")

            #Figure out what to do with the inputted value.
            flag = self.determineFlag(callsign_to_print.lower())

            #Process inputted value accordingly.
            if flag == "Print":
                self.request_callsign(callsign_to_print)
            elif flag == "Scan":
                self.scan.scan(callsign_to_print)
            elif flag == "TEST":
                self.printer.print_memoryAids()
            elif flag == "PURGE":
                self.scan.purgeQueue()
            elif flag == "TIME":
                self.scan.listTimes()
            elif flag == "CONVERT":
                callsign_to_print = callsign_to_print[6:].strip()
                self.scan.convert_identity(callsign_to_print)
            elif flag == "GI_MSG":
                self.printer.print_gi_messages(callsign_to_print)
            elif flag == "DROP":
                callsign_to_print = callsign_to_print[4:].strip()
                self.scan.dropTime(callsign_to_print)
            elif flag == "FRC":                                         #prints full strips. This definitely needs to be cleaned up in the future...
                callsign_to_print = callsign_to_print.upper()
                if callsign_to_print[0:3] == "SR ":
                    callsign_to_print = callsign_to_print[3:].strip()
                if callsign_to_print[0:4] == "FRC ":
                    callsign_to_print = callsign_to_print[4:].strip()
                self.printer.print_callsign_data(self.data_collector.get_callsign_data(callsign_to_print), callsign_to_print, self.control_area, "frc")
    
    def request_callsign(self, callsign):
        callsign_to_print = callsign.upper()
        self.printer.print_callsign_data(self.data_collector.get_callsign_data(callsign_to_print), callsign_to_print, self.control_area)

    def determineFlag(self,callsign_to_print):
        flag = "Print"
        #Detect if this is to print memory aids
        callsign_to_print = callsign_to_print.lower()
        callsign_to_print = callsign_to_print.strip()
        if callsign_to_print == "memoryaids":
            return "TEST"
        if callsign_to_print == "purge":
            return "PURGE"
        if callsign_to_print == "times":
            return "TIME"
        if callsign_to_print[0:3] == "gi ":
          return "GI_MSG"
        if callsign_to_print[0:3] == "sr ":
          return "FRC"
        if callsign_to_print[0:4] == "frc ":
          return "FRC"

        #What are we doing with this? Depends on what position the guy is working, maybe?
        #If they're NOT working Ground or Local, they shouldn't be scanning strips.
        control_area_type = self.control_area["type"].upper()
        if control_area_type != "GC" and control_area_type != "LC": 
            return "Print"
        else:
            if len(callsign_to_print) < 6: #If the callsign is less than 6 characters, it can NOT be a CID. Therefore, we're printing a flight strip.    
                return "Print"     
            elif callsign_to_print[0:4] == "drop":
                return "DROP"        
            elif callsign_to_print[0:6] == "lookup":
                return "CONVERT"          
            elif (callsign_to_print.upper().replace("V","",1)).isnumeric(): #We're checking to see if the callsign starts with a "V" to indicate "visual separation".
                if callsign_to_print[0] == "V" and callsign_to_print[1].isnumeric():
                    Visual = True
                return "Scan"
            elif callsign_to_print.isalnum(): #If the callsign has numbers AND letters, it can NOT be a CID. Therefore, we're printing a flight strip.
                return "Print"
            else:
                return flag

            #If callsign, print strip
            #If not callsign, function changes depending on GND or TWR
            #If ground, check to see in and out time. What if an airplane despawns on the taxi out?
            #If TWR, check if theres a "V" preceding the CID (transmits "VISUAL SEPARATION" to A80). Also, STOP timer. 