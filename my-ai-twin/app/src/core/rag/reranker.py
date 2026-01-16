from core.config import settings
from langchain_openai import ChatOpenAI

from core.rag.prompt_templates import ReRankingTemplate
from core.rag.cross_encoders import CrossEncoderModelSingleton

class ReRanker:

    @staticmethod
    def generate_response_using_llm(query:str, passages: list[str], keep_top_k: int) -> list[str]:
        reranking_template = ReRankingTemplate()
        prompt = reranking_template.create_template(keep_top_k = keep_top_k)
        model = ChatOpenAI(
            model=settings.OPENAI_MODEL_ID,
            api_key= settings.OPENAI_API_KEY
        )
        chain = prompt | model

        stripped_passages = [
            stripped_item for item in passages if (stripped_item := item.strip())
        ]
        passages_str = reranking_template.separator.join(stripped_passages)
        ## - replaced below line with further below given the error "cannot import name PipelinePromptTemplate...."
        response = chain.invoke({"question": query, "passages": passages_str})
        # prompt_response = prompt.invoke({"question": query, "passages": passages_str})
        # response = model.invoke(prompt_response)

        response = response.content

        reranked_passages = response.strip().split(reranking_template.separator)
        stripped_passages = [
            stripped_item for item in reranked_passages if (stripped_item := item.strip())
        ]

        return stripped_passages


    @staticmethod
    def generate_response_using_crossencoder(
                query: str,
                passages: list[str]) -> list[str]:

        pairs = [[query, f"{passage.text}"] for passage in passages]
        cross_encoder = CrossEncoderModelSingleton()
        ranked_pairs = cross_encoder(pairs)
        sorted_ranked_pairs = sorted(zip(passages, ranked_pairs), key= lambda x: x[1], reverse=True)

        final_ranked_pairs = []
        for passage, rank_score in sorted_ranked_pairs:
            final_ranked_pairs.append(passage)

        return final_ranked_pairs