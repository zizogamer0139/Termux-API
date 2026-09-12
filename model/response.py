from __future__ import annotations


class ResponseEngine:

    def generate(
        self,
        result: dict,
    ) -> str:

        response = result.get("response")

        if response is not None:
            return str(response)

        return (
            "I wasn't able to construct a response."
        )


response_engine = ResponseEngine()