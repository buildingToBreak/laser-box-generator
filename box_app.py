import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ezdxf

# ==========================================
# LOGIC: GENERATION ALGORITHMS
# ==========================================

def setup_dxf():
    doc = ezdxf.new()
    doc.header['$INSUNITS'] = 4  # Millimeters
    msp = doc.modelspace()
    doc.layers.new(name='CUT', dxfattribs={'color': 1})  # Red
    doc.layers.new(name='FOLD', dxfattribs={'color': 5}) # Blue
    return doc, msp

def add_line(msp, p1, p2, layer):
    msp.add_line(p1, p2, dxfattribs={'layer': layer})

def add_poly(msp, points, layer, closed=False):
    msp.add_lwpolyline(points, dxfattribs={'layer': layer, 'closed': closed})

# --- TYPE 1: ONE-PIECE GLUED (FIXED TABS) ---
def generate_one_piece(l, w, h, pad, thick, filename):
    L, W, H = l + (pad*2), w + (pad*2), h + (pad*2)
    doc, msp = setup_dxf()

    # Base (Blue Loop)
    add_poly(msp, [(0,0), (L,0), (L,W), (0,W)], 'FOLD', closed=True)

    # Front Wall (U-Shape Cut)
    # Attaches to (0,0)-(L,0). We cut the other 3 sides.
    add_poly(msp, [(0,0), (0,-H), (L,-H), (L,0)], 'CUT', closed=False)

    # Back Wall (Sides Only)
    # Attaches to (0,W)-(L,W) (Base) AND (0,W+H)-(L,W+H) (Lid).
    # So we only CUT the left and right vertical edges.
    add_line(msp, (0,W), (0,W+H), 'CUT')   
    add_line(msp, (L,W), (L,W+H), 'CUT')   
    add_line(msp, (0,W+H), (L,W+H), 'FOLD') # Hinge to Lid

    # Side Walls (Outer Edge Only)
    # The top/bottom edges connect to Tabs, so they must be FOLDS, not CUTS.
    # Left Wall Outer Edge
    add_line(msp, (-H,0), (-H,W), 'CUT')
    # Right Wall Outer Edge
    add_line(msp, (L+H,0), (L+H,W), 'CUT')

    # Tabs (U-Shape Cuts attached to Side Walls)
    offset, tab_d = 3, 15
    
    # Left Top Tab
    add_poly(msp, [(-H,W), (-H+offset,W+tab_d), (0-offset,W+tab_d), (0,W)], 'CUT', closed=False)
    add_line(msp, (-H,W), (0,W), 'FOLD') # Hinge to Side Wall
    
    # Left Bottom Tab
    add_poly(msp, [(-H,0), (-H+offset,-tab_d), (0-offset,-tab_d), (0,0)], 'CUT', closed=False)
    add_line(msp, (-H,0), (0,0), 'FOLD') # Hinge to Side Wall

    # Right Top Tab
    add_poly(msp, [(L,W), (L+offset,W+tab_d), (L+H-offset,W+tab_d), (L+H,W)], 'CUT', closed=False)
    add_line(msp, (L,W), (L+H,W), 'FOLD') # Hinge to Side Wall

    # Right Bottom Tab
    add_poly(msp, [(L,0), (L+offset,-tab_d), (L+H-offset,-tab_d), (L+H,0)], 'CUT', closed=False)
    add_line(msp, (L,0), (L+H,0), 'FOLD') # Hinge to Side Wall

    # Lid
    lid_depth = W + (thick * 0.5)
    flap_h, inset = min(30, H * 0.6), 3
    lid_tl, lid_tr = (0, W+H+lid_depth), (L, W+H+lid_depth)
    
    # Lid Sides
    add_line(msp, (0,W+H), lid_tl, 'CUT')
    add_line(msp, (L,W+H), lid_tr, 'CUT')
    add_line(msp, lid_tl, lid_tr, 'FOLD')
    
    # Flap
    add_poly(msp, [lid_tl, (inset, W+H+lid_depth+flap_h), (L-inset, W+H+lid_depth+flap_h), lid_tr], 'CUT', closed=False)

    doc.saveas(filename)

