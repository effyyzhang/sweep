"""
We should input an updated snippet generated by Sweep, and output the comment that was left in the code
"""

import re

from loguru import logger

from sweepai.core.chat import ChatGPT
from sweepai.core.entities import Message, RegexMatchableBaseModel
from sweepai.utils.comment_utils import check_comments_presence

system_message_prompt = """You are a genius engineer tasked with identifying any incomplete logic for the following code change.
You have been provided with the relevant metadata to the issue.
Please identify and extract any leftover comments from the new_code. If there are none, return empty tags."""

user_prompt = """# Code
File path: {file_path}
# Original request
{request}

<new_code>
{new_code}
</new_code>

Review new_code and provide your response in the format:
<leftover_comments>
<leftover_comment>
leftover comment verbatim from the new_code that mentions incomplete changes like "rest of code here". these comments are written like instructions or notes
</leftover_comment>
...
</leftover_comments>"""


class LeftoverComments(RegexMatchableBaseModel):
    leftover_comments: list[str] = []

    @classmethod
    def from_string(cls, leftover_comments_response: str, **kwargs):
        leftover_comments = []
        leftover_comments_pattern = (
            r"""<leftover_comment>(\n)?(?P<leftover_comment>.*?)</leftover_comment>"""
        )
        for match_ in re.finditer(
            leftover_comments_pattern, leftover_comments_response, re.DOTALL
        ):
            leftover_comment = match_.group("leftover_comment").strip("\n")
            if leftover_comment:
                logger.info(f"leftover_comments: {leftover_comment}")
                leftover_comments.append(leftover_comment)
        return cls(
            leftover_comments=leftover_comments,
        )


class ExtractLeftoverComments(ChatGPT):
    def extract_leftover_comments(self, new_code, file_path, request, **kwargs):
        try:
            if not check_comments_presence(file_path, new_code):
                return []
            self.messages = [Message(role="system", content=system_message_prompt, key="system")]
            response = self.chat(user_prompt.format(new_code = new_code,
                                                     file_path = file_path,
                                                     request = request))
            leftover_comments = LeftoverComments.from_string(response)
            return leftover_comments.leftover_comments
        except SystemExit:
            raise SystemExit
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return []


if __name__ == "__main__":
    leftover_comment_response = """<leftover_comments>
<leftover_comment>
TODO(sweep): We don't handle renamed files
</leftover_comment>
</leftover_comments>"""

    leftover_comments = LeftoverComments.from_string(leftover_comment_response)
    print(leftover_comments.leftover_comments)
