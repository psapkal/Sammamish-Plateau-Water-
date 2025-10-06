import arcpy
import json
from datetime import datetime
from arcgis.gis import GIS
import os

def load_config():
    """
    Load configuration settings from config.json file
    
    Returns:
        dict: Configuration dictionary containing:
            - Portal connection credentials
            - Project file paths
            - Output PDF paths for mapbooks and indexes
    """
    # Build path to config.json in same directory as this script
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    
    # Open and parse JSON configuration file
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
    """
    Main function to orchestrate the complete mapbook generation workflow
    """
    # ===== CONFIGURATION SETUP =====
    # Load configuration settings from JSON file
    config = load_config()
    map_book_config = config['generateMapBook']

    # ===== PORTAL CONNECTION =====
    # Initialize GIS connection to ArcGIS Portal using credentials from config
    gis = GIS(map_book_config['portalUrl'], map_book_config['username'], map_book_config['password'])

    # ===== PROJECT SETUP =====
    # Open the ArcGIS Pro project file containing the mapbook layouts
    p = arcpy.mp.ArcGISProject(map_book_config['mapBookPath'])

    # ===== LAYOUT RETRIEVAL =====
    sewerIndex = p.listLayouts()[1]
    sewer = p.listLayouts()[2]

    waterIndex = p.listLayouts()[0]
    water = p.listLayouts()[3]

    # ===== DATE ELEMENT SETUP =====
    # Find "DateExported" text elements in each layout for timestamp updates
    sewerIndexElements = sewerIndex.listElements("TEXT_ELEMENT", "DateExported")[0]
    waterIndexElements = waterIndex.listElements("TEXT_ELEMENT", "DateExported")[0]
    sewerElements = sewer.listElements("TEXT_ELEMENT", "DateExported")[0]
    waterElements = water.listElements("TEXT_ELEMENT", "DateExported")[0]

    # ===== DATE STAMP UPDATE =====
    # Generate current date string and update all layout date elements
    current_date = datetime.now().strftime("%m/%d/%Y")
    export_text = f"Exported: {current_date}"

    # Update date text on all four layouts
    sewerIndexElements.text = export_text
    waterIndexElements.text = export_text
    sewerElements.text = export_text
    waterElements.text = export_text

    # ===== INDEX MAP EXPORT =====
    # Export standalone index maps as separate PDFs
    sewerIndex.exportToPDF(map_book_config['sewerIndexPdfPath'])
    waterIndex.exportToPDF(map_book_config['waterIndexPdfPath'])

    # ===== COMPLETE MAPBOOK GENERATION =====
    # Create sewer mapbook with map series + index page
    createPdf(sewer, map_book_config['sewerMapbookPath'], 
              map_book_config['sewerPagesMapbookPath'], 
              map_book_config['sewerIndexPdfPath'])
    
    # Create water mapbook with map series + index page
    createPdf(water, map_book_config['waterMapbookPath'], 
              map_book_config['waterPagesMapbookPath'], 
              map_book_config['waterIndexPdfPath'])

# ===== SCRIPT EXECUTION =====
# Only run main() when script is executed directly (not imported as module)
if __name__ == "__main__":
    main()
