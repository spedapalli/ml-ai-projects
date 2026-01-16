import re

class DocumentChunker:

    @classmethod
    def chunk_documents(cls, documents:list[str], min_length:int = 1000, max_length:int = 2000) -> list[str]:
        chunked_docs = []
        for document in documents:
            chunks = cls._extract_substrings_(document, min_len=min_length, max_len=max_length)
            chunked_docs.extend(chunks)

        return chunked_docs


    @classmethod
    def _extract_substrings_(cls, txt, min_len:int, max_len:int) -> list[str]:

        sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s", txt)

        extracts = []
        current_chunk = ""
        for sentence in sentences :
            sentence = sentence.strip()
            if not sentence:
                continue

            # c + s < min len - continue
            # c + s >= min len & < max_len - check if adding chunk blows max len, add and reset. Else continue
            # c + s <= max len
            # c + s > max len

            # current chunk with abv sentence does not exceed max len. Take care of below scenarios :
            # (1) first iteration, (2) all cases where len is less than max length
            if len(current_chunk) + len(sentence) <= max_len:
                current_chunk += sentence + " "

            else:
                # handles scenario : greater than min len and less than max len
                if len(current_chunk) >= min_len:
                    extracts.append(current_chunk.strip())

                current_chunk = sentence + " "

        if len(current_chunk) >= min_len:
            extracts.append(current_chunk.strip())

        return extracts


