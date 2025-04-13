import time
import json
import requests
from Printer import Printer
from DataCollector import DataCollector
from JSONRefreshTimer import JSONRefreshTimer

__author__ = "KK"

#Want this to track:
#Pertinent ATIS changes (Wind, Ceiling, Letter (lol), Etc)
#Alert if an ATIS goes DOWN or is "Operational"
#TODO: Update sync for ATIS


class ATISInfoUhhh:
    def __init__(self, control_area, printer:Printer, data_collector:DataCollector, jsonTimer:JSONRefreshTimer, airports) -> None:
        self.ATISFields = {}

# callsign
# network callsign (KATL_D_ATIS)

# atis_code
# string
# Current ATIS phonetic letter (D)

# text_atis
# string[]
# Text ATIS (stupid)

# last_updated
# date-time
# When this ATIS's status was last received

        self.airports = airports['airfields']
        self.control_area = []
        self.control_area = control_area
        self.printer = printer
        self.data = data_collector
        self.jsonTimer = jsonTimer
        self.AirportManager = set()
        self.ATISManager = dict()
        #Find what airports we need to track
        for airfield in self.control_area['airports']: self.AirportManager.add(airfield) #Find out what airports we care about

    def scan_atis(self):
        json_file = self.data.get_json()
        atis_stations = json_file["atis"]
        atis_changes = []
        online_airports = []
        global_online_atis = []
        dumped_atis = []
        for connection in atis_stations: 
            if connection['text_atis'] is None or connection['atis_code'] is None: continue
            # print(connection['text_atis'])
            if len(connection['text_atis']) <= 2: continue
            airport, atis_type = self.check_airport(connection['callsign'])
            atis_letter = connection['atis_code']
            global_online_atis.append(connection['callsign'])
            if airport in self.AirportManager: #Is this an ATIS we care about?
                if airport in self.ATISManager: #Are we already tracking this ATIS?
                    if atis_type in self.ATISManager[airport]: #Are we already tracking this type of ATIS?
                        current_text = self.format_text_atis(connection['text_atis'])
                        was_change, changes = self.check_for_changes(self.ATISManager[airport][atis_type], current_text)
                        if was_change: 
                            atis_changes.append(f"{airport} {atis_type} / {changes}")
                            self.ATISManager[airport].update({atis_type:current_text})
                        online_airports.append(connection['callsign'])
                    else: #if its not in (due to type or airport) add
                        text_atis = self.format_text_atis(connection['text_atis'])
                        self.ATISManager[airport].update({atis_type:text_atis})
                        atis_changes.append(f'{airport} {atis_type} ATIS NOW OPERATIONAL... {atis_letter}... {text_atis} / ')
                else:
                    text_atis = self.format_text_atis(connection['text_atis'])
                    self.ATISManager.update({airport:{atis_type:text_atis}})
                    atis_changes.append(f'{airport} {atis_type} ATIS NOW OPERATIONAL... {atis_letter}... {text_atis} / ')
            # print(connection['callsign'], airport, atis_type, airport in self.AirportManager, airport in self.ATISManager)
        #Check for disconnections...
        for connection in self.ATISManager.copy():
            for type_logged in self.ATISManager[connection].copy():
                callsign_regex = connection
                atis_type = type_logged
                if atis_type == "combined": callsign_regex = f'{connection}_ATIS'.strip()
                else: callsign_regex=f'{connection}_{atis_type[:1]}_ATIS'.strip().upper()
                # print(f'ugh... {callsign_regex} vs {global_online_atis}')
                if callsign_regex not in global_online_atis: 
                    dumped_atis.append(callsign_regex)
                    self.ATISManager[connection].pop(type_logged)
                    # to_purge.append([connection][type_logged])
        if len(dumped_atis) > 0: 
            dumped_airports = " DISCONNECTED ATIS: "
            for dumped in dumped_atis:
                dumped_airports = f'{dumped_airports} {dumped}'
                # if len(self.ATISManager[dumped])
            atis_changes.append(dumped_airports)
            # print(dumped_airports)
        for connection in self.ATISManager.copy(): #clean up ATISManager
            if len(self.ATISManager[connection])==0: self.ATISManager.pop(connection)
        # for purgin in to_purge:
        #     try:
        #         print(f'purgin {purgin} .. {to_purge}')
        #         if len(self.ATISManager[purgin]) == 1 and len(to_purge[purgin]) == 1: self.ATISManager.pop(purgin)
        #         else: self.ATISManager[purgin].pop(to_purge[purgin])
        #     except Exception as e34: print(f'Error purging ATIS from list: {e34}')
        atis_changes = str(atis_changes).upper().strip()
        atis_changes=atis_changes.replace('[',"")
        atis_changes=atis_changes.replace(']',"")
        # print(f'Currently stored: {self.ATISManager}')
        # print(f'debug... {atis_changes} ... {len(atis_changes)}')
        if len(atis_changes) > 0: 
            while len(atis_changes) > 320:
                self.printer.print_gi_messages(atis_changes[:320])
                atis_changes = atis_changes[320:]
                time.sleep(3)
            else: self.printer.print_gi_messages(atis_changes)

    def start_refreshing(self, delay:int = 60):
        time.sleep(self.jsonTimer.calculateDelay()+45)
        while(True):
            self.scan_atis()
            time.sleep(delay)

    def check_airport(self, callsign):
        what_type = 'combined'
        try:
            callsign_fields = str(callsign).upper().split("_")
            if len(callsign_fields) != 2:
                if callsign_fields[1] == "D": what_type = "departure"
                elif callsign_fields[1] == "A": what_type = "arrival"
            airport = callsign_fields[0]
            return airport, what_type
        except: print('exception in ATIS system')

    def format_text_atis(self, entry):
        try:
            entry_combined = ""
            for line_item in entry: entry_combined = f"{entry_combined} {line_item}"
            annoying_items = ['[',']','"']
            for item in annoying_items: entry_combined = entry_combined.replace(item," ")
            entry_combined = entry_combined.replace("  "," ") #Replace any double spaces...
        except Exception as e1: print(f'Error in formatting text ATIS: {e1}')
        return entry_combined

    def check_for_changes(self, old, new):
        was_change = False
        changes = ''
        # print(f'CHECKING FOR CHANGES BETWEEN {old} AND {new}!')
        try: 
            old_atis_content = {"letter":"","time":"","wind":"","visibility":"","clouds":"","temp":"","dewpt":"","altimeter":"","airport_conditions":"","notams":""}
            new_atis_content = {"letter":"","time":"","wind":"","visibility":"","clouds":"","temp":"","dewpt":"","altimeter":"","airport_conditions":"","notams":""}
            #start by breaking up the atis content...
            self.process_changes(old, old_atis_content)
            self.process_changes(new, new_atis_content)

            # print(old_atis_content, new_atis_content)

            for content_item in old_atis_content:
                if old_atis_content[content_item] != new_atis_content[content_item]: changes = f'{changes}{content_item}: {new_atis_content[content_item]} '
            
            if changes != '': was_change = True
        except Exception as e1: print(f'Error in discerning ATIS changes... {e1}')
        return was_change, changes

    def process_changes(self, atis_raw, atis_content):
        try:
            atis_raw = str(atis_raw).split('INFO',1)[1].strip() #This should discard the old opening...
            atis_raw = atis_raw.split('...ADVS YOU HAVE INFO',1)[0]
            atis_content['letter'] = atis_raw[0]

            vis_pos = 0
            temp_pos = 0
            for content_item in atis_raw.split(' '):
                if content_item.endswith('Z.'): atis_content['time']=content_item
                elif content_item.find('KT') != -1: atis_content['wind']=content_item
                elif content_item.endswith('SM'): 
                    atis_content['visibility']=content_item
                    vis_pos = atis_raw.find(content_item)+len(content_item)
                elif content_item.find('/') != -1:
                    if 2 <= len(content_item.split('/')[0]) <= 3: atis_content['temp']=content_item.split('/')[0]
                    if 2 <= len(content_item.split('/')[1]) <= 3: atis_content['dewpt']=content_item.split('/')[1]
                    temp_pos = atis_raw.find(content_item)
                elif content_item.startswith('A') and len(content_item)==5 and content_item[1:4].isnumeric(): atis_content['altimeter'] = content_item
                elif content_item =='.': break
            atis_content['clouds'] = str(atis_raw[vis_pos:temp_pos]).strip()
            atis_content['notams'] = atis_raw.split('NOTAMS...')[1].strip()
            atis_content['airport_conditions'] = atis_raw[atis_raw.find(')')+2:atis_raw.find('NOTAMS...')].strip()
        except Exception as e2: print(f'Exception in determining ATIS content... {e2}')