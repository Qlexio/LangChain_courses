from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.output_parsers.retry import RetryWithErrorOutputParser, NAIVE_RETRY_WITH_ERROR_PROMPT
from langchain_core.runnables import RunnableParallel, RunnableLambda

from . import technical_analysis_pydantic_model as _pydantic_models
from time import time as _time


class TechnicalAnalysisLLMLogic():

    MODEL = "cogito:8b"
    DEEP_THINKING_INSTRUCTION = "Enable deep thinking subroutine.\n\n"
    INDICATOR_REQUIRED_PYDANTIC_MODELS = {
        "rsi": _pydantic_models.RSIEvaluation,
        "macd": _pydantic_models.MACDEvaluation,
        "bollinger_bands": _pydantic_models.BOLLINGER_BANDSEvaluation,
    }
    TIMEFRAME_DATA_REQUIRED_PYDANTIC_MODELS = {
        "support": _pydantic_models.SUPPORTEvaluation,
        "resistance": _pydantic_models.RESISTANCEEvaluation,
        "prices": _pydantic_models.PRICESEvaluation,
        "indicators": _pydantic_models.Indicators,
        "volumes": _pydantic_models.VOLUMESEvaluation,
    }
    TICKER_REQUIRED_PYDANTIC_MODELS = {
        "short_timeframe_data": _pydantic_models.ShortTimeframeData,
        "long_timeframe_data": _pydantic_models.LongTimeframeData,
    }
    GENERIC_SYSTEM_TEMPLATE = DEEP_THINKING_INSTRUCTION + (
        "As trading technical analyst expert, your task is to generate the technical analysis report for {stock} at the specified JSON format. "
        "Use the data (simulated for the exercice) to generate the technical analysis of {stock} action totally filling the JSON schema described below. "
        "The timeframe of {stock} data is {timeframe}. "
        "The format of your response is CRITICAL and MUST ADHERE EXACTLY to the JSON schema described here:"
        "\n{format_instructions}\n"
        "Thus, You MUST RESPECT the type of JSON schema entries. "
        "Once again, the JSON schema described above is CRITICAL and MUST BE RESPECTED."
        )
    INDICATORS_SYSTEM_TEMPLATE = DEEP_THINKING_INSTRUCTION + (
        "As trading technical analyst expert, your task is to generate the technical analysis report for {stock} at the specified JSON format. "
        "The JSON of the RSI evaluation is provided here:\n{rsi_json}\n"
        "The JSON of the MACD evaluation is provided here:\n{macd_json}\n"
        "The JSON of the Bollinger Bands evaluation is provided here:\n{bollinger_bands_json}\n"
        "Use the data (simulated for the exercice) to generate the technical analysis of {stock} action totally filling the JSON schema described below. "
        "The timeframe of {stock} data is {timeframe}. "
        "The format of your response is CRITICAL and MUST ADHERE EXACTLY to the JSON schema described here:"
        "\n{format_instructions}\n"
        "Thus, You MUST RESPECT the type of JSON schema entries. "
        "Once again, the JSON schema described above is CRITICAL and MUST BE RESPECTED."
        )
    TIMEFRAME_DATA_SYSTEM_TEMPLATE = DEEP_THINKING_INSTRUCTION + (
        "As trading technical analyst expert, your task is to generate the technical analysis report for {stock} at the specified JSON format. "
        "The JSON of the supports evaluation is provided here:\n{support_json}\n"
        "The JSON of the resistances evaluation is provided here:\n{resistance_json}\n"
        "The JSON of the prices evaluation is provided here:\n{prices_json}\n"
        "The JSON of the indicators evaluation is provided here:\n{indicators_json}\n"
        "The JSON of the volumes evaluation is provided here:\n{volumes_json}\n"
        "Use the data (simulated for the exercice) to generate the technical analysis of {stock} action totally filling the JSON schema described below. "
        "The timeframe of {stock} data is {timeframe}. "
        "The format of your response is CRITICAL and MUST ADHERE EXACTLY to the JSON schema described here:"
        "\n{format_instructions}\n"
        "Thus, You MUST RESPECT the type of JSON schema entries. "
        "Once again, the JSON schema described above is CRITICAL and MUST BE RESPECTED."
        )
    TICKER_SYSTEM_TEMPLATE = DEEP_THINKING_INSTRUCTION + (
        "As trading technical analyst expert, your task is to generate the technical analysis report for {stock} at the specified JSON format. "
        "The JSON of the short timeframe analysis is {short_timeframe_data_json}."
        "The JSON of the long timeframe analysis is {long_timeframe_data_json}."
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
        # self.model = ChatOllama(model=self.MODEL, num_gpu=256, num_ctx=4092 * 2, num_predict=1000 * 2)
        # self.error_model = ChatOllama(model=self.MODEL, num_gpu=256, num_ctx=4092 * 4, num_predict=1000 * 4)
        self.stock = stock
        self.short_timeframe = "5 minutes"
        self.long_timeframe = "1 hour"
        self.timers = []

    def generic_output_parser(self, pydantic_model, system_prompt_template: str, timeframe: str = None, input_variables: list = None, json_docs: dict = None):
        """Generic template to generate Pydantic outputs.

        Args:
            pydantic_model: The Pydantic model to product the return on.
            system_prompt_template (str): System prompt template for this LLM run.
            timeframe (str): Base timeframe of the stock evaluation, e.g. "5 minutes" or "1 hour".
            input_variables (list): PromptTemplate additionnal input variables.
            json_docs (dict): Additionnal values from documentations to pass at model invocation.
        """
        start_time = _time()
        init_input_variables = ["stock"]
        invocation = {"stock": self.stock}
        if timeframe:
            init_input_variables += ["timeframe"]
            invocation.update({"timeframe": timeframe})
        if input_variables:
            init_input_variables += input_variables
        if json_docs:
            invocation.update(json_docs)

        evaluation_parser = PydanticOutputParser(pydantic_object=pydantic_model)

        if isinstance(pydantic_model, _pydantic_models.TickerTechnicalAnalysis):
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

    def indicators_components_output_parser(self, pydantic_model, timeframe):
        """Generate components of 'Indicators' Pydantic output.

        Args:
            pydantic_model: The Pydantic model to product the return on.
            timeframe (str): Base timeframe of the stock evaluation, e.g. "5 minutes" or "1 hour".
        """
        return self.generic_output_parser(pydantic_model=pydantic_model, system_prompt_template=self.GENERIC_SYSTEM_TEMPLATE,
                                          timeframe=timeframe)

    def indicators_output_parser(self, timeframe):
        """Generate the 'Indicators' output parser.

        Args:
            timeframe (str): Base timeframe of the stock evaluation, e.g. "5 minutes" or "1 hour".
        """
        json_input = {}
        for name, pydantic_model in self.INDICATOR_REQUIRED_PYDANTIC_MODELS.items():
            print("\t\t** ", name)
            json_value = self.indicators_components_output_parser(pydantic_model=pydantic_model, timeframe=timeframe)
            # print(name, " ", json_value)
            json_input[name + "_json"] = json_value  # .model_dump_json()

        print("\t** indicators gathering")
        # print("JSON inputs", json_input)
        return self.generic_output_parser(pydantic_model=_pydantic_models.Indicators, system_prompt_template=self.INDICATORS_SYSTEM_TEMPLATE,
                                          timeframe=timeframe, input_variables=list(json_input.keys()), json_docs=json_input)

    def timeframe_data_components_output_parser(self, pydantic_model, timeframe):
        """Generate components of 'Timeframe Data' Pydantic output.

        Args:
            pydantic_model: The Pydantic model to product the return on.
            timeframe (str): Base timeframe of the stock evaluation, e.g. "5 minutes" or "1 hour".
        """
        return self.generic_output_parser(pydantic_model=pydantic_model, system_prompt_template=self.GENERIC_SYSTEM_TEMPLATE,
                                          timeframe=timeframe)

    def timeframe_data_output_parser(self, timeframe_pydantic_model, timeframe: str):
        """Generate 'Timeframe Data' output parser.

        Args:
            timeframe_pydantic_model: The Pydantic model to product the return on.
            timeframe (str): Base timeframe of the stock evaluation, e.g. "5 minutes" or "1 hour".
        """
        json_input = {}
        for name, pydantic_model in self.TIMEFRAME_DATA_REQUIRED_PYDANTIC_MODELS.items():
            print("\t** ", name)
            if "indicators" in name:
                json_value = self.indicators_output_parser(timeframe=timeframe)
            else:
                json_value = self.timeframe_data_components_output_parser(pydantic_model=pydantic_model, timeframe=timeframe)
            json_input[name + "_json"] = json_value  # .model_dump_json()

        print("\t**  synthesis")
        return self.generic_output_parser(pydantic_model=timeframe_pydantic_model, system_prompt_template=self.TIMEFRAME_DATA_SYSTEM_TEMPLATE,
                                          timeframe=timeframe, input_variables=list(json_input.keys()), json_docs=json_input)

    def tickers_output_parser(self, timeframe=None):
        """Generate the ticker technical analysis.

        Args:
            timeframe (list): Timeframes list: e.g. ["5 minutes", "1 hour"].
        """
        json_input = {}
        for (name, pydantic_model), timer in zip(self.TICKER_REQUIRED_PYDANTIC_MODELS.items(), timeframe):
            print("** ", name, " => ", timer)
            json_value = self.timeframe_data_output_parser(timeframe_pydantic_model=pydantic_model, timeframe=timer)
            json_input[name + "_json"] = json_value  # .model_dump_json()

        print()
        print("Ticker Ananlysis")
        print()
        return self.generic_output_parser(pydantic_model=_pydantic_models.TickerTechnicalAnalysis, system_prompt_template=self.TICKER_SYSTEM_TEMPLATE,
                                          input_variables=list(json_input.keys()), json_docs=json_input)
