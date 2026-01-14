import PIL.Image

from skillweaver.util import J
from skillweaver.lm import LM


async def check_success_simple(
    lm: LM, task: str, trajectory_stringified: str, final_screenshot: PIL.Image.Image
):
    return await lm(
        [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Please observe the following action log of someone using a computer. They were trying to do the following task: {task}. Given this log and the screenshot of their screen at the end of their attempt, please conclude whether they were successful.\n\nTrajectory:\n{trajectory_stringified}",
                    },
                    lm.image_url_content_piece(final_screenshot),
                ],
            }
        ],
        json_schema=J.struct(step_by_step_reasoning=J.string(), success=J.boolean()),
    )
