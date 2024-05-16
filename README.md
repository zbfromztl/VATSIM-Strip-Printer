Version: Python 3.11.3
# Overview:
  * WIP flight progress strips for [vZTL](https://ztlartcc.org), on the [VATSIM Network](https://vatsim.net).
  * Code Author: Simon Heck [(Simon-Heck)](https://github.com/Simon-Heck)
  * Printer Technician: Joey Costello [(JoeyTheDev1)](https://github.com/JoeyTheDev1/)
  * Technical Advisor: [Zack B)](https://github.com/zbfromztl)

# In Progress:
  * Electronic Flight Strip Transfer System (EFSTS) / Networking
  * Print all the memory aid things
  * Add more comments and documentation

# To do:
  * Make starting text prompts easier to understand
  * Don't print VFR strips/Don't print amended VFR strips?
  * Clean up Code for new airports. Add new airports. Store in JSON?
  * Add visual flag to scanner elements. Build network for scanner.
  * Add GUI elements to the program

# Features:
  * Barcode with pilot VATSIM CID on ATL strips (for strip scanning)
  * Truncates route to first 3 waypoints
  * Prints only remarks after RMK/
  * Multi-threaded to simultaneously listen for user input, update JSON data, and scan for new departures
  * Print Hazardous Weather Information
  * Log airport delays & limited logic to determine cause.
  * Data refresh syncs with VATSIM data refresh cycle
  * GI command to print GI stuff.
  * Others

# Hardware:
  * [ZebraZD410 Printer](https://www.zebra.com/us/en/products/spec-sheets/printers/desktop/zd410.html)
  * [1x8 Flight Strips](https://bocathermal.txdesign.com/thermal-general-admission-ticket/details/boca-flight-strip-1-x-8/)
  * Computer with [python](https://www.python.org/downloads/) 3.1 or greater
  * Install [Flight Progress Strip font](https://www.dropbox.com/s/lqtvsngjdjonngv/Flight-Strip-Printer.ttf?dl=0) to the Zebra ZD410 printer.


# How to Run:
  * Aquire the following modules:
```
pip install zpl
pip install zebra
pip install requests
```
Run python on [main.py](src/main.py). For example:
```
python main.py
```

# Strip Alignment [To Do]:
 * Strips require manual alignment prior to first print.
 1. Launch program. Type "Align" after selecting positions.
 2. Move "line" on alignment strip to mouth of printer. 

# Commands:
 * Memoryaids - Prints several memory aids, including STOP and NO LUAW.
 * Times - Prints the current taxi times & associated callsigns.
 * Purge - Clears queue count for delay reporting
 * DROP (Callsign) - Removes cid from queue counter.
 * Align - Prints blank strip with singular line. Align line with mouth of printer to achieve serenity.
 * FRC (ACID) or SR (ACID) - Prints strip with all flight plan info.
 * GI (message) - Prints a strip of inputted text.

# ARMT commands (ATL only)
 * countproposals - Counts all the aircraft on the ground and organizes it based on filed departure gate.
 * ALL north/center/south - Amends the departure split.
 * {departure} OR {gate} north/center/south - Amends the departure split (to determine queue count).
 * worst queue or queue count - Generates length of line for departure if all aircraft on the ground were holding short of their runway, according to the departure split.
 * FTD - enables/disables runway 10/28
 * display or current - shows the current split

 # Configuring the Positions File:
 * Start with Facility
    - Next in heirarchy are the position(s) within the facililty.
      - Within each position, list the "airports" to watch out for. Must be found in airports.json.
      - Type of position (Determines "how far out" the program is looking for each airport & other additional functions, such as strip scanning): CD (Clearance Delivery), GC (Ground Control), LC (Local Control), TAR (Feeder), DR (Departure), TMU, COMBINED 
      - Auto_Print_strips: true/false
      - hasBarcode (Departure Strips Only): true/false
      - stripType: Both/Departure/Arrival
 * Example setups are already included in program.