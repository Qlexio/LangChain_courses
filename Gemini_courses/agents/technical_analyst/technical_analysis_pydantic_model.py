from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from typing import Optional, Type, Dict, Any
from datetime import datetime


# Enums
class TrendCategories(Enum):
    """List of actionnables for the trends."""
    STRONG_BULLISH = "STRONG_BULLISH"
    BULLISH = "BULLISH"
    CONSOLIDATION = "CONSOLIDATION"
    BEARISH = "BEARISH"
    STRONG_BEARISH = "STRONG_BEARISH"


class TradingActions(Enum):
    """List of trading actions."""
    BUY = "BUY"
    OUTPERFORM = "OUTPERFORM"
    HOLD = "HOLD"
    UNDERPERFORM = "UNDERPERFORM"
    SELL = "SELL"


class SupportResistanceInteractionStatus(Enum):
    """List of support and resistance status."""
    PRICE_ABOVE_SUPPORT = "PRICE_ABOVE_SUPPORT"
    TESTING_SUPPORT = "TESTING_SUPPORT"
    BREAKING_BELOW_SUPPORT = "BREAKING_BELOW_SUPPORT"
    PRICE_BELOW_RESISTANCE = "PRICE_BELOW_RESISTANCE"
    TESTING_RESISTANCE = "TESTING_RESISTANCE"
    BREAKING_ABOVE_RESISTANCE = "BREAKING_ABOVE_RESISTANCE"
    CONSOLIDATING_NEAR_SUPPORT_RESISTANCE = "CONSOLIDATING_NEAR_SUPPORT_RESISTANCE"


class SupportResistanceInteractionImplication(Enum):
    """List of support and resistance interaction implication."""
    POTENTIAL_BUY_ZONE = "POTENTIAL_BUY_ZONE"
    STOP_LOSS_ZONE = "STOP_LOSS_ZONE"
    POTENTIAL_SELL_ZONE = "POTENTIAL_SELL_ZONE"
    TAKE_PROFIT_ZONE = "TAKE_PROFIT_ZONE"
    CONFIRMATION_SIGNAL = "CONFIRMATION_SIGNAL"


