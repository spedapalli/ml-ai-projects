import opik
from langchain_openai import ChatOpenAI
from opik.integrations.langchain import OpikTracer

from core.logger_utils import get_logger
from core.config import settings
from core import string_utils
from models.db.documents import UserDocument
from core.rag.prompt_templates import SelfQueryTemplate

logger = get_logger(__name__)


class SelfQuery:

    opik_tracker = OpikTracer(tags=["SelfQuery"])

    @staticmethod
    @opik.track(name="SelfQuery.generate_response")
    def generate_response(query:str) -> str | None :
        prompt = SelfQueryTemplate().create_template()

        model = ChatOpenAI(
            model=settings.OPENAI_MODEL_ID,
            api_key=settings.OPENAI_API_KEY,
            temperature=0,
        )

        # - replaced below lines with further below given the error "cannot import name PipelinePromptTemplate...."
        # chain = prompt | model
        # chain = chain.with_config({"callbacks": [SelfQuery.opik_tracker]})

        # response = chain.invoke({"question": query})
        prompt_response = prompt.invoke({"question": query}, {"callbacks": [SelfQuery.opik_tracker]})
        response = model.invoke(prompt_response, {"callbacks": [SelfQuery.opik_tracker]})
        response = response.content
        user_full_name = response.strip("\n")

        if user_full_name == "none":
            logger.warn("Unable to retrieve the user full name.")
            return None

        logger.info(f"Successfully extracted the user full name from the query.",
                    user_full_name = user_full_name)

        first_name, last_name = string_utils.split_user_full_name(user_full_name)
        logger.info(f"The extracted user first and last name from the query are: ",
                    first_name = first_name,
                    last_name = last_name)
        user_id = UserDocument.get_or_create(first_name=first_name, last_name=last_name)

        return user_id