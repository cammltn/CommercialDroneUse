# Camille Milton
# Geog 666
# Final Project
# 15 August 2021


# Data Production Creation

#######################

# Import modules
import arcpy
from arcpy import env
import os
import PyPDF2


# Set workspace
arcpy.env.workspace = "Y:/CMilton_Final"

#### Load all data ####

# Load boundaries shapefile
arcpy.MakeFeatureLayer_management("Y:/CMilton_Final/Boundaries.shp", "Boundaries_lyr")

# Load raster layers
arcpy.MakeRasterLayer_management("Y:/CMilton_Final/TechPark_dsm.tif", "tmpLyrDsm") #dsm
arcpy.MakeRasterLayer_management("Y:/CMilton_Final/TechPark_dtm.tif", "tmpLyrDtm") #dtm
arcpy.MakeRasterLayer_management("Y:/CMilton_Final/TechPark_orthomosaic.tif") #orthomosaic


# Set environment settings
env.workspace = "Y:/CMilton_Final"

#######################

#### Raster Calculation ####
# Complete a raster calculation on the dsm and dtm layers

# Create variable for each layer
inRaster1 = "TechPark_dsm.tif"
inRaster2 = "TechPark_dtm.tif"

# Check out the 3D Analyst extension
arcpy.CheckOutExtension("3D")

# Execute calculation
arcpy.Minus_3d(inRaster1, inRaster2, "Y:/CMilton_Final/TechRcalc.tif")

arcpy.MakeRasterLayer_management("Y:/CMilton_Final/TechRcalc.tif") #output                   

#######################



#### Reclassify ####

# Reclassify the new raster layer to better identify buildings

# Import modules for tool
from arcpy.sa import *

# Set environment settings
env.workspace = "Y:/CMilton_Final"

# Set local variables
inRaster = "Y:/CMilton_Final/TechRcalc.tif"
reclassField = "VALUE"
# Reclassify Values to split at 7 as the lowest value that could be identified as a building
remapString = "0 7 1; 7.01 28 2"
# Store output
outRaster = "Y:/CMilton_Final/reclass"

# Run reclassification
arcpy.Reclassify_3d(inRaster, reclassField, remapString, outRaster, "DATA")



#######################

#### Raster to Polygon ####
# Create a polygon layer from the reclassified raster layer to better identify buildings in the imagery
# and be able to calculate height an area

# Import system modules
import arcpy
from arcpy import env

# Set environment settings
env.workspace = "Y:/CMilton_Final"

# Set local variables
inRaster = "Y:/CMilton_Final/reclass"
outPolygons = "Y:/CMilton_Final/buildings.shp"
field = "VALUE"

# Execute RasterToPolygon, smooth edges of polygons
arcpy.RasterToPolygon_conversion(inRaster, outPolygons, "SIMPLIFY ", field)



#######################


#### Polygon to Point ####
# Create a point for each building in order to obtain height/area in later steps

# Set environment settings
env.workspace = "Y:/CMilton_Final"

#  Set local variables
inFeatures = "Y:/CMilton_Final/buildings.shp"
outFeatureClass = "Y:/CMilton_Final//building_pt"

# Use FeatureToPoint function to indentify a point within each building
arcpy.FeatureToPoint_management(inFeatures, outFeatureClass, "INSIDE")


#######################


#### Extract Values to Points ####
# Calculate height for each building based on point layer and detected surface level


# Set environment settings
env.workspace = "Y:/CMilton_Final"

# Set local variables
inPointFeatures = "Y:/CMilton_Final//building_pt.shp"
inRaster = "Y:/CMilton_Final/TechPark_dsm.tif"
outPointFeatures = "Y:/CMilton_Final/buildingheight.shp"

# Execute ExtractValuesToPoints
ExtractValuesToPoints(inPointFeatures, inRaster, outPointFeatures,
                      "INTERPOLATE", "VALUE_ONLY")



#######################


#### Area of Polygons ####
# Calculate the area of each building

 
# Set environment settings
env.workspace = "Y:/CMilton_Final"