# Creators funtions
def create_generic_evaluation_model(evaluation_name: str, raw_tool_class: Optional[Type[BaseModel]] = None) -> Type[BaseModel]:
    """Creates a Pydantic model for a specific evaluation dynamically, allowing conditional field additions."""

    # Définir les alias et descriptions dynamiquement
    trend_alias = f"{evaluation_name}_trend"
    trading_action_alias = f"{evaluation_name}_trading_action"
    primary_trend_alias = f"primary_{evaluation_name}_trend"
    primary_trend_touches_alias = f"primary_{evaluation_name}_trend_number_of_touches"
    secondary_trend_alias = f"secondary_{evaluation_name}_trend"
    secondary_trend_touches_alias = f"secondary_{evaluation_name}_trend_number_of_touches"
    minor_trend_alias = f"minor_{evaluation_name}_trend"
    minor_trend_touches_alias = f"minor_{evaluation_name}_trend_number_of_touches"
    raw_tool_data_alias = "raw_tool_data"

    annotations: Dict[str, Type] = {
        'trend': str,
        'trading_action': TradingActions,
        'primary_trend': TrendCategories,
        'primary_trend_number_of_touches': int,
        'secondary_trend': TrendCategories,
        'secondary_trend_number_of_touches': int,
        'minor_trend': TrendCategories,
        'minor_trend_number_of_touches': int,
    }

    attributes_dict: Dict[str, Any] = {
        'trend': Field(..., alias=trend_alias, description=f"(str) {evaluation_name.upper()} trend on the graph."),
        'trading_action': Field(..., alias=trading_action_alias, description=(f"(enum) Action to take based on {evaluation_name.upper()}. "
                                                                              "Type of action: TradingActions")),
        'primary_trend': Field(..., alias=primary_trend_alias, description=(f"(enum) Category of the primary {evaluation_name.upper()} trend. "
                                                                            "Type of category: TrendCategories")),
        'primary_trend_number_of_touches': Field(..., alias=primary_trend_touches_alias, description=("(int) Number of times the prices touch the primary "
                                                                                                      f"{evaluation_name.upper()} trend.")),
        'secondary_trend': Field(..., alias=secondary_trend_alias, description=(f"(enum) Category of the secondary {evaluation_name.upper()} trend. "
                                                                                "Type of category: TrendCategories")),
        'secondary_trend_number_of_touches': Field(..., alias=secondary_trend_touches_alias, description=("(int) Number of times the prices touch the secondary"
                                                                                                          f" {evaluation_name.upper()} trend.")),
        'minor_trend': Field(..., alias=minor_trend_alias, description=(f"(enum) Category of the minor {evaluation_name.upper()} trend. Type of category:"
                                                                        " TrendCategories")),
        'minor_trend_number_of_touches': Field(..., alias=minor_trend_touches_alias, description=("(int) Number of times the prices prices touch the minor"
                                                                                                  f" {evaluation_name.upper()} trend.")),

        # Configuration Pydantic pour la classe générée
        'model_config': ConfigDict(populate_by_name=True),
    }

    if raw_tool_class:
        annotations.update({
            'raw_tool_data': Optional[raw_tool_class]  # Utilise la classe RawToolData passée en argument
        })
        attributes_dict.update({
            'raw_tool_data': Field(None, alias=raw_tool_data_alias, description=f"Raw data specific to the {evaluation_name.upper()} tool."),
        })

    if evaluation_name in ["prices", "volumes"]:
        # Définir les alias et descriptions pour les champs spécifiques
        trend_evaluation_alias = f"{evaluation_name}_trend_evaluation"
        # Ajouter les champs à attributes_dict avec leurs définitions (Field, valeur par défaut, etc.)
        attributes_dict.update({
            'trend_evaluation': Field(..., alias=trend_evaluation_alias, description=f"(str) {evaluation_name.upper()} trend on the graph."),
        })
        # Ajouter les annotations de type pour les champs spécifiques à annotations
        annotations.update({
           'trend_evaluation': str,
        })

    if evaluation_name in ["prices"]:
        additional_attributes: Dict[str, Any] = {
            "chart_pattern": Field(..., alias="chart_pattern", description="(str) Description of the chart pattern if any"),
            "potential_chart_pattern": Field(..., alias="potential_chart_pattern", description=("(str) Description of potentials coming chart pattern to focus"
                                                                                                " on if any")),
            "candlestick_pattern": Field(..., alias="candlestick_pattern", description="(str) Description of the candlestick pattern if any"),
            "potential_candlestick_pattern": Field(..., alias="potential_candlestick_pattern", description=("(str) Description of potentials coming candlestick"
                                                                                                            " pattern to focus on if any")),
        }
        attributes_dict.update(additional_attributes)
        annotations.update({
            "chart_pattern": str,
            "potential_chart_pattern": str,
            "candlestick_pattern": str,
            "potential_candlestick_pattern": str,
        })

    attributes_dict['__annotations__'] = annotations

    # Utiliser type() pour créer dynamiquement la classe du modèle d'évaluation
    evaluation_model_name = f"{evaluation_name.capitalize()}Evaluation"  # Ex: RsiEvaluation
    return type(evaluation_model_name, (BaseModel,), attributes_dict)


