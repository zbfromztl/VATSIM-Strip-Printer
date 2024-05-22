import requests
from Printer import Printer
import time
import json
import pickle
__author__ = "Simon Heck"

class DataCollector:
    def __init__(self, json_url:str, control_area:str, printer:Printer, cached_printed_departures:list, cached_departures_file_path:str, positions: dict, airports:dict) -> None:
        self.callsign_list = {}
        self.json_url = json_url
        self.control_area = control_area
        self.printer = printer
        self.printed_callsigns = cached_printed_departures
        self.cached_departures_file_path = cached_departures_file_path
        # TODO Load from saved JSON File
        self.control_area_dict = positions['facilities']
        self.fence = positions['fence_data']
        self.airports = airports

    def check_for_updates(self):
        self.update_json(self.json_url)
        self.scan_pilots()

    def get_json(self):
        return self.json_file
    
    def get_callsign_list(self):
        return self.callsign_list
    
    def add_callsign_to_dep_list(self, pilot_callsign:str, new_pilot_data_associated_with_callsign:dict, strip_type):
        new_pilot_route:str = new_pilot_data_associated_with_callsign['flight_plan']['route']
        if '+' in new_pilot_route:
            new_pilot_route = new_pilot_route.replace('+', '')
        
        if pilot_callsign in self.callsign_list:
            current_pilot_route:str = self.callsign_list[pilot_callsign]['flight_plan']['route']
            if '+' in current_pilot_route:
                current_pilot_route = current_pilot_route.replace('+', '')

            if new_pilot_route != current_pilot_route:
                # pilot has received a reroute
                self.callsign_list[pilot_callsign] = new_pilot_data_associated_with_callsign
                self.printer.print_callsign_data(self.callsign_list[pilot_callsign], pilot_callsign, self.control_area, strip_type)
        else:
            # new_pilot_data_associated_with_callsign['flight_plan']['route'] = new_pilot_route
            self.callsign_list[pilot_callsign] = new_pilot_data_associated_with_callsign

    def scan_for_new_aircraft_automatic(self):
        while(self.control_area['auto_Print_Strips']): #This used to be while(True)
            callsign_table = self.get_callsign_list()
            # TODO, lock callsign list to leep them synced
            for callsign_to_print in callsign_table:
                if callsign_to_print not in self.printed_callsigns:
                    
                    #What field should we check for? Departing or Arriving?
                    lookfor = self.control_area['stripType']
                    if str(lookfor) == 'both':
                        fp_data = callsign_table.get(callsign_to_print)
                        if fp_data['flight_plan']['departure'] in tuple(self.control_area['airports']):
                            lookfor = 'departure'
                        elif fp_data['flight_plan']['arrival'] in tuple(self.control_area['airports']):
                            lookfor = 'arrival'

                    self.printer.print_callsign_data(callsign_table.get(callsign_to_print), callsign_to_print, self.control_area, lookfor)
                    self.printed_callsigns.append(callsign_to_print)
                # auto_update cached callsigns
            file = open(self.cached_departures_file_path, 'wb')
            pickle.dump(self.printed_callsigns, file)
            file.close()
            time.sleep(1)

    def get_callsign_data(self, callsign) -> dict:
        if callsign not in self.callsign_list:
            return None
        else:
            return self.callsign_list.get(callsign)
    
    def in_geographical_region_wip(self, control_area:str, airport:str, airplane_lat_long:tuple) -> bool:
        airports_dict = self.airports['airfields']
        control_area_type = control_area["type"].upper()

        #create fence
        #Airport NW Lat_Long point
        northern_latitude = airports_dict.get(airport)["LAT"] + self.fence[control_area_type]
        western_longitude = airports_dict.get(airport)["LON"] - self.fence[control_area_type]
        #Airport SE Lat_long point
        southern_latitude = airports_dict.get(airport)["LAT"] - self.fence[control_area_type]
        eastern_longitude = airports_dict.get(airport)["LON"] + self.fence[control_area_type]

        # airplane lat_long position
        airplane_lat, airplane_long = airplane_lat_long
    
        if (airplane_lat < northern_latitude and airplane_lat > southern_latitude) and (airplane_long > western_longitude and airplane_long < eastern_longitude):
            return True
        # else:
        #     return False
        
    def scan_pilots(self):
        connected_pilots = self.json_file['pilots']
        #lookupdefinitions = {"CD":"departure","GC":"departure","LC":"departure","TAR":"arrival","DR":"departure","COMBINED":"both"}

        # Determine what aircraft have disconnected and alert someone so the strip can be retrieved.
        disconnected = []
        for departure in self.callsign_list:
            disconnected.append(departure)

        # Interpreting/Filtering JSON Data
        for i in range(len(connected_pilots)):
            #What field should we check for? Departing or Arriving?
            lookfor = self.control_area['stripType']
            # pilot at index i information
            current_pilot = connected_pilots[i]
            #If they're connected, remove the callsign from the "disconnected" list
            if current_pilot['callsign'] in disconnected:
                disconnected.remove(current_pilot['callsign'].upper())
            
            try:
                if str(lookfor) == 'both':
                    #print(f"checking to see if {current_pilot['flight_plan']['departure']} is in {self.control_area['airports']}")
                    if current_pilot['flight_plan']['departure'] in tuple(self.control_area['airports']):
                        lookfor = 'departure'
                    elif current_pilot['flight_plan']['arrival'] in tuple(self.control_area['airports']):
                        lookfor = 'arrival'
                if lookfor != 'both':
                    lat_long_tuple = (current_pilot['latitude'], current_pilot['longitude'])
                    pilot_callsign = current_pilot['callsign'].upper()
                    pilot_departure_airport = current_pilot['flight_plan'][lookfor]
                    if pilot_departure_airport in tuple(self.control_area['airports']) and self.in_geographical_region_wip(self.control_area, pilot_departure_airport, lat_long_tuple):
                        # Save callsign of pilot and associated JSON Info
                        # to access, use: self.callsign_list.get(**callsign**)
                        # that will return the portion of the JSON with all of the pilot's info from when the system added them(flightplan, CID, etc.)
                        self.add_callsign_to_dep_list(pilot_callsign, current_pilot, lookfor)

                    elif self.requires_removal(pilot_callsign, pilot_departure_airport, self.control_area, lat_long_tuple):
                        self.remove_callsign_from_lists(pilot_callsign)

            except TypeError as e1:
                pass        
            except Exception as e2:
                print(e2)
            
        for user in disconnected:
            try:
                self.remove_callsign_from_lists(user)
                print(f"FLIGHT PLAN FOR {user} HAS TIMED OUT.")
            except:
                continue
        

    def requires_removal(self, callsign, filed_dep, airports_list, lat_long): #This is to process when aircraft leave the area of jurisdiction who have previously had strips printed out.
        result = False
        if filed_dep in tuple(self.control_area['airports']) and callsign in self.callsign_list:
            if self.in_geographical_region_wip(airports_list, filed_dep, lat_long):
                pass
            else:
                result = True
        return result
        

    def remove_callsign_from_lists(self, callsign_to_remove):
        try:
            self.callsign_list.pop(callsign_to_remove)
            if callsign_to_remove in self.printed_callsigns:
                self.printed_callsigns.remove(callsign_to_remove)
        except:
            print(f'Error removing {callsign_to_remove}: not found in stored lists.')

    def update_json(self, json_url):
        r = requests.get(json_url)
        self.json_file = r.json()