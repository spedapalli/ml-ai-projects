import opik
from langchain_openai import ChatOpenAI
# from langchain.prompts import PromptTemplate
from opik.integrations.langchain import OpikTracer


from core.config import settings
from core.rag.prompt_templates import QueryExpansionTemplate

class QueryExpansion:
    """ In

    Returns:
        _type_: _description_
    """
    # for observability
    opik_tracer = OpikTracer(tags=["QueryExpansion"])

    @staticmethod
    @opik.track(name="QueryExpansion.generate_response")
    def generate_response(query:str, to_expand_to_n: int) -> list[str]:
        query_expansion_template = QueryExpansionTemplate()
        prompt = query_expansion_template.create_template(to_expand_to_n)
        model = ChatOpenAI(
            model=settings.OPENAI_MODEL_ID,
            api_key=settings.OPENAI_API_KEY,
            temperature=0,
        )
        chain = prompt | model
        chain = chain.with_config({"callbacks": [QueryExpansion.opik_tracer]})

        response = chain.invoke({"question": query}, config={"callbacks": [QueryExpansion.opik_tracer]})

        # Below are other ways to call the template
        # prompt_response = prompt.invoke({"question": query}, config={"callbacks": [QueryExpansion.opik_tracer]})
        # response = model.invoke(prompt_response, config={"callbacks": [QueryExpansion.opik_tracer]})
        response = response.content

        queries = response.strip().split(query_expansion_template.separator)
        stripped_queries = [
            stripped_item for item in queries if (stripped_item := item.strip(" \\n"))
        ]

        return stripped_queries
