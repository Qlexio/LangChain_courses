from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from typing import Optional, Type, Dict, Any
from datetime import datetime


class ESGRiskLevel(Enum):
    """List of the ESG risk levels.

    The higher the rating, the greater the risk. Maximum value is 100.
    - 0-10: Negligible
    - 10-20: Weak
    - 20-30: Medium
    - 30-40: High
    - 40+: Serious
    """
    NEGLIGIBLE = "NEGLIGIBLE"
    WEAK = "WEAK"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    SERIOUS = "SERIOUS"


class ExposureRiskLevel(Enum):
    """List of the ESG exposure risk levels.

    The higher the rating, the greater the risk. Maximum value is 100.
    - 0-35: Low
    - 35-55: Medium
    - 55-100: High
    """
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ESGManagementScore(Enum):
    """List of the ESG management score levels.

    The higher the rating, the better this risk is managed by the company. Maximum value is 100.
    - 0-25: Low
    - 25-50: Medium
    - 50-100: High
    """
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class CarbonEmissionsLevel(Enum):
    """List of the ESG risk levels.

    The higher the rating, the greater the risk. Maximum value is 100.
    - 0: Negligible
    - >0-10: Weak
    - 10-30: Medium
    - 30-50: High
    - 50+: Serious
    """
    NEGLIGIBLE = "NEGLIGIBLE"
    WEAK = "WEAK"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    SERIOUS = "SERIOUS"


class RisksLevel(Enum):
    """List of the risk levels.

    The higher the rating, the greater the risk. Maximum value is 100.
    - 0: Negligible
    - >0-10: Weak
    - 10-20: Medium Weak
    - 20-30: Medium
    - 30-40: Medium High
    - 40-50: High
    - 50+: Serious
    """
    NEGLIGIBLE = "NEGLIGIBLE"
    WEAK = "WEAK"
    MEDIUM_WEAK = "MEDIUM WEAK"
    MEDIUM = "MEDIUM"
    MEDIUM_HIGH = "MEDIUM HIGH"
    HIGH = "HIGH"
    SERIOUS = "SERIOUS"


class TradingActions(Enum):
    """List of trading actions."""
    BUY = "BUY"
    OUTPERFORM = "OUTPERFORM"
    HOLD = "HOLD"
    UNDERPERFORM = "UNDERPERFORM"
    SELL = "SELL"


class SustainabillityRiskRawValue(BaseModel):
    """Sustainability Risk raw value provided by the tool."""
    global_notation_value: float = Field(alias="global_notation_value", description="(float) ESG risk global notation in percentage")
    environmental_issues_value: float = Field(alias="environmental_issues_value", description="(float) Environmental part of ESG risk in percentage")
    societal_issues_value: float = Field(alias="societal_issues_value", description="(float) Societal part of ESG risk in percentage")
    governance_issues_value: float = Field(alias="governance_issues_value", description="(float) Governance part of ESG risk in percentage")

    model_config = ConfigDict(populate_by_name=True)


class SustainabilityRisk(BaseModel):
    """"""
    esg_risk_evaluation: str = Field(..., alias="esg_risk_evaluation",
                                     description="(str) ESG risk evaluation according to environmental, societal and governance evaluations")
    esg_risk_level: ESGRiskLevel = Field(..., alias="esg_risk_level", description="(enum) Level of the ESG risk, Type of level: ESGRiskLevel")
    environmental_issues_evaluation: str = Field(..., alias="environmental_issues_evaluation",
                                                 description="(str) Evaluation of the environmental part of ESG risk")
    societal_issues_evaluation: str = Field(..., alias="societal_issues_evaluation", description="(str) Evaluation of the societal part of ESG risk")
    governance_issues_evaluation: str = Field(..., alias="governance_issues_evaluation", description="(str) Evaluation of the governance part of ESG risk")
    raw_tool_data: Optional[SustainabillityRiskRawValue] = Field(None, alias="raw_tool_data", description="Raw data specific to the ESG sustainability tool.")

    model_config = ConfigDict(populate_by_name=True)


class ExposureRiskRawValue(BaseModel):
    """Exposure risk raw value provided by the tool."""
    exposure_risk_value: float = Field(alias="exposure_risk_value", description="(float) ESG risk exposure of the company in percentage")

    model_config = ConfigDict(populate_by_name=True)


class ExposureRisk(BaseModel):
    """"""
    esg_exposure_risk_evaluation: str = Field(..., alias="esg_exposure_risk_evaluation", description="(str) ESG exposure risk evaluation")
    esg_exposure_risk_level: ExposureRiskLevel = Field(..., alias="esg_exposure_risk_level", description="(enum) Level of the ESG exposure risk. Type of level: ExposureRiskLevel")
    raw_tool_data: Optional[ExposureRiskRawValue] = Field(None, alias="raw_tool_data", description="Raw data specific to the ESG exposure risk tool.")

    model_config = ConfigDict(populate_by_name=True)


class ManagementScoreRawValue(BaseModel):
    """Management score raw value provided by the tool."""
    management_score_value: float = Field(alias="management_score_value", description="(float) ESG risk manageable by the company")

    model_config = ConfigDict(populate_by_name=True)


class ManagementScore(BaseModel):
    """"""
    esg_management_score_evaluation: str = Field(..., alias="esg_management_score_evaluation", description="(str) ESG management score evaluation.")
    esg_management_score_level: ESGManagementScore = Field(..., alias="esg_management_score_level",
                                                           description="(enum) Level of the ESG management. Type of level: ESGManagementScore")
    raw_tool_data: Optional[ManagementScoreRawValue] = Field(None, alias="raw_tool_data", description="Raw data specific to the ESG management score tool.")

    model_config = ConfigDict(populate_by_name=True)


def create_carbon_year_raw_values_model(year_number: int) -> Type[BaseModel]:
    """Creates a Pydantic model for years values of carbon emissions raw data tool.

    Args:
        year_number (int): Number of the carbon emissions year to which create the values.
    """
    total_alias = f"total_year_{year_number}_value"
    scope_1_alias = f"scope_1_year_{year_number}_value"
    scope_2_alias = f"scope_2_year_{year_number}_value"

    annotations: Dict[str, Type] = {
        "total": float,
        "scope_1": float,
        "scope_2": float,
    }

    attributes_dict: Dict[str, Any] = {
        "total": Field(..., alias=total_alias, description="(float) Total carbon emissions in tons of CO2."),
        "scope_1": Field(..., alias=scope_1_alias, description="(float) Greenhouse gases emitted directly by the company in tonnes of CO2."),
        "scope_2": Field(..., alias=scope_2_alias, description="(float) Indirect emissions linked to energy in tonnes of CO2."),

        "model_config": ConfigDict(populate_by_name=True),
    }

    attributes_dict["__annotations__"] = annotations
    class_name = f"Year{year_number}RawValues"
    return type(class_name, (BaseModel,), attributes_dict)


Year1RawValues = create_carbon_year_raw_values_model(year_number=1)
Year2RawValues = create_carbon_year_raw_values_model(year_number=2)
Year3RawValues = create_carbon_year_raw_values_model(year_number=3)


class CarbonEmissionsRawValue(BaseModel):
    """Carbon Emissions raw value provided by the tool."""
    carbon_risk_value: float = Field(..., alias="carbon_risk_value", description="(float) The carbon risk that could impact the financial performance of the company.")
    year_1_value: Optional[Year1RawValues] = Field(None, alias="year_1_value", description="Carbon emissions values of 1 year ago.")
    year_2_value: Optional[Year2RawValues] = Field(None, alias="year_2_value", description="Carbon emissions values of 2 year ago.")
    year_3_value: Optional[Year3RawValues] = Field(None, alias="year_3_value", description="Carbon emissions values of 3 year ago.")

    model_config = ConfigDict(populate_by_name=True)