# --- TYPE 2: SHOEBOX (FIXED TABS) ---
def generate_shoebox(l, w, h, pad, thick, lid_h, filename):
    base_L, base_W, base_H = l+(pad*2), w+(pad*2), h+(pad*2)
    doc, msp = setup_dxf()

    def draw_tray(sx, sy, bw, bl, bh):
        # Floor (Blue Loop)
        add_poly(msp, [(sx,sy), (sx+bl,sy), (sx+bl,sy+bw), (sx,sy+bw)], 'FOLD', closed=True)
        
        # Top/Bottom Walls (No Tabs attached to these, so they are U-Shape Cuts)
        # Top Wall
        add_poly(msp, [(sx, sy+bw), (sx, sy+bw+bh), (sx+bl, sy+bw+bh), (sx+bl, sy+bw)], 'CUT', closed=False)
        # Bottom Wall
        add_poly(msp, [(sx, sy), (sx, sy-bh), (sx+bl, sy-bh), (sx+bl, sy)], 'CUT', closed=False)
        
        # Left/Right Walls (Tabs attach here, so ONLY cut the outer vertical edge)
        # Left Wall Outer Edge
        add_line(msp, (sx-bh, sy), (sx-bh, sy+bw), 'CUT')
        # Right Wall Outer Edge
        add_line(msp, (sx+bl+bh, sy), (sx+bl+bh, sy+bw), 'CUT')
        
        # Tabs (Attached to Left/Right Walls)
        tab_d = min(bh*0.8, 20)
        
        # Left Top
        add_poly(msp, [(sx-bh,sy+bw), (sx-bh+3,sy+bw+tab_d), (sx-3,sy+bw+tab_d), (sx,sy+bw)], 'CUT', closed=False)
        add_line(msp, (sx-bh,sy+bw), (sx,sy+bw), 'FOLD')
        # Left Bottom
        add_poly(msp, [(sx-bh,sy), (sx-bh+3,sy-tab_d), (sx-3,sy-tab_d), (sx,sy)], 'CUT', closed=False)
        add_line(msp, (sx-bh,sy), (sx,sy), 'FOLD')
        
        # Right Top
        add_poly(msp, [(sx+bl,sy+bw), (sx+bl+3,sy+bw+tab_d), (sx+bl+bh-3,sy+bw+tab_d), (sx+bl+bh,sy+bw)], 'CUT', closed=False)
        add_line(msp, (sx+bl,sy+bw), (sx+bl+bh,sy+bw), 'FOLD')
        # Right Bottom
        add_poly(msp, [(sx+bl,sy), (sx+bl+3,sy-tab_d), (sx+bl+bh-3,sy-tab_d), (sx+bl+bh,sy)], 'CUT', closed=False)
        add_line(msp, (sx+bl,sy), (sx+bl+bh,sy), 'FOLD')

    draw_tray(0, 0, base_W, base_L, base_H)
    gap = 2
    lid_L, lid_W = base_L + (thick*2) + gap, base_W + (thick*2) + gap
    draw_tray(base_L + base_H*2 + lid_h*2 + 50, 0, lid_W, lid_L, lid_h)
    doc.saveas(filename)

