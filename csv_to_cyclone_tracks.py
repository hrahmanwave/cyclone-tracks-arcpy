import arcpy, os

arcpy.env.overwriteOutput = True

in_csv = r"input_Directory"
out_folder = r"C:\Users\USER\Documents\ArcGIS"
gdb_name = "CycloneTracks.gdb"

x_field, y_field = "Lon", "Lat"
line_field = "StormID"
time_field = "DatetimeUTC_str_new"  # if exists

gdb = os.path.join(out_folder, gdb_name)
if not arcpy.Exists(gdb):
    arcpy.CreateFileGDB_management(out_folder, gdb_name)
arcpy.env.workspace = gdb

sr = arcpy.SpatialReference(4326)

xy_layer = "track_xy"
pts = os.path.join(gdb, "Track_Points")
pts2 = os.path.join(gdb, "Track_Points_2plus")
pts_sorted = os.path.join(gdb, "Track_Points_Sorted")
lines = os.path.join(gdb, "Cyclone_Tracks")

# 1) CSV -> points
arcpy.MakeXYEventLayer_management(in_csv, x_field, y_field, xy_layer, sr)
arcpy.CopyFeatures_management(xy_layer, pts)

# 2) Add Seq
fields = [f.name for f in arcpy.ListFields(pts)]
if "Seq" not in fields:
    arcpy.AddField_management(pts, "Seq", "LONG")
arcpy.CalculateField_management(pts, "Seq", "!OBJECTID!", "PYTHON_9.3")

# 3) Keep only StormIDs that have >=2 points (NO JOIN SQL)
freq = os.path.join(gdb, "StormID_Freq")
arcpy.Frequency_analysis(pts, freq, [line_field])

stormids_2plus = []
with arcpy.da.SearchCursor(freq, [line_field, "FREQUENCY"]) as cur:
    for sid, n in cur:
        if n >= 2 and sid not in (None, ""):
            stormids_2plus.append(sid)

if not stormids_2plus:
    raise RuntimeError("No StormID found with >=2 points. Check your StormID field.")

# Build IN() SQL safely in chunks (ArcMap has expression-length limits)
arcpy.MakeFeatureLayer_management(pts, "pts_lyr")
stormid_field_sql = arcpy.AddFieldDelimiters("pts_lyr", line_field)

def select_in_chunks(values, chunk_size=900):
    arcpy.SelectLayerByAttribute_management("pts_lyr", "CLEAR_SELECTION")
    first = True
    for i in range(0, len(values), chunk_size):
        chunk = values[i:i+chunk_size]
        # escape single quotes
        chunk = [v.replace("'", "''") for v in chunk]
        in_list = ",".join(["'{}'".format(v) for v in chunk])
        where = "{} IN ({})".format(stormid_field_sql, in_list)
        arcpy.SelectLayerByAttribute_management(
            "pts_lyr",
            "NEW_SELECTION" if first else "ADD_TO_SELECTION",
            where
        )
        first = False

select_in_chunks(stormids_2plus)

arcpy.CopyFeatures_management("pts_lyr", pts2)

# 4) Sort
fields2 = [f.name for f in arcpy.ListFields(pts2)]
sort_fields = [[line_field, "ASCENDING"]]
if time_field in fields2:
    sort_fields.append([time_field, "ASCENDING"])
sort_fields.append(["Seq", "ASCENDING"])
arcpy.Sort_management(pts2, pts_sorted, sort_fields)

# 5) Points -> Lines (by StormID)
sort_for_lines = time_field if time_field in fields2 else "Seq"
arcpy.PointsToLine_management(pts_sorted, lines, line_field, sort_for_lines)

print("DONE ✅ Output lines:", lines)
print("StormIDs with >=2 points:", len(stormids_2plus))