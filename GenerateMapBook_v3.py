import arcpy
import os
import sys
import time
from datetime import datetime
from IPython.display import display
from arcgis.gis import GIS

gis = GIS("https://gisweb.spwater.org/portal/","portaladmin", "portaladmin01")

p = arcpy.mp.ArcGISProject(r"J:\EnterpriseGISWorkflows\GIS_Mapbooks\GIS_Mapbooks\GIS_MapbooksUN.aprx")


sewerIndex = p.listLayouts()[1]
sewer = p.listLayouts()[2]

waterIndex = p.listLayouts()[0]
water = p.listLayouts()[3]

sewerIndexElements = sewerIndex.listElements("TEXT_ELEMENT", "DateExported")[0]
waterIndexElements = waterIndex.listElements("TEXT_ELEMENT", "DateExported")[0]
sewerElements = sewer.listElements("TEXT_ELEMENT", "DateExported")[0]
waterElements = water.listElements("TEXT_ELEMENT", "DateExported")[0]

d = datetime.today()
date = d.date().strftime("%m/%d/%Y")

sewerIndexElements.text = "Exported: " + date
waterIndexElements.text = "Exported: " + date
sewerElements.text = "Exported: " + date
waterElements.text = "Exported: " + date

sewerIndex.exportToPDF(r"J:\EnterpriseGISOperations\MapbooksUN\SewerIndex.pdf")
waterIndex.exportToPDF(r"J:\EnterpriseGISOperations\MapbooksUN\WaterIndex.pdf")

if not sewer.mapSeries is None:
    ms = sewer.mapSeries
    if ms.enabled:
        ms = sewer.mapSeries
        indexLyr = ms.indexLayer

        ms.exportToPDF(r"J:\EnterpriseGISOperations\MapbooksUN\SewerMapbook.pdf", "ALL")
        ms.exportToPDF(r"J:\EnterpriseGISOperations\MapbooksUN\SewerPages\SewerMapbook.pdf", "ALL", "", "PDF_MULTIPLE_FILES_PAGE_NAME")
         
        pdfDoc = arcpy.mp.PDFDocumentOpen(r"J:\EnterpriseGISOperations\MapbooksUN\SewerMapbook.pdf")
        pdfDoc.insertPages(r"J:\EnterpriseGISOperations\MapbooksUN\SewerIndex.pdf", 1)
        pdfDoc.saveAndClose()
        del pdfDoc

##        item_id = "eed592c285bd407ab212d4e3d260baa0"
##        sdItem = gis.content.search(item_id)[0]
##        sd = r"J:\EnterpriseGISOperations\Mapbooks\SewerMapbook.pdf"      
##        sdItem.update(data=sd)

if not water.mapSeries is None:
    ms = water.mapSeries
    if ms.enabled:
        ms = water.mapSeries
        indexLyr = ms.indexLayer

        ms.exportToPDF(r"J:\EnterpriseGISOperations\MapbooksUN\WaterMapbook.pdf", "ALL")
        ms.exportToPDF(r"J:\EnterpriseGISOperations\MapbooksUN\WaterPages\WaterMapbook.pdf", "ALL", "", "PDF_MULTIPLE_FILES_PAGE_NAME")
        
        pdfDoc = arcpy.mp.PDFDocumentOpen(r"J:\EnterpriseGISOperations\MapbooksUN\WaterMapbook.pdf")
        pdfDoc.insertPages(r"J:\EnterpriseGISOperations\MapbooksUN\WaterIndex.pdf", 1)
        pdfDoc.saveAndClose()
        del pdfDoc

##        item_id = "05b278774c6e4bdea549f0693218a76d"
##        sdItem = gis.content.search(item_id)[0]
##        sd = r"J:\EnterpriseGISOperations\Mapbooks\WaterMapbook.pdf"      
##        sdItem.update(data=sd)