# --- TYPE 3: MAILER (WITH KERF COMP) ---
def generate_mailer(l, w, h, pad, thick, filename):
    L, W, H = l+(pad*2), w+(pad*2), h+(pad*2)
    T = thick
    kerf = 0.1 

    doc, msp = setup_dxf()

    add_poly(msp, [(0,0), (L,0), (L,W), (0,W)], 'FOLD', closed=True)

    # Slots
    slot_margin, slot_w, slot_len = 2.0, (T + 0.5 - kerf), 20
    msp.add_lwpolyline([(slot_margin, W/2 - slot_len/2), (slot_margin, W/2 + slot_len/2), 
                        (slot_margin + slot_w, W/2 + slot_len/2), (slot_margin + slot_w, W/2 - slot_len/2)], 
                        dxfattribs={'layer':'CUT', 'closed':True})
    msp.add_lwpolyline([(L - slot_margin, W/2 - slot_len/2), (L - slot_margin, W/2 + slot_len/2), 
                        (L - slot_margin - slot_w, W/2 + slot_len/2), (L - slot_margin - slot_w, W/2 - slot_len/2)], 
                        dxfattribs={'layer':'CUT', 'closed':True})

    add_line(msp, (0,-H), (L,-H), 'CUT')
    pts_lear = [(0,-H), (-H+T,-H), (-H+T,-T), (0,-T)]
    add_poly(msp, pts_lear, 'CUT', closed=False)
    pts_rear = [(L,-H), (L+H-T,-H), (L+H-T,-T), (L,-T)]
    add_poly(msp, pts_rear, 'CUT', closed=False)
    add_line(msp, (0,0), (0,-H), 'FOLD')
    add_line(msp, (L,0), (L,-H), 'FOLD')

    add_line(msp, (0,W+H), (L,W+H), 'FOLD') 
    pts_blear = [(0,W+H), (-H+T,W+H), (-H+T,W+T), (0,W+T)]
    add_poly(msp, pts_blear, 'CUT', closed=False)
    add_line(msp, (0,W), (0,W+H), 'FOLD') 
    pts_brear = [(L,W+H), (L+H-T,W+H), (L+H-T,W+T), (L,W+T)]
    add_poly(msp, pts_brear, 'CUT', closed=False)
    add_line(msp, (L,W), (L,W+H), 'FOLD')

    rim_x = -H
    add_line(msp, (rim_x, 0), (rim_x, W), 'FOLD') 
    add_line(msp, (0,W), (rim_x, W), 'CUT')
    add_line(msp, (0,0), (rim_x, 0), 'CUT')
    
    iw_len = H - 1
    inner_end_x = rim_x - iw_len
    tab_reach, tab_base_w = slot_margin + 15, 18 + kerf
    
    pts_l = [
        (rim_x, W), (inner_end_x, W), (inner_end_x, W/2 + tab_base_w/2),
        (inner_end_x - tab_reach, W/2 + tab_base_w/2 - 2), 
        (inner_end_x - tab_reach, W/2 - tab_base_w/2 + 2), 
        (inner_end_x, W/2 - tab_base_w/2), (inner_end_x, 0), (rim_x, 0)
    ]
    add_poly(msp, pts_l, 'CUT', closed=False)

    rim_xr = L + H
    add_line(msp, (rim_xr, 0), (rim_xr, W), 'FOLD')
    add_line(msp, (L,W), (rim_xr,W), 'CUT')
    add_line(msp, (L,0), (rim_xr,0), 'CUT')
    
    inner_end_xr = rim_xr + iw_len
    pts_r = [
        (rim_xr, W), (inner_end_xr, W), (inner_end_xr, W/2 + tab_base_w/2),
        (inner_end_xr + tab_reach, W/2 + tab_base_w/2 - 2),
        (inner_end_xr + tab_reach, W/2 - tab_base_w/2 + 2),
        (inner_end_xr, W/2 - tab_base_w/2), (inner_end_xr, 0), (rim_xr, 0)
    ]
    add_poly(msp, pts_r, 'CUT', closed=False)

    lid_h = W
    wing_clearance = (2 * T) + 1
    wing_w = H - wing_clearance
    add_line(msp, (0,W+H), (0,W+H+lid_h), 'FOLD')
    pts_lw = [(0, W+H), (-wing_w, W+H+5), (-wing_w, W+H+lid_h-5), (0, W+H+lid_h)]
    add_poly(msp, pts_lw, 'CUT', closed=False)
    add_line(msp, (L,W+H), (L,W+H+lid_h), 'FOLD')
    pts_rw = [(L, W+H), (L+wing_w, W+H+5), (L+wing_w, W+H+lid_h-5), (L, W+H+lid_h)]
    add_poly(msp, pts_rw, 'CUT', closed=False)

    tuck_h = min(40, H * 0.7)
    add_line(msp, (0,W+H+lid_h), (L,W+H+lid_h), 'FOLD')
    pts_tuck = [(0, W+H+lid_h), (5, W+H+lid_h+tuck_h), (L-5, W+H+lid_h+tuck_h), (L, W+H+lid_h)]
    add_poly(msp, pts_tuck, 'CUT', closed=False)

    doc.saveas(filename)

# --- TYPE 4: ECO PACKING ---
def generate_eco_packing(filename, sheet_w_inch, sheet_h_inch):
    doc, msp = setup_dxf()
    inch_to_mm = 25.4
    total_w = sheet_w_inch * inch_to_mm
    total_h = sheet_h_inch * inch_to_mm
    shred_l = 1.0 * inch_to_mm
    shred_w = 0.25 * inch_to_mm
    cols = int(sheet_w_inch / 1.0)
    rows = int(sheet_h_inch / 0.25)
    for i in range(cols + 1):
        x = i * shred_l
        if x <= total_w:
            add_line(msp, (x, 0), (x, total_h), 'CUT')
    for j in range(rows + 1):
        y = j * shred_w
        if y <= total_h:
            add_line(msp, (0, y), (total_w, y), 'CUT')
    doc.saveas(filename)

# ==========================================
# GUI INTERFACE
# ==========================================

# Descriptions Map (Updated)
DESCRIPTIONS = {
    "one_piece": "A classic 'Pizza Box' style with a hinged lid.\n\nGood For: General purpose storage, lightweight items.\nAssembly: Requires GLUE on the 4 corner tabs.",
    "shoebox": "Two separate pieces (Base + Telescoping Lid).\n\nGood For: Shoes or taller items.\nAssembly: Requires GLUE on all tabs.",
    "mailer": "Professional 'Subscription Box' style. (RETF)\n\nGood For: Shipping. Very strong double-walls.\nAssembly: NO GLUE required. Self-locking tabs snap into place.",
    "eco_shreds": "Turns scrap cardboard into Packing Material.\n\nGood For: Recycling waste into free bubble-wrap replacement.\nOutput: Cuts a grid of 1\" x 0.25\" strips."
}

