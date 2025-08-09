from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.output_parsers.retry import RetryWithErrorOutputParser, NAIVE_RETRY_WITH_ERROR_PROMPT
from langchain_core.runnables import RunnableParallel, RunnableLambda

from . import esg_analysis_pydantic_model as _pydantic_models
from time import time as _time


class ESGAnalysisLLMLogic():

    MODEL = "cogito:8b"
    DEEP_THINKING_INSTRUCTION = "Enable deep thinking subrouting.\n\n"
    CARBON_EMISSIONS_RAW_VALUE_PYDANTIC_MODELS = {
        "year-1_value": _pydantic_models.Year1RawValues,
        "year-2_value": _pydantic_models.Year2RawValues,
        "year-3_value": _pydantic_models.Year3RawValues,
    }
    TICKER_REQUIRED_PYDANTIC_MODELS = {
        "sustainability_risk": _pydantic_models.SustainabilityRisk,
        "exposure_risk": _pydantic_models.ExposureRisk,
        "management_score": _pydantic_models.ManagementScore,
        "carbon_emissions": _pydantic_models.CarbonEmissions,
        "activities_involvements": _pydantic_models.ActivitiesInvolvements,
    }
    GENERIC_SYSTEM_TEMPLATE = DEEP_THINKING_INSTRUCTION + (
        "As trading ESG analyst expert, your task is to generate the ESG analysis report for {stock} at the specified JSON format. "
        "Use the data (simulated for the exercice) to generate the ESG analysis of {stock} action totally filling the JSON schema described below. "
        # "The timeframe of {stock} data is {timeframe}. "
        "The format of your response is CRITICAL and MUST ADHERE EXACTLY to the JSON schema described here:"
        "\n{format_instructions}\n"
        "Thus, You MUST RESPECT the type of JSON schema entries. "
        "Once again, the JSON schema described above is CRITICAL and MUST BE RESPECTED."
        )
    CARBON_EMISSIONS_SYSTEM_TEMPLATE = DEEP_THINKING_INSTRUCTION + (
        "As trading ESG analyst expert, your task is to generate the ESG analysis report for {stock} at the specified JSON format. "
        "The JSON of the Year 1 Carbon Emissions raw values are provided here:\n{year-1_value_json}\n"
        "The JSON of the Year 2 Carbon Emissions raw values are provided here:\n{year-2_value_json}\n"
        "The JSON of the Year 3 Carbon Emissions raw values are provided here:\n{year-3_value_json}\n"
        "Use the data (simulated for the exercice) to generate the technical analysis of {stock} action totally filling the JSON schema described below. "
        # "The timeframe of {stock} data is {timeframe}. "
        "The format of your response is CRITICAL and MUST ADHERE EXACTLY to the JSON schema described here:"
        "\n{format_instructions}\n"
        "Thus, You MUST RESPECT the type of JSON schema entries. "
        "Once again, the JSON schema described above is CRITICAL and MUST BE RESPECTED."
        )
    TICKER_SYSTEM_TEMPLATE = DEEP_THINKING_INSTRUCTION + (
        "As trading ESG analyst expert, your task is to generate the ESG analysis report for {stock} at the specified JSON format. "
        "The JSON of the sustainability risk analysis is {sustainability_risk_json}."
        "The JSON of the exposure risk analysis is {exposure_risk_json}."
        "The JSON of the management score analysis is {management_score_json}."
        "The JSON of the carbon emissions analysis is {carbon_emissions_json}."
        "The JSON of the activities involvements analysis is {activities_involvements_json}."
        "Use the data (simulated for the exercice) to generate the technical analysis of {stock} action totally filling the JSON schema described below. "
        "The format of your response is CRITICAL and MUST ADHERE EXACTLY to the JSON schema described here:"
        "\n{format_instructions}\n"
        "Once again, the JSON schema described above is CRITICAL and MUST BE RESPECTED."
        )

    def __new__(cls, *args, **kwargs):
        retry_template = NAIVE_RETRY_WITH_ERROR_PROMPT.template.split("\n")
        retry_template = retry_template[:-1] + ["YOU MUST RESPECT THE SCHEMA PROVIDED IN THE PROMPT."] + retry_template[-1:]
        cls.RETRY_PROMPT_TEMPLATE = cls.DEEP_THINKING_INSTRUCTION + "\n".join(retry_template)
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, stock: str = "AAPL"):
        self.stock = stock
        self.timers = []

    def generic_output_parser(self, pydantic_model, system_prompt_template: str, input_variables: list = None, json_docs: dict = None):
        """Generic template to generate Pydantic outputs.

        Args:
            pydantic_model: The Pydantic model to product the return on.
            system_prompt_template (str): System prompt template for this LLM run.
            input_variables (list): PromptTemplate additionnal input variables.
            json_docs (dict): Additionnal values from documentations to pass at model invocation.
        """
        start_time = _time()
        init_input_variables = ["stock"]
        invocation = {"stock": self.stock}
        if input_variables:
            init_input_variables += input_variables
        if json_docs:
            invocation.update(json_docs)

        evaluation_parser = PydanticOutputParser(pydantic_object=pydantic_model)

        if isinstance(pydantic_model, _pydantic_models.TickerESGAnalysis):
            factor = 2
        else:
            factor = 1

        prompt_template = ChatPromptTemplate([
            SystemMessagePromptTemplate.from_template(template=system_prompt_template),
            HumanMessagePromptTemplate.from_template(template="{stock}"),
            ],
            input_variables=init_input_variables,
            partial_variables={"format_instructions": evaluation_parser.get_format_instructions()}
        )

        error_model = ChatOllama(model=self.MODEL, num_gpu=256, num_ctx=4092 * 4 * factor, num_predict=1000 * 4 * factor)
        retry_parser = RetryWithErrorOutputParser(
            parser=evaluation_parser,
            retry_chain=PromptTemplate.from_template(self.RETRY_PROMPT_TEMPLATE) | error_model | (lambda response:  response.content),
            max_retries=15,
        )

        model = ChatOllama(model=self.MODEL, num_gpu=256, num_ctx=4092 * 2 * factor, num_predict=1000 * 2 * factor)
        structured_model = model.with_structured_output(pydantic_model)
        completion_chain = prompt_template | structured_model  # | RunnableLambda(lambda response: re.sub(r"<think>[\n\W\w]+</think>", "", response.content))
        chain = RunnableParallel(
            completion=completion_chain, prompt_value=prompt_template
        ) | RunnableLambda(lambda response: retry_parser.parse_with_prompt(completion=response["completion"].model_dump_json(),
                                                                           prompt_value=response["prompt_value"]))

        response = chain.invoke(invocation)

        self.timers.append(round(_time() - start_time, 3))
        print("\t\t\tTime:", self.timers[-1])

        return response

    def carbon_emissions_components_output_parser(self, pydantic_model):
        """Generate components of 'Indicators' Pydantic output.

        Args:
            pydantic_model: The Pydantic model to product the return on.
        """
        return self.generic_output_parser(pydantic_model=pydantic_model, system_prompt_template=self.GENERIC_SYSTEM_TEMPLATE)

    def carbon_emissions_output_parser(self):
        """Generate the 'Indicators' output parser."""
        json_input = {}
        for name, pydantic_model in self.CARBON_EMISSIONS_RAW_VALUE_PYDANTIC_MODELS.items():
            print("\t\t** ", name)
            json_value = self.carbon_emissions_components_output_parser(pydantic_model=pydantic_model)
            # json_value = self.generic_output_parser(pydantic_model=pydantic_model, system_prompt_template=self.GENERIC_SYSTEM_TEMPLATE)
            print(json_value)
            json_input[name + "_json"] = json_value

        print("\t** carbon emissions gathering")
        # print("JSON inputs", json_input)
        return self.generic_output_parser(pydantic_model=_pydantic_models.CarbonEmissions, system_prompt_template=self.CARBON_EMISSIONS_SYSTEM_TEMPLATE,
                                          input_variables=list(json_input.keys()), json_docs=json_input)

    def tickers_output_parser(self):
        """Generate the ticker technical analysis."""
        json_input = {}
        for name, pydantic_model in self.TICKER_REQUIRED_PYDANTIC_MODELS.items():
            print("** ", name)
            if "carbon_emissions" in name:
                json_value = self.carbon_emissions_output_parser()
            else:
                json_value = self.generic_output_parser(pydantic_model=pydantic_model, system_prompt_template=self.GENERIC_SYSTEM_TEMPLATE)
            print(json_value)
            json_input[name + "_json"] = json_value  # .model_dump_json()

        print()
        print("Ticker Ananlysis")
        print()
        return self.generic_output_parser(pydantic_model=_pydantic_models.TickerESGAnalysis, system_prompt_template=self.TICKER_SYSTEM_TEMPLATE,
                                          input_variables=list(json_input.keys()), json_docs=json_input)
