from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# ref to project root dir
ROOT_DIR = str(Path(__file__).parent.parent.parent.parent)

class AppSettings(BaseSettings) :
    model_config = SettingsConfigDict(env_file=f"{ROOT_DIR}/.env", env_file_encoding='utf-8', extra='ignore')

    MONGO_DB_1:str = 'mongodb1:30001'
    MONGO_DB_2:str = 'mongodb2:30002'
    MONGO_DB_3:str = 'mongodb3:30003'
    MONGO_REPLICA_SET:str = 'mdb-replica-set'

    MONGO_DATABASE_HOST: str= (
        f"mongodb://{MONGO_DB_1},{MONGO_DB_2},{MONGO_DB_3}/?replicaSet={MONGO_REPLICA_SET}"
    )
    MONGO_DATABASE_NAME:str = "twin"

    # MQ config
    RABBITMQ_DEFAULT_USERNAME: str | None = None
    RABBITMQ_DEFAULT_PASSWORD: str | None = None
    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int =5672

    #QdrantDB config
    QDRANT_CLOUD_URL:str = "str"
    QDRANT_DATABASE_HOST:str = "qdrant"
    QDRANT_DATABASE_PORT:int = 6333
    USE_QDRANT_CLOUD:bool = False
    QDRANT_API_KEY:str | None = None

    # OpenAI config
    OPENAI_MODEL_ID: str = "gpt-4o-mini"
    OPENAI_API_KEY: SecretStr | None = None

    # CometML config
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
    EMBEDDING_MODEL_MINI_ID: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_MODEL_MAX_INPUT_LENGTH: int = 512
    EMBEDDING_SIZE: int = 384 # default size output by the abv model BAAI/bge-small-en-v1.5
    # embedding models for github code
    # EMBEDDING_MODEL_FOR_CODE_ID: str = "hkunlp/instructor-xl"
    # EMBEDDING_MODEL_FOR_CODE_VECTOR_LENGTH: int = 768    # default output size of embeddings by hkunlp/instructor-xl
    EMBEDDING_MODEL_FOR_CODE_ID: str = "BAAI/bge-large-en-v1.5"
    EMBEDDING_MODEL_FOR_CODE_VECTOR_LENGTH: int = 1024    # max input text length for code embeddings
    EMBEDDING_MODEL_DEVICE: str = "cpu"
    EMBEDDING_MODEL_GPU_DEVICE: str = "cuda"

    CROSS_ENCODER_MODEL_ID: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    CROSS_ENCODER_MODEL_DEVICE: str = "cpu" # or cuda

    # Opik config
    OPIK_API_KEY: str | None = None

    def patch_localhost(self) -> None:
        self.MONGO_DATABASE_HOST = "mongodb://localhost:30003/?directConnection=true"
        # self.MONGO_DATABASE_HOST = f"mongodb://localhost:30001,localhost:30002,localhost:30003/?replicaSet={self.MONGO_REPLICA_SET}"
        self.QDRANT_DATABASE_HOST = "localhost"
        self.RABBITMQ_HOST = "localhost"

settings = AppSettings()