def create_support_resistance_evaluation_model(evaluation_name: str, raw_tool_class: Type[BaseModel]) -> Type[BaseModel]:
    """Creates a Pydantic model for either support or resistance evaluation dynamically."""

    evaluation_alias = f"{evaluation_name}s_evaluation"
    interaction_status_alias = f"{evaluation_name}_interaction_status"
    interaction_implication_alias = f"{evaluation_name}_interaction_implication"
    close_level_alias = f"close_{evaluation_name}_level"
    middle_level_alias = f"middle_{evaluation_name}_level"
    far_level_alias = f"far_{evaluation_name}_level"
    raw_tool_data_alias = "raw_tool_data"

    annotations: Dict[str, Type] = {
        "evaluation": str,
        "interaction_status": SupportResistanceInteractionStatus,
        "interaction_implication": SupportResistanceInteractionImplication,
        "close_level": str,
        "middle_level": str,
        "far_level": str,
        "raw_tool_data": Optional[raw_tool_class],
    }

    attributes_dict: Dict[str, Any] = {
        "evaluation": Field(..., alias=evaluation_alias, description=f"(str) Global evaluation of the {evaluation_name.upper()}s."),
        "interaction_status": Field(..., alias=interaction_status_alias, description=(f"(enum) Category of the {evaluation_name.upper()} status, Type of"
                                                                                      " category: SupportResistanceInteractionStatus.")),
        "interaction_implication": Field(..., alias=interaction_implication_alias, description=(f"(enum) Category of the {evaluation_name.upper()} implication,"
                                                                                                " Type of category: SupportResistanceInteractionImplication.")),
        "close_level": Field(..., alias=close_level_alias, description=(f"(str) Evaluation and/or value of the closiest {evaluation_name.upper()} in relation "
                                                                        "to the price.")),
        "middle_level": Field(..., alias=middle_level_alias, description=(f"(str) Evaluation and/or value of the middle {evaluation_name.upper()} in relation "
                                                                          "to the price.")),
        "far_level": Field(..., alias=far_level_alias, description=(f"(str) Evaluation and/or value of the farest {evaluation_name.upper()} in relation to "
                                                                    "the price.")),
        # 'raw_tool_data': Field(None, alias=raw_tool_data_alias, description=f"Raw data specific to the {evaluation_name.upper()} tool."),
        'raw_tool_data': Field(None, alias=raw_tool_data_alias, description=f"Raw data specific to the {evaluation_name.upper()} tool."),

        "model_config": ConfigDict(populate_by_name=True),
    }

    attributes_dict["__annotations__"] = annotations

    evaluation_model_name = f"{evaluation_name.capitalize()}Evaluation"
    return type(evaluation_model_name, (BaseModel,), attributes_dict)


def create_support_resistance_raw_values_model(model_name: str) -> Type[BaseModel]:
    """Creates a Pydantic model for either support or resistance raw values profided by prices graphical analysis."""

    close_value_alias = f"close_{model_name}_value"
    middle_value_alias = f"middle_{model_name}_value"
    far_value_alias = f"far_{model_name}_value"

    annotations: Dict[str, Type] = {
        "close_value": float,
        "middle_value": float,
        "far_value": float,
    }

    attributes_dict: Dict[str, Any] = {
        "close_value": Field(..., alias=close_value_alias, description=f"Raw value of the closest {model_name.upper()} in relation to the price."),
        "middle_value": Field(..., alias=middle_value_alias, description=f"Raw value of the middle {model_name.upper()} in relation to the price."),
        "far_value": Field(..., alias=far_value_alias, description=f"Raw value of the farest {model_name.upper()} in relation to the price."),

        "model_config": ConfigDict(populate_by_name=True),
    }

    attributes_dict["__annotations__"] = annotations

    model_class_name = f"{model_name.capitalize()}RawToolData"
    return type(model_class_name, (BaseModel,), attributes_dict)


# Raw Values
class PRICESRawValue(BaseModel):
    """PRICES raw value provided by the chart."""
    prices_value: float = Field(alias="prices_value", description="PRICES raw value provided by the chart.")
    model_config = ConfigDict(populate_by_name=True)


class VOLUMESRawValue(BaseModel):
    """VOLUMES raw value provided by the chart."""
    volumes_value: float = Field(alias="volumes_value", description="VOLUMES raw value provided by the chart.")
    model_config = ConfigDict(populate_by_name=True)


class RSIRawValue(BaseModel):
    """RSI raw value provided by the RSI tool."""
    rsi_value: float = Field(alias="rsi_value", description="RSI raw value provided by the RSI tool.")
    model_config = ConfigDict(populate_by_name=True)


