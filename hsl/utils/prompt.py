from noneprompt import ListPrompt, InputPrompt, Choice
from hsl.core.locale import Locale
import asyncio
locale = Locale()
OPTIONS_YN = locale.trans_key(['yes','no'])
async def promptSelect(options: list,prompt: str) -> int:
    choices = [Choice(options[i],data=i) for i in range(len(options))]
    prompt_task = asyncio.create_task(ListPrompt(prompt, choices=choices,annotation=locale.trans_key('choice-prompt-annotation')).prompt_async())
    select = await asyncio.gather(prompt_task)
    return select[0].data
async def promptInput(prompt: str) -> str:
    prompt_task = asyncio.create_task(InputPrompt(prompt, validator=lambda string: True).prompt_async())
    _input = await asyncio.gather(prompt_task)
    return _input[0]
async def promptConfirm(prompt: str) -> bool:
    # prompt_task = asyncio.create_task(ConfirmPrompt(prompt,default_choice=False).prompt_async())
    # confirm = await asyncio.gather(prompt_task)
    # return confirm[0]
    return bool(await promptSelect(OPTIONS_YN,prompt) == 0)