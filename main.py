import warnings


def ignore_pydantic_serialization_userwarning(
    message, category, filename, lineno, file=None, line=None
):
    if category is UserWarning and "PydanticSerializationUnexpectedValue" in str(
        message
    ):
        return
    warnings.showwarning_orig(message, category, filename, lineno, file, line)


warnings.showwarning_orig = warnings.showwarning
warnings.showwarning = ignore_pydantic_serialization_userwarning

if __name__ == "__main__":
    import asyncio
    from app import start_fastapi
    import argparse

    args = argparse.ArgumentParser()
    parsed_args = args.parse_args()
    asyncio.run(start_fastapi(parsed_args))
