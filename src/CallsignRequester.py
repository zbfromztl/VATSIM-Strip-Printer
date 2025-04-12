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
                self.scan.push_gi_message(callsign_to_print)
            elif flag == "DROP":
                callsign_to_print = callsign_to_print[4:].strip()
                self.scan.dropTime(callsign_to_print)
            elif flag == "RECALL":
                callsign_to_print = callsign_to_print[6:].strip()
                self.printer.recall_inator(callsign_to_print)
            elif flag == "PRINTER":
                if self.printer.printer: self.printer.printer = False
                else: self.printer.printer = True
            elif flag == "UPPER_AIR_REPORT":
                print('Loading PIREP form...')
                time.sleep(.5) #https://www.faasafety.gov/files/helpcontent/Courses/One%20Flight%20One%20PIREP/ARTICULATE%20FILES/PIREP/story_content/external_files/PIREP_FORM.pdf
                type_of_ua = input("Enter type of PIREP (UA for routine or UUA for urgent): ")
                location = f'/OV {input("Enter location: ")}'
                report_time = f'/TM {input("Enter time (leave blank if now): ")}'
                if report_time.strip() == '/TM': report_time = f'/TM {time.strftime("%H%M",time.gmtime())}'
                altitude = f'/FL {input("Enter flight level (FL050, FL350, etc): ")}'
                ac_type = f'/TP {input("Enter aircraft type: ")}'
                print("Now that the mandatory items are covered, let's fill in the optional items. Leave it blank if you want to skip the item.")
                time.sleep(1)
                sky_cover = f' /SK {input("Enter Sky Cover: ")}'
                if sky_cover.strip() == '/SK': sky_cover = ''
                weather_vis = f' /WX {input("Enter Visibility/Wx (vis first): ")}'
                if weather_vis.strip() == '/WX': weather_vis = ''
                temp = f' /TA {input("Enter Temperature (C, if below 0, prefix with -): ")}'
                if temp.strip() == '/TA': temp = ''
                wind = f' /WV {input("Enter Wind (Direction/Speed in 6 digits... 270045): ")}'
                if wind.strip() == '/WV': wind = ''
                turb = f' /TB {input("Enter Turbulence (CAT/CHOP LIGT-MOD BLO-090, EXTRM): ")}'
                if turb.strip() == '/TB': turb = ''
                icing = f' /IC {input("Enter Icing Conditions (LGT-MDT RIME, SVR CLR): ")}'
                if icing.strip() == '/IC': icing = ''
                remarks = f' /RM {input("Enter Remarks (most hazardous items first): ")}'
                if remarks.strip() == '/RM': remarks = ''
                self.printer.print_gi_messages(f'GI {type_of_ua} {location} {report_time} {altitude} {ac_type}{sky_cover}{weather_vis}{temp}{wind}{turb}{icing}{remarks}'.upper())
            elif flag == "BAN":
                callsign_to_print = callsign_to_print[3:].strip().upper()
                if callsign_to_print in self.data_collector.banned_callsigns: self.data_collector.banned_callsigns.remove(callsign_to_print)
                else: self.data_collector.banned_callsigns.add(callsign_to_print)
                print(f'BANNED CALLSIGN LIST UPDATED: {self.data_collector.banned_callsigns}')
            elif flag == "FILTER":
                set_filter = callsign_to_print[6:].strip()
                self.printer.update_filters(set_filter)
            elif flag == "CURRENT PROPOSALS":
                callsign_to_print = callsign_to_print[6:].strip()
                current_callsign_list = self.data_collector.get_callsign_list()
                current_callsigns = ""
                for callsign in current_callsign_list: current_callsigns = f"{current_callsigns}, {callsign} (P{current_callsign_list[callsign]['flight_plan']['deptime']})"
                if len(current_callsigns) > 2: current_callsigns = current_callsigns[2:]
                else: current_callsigns = "THERE ARE NO CURRENT PROPOSALS."
                self.printer.print_gi_messages(current_callsigns)
            elif flag == "DUMPED":
                dumped_plans = self.data_collector.dumped_flights.copy()
                self.data_collector.dumped_flights = set()
                if len(dumped_plans) > 0: 
                    dumped_flight_string = 'FLIGHT PLANS THAT TIMED OUT: '
                    for aircraft_callsign in dumped_plans:
                        if len(dumped_flight_string) + len(aircraft_callsign) <= 320: dumped_flight_string = f"{dumped_flight_string} {aircraft_callsign}"
                        else:
                            self.printer.print_gi_messages(dumped_flight_string)
                            dumped_flight_string = str(aircraft_callsign)
                    if len(dumped_flight_string)+26 <= 320: 
                        self.printer.print_gi_messages(dumped_flight_string[-26:])
                        time.sleep(1)
                        self.printer.print_gi_messages(f'{dumped_flight_string[:-26]}... SETTING LIST TO EMPTY.')
                    else: self.printer.print_gi_messages(f'{dumped_flight_string}... SETTING LIST TO EMPTY.')
                else: self.printer.print_gi_messages(f'FLIGHT PLAN TIME OUT LIST EMPTY.')
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
        if callsign_to_print[0:6] == "recall":
            return "RECALL"
        if callsign_to_print[0:8] == "currentp":
            return "CURRENT PROPOSALS"
        if callsign_to_print[0:7] == "printer":
            return "PRINTER"
        if callsign_to_print[0:5] == "pirep":
            return "UPPER_AIR_REPORT"
        if callsign_to_print[0:4] == "ban ":
            return "BAN"
        if callsign_to_print[0:6] == "filter":
            return "FILTER"
        if callsign_to_print[0:6] == "dumped":
            return "DUMPED"

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