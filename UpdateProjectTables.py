import arcpy
import json
import os

def loadConfig():
    """Load configuration from config.json file"""
    # Get the directory where this script is located
    scriptDir = os.path.dirname(os.path.abspath(__file__))
    configPath = os.path.join(scriptDir, 'config.json')

    try:
        with open(configPath, 'r') as configFile:
            config = json.load(configFile)
        return config
    except FileNotFoundError:
        print(f"Config file not found at: {configPath}")
        raise
    except json.JSONDecodeError as e:
        print(f"Error parsing config file: {e}")
        raise


def Model():
    # Load configuration for updating project tables script
    config = loadConfig()
    updateConfig = config['updateProjectTables']

    # Sign in to portal
    arcpy.SignInToPortal(
        updateConfig['portalUrl'],
        updateConfig['username'],
        updateConfig['password']
    )
    
    # To allow overwriting outputs change overwriteOutput option to True.
    arcpy.env.overwriteOutput = False

    reporting_dbo_VIEW_EDEN_CIP_PROJECTS_FOR_INSPECTIONS = updateConfig['reporting_dbo_VIEW_EDEN_CIP_PROJECTS_FOR_INSPECTIONS']
    L0view_Eden_CIP_Projects_for_Inspections = updateConfig['L0view_Eden_CIP_Projects_for_Inspections']
    reporting_dbo_VIEW_EDEN_DEA_PROJECTS_FOR_INSPECTIONS = updateConfig['reporting_dbo_VIEW_EDEN_DEA_PROJECTS_FOR_INSPECTIONS']
    L1view_Eden_DEA_Projects_for_Inspections = updateConfig['L1view_Eden_DEA_Projects_for_Inspections']

    # Process: Make Table View (Make Table View) (management)
    initialTableView = updateConfig['tableView']
    with arcpy.EnvManager(scratchWorkspace=r"J:\EnterpriseGISProjects\SPW_DailyInspectionReports\WebServices\EdenProjects\Default.gdb", workspace=r"J:\EnterpriseGISProjects\SPW_DailyInspectionReports\WebServices\EdenProjects\Default.gdb"):
        arcpy.management.MakeTableView(in_table=reporting_dbo_VIEW_EDEN_CIP_PROJECTS_FOR_INSPECTIONS, out_view=initialTableView, where_clause="", workspace="", field_info="project_ID project_ID VISIBLE NONE;Title Title VISIBLE NONE;Project_No Project_No VISIBLE NONE;Manager Manager VISIBLE NONE;Month11InspectionDue Month11InspectionDue VISIBLE NONE;Month23InspectionDue Month23InspectionDue VISIBLE NONE;AddExistingSewerERU AddExistingSewerERU VISIBLE NONE;AddExistingWaterERU AddExistingWaterERU VISIBLE NONE;ContractorCityStateZip ContractorCityStateZip VISIBLE NONE;ContractorCompanyName ContractorCompanyName VISIBLE NONE;ContractorContactEMail ContractorContactEMail VISIBLE NONE;ContractorFax ContractorFax VISIBLE NONE;ContractorName ContractorName VISIBLE NONE;ContractorPhone ContractorPhone VISIBLE NONE;ContractorStreetAddress ContractorStreetAddress VISIBLE NONE;DelinquentFinalLetter DelinquentFinalLetter VISIBLE NONE;DelinquentInitialLetter DelinquentInitialLetter VISIBLE NONE;DeveloperCityStateZip DeveloperCityStateZip VISIBLE NONE;DeveloperCompanyName DeveloperCompanyName VISIBLE NONE;DeveloperContactEMail DeveloperContactEMail VISIBLE NONE;DeveloperFax DeveloperFax VISIBLE NONE;DeveloperName DeveloperName VISIBLE NONE;DeveloperPhone DeveloperPhone VISIBLE NONE;DeveloperStreetAddress DeveloperStreetAddress VISIBLE NONE;DevelopmentServicesFee DevelopmentServicesFee VISIBLE NONE;DrawingsSignedDate DrawingsSignedDate VISIBLE NONE;EngineerAddress EngineerAddress VISIBLE NONE;EngineerCityStateZip EngineerCityStateZip VISIBLE NONE;EngineerCompanyName EngineerCompanyName VISIBLE NONE;EngineerContactEMail EngineerContactEMail VISIBLE NONE;EngineerFax EngineerFax VISIBLE NONE;EngineerName EngineerName VISIBLE NONE;EngineerPhone EngineerPhone VISIBLE NONE;FinalResolutionDate FinalResolutionDate VISIBLE NONE;FinalResolutionNo FinalResolutionNo VISIBLE NONE;FinalTotalSewerERUs FinalTotalSewerERUs VISIBLE NONE;FinalTotalWaterERUs FinalTotalWaterERUs VISIBLE NONE;FinalWaterDomesticERUs FinalWaterDomesticERUs VISIBLE NONE;FinalWaterIrrigationERUs FinalWaterIrrigationERUs VISIBLE NONE;GrinderPumpsRequired GrinderPumpsRequired VISIBLE NONE;InitialResolutionDate InitialResolutionDate VISIBLE NONE;InitialResolutionNo InitialResolutionNo VISIBLE NONE;InitialSewerERU InitialSewerERU VISIBLE NONE;InitialWaterDomesticERU InitialWaterDomesticERU VISIBLE NONE;InitialWaterIrrigationERU InitialWaterIrrigationERU VISIBLE NONE;MeterInstallRequired MeterInstallRequired VISIBLE NONE;NeedsProjectZeroing NeedsProjectZeroing VISIBLE NONE;NumberofGrinderPumps NumberofGrinderPumps VISIBLE NONE;NumberofMeterInstalls NumberofMeterInstalls VISIBLE NONE;OwnerCityStateZip OwnerCityStateZip VISIBLE NONE;OwnerEMail OwnerEMail VISIBLE NONE;OwnerName OwnerName VISIBLE NONE;OwnerPhoneNumber OwnerPhoneNumber VISIBLE NONE;OwnerStreetAddress OwnerStreetAddress VISIBLE NONE;PhasingResolutionDate PhasingResolutionDate VISIBLE NONE;PhasingResolutionNumber PhasingResolutionNumber VISIBLE NONE;PreconstructionMeetingDate PreconstructionMeetingDate VISIBLE NONE;SewerCertificateDate SewerCertificateDate VISIBLE NONE;SewerGFCCredits SewerGFCCredits VISIBLE NONE;SewerGFCsLocked SewerGFCsLocked VISIBLE NONE;SewerGFCsPaidDate SewerGFCsPaidDate VISIBLE NONE;SewerLFCPaid SewerLFCPaid VISIBLE NONE;SewerLFCPaidDate SewerLFCPaidDate VISIBLE NONE;SewerReimbursementApp SewerReimbursementApp VISIBLE NONE;SewerReimbursementExpiration SewerReimbursementExpiration VISIBLE NONE;SewerReimbursementResDate SewerReimbursementResDate VISIBLE NONE;SewerReimbursementResolution SewerReimbursementResolution VISIBLE NONE;Status Status VISIBLE NONE;TaxParcelNumbers TaxParcelNumbers VISIBLE NONE;WaterCertificateDate WaterCertificateDate VISIBLE NONE;WaterGFCCredits WaterGFCCredits VISIBLE NONE;WaterGFCsLocked WaterGFCsLocked VISIBLE NONE;WaterGFCsPaidDate WaterGFCsPaidDate VISIBLE NONE;WaterLFCPaid WaterLFCPaid VISIBLE NONE;WaterLFCPaidDate WaterLFCPaidDate VISIBLE NONE;WaterorSewerPartResDate WaterorSewerPartResDate VISIBLE NONE;WaterorSewerPartResolution WaterorSewerPartResolution VISIBLE NONE;WaterorSewerParticipation WaterorSewerParticipation VISIBLE NONE;WaterReimbursementApp WaterReimbursementApp VISIBLE NONE;WaterReimbursementExpiration WaterReimbursementExpiration VISIBLE NONE;WaterReimbursementResDate WaterReimbursementResDate VISIBLE NONE;WaterReimbursementResolution WaterReimbursementResolution VISIBLE NONE;YearConstructed YearConstructed VISIBLE NONE")

    # Process: Truncate Table (Truncate Table) (management)
    Truncated_Table = arcpy.management.TruncateTable(in_table=L0view_Eden_CIP_Projects_for_Inspections)[0]

    # Process: Append (Append) (management)
    view_Eden_CIP_Projects_for_Inspections_3_ = arcpy.management.Append(inputs=[initialTableView], target=Truncated_Table, schema_type="TEST_AND_SKIP", field_mapping="", subtype="", expression="")[0]

    # Process: Make Table View (2) (Make Table View) (management)
    view_Eden_DEA_Projects_for_Inspections_2_ = "view_Eden_DEA_Projects_for_Inspections"
    with arcpy.EnvManager(scratchWorkspace=r"J:\EnterpriseGISProjects\SPW_DailyInspectionReports\WebServices\EdenProjects\Default.gdb", workspace=r"J:\EnterpriseGISProjects\SPW_DailyInspectionReports\WebServices\EdenProjects\Default.gdb"):
        arcpy.management.MakeTableView(in_table=reporting_dbo_VIEW_EDEN_DEA_PROJECTS_FOR_INSPECTIONS, out_view=view_Eden_DEA_Projects_for_Inspections_2_, where_clause="", workspace="", field_info="project_ID project_ID VISIBLE NONE;Title Title VISIBLE NONE;Project_No Project_No VISIBLE NONE;Manager Manager VISIBLE NONE;Month11InspectionDue Month11InspectionDue VISIBLE NONE;Month23InspectionDue Month23InspectionDue VISIBLE NONE;AddExistingSewerERU AddExistingSewerERU VISIBLE NONE;AddExistingWaterERU AddExistingWaterERU VISIBLE NONE;ContractorCityStateZip ContractorCityStateZip VISIBLE NONE;ContractorCompanyName ContractorCompanyName VISIBLE NONE;ContractorContactEMail ContractorContactEMail VISIBLE NONE;ContractorFax ContractorFax VISIBLE NONE;ContractorName ContractorName VISIBLE NONE;ContractorPhone ContractorPhone VISIBLE NONE;ContractorStreetAddress ContractorStreetAddress VISIBLE NONE;DelinquentFinalLetter DelinquentFinalLetter VISIBLE NONE;DelinquentInitialLetter DelinquentInitialLetter VISIBLE NONE;DeveloperCityStateZip DeveloperCityStateZip VISIBLE NONE;DeveloperCompanyName DeveloperCompanyName VISIBLE NONE;DeveloperContactEMail DeveloperContactEMail VISIBLE NONE;DeveloperFax DeveloperFax VISIBLE NONE;DeveloperName DeveloperName VISIBLE NONE;DeveloperPhone DeveloperPhone VISIBLE NONE;DeveloperStreetAddress DeveloperStreetAddress VISIBLE NONE;DevelopmentServicesFee DevelopmentServicesFee VISIBLE NONE;DrawingsSignedDate DrawingsSignedDate VISIBLE NONE;EngineerAddress EngineerAddress VISIBLE NONE;EngineerCityStateZip EngineerCityStateZip VISIBLE NONE;EngineerCompanyName EngineerCompanyName VISIBLE NONE;EngineerContactEMail EngineerContactEMail VISIBLE NONE;EngineerFax EngineerFax VISIBLE NONE;EngineerName EngineerName VISIBLE NONE;EngineerPhone EngineerPhone VISIBLE NONE;FinalResolutionDate FinalResolutionDate VISIBLE NONE;FinalResolutionNo FinalResolutionNo VISIBLE NONE;FinalTotalSewerERUs FinalTotalSewerERUs VISIBLE NONE;FinalTotalWaterERUs FinalTotalWaterERUs VISIBLE NONE;FinalWaterDomesticERUs FinalWaterDomesticERUs VISIBLE NONE;FinalWaterIrrigationERUs FinalWaterIrrigationERUs VISIBLE NONE;GrinderPumpsRequired GrinderPumpsRequired VISIBLE NONE;InitialResolutionDate InitialResolutionDate VISIBLE NONE;InitialResolutionNo InitialResolutionNo VISIBLE NONE;InitialSewerERU InitialSewerERU VISIBLE NONE;InitialWaterDomesticERU InitialWaterDomesticERU VISIBLE NONE;InitialWaterIrrigationERU InitialWaterIrrigationERU VISIBLE NONE;MeterInstallRequired MeterInstallRequired VISIBLE NONE;NeedsProjectZeroing NeedsProjectZeroing VISIBLE NONE;NumberofGrinderPumps NumberofGrinderPumps VISIBLE NONE;NumberofMeterInstalls NumberofMeterInstalls VISIBLE NONE;OwnerCityStateZip OwnerCityStateZip VISIBLE NONE;OwnerEMail OwnerEMail VISIBLE NONE;OwnerName OwnerName VISIBLE NONE;OwnerPhoneNumber OwnerPhoneNumber VISIBLE NONE;OwnerStreetAddress OwnerStreetAddress VISIBLE NONE;PhasingResolutionDate PhasingResolutionDate VISIBLE NONE;PhasingResolutionNumber PhasingResolutionNumber VISIBLE NONE;PreconstructionMeetingDate PreconstructionMeetingDate VISIBLE NONE;SewerCertificateDate SewerCertificateDate VISIBLE NONE;SewerGFCCredits SewerGFCCredits VISIBLE NONE;SewerGFCsLocked SewerGFCsLocked VISIBLE NONE;SewerGFCsPaidDate SewerGFCsPaidDate VISIBLE NONE;SewerLFCPaid SewerLFCPaid VISIBLE NONE;SewerLFCPaidDate SewerLFCPaidDate VISIBLE NONE;SewerReimbursementApp SewerReimbursementApp VISIBLE NONE;SewerReimbursementExpiration SewerReimbursementExpiration VISIBLE NONE;SewerReimbursementResDate SewerReimbursementResDate VISIBLE NONE;SewerReimbursementResolution SewerReimbursementResolution VISIBLE NONE;Status Status VISIBLE NONE;TaxParcelNumbers TaxParcelNumbers VISIBLE NONE;WaterCertificateDate WaterCertificateDate VISIBLE NONE;WaterGFCCredits WaterGFCCredits VISIBLE NONE;WaterGFCsLocked WaterGFCsLocked VISIBLE NONE;WaterGFCsPaidDate WaterGFCsPaidDate VISIBLE NONE;WaterLFCPaid WaterLFCPaid VISIBLE NONE;WaterLFCPaidDate WaterLFCPaidDate VISIBLE NONE;WaterorSewerPartResDate WaterorSewerPartResDate VISIBLE NONE;WaterorSewerPartResolution WaterorSewerPartResolution VISIBLE NONE;WaterorSewerParticipation WaterorSewerParticipation VISIBLE NONE;WaterReimbursementApp WaterReimbursementApp VISIBLE NONE;WaterReimbursementExpiration WaterReimbursementExpiration VISIBLE NONE;WaterReimbursementResDate WaterReimbursementResDate VISIBLE NONE;WaterReimbursementResolution WaterReimbursementResolution VISIBLE NONE;YearConstructed YearConstructed VISIBLE NONE")

    # Process: Truncate Table (2) (Truncate Table) (management)
    Truncated_Table_2_ = arcpy.management.TruncateTable(in_table=L1view_Eden_DEA_Projects_for_Inspections)[0]

    # Process: Append (2) (Append) (management)
    view_Eden_CIP_Projects_for_Inspections_2_ = arcpy.management.Append(inputs=[view_Eden_DEA_Projects_for_Inspections_2_], target=Truncated_Table_2_, schema_type="TEST_AND_SKIP", field_mapping="", subtype="", expression="")[0]

if __name__ == '__main__':
    # Global Environment settings
    with arcpy.EnvManager(scratchWorkspace=r"J:\EnterpriseGISProjects\SPW_DailyInspectionReports\WebServices\EdenProjects\Default.gdb", workspace=r"J:\EnterpriseGISProjects\SPW_DailyInspectionReports\WebServices\EdenProjects\Default.gdb"):
        Model()