class MACDRawValues(BaseModel):
    """MACD raw values provided by the MACD tool."""
    short_moving_average_value: float = Field(alias="short_moving_average_value", description="Short moving avering raw value provided by the MACD tool.")
    long_moving_average_value: float = Field(alias="long_moving_average_value", description="Long moving avering raw value provided by the MACD tool.")
    signal_value: float = Field(alias="signal_value", description="Signal raw value provided by the MACD tool.")
    model_config = ConfigDict(populate_by_name=True)


class BollignerBandsRawValues(BaseModel):
    """Bollinger Bands raw values provided by the Bollinger Bands tool."""
    bollinger_bands_moving_average_value: float = Field(alias="bollinger_bands_moving_average_value",
                                                        description=("Moving avering raw value provided by the Bollinger Bands tool."))
    bollinger_bands_above_standard_deviation_value: float = Field(alias="bollinger_bands_above_standard_deviation_value",
                                                                  description=("Upper standard deviation provided by the Bollinger Bands tools."))
    bollinger_bands_below_standard_deviation_value: float = Field(alias="bollinger_bands_below_standard_deviation_value",
                                                                  description=("Lower standard deviation provided by the Bollinger Bands tools."))
    model_config = ConfigDict(populate_by_name=True)


# Submodels
# ## Indicators
RSIEvaluation = create_generic_evaluation_model(evaluation_name="rsi", raw_tool_class=RSIRawValue)
MACDEvaluation = create_generic_evaluation_model(evaluation_name="macd", raw_tool_class=MACDRawValues)
BOLLINGER_BANDSEvaluation = create_generic_evaluation_model(evaluation_name="bollinger_bands", raw_tool_class=BollignerBandsRawValues)


class Indicators(BaseModel):
    """Various prices related indicators."""
    rsi_evaluation: Optional[RSIEvaluation] = Field(None, alias="rsi_evaluation", description="RSI evaluation.")
    macd_evaluation: Optional[MACDEvaluation] = Field(None, alias="macd_evaluation", description="MACD evaluation.")
    bollinger_bands_evaluation: Optional[BOLLINGER_BANDSEvaluation] = Field(None, alias="bollinger_bands_evaluation", description="Bollinger Bands evaluation.")
    model_config = ConfigDict(populate_by_name=True)


# ## Support an d Resistance
SUPPORTRawToolData = create_support_resistance_raw_values_model(model_name="support")
RESISTANCERawToolData = create_support_resistance_raw_values_model(model_name="resistance")

SUPPORTEvaluation = create_support_resistance_evaluation_model(evaluation_name="support", raw_tool_class=SUPPORTRawToolData)
RESISTANCEEvaluation = create_support_resistance_evaluation_model(evaluation_name="resistance", raw_tool_class=RESISTANCERawToolData)


# ## Price and Volume
PRICESEvaluation = create_generic_evaluation_model(evaluation_name="prices", raw_tool_class=PRICESRawValue)
VOLUMESEvaluation = create_generic_evaluation_model(evaluation_name="volumes", raw_tool_class=VOLUMESRawValue)


# ## Synthesis
class Synthesis(BaseModel):
    """Synthesis and conclusion about the related data."""
    conclusion: str = Field(..., alias="conclusion", description="(str) Conclusion about the market at his time.")
    synthese_remarkable_values: Optional[Dict[str, Any]] = Field(None, alias="synthese_remarkable_values",
                                                                 description=("(dict) Remarkables values to keep in mind as dictionary. "
                                                                              "Values of the dictionary can be anything (str, int, float, dict, list, etc...)"
                                                                              ))
    synthese_trading_action: TradingActions = Field(..., alias="synthese_trading_action", description="(enum) Action to take. Type of action: TradingAction.")
    synthese_support_resistance_comment: str = Field(..., alias="synthese_support_resistance_comment",
                                                     description="(str) Comments about supports and/or resistances.")
    synthese_support_resistance_interaction_status: SupportResistanceInteractionStatus = Field(..., alias="synthese_support_resistance_interaction_status",
                                                                                               description=("(enum) Category of the support status, Type of "
                                                                                                            "category: SupportResistanceInteractionStatus")
                                                                                               )
    synthese_support_resistance_interaction_implication: SupportResistanceInteractionImplication \
        = Field(..., alias="synthese_support_resistance_interaction_implication",
                description=("(enum) Category of the support implication, Type of category: SupportResistanceInteractionImplication"))

    model_config = ConfigDict(populate_by_name=True)


