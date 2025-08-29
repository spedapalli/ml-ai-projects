from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# ref to project root dir
ROOT_DIR = str(Path(__file__).parent.parent.parent)

class AppSettings(BaseSettings) :
    model_config = SettingsConfigDict(env_file=ROOT_DIR, env_file_encoding='utf-8')

    MONGO_DATABASE_HOST: str= (
        "mongodb://mongo1:30001, mongo2:30002:30003/?replicaSet=my-replica-set"
    )
    MONGO_DATABASE_NAME:str = "twin"

    # MQ config
    RABBITMQ_DEFAULT_USERNAME: str = "guest"
    RABBITMQ_DEFAULT_PASSWORD: str = "guest"
    RABBITMQ_HOST: str = "mq"
    RABBITMQ_PORT: int = 5673

    #QdrantDB config
    QDRANT_CLOUD_URL:str = "str"
    QDRANT_DATABASE_HOST:str = "qdrant"
    QDRANT_DATABASE_PORT:int = 6333
    USE_QDRANT_CLOUD:bool = False
    QDRANT_API_KEY:str | None = None

    # OpenAI config
    OPENAI_MODEL_ID: str = "gpt-4o-mini"
    OPENAI_API_KEY: str | None = None

    # ComentML config
    COMET_API_KEY: str | None = None
    COMET_WORKSPACE: str | None = None
    COMET_PROJECT: str = "llm-twin"

    # AWS Authentication
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY:str | None = None
    AWS_SECRET_KEY: str | None = None
    AWS_ARN_ROLE: str | None = None

    #LLM Model config
    HUGGINGFACE_ACCESS_TOKEN: str | None = None
    MODEL_ID: str = "pauliusztin/LLMTwin-Llama-3.1-8B"
    DEPLOYMENT_ENDPOINT_NAME: str = "twin"

    MAX_INPUT_TOKENS: int = 1536    # max length of input text
    MAX_TOTAL_TOKENS: int = 2048    # max length of generation (incl input)
    MAX_BATCH_TOTAL_TOKENS: int = 2048  #limits # of tokens that can be processed in parallel during generation

    # Embeddings config
    EMBEDDING_MODEL_ID: str = "BAAI/bge-small-en-v1.5"
    EMNEDDING_MODEL_MAX_INPUT_LENGTH: int = 512
    EMBEDDING_SIZE: int = 348
    EMBEDDING_MODEL_DEVICE: str = "cpu"

    def patch_localhost(self) -> None:
        self.MONGO_DATABASE_HOST = "mongodb://localhost:30001, localhost:30002, localhost:30003/?replicaSet=my-replica-set"
        self.QDRANT_DATABASE_HOST = "localhost"
        self.RABBITMQ_HOST = "localhost"

settings = AppSettings()