class CarbonEmissions(BaseModel):
    """"""
    carbon_emissions_evaluation: str = Field(..., alias="carbon_emissions_evaluation",
                                             description="(str) Evaluation of the carbon emissions according to the years 1, 2 and 3 emissions values.")
    carbon_emissions_risk_level: CarbonEmissionsLevel = Field(..., alias="carbon_emissions_risk_level",
                                                              description="(enum) Level of the carbon emission risk. Type of level: CarbonEmissionsLevel")
    raw_tool_data: Optional[CarbonEmissionsRawValue] = Field(None, alias="raw_tool_data", description="Raw data specific to the carbon emissions tool.")


class ActivitiesInvolvementsRawValue(BaseModel):
    """Activities involvements raw value provided by the tool."""
    positive_involvements_value: int = Field(alias="positive_involvements_value",
                                             description="(int) Involvements in activities with a positive impact. Notation out of 12, e.g. 0/12")
    negative_involvements_value: int = Field(alias="negative_involvements_value",
                                             description="(int) Involvements in activities with a negative impact. Notation out of 23, e.g. 1/23")
    controversies_risk_value: int = Field(alias="controversies_risk_value", description="(int) Risk linked to controversies. Notation out of 5, e.g. 2/5")

    model_config = ConfigDict(populate_by_name=True)


class ActivitiesInvolvements(BaseModel):
    """"""
    positive_involvements_evaluation: str = Field(..., alias="positive_involvements_evaluation", description=("(str) Evaluation of involvements in activities with a positive impact."))
    negative_involvements_evaluation: str = Field(..., alias="negative_involvements_evaluation", description=("(str) Evaluation of involvements in activities with a negative impact."))
    controversies_risk_evaluation: str = Field(..., alias="controversies_risk_evaluation", description=("(str) Evaluation of involvements in controversies."))
    raw_tool_data: Optional[ActivitiesInvolvementsRawValue] = Field(None, alias="raw_tool_data", description="Raw data specific to the activities involvements tool.")

    model_config = ConfigDict(populate_by_name=True)


class Synthesis(BaseModel):
    """"""
    conclusion: str = Field(..., alias="conclusion", description="(str) Conclusion about the impact of the previous values on the market")
    synthesis_trading_action: TradingActions = Field(..., alias="synthesis_trading_action" , description="(enum) Action to take. Type of action: TradingActions.")
    synthesis_risk: RisksLevel = Field(..., alias="synthesis_risk", description="(enum) Risk level according to the conclusion. Type of level: RisksLevel")

    model_config = ConfigDict(populate_by_name=True)


class TickerESGAnalysis(BaseModel):
    """Ticker ESG analysis based on ESG risk, exposure and management, carbon emissions and activities involvements."""
    name_of_the_company: str = Field(..., alias="name_of_the_company", description="(str) Name of the company.")
    isin_of_the_company: str = Field(..., alias="isin_of_the_company", description="(str) ISIN code of the company.")
    time_of_the_report: datetime = Field(..., alias="time_of_the_report", description="(str) datetime of the current report.")
    sustainability_risk: SustainabilityRisk = Field(..., alias="sustainability_risk", description="(SustainabilityRisk) Sustainability risk data.")
    exposure_risk: ExposureRisk = Field(..., alias="exposure_risk", description="(ExposureRisk) Exposure risk data.")
    management_score: ManagementScore = Field(..., alias="management_score", description="(ManagementScore) Management score data.")
    carbon_emissions: CarbonEmissions = Field(..., alias="carbon_emissions", description="(CarbonEmissions) Carbon emissions data.")
    activities_involvements: ActivitiesInvolvements = Field(..., alias="activities_involvements",
                                                            description="(ActivitiesInvolvements) Activities involvements data.")
    synthesis: Synthesis = Field(..., alias="synthesis",
                                 description="(Synthesis) Synthesis and conslusions made on every ESG, caron emissions and activities related data.")
