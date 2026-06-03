# from traders import Trader
# from typing import List
# import asyncio
# from tracers import LogTracer
# from agents import add_trace_processor
# from market import is_market_open
# from dotenv import load_dotenv
# import os

# load_dotenv(override=True)

# RUN_EVERY_N_MINUTES = int(os.getenv("RUN_EVERY_N_MINUTES", "60"))
# RUN_EVEN_WHEN_MARKET_IS_CLOSED = (
#     os.getenv("RUN_EVEN_WHEN_MARKET_IS_CLOSED", "false").strip().lower() == "true"
# )
# USE_MANY_MODELS = os.getenv("USE_MANY_MODELS", "false").strip().lower() == "true"

# names = ["Warren", "George", "Ray", "Cathie"]
# lastnames = ["Patience", "Bold", "Systematic", "Crypto"]

# if USE_MANY_MODELS:
#     model_names = [
#         "gpt-4.1-mini",
#         "deepseek-chat",
#         "gemini-2.5-flash-preview-04-17",
#         "grok-3-mini-beta",
#     ]
#     short_model_names = ["GPT 4.1 Mini", "DeepSeek V3", "Gemini 2.5 Flash", "Grok 3 Mini"]
# else:
#     model_names = ["gpt-4o-mini"] * 4
#     short_model_names = ["GPT 4o mini"] * 4


# def create_traders() -> List[Trader]:
#     traders = []
#     for name, lastname, model_name in zip(names, lastnames, model_names):
#         traders.append(Trader(name, lastname, model_name))
#     return traders


# async def run_every_n_minutes():
#     add_trace_processor(LogTracer())
#     traders = create_traders()
#     while True:
#         if RUN_EVEN_WHEN_MARKET_IS_CLOSED or is_market_open():
#             await asyncio.gather(*[trader.run() for trader in traders])
#         else:
#             print("Market is closed, skipping run")
#         await asyncio.sleep(RUN_EVERY_N_MINUTES * 60)


# if __name__ == "__main__":
#     print(f"Starting scheduler to run every {RUN_EVERY_N_MINUTES} minutes")
#     asyncio.run(run_every_n_minutes())

from traders import (
    Trader,
    adesso_model,
    vultr_model,
    cerebras_model,
    groq_model,
)
from typing import List
import asyncio
from tracers import LogTracer
from agents import add_trace_processor
from market import is_market_open
from dotenv import load_dotenv
import os

load_dotenv(override=True)

RUN_EVERY_N_MINUTES = int(os.getenv("RUN_EVERY_N_MINUTES", "60"))
RUN_EVEN_WHEN_MARKET_IS_CLOSED = (
    os.getenv("RUN_EVEN_WHEN_MARKET_IS_CLOSED", "false").strip().lower() == "true"
)
USE_MANY_MODELS = os.getenv("USE_MANY_MODELS", "false").strip().lower() == "true"

names = ["Warren", "George", "Ray", "Cathie"]
lastnames = ["Patience", "Bold", "Systematic", "Crypto"]

if USE_MANY_MODELS:
    trader_models = [
        adesso_model,
        vultr_model,
        cerebras_model,
        groq_model,
    ]

    short_model_names = [
        "Adesso - gpt-oss-120b-sovereign",
        "Vultr - nvidia/DeepSeek-V3.2-NVFP4",
        "Cerebras - zai-glm-4.7",
        "Groq - llama-3.3-70b-versatile",
    ]
else:
    trader_models = [vultr_model] * 4
    short_model_names = ["Vultr - nvidia/DeepSeek-V3.2-NVFP4"] * 4


def create_traders() -> List[Trader]:
    traders = []

    for name, lastname, model, short_model_name in zip(
        names,
        lastnames,
        trader_models,
        short_model_names,
    ):
        print(f"Creating trader {name} {lastname} with model: {short_model_name}")
        traders.append(Trader(name, lastname, model))

    return traders


async def run_every_n_minutes():
    add_trace_processor(LogTracer())
    traders = create_traders()

    while True:
        if RUN_EVEN_WHEN_MARKET_IS_CLOSED or is_market_open():
            await asyncio.gather(*[trader.run() for trader in traders])
        else:
            print("Market is closed, skipping run")

        await asyncio.sleep(RUN_EVERY_N_MINUTES * 60)


if __name__ == "__main__":
    print(f"Starting scheduler to run every {RUN_EVERY_N_MINUTES} minutes")
    asyncio.run(run_every_n_minutes())