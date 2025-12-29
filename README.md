LASER CUT BOX GENERATOR


A Python application that generates DXF files for custom packaging. Designed for direct import into LightBurn and for diode lasers (such as the Creality Falcon 2 22-watt, used in the creation of this application)

KEY FEATURES

1. Dynamic Interface: The window changes automatically to show only the inputs needed for the selected box type, as well as brief descriptions.
2. Smart Geometry:
   - Kerf Compensation: The "Mailer Box" mode automatically adjusts tab and slot sizes by 0.1mm to ensure a tight fit, compensating for the width of the laser beam.
   - Continuous Paths: Uses continuous loops for cutting lines to prevent "open shape" errors.
   - No Double-Cuts: Wall geometry is designed so that cut lines never overlap fold lines, preventing the box from being cut apart.
   - The mailer box design has tabs that remain connected to the stock cardboard equal to the width of the cardboard to allow for better
performance when cutting more than 1 layers at a time.
3. Automatic Layering: The exported DXF files have two distinct layers:
   - Red Layer: For cutting.
   - Blue Layer: For scoring/folding.
4. Standalone Application: The provided .exe file runs on any Windows computer without needing to install Python.


BOX MODES

1. One-Piece Box (Glued)
   - Style: Classic hinged lid with side flaps (similar to a pizza box).
   - Assembly: Requires glue on the 4 corner tabs.
   - Best For: General storage, lightweight items, rapid assembly.

2. Shoebox (Telescoping)
   - Style: Two separate pieces (Base and Lid). The software automatically calculates the lid size to slide perfectly over the base, accounting for material thickness.
   - Assembly: Requires glue on the corner tabs of both the base and lid.
   - Best For: Shoes, heavy items, or projects requiring double-wall strength.

3. Mailer Box (No Glue)
   - Style: Roll-End Tuck-Front (RETF). This is the standard style for professional shipping and subscription boxes.
   - Assembly: No glue required. The side walls roll over and lock into the base using engineered tabs (tabs are longer than the thickness of the stock for better structural integrity.
   - Best For: E-commerce, shipping, professional presentation.

4. Eco Packing (Shredder)
   - Style: Variable Grid Cut.
   - Function: Converts scrap cardboard sheets into professional packing material.
   - Output: Creates a grid of 1 inch by 0.25 inch flexible strips.


INSTALLATION AND USAGE
----------------------

OPTION A
1. Download the "box_app.exe" file from the Releases section of this repository.
2. Double-click the file to run it.
3. Select your box type, enter the dimensions, and click "Generate".

OPTION B
1. Clone this repository to your computer.
2. Install the required libraries using the command: 
   pip install -r requirements.txt
3. Run the script using the command:
   python box_app.py


RECOMMENDED LASER SETTINGS

These settings are tested on a Creality Falcon 2 (22W) using 3mm Single-Wall Corrugated Cardboard.

RED LAYER (CUT)
- Mode: Line
- Speed: 1400 mm/min
- Power: 80%
- Air Assist: HIGH (prevent charring)

BLUE LAYER (FOLD)
- Mode: Line
- Speed: 4000 mm/min
- Power: 30%
- Using the perforation feature, and setting to 2mm cuts 5-8mm gaps with red layer settings is also recommended as an alternative
- Air Assist: LOW or OFF

SAFETY WARNING: Cardboard is highly flammable. Never leave the laser unattended while operating.


BUILDING THE EXE

If you modify the Python code and want to rebuild the standalone executable file:

1. Open your command prompt or terminal.
2. Run the following command:
   python -m PyInstaller --noconsole --onefile box_app.py
3. The new executable file will be created in the "dist" folder.


LICENSE

This project is open-source. You are free to modify, and use this software for personal or commercial packaging.