# Set local variables
inPolygon = "Y:/CMilton_Final/buildings.shp"
calculate_output = "Y:/CMilton_Final/buildingarea.shp"
 
# Calculate area
arcpy.CalculateAreas_stats(inPolygon, calculate_output)


#######################



#### Create/Update map layout  ####
########
# Allow overwriting of files
arcpy.env.overwriteOutput = True

# Get project name
aprx = arcpy.mp.ArcGISProject(aprx_path)
# Select first map in the dataframe
map1 = aprx.listMaps()[0]

# Path with the aprx
service = os.path.basename(aprx_path)[:-5]
# Service definition
sddraft = os.path.join(os.path.dirname(aprx_path), service + ".sd")
sd = os.path.join(os.path.dirname(aprx_path), service + ".sd")

sharing_draft = arcpy.sharing.CreateSharingDraft("STANDALONE_SERVER", "MAP_SERVICE", service, map1)
sharing_draft.targetServer = server
sharing_draft.description = "Test"
sharing_draft.portalFolder = "Test"
sharing_draft.exportToSDDraft(sddraft)

# Upload to server
arcpy.StageService_server(sddraft, sd)
arcpy.UploadServiceDefinition_server(sd, server, in_folder_type = "EXSISTING", in_folder = "Test")

########
#### Update Layout Template ####

# I created a layout template in ArcGIS Pro for the following steps
# Use the layout template created for this project 

# Connect to layout pagx file

template = "Y:/CMilton_Final/layout.pagx"

# Input layout size
layout = "Portrait8.5x11"
template_pagx = os.path.join(template, layout + '.pagx')

# Create new map layout using the template
maplayout = arcpy.mp.ConvertLayoutFileToLayout(template_pagx)

#### Update the layout ####

# Reference variables in the layout
aprx = arcpy.mp.ArcGISProject('CURRENT')
layout2 = aprx.listLayouts('Layout')[0]
ms= layout.mapSeries
mf = layout.listElements('MAPFRAME_ELEMENT', "Map Frame Series")[0]
mapSeriesLyr = mf.map.ListLayers("Map1")[0]


m = aprx.listMaps("Map1")[0]
lyr = m.listLayers("Layout2")[0]
lyt = aprx.listLayouts("Points of Interest")[0]
horzLine = lyt.listElements("Building ID", "horzLine")[0]
vertLine = lyt.listElements("Zone", "vertLine")[0]
tableTitle = lyt.listElements("Title1", "cellText")[0]
tableText = lyt.listElements("Table1", "cellText")[0]

#### Update Map Title ####

for lyt in aprx.listLayouts("Layout2"):
    for elm in lyt.listElements("Title1"):
        if elm.text == "Buildings in Zone 0":
            elm.text = "Buildings in Zone 1"

#### Update data table ####


#Get information about the table
numRows = int(arcpy.GetCount_management(lyr).getOutput(0))
rowHeight = 0.2
fieldNames = ["Building ID", "Height", "Area"]
numColumns = len(fieldNames)
colWidth = 1.5


######






#####



#######################

#### Export PDFs ####

# Set environment settings
env.workspace = "Y:/CMilton_Final/Maps"

# Create a list of all mxd files in the workspace
mxd_list = arcpy.ListFiles("*.mxd")

# For all mxd files in the list create export as PDF
for mxd in mxd_list:
    
    current_mxd = arcpy.mapping.MapDocument(os.path.join(ws, mxd))
    pdf_name = mxd[:-4] + ".pdf"
    arcpy.mapping.ExportToPDF(current_mxd, pdf_name)

# Remove list
del mxd_list

#### Combine PDFs ####

# Using PyPDF module
from PyPDF2 import PdfFileMerger

# Set directory for final maps
source = "Y:/CMilton_Final\Maps"

Merger = PdfFileMerger()

for item in os.listdir(source):
    if item.endswith(pdf):
        merger.append(item)

Merger.write("CMilton_Final.pdf"))
Merger.close()

#### Close Files ####

#######################