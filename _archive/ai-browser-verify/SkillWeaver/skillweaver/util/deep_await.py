from asyncio import iscoroutine


async def deep_await(obj, awaits: list, path="retval"):
    if type(obj) == list:
        return [await deep_await(o, awaits, f"{path}[{i}]") for i, o in enumerate(obj)]
    elif type(obj) == dict:
        return {
            k: await deep_await(v, awaits, f"{path}[{repr(k)}]") for k, v in obj.items()
        }
    elif iscoroutine(obj):
        awaits.append(path)
        result = await obj
        return await deep_await(result, awaits, f"(await {path})")
    else:
        return obj