# ## Timeframe data
class ShortTimeframeData(BaseModel):
    """Various evaluations related to the shorter timeframe."""
    data_timeframe: int = Field(default=5, alias="data_timeframe",
                                description="(int) Value in minutes of graph timeframe used as reference for the next values.")
    supports_evaluation: SUPPORTEvaluation = Field(..., alias="supports_evaluation",
                                                   description="(SUPPORTEvaluation) The evaluation of the prices supports for the current timeframe.")
    resistances_evaluation: RESISTANCEEvaluation = Field(..., alias="resistances_evaluation",
                                                         description=("(RESISTANCEEvaluation) The evaluation of the prices resistances for the current "
                                                                      "timeframe."))
    prices_evaluation: PRICESEvaluation = Field(..., alias="prices_evaluation",
                                                description="(PRICESEvaluation) The evaluation of the prices for the current timeframe.")
    indicators: Indicators = Field(..., alias="indicators", description="(Indicators) The evaluation of the prices for the current timeframe.")
    volumes_evaluation: VOLUMESEvaluation = Field(..., alias="volumes_evaluation",
                                                  description="(VOLUMESEvaluation) The evaluation of the prices volumes for the current timeframe.")
    short_timeframe_data_synthesis: Synthesis = Field(..., alias="short_timeframe_data_synthesis",
                                                      description="(Synthesis) Short timeframe data synthesis and conclusions.")

    model_config = ConfigDict(populate_by_name=True)


class LongTimeframeData(BaseModel):
    """Various evaluations related to the longer timeframe."""
    data_timeframe: int = Field(default=60, alias="data_timeframe",
                                description="(int) Value in minutes of graph timeframe used as reference for the next values.")
    supports_evaluation: SUPPORTEvaluation = Field(..., alias="supports_evaluation",
                                                   description="(SUPPORTEvaluation) The evaluation of the prices supports for the current timeframe.")
    resistances_evaluation: RESISTANCEEvaluation = Field(..., alias="resistances_evaluation",
                                                         description=("(RESISTANCEEvaluation) The evaluation of the prices resistances for the current "
                                                                      "timeframe."))
    prices_evaluation: PRICESEvaluation = Field(..., alias="prices_evaluation",
                                                description="(PRICESEvaluation) The evaluation of the prices for the current timeframe.")
    indicators: Indicators = Field(..., alias="indicators", description="(Indicators) The evaluation of the prices for the current timeframe.")
    volumes_evaluation: VOLUMESEvaluation = Field(..., alias="volumes_evaluation",
                                                  description="(VOLUMESEvaluation) The evaluation of the prices volumes for the current timeframe.")
    long_timeframe_data_synthesis: Synthesis = Field(..., alias="long_timeframe_data_synthesis",
                                                     description="(Synthesis) Long timeframe data synthesis and conclusions.")

    model_config = ConfigDict(populate_by_name=True)


# Model
class TickerTechnicalAnalysis(BaseModel):
    """Ticker technical analysis and synthesis based on both shorter and longer timeframes analyses."""
    name_of_the_company: str = Field(..., alias="name_of_the_company", description="(str) Name of the company.")
    isin_of_the_company: str = Field(..., alias="isin_of_the_company", description="(str) ISIN code of the company.")
    time_of_the_report: datetime = Field(..., alias="time_of_the_report", description="(str) datetime of the current report.")
    short_timeframe_data: ShortTimeframeData = Field(..., alias="short_timeframe_data",
                                                     description="(ShortTimeframeData) Short timeframe data and synthesis.")
    long_timeframe_data: LongTimeframeData = Field(..., alias="long_timeframe_data",
                                                   description="(LongTimeframeData) Long timeframe data and synthesis.")
    synthesis: Synthesis = Field(..., alias="synthesis", description="(Synthesis) Synthesis and conslusions made on both shorter and longer timeframes data.")

    model_config = ConfigDict(populate_by_name=True)