def update_ui(*args):
    mode = box_type.get()
    
    # Update Description Text
    lbl_desc.config(text=DESCRIPTIONS.get(mode, ""))

    # UI Logic
    lbl_lid.grid_remove()
    entry_lid.grid_remove()
    
    if mode == "eco_shreds":
        lbl_l.config(text="Sheet Width (inch):")
        lbl_w.config(text="Sheet Height (inch):")
        lbl_h.grid_remove(); entry_h.grid_remove()
        lbl_pad.grid_remove(); entry_pad.grid_remove()
        lbl_thick.grid_remove(); entry_thick.grid_remove()
    else:
        lbl_l.config(text="Item Length (mm):")
        lbl_w.config(text="Item Width (mm):")
        lbl_h.grid(); entry_h.grid()
        lbl_pad.grid(); entry_pad.grid()
        lbl_thick.grid(); entry_thick.grid()
        
        if mode == "shoebox":
            lbl_lid.grid(); entry_lid.grid()

def run_generator():
    try:
        mode = box_type.get()
        l = float(entry_l.get())
        w = float(entry_w.get())
        
        default_name = f"box_{mode}.dxf"
        if mode == "eco_shreds": default_name = "eco_shreds.dxf"

        file_path = filedialog.asksaveasfilename(defaultextension=".dxf", initialfile=default_name, title="Save Design")
        if not file_path: return 

        if mode == "eco_shreds":
            generate_eco_packing(file_path, l, w)
            messagebox.showinfo("Success", f"Packing Shreds saved!\nSheet: {l}x{w} inches")
        else:
            h = float(entry_h.get())
            pad = float(entry_pad.get())
            thick = float(entry_thick.get())

            if mode == "one_piece": generate_one_piece(l, w, h, pad, thick, file_path)
            elif mode == "shoebox": generate_shoebox(l, w, h, pad, thick, float(entry_lid.get()), file_path)
            elif mode == "mailer": generate_mailer(l, w, h, pad, thick, file_path)
            
            messagebox.showinfo("Success", f"Saved: {file_path}")
        
    except Exception as e:
        messagebox.showerror("Error", f"Invalid Input.\n{e}")

root = tk.Tk()
root.title("Box Generator Ultimate")
root.geometry("400x650")

style = ttk.Style()
style.configure("Bold.TLabel", font=("Arial", 10, "bold"))

frame = ttk.Frame(root, padding=20)
frame.pack()

# Inputs
lbl_l = ttk.Label(frame, text="Item Length (mm):"); lbl_l.grid(row=0, column=0, sticky="e", pady=5)
entry_l = ttk.Entry(frame); entry_l.grid(row=0, column=1)

lbl_w = ttk.Label(frame, text="Item Width (mm):"); lbl_w.grid(row=1, column=0, sticky="e", pady=5)
entry_w = ttk.Entry(frame); entry_w.grid(row=1, column=1)

lbl_h = ttk.Label(frame, text="Item Height (mm):"); lbl_h.grid(row=2, column=0, sticky="e", pady=5)
entry_h = ttk.Entry(frame); entry_h.grid(row=2, column=1)

lbl_pad = ttk.Label(frame, text="Padding (mm):"); lbl_pad.grid(row=3, column=0, sticky="e", pady=5)
entry_pad = ttk.Entry(frame); entry_pad.insert(0, "5"); entry_pad.grid(row=3, column=1)

lbl_thick = ttk.Label(frame, text="Thickness (mm):"); lbl_thick.grid(row=4, column=0, sticky="e", pady=5)
entry_thick = ttk.Entry(frame); entry_thick.insert(0, "3"); entry_thick.grid(row=4, column=1)

lbl_lid = ttk.Label(frame, text="Lid Depth (mm):"); lbl_lid.grid(row=5, column=0, sticky="e", pady=5)
entry_lid = ttk.Entry(frame); entry_lid.insert(0, "40"); entry_lid.grid(row=5, column=1)

ttk.Separator(root, orient='horizontal').pack(fill='x', padx=20, pady=10)

# Mode Selection
box_type = tk.StringVar(value="one_piece")
box_type.trace("w", update_ui)

ttk.Radiobutton(root, text="One-Piece (Glued)", variable=box_type, value="one_piece").pack(anchor="w", padx=40)
ttk.Radiobutton(root, text="Shoebox (Telescoping)", variable=box_type, value="shoebox").pack(anchor="w", padx=40)
ttk.Radiobutton(root, text="Mailer (No Glue)", variable=box_type, value="mailer").pack(anchor="w", padx=40)
ttk.Radiobutton(root, text="Eco Packing (Shredder)", variable=box_type, value="eco_shreds").pack(anchor="w", padx=40)

# Description Label
lbl_desc = ttk.Label(root, text="", foreground="#555", wraplength=350, justify="left", padding=10)
lbl_desc.pack(pady=10)

update_ui() # Init
ttk.Button(root, text="GENERATE DXF", command=run_generator).pack(pady=10)
root.mainloop()