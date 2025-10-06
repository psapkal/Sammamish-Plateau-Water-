import arcpy
import json
from datetime import datetime
from arcgis.gis import GIS
import os

# Load configuration from config.json file
def load_config():
    """Load configuration from config.json file"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r', encoding='utf-8') as config_file:
        return json.load(config_file)

def createPdf(layout, mapbookPath, pagesPath, indexPdfPath):
    """
    Create PDF mapbook from ArcGIS Pro layout with map series
    
    Args:
        layout: ArcGIS Pro layout object containing map series
        mapbookPath: Output path for combined mapbook PDF
        pagesPath: Output path for individual page PDFs
        indexPdfPath: Path to index PDF to insert at beginning
    """
    # Check if layout has a map series configured
    if not layout.mapSeries is None:
        ms = layout.mapSeries
        
        # Only proceed if map series is enabled in the layout
        if ms.enabled:
            ms = layout.mapSeries
            indexLyr = ms.indexLayer  # Get the index layer for map series

            # Export all pages of map series to single PDF
            ms.exportToPDF(mapbookPath, "ALL")
            
            # Export each page as separate PDF files (for individual page access)
            ms.exportToPDF(pagesPath, "ALL", "", "PDF_MULTIPLE_FILES_PAGE_NAME")

            # Open the main mapbook PDF to insert index page
            pdfDoc = arcpy.mp.PDFDocumentOpen(mapbookPath)
            
            # Insert the index PDF as the first page (position 1)
            pdfDoc.insertPages(indexPdfPath, 1)
            
            # Save changes and close PDF document
            pdfDoc.saveAndClose()
            
            # Clean up PDF document object from memory
            del pdfDoc

def main():

    # Load configuration
    config = load_config()
    map_book_config = config["generateMapBook"]

    # Initialize GIS connection using config
    gis = GIS(map_book_config["portalUrl"], map_book_config["username"], map_book_config["password"])

    # Load ArcGIS Pro project from config
    p = arcpy.mp.ArcGISProject(map_book_config["mapBookPath"])


    sewerIndex = p.listLayouts()[1]
    sewer = p.listLayouts()[2]

    waterIndex = p.listLayouts()[0]
    water = p.listLayouts()[3]

    sewerIndexElements = sewerIndex.listElements("TEXT_ELEMENT", "DateExported")[0]
    waterIndexElements = waterIndex.listElements("TEXT_ELEMENT", "DateExported")[0]
    sewerElements = sewer.listElements("TEXT_ELEMENT", "DateExported")[0]
    waterElements = water.listElements("TEXT_ELEMENT", "DateExported")[0]

    # Update export date on all layouts
    current_date = datetime.now().strftime("%m/%d/%Y")
    export_text = f"Exported: {current_date}"

    sewerIndexElements.text = export_text
    waterIndexElements.text = export_text
    sewerElements.text = export_text
    waterElements.text = export_text

    # Export index maps using config paths
    sewerIndex.exportToPDF(map_book_config["sewerIndexPdfPath"])
    waterIndex.exportToPDF(map_book_config["waterIndexPdfPath"])

    # Create sewer mapbook using createPdf function
    createPdf(sewer, map_book_config["sewerMapbookPath"], 
            map_book_config["sewerPagesMapbookPath"], 
            map_book_config["sewerIndexPdfPath"])

    # Create water mapbook using createPdf function
    createPdf(water, map_book_config["waterMapbookPath"], 
              map_book_config["waterPagesMapbookPath"], 
              map_book_config["waterIndexPdfPath"])

if __name__ == "__main__":
    main()
