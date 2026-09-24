from dataclasses import dataclass
from typing import List, Callable, Iterable


class InputText:
    value: str


class Reference:
    resource_url: str

    def to_text(self) -> str:
        return f"[resource: {self.resource_url}]"


@dataclass
class Draft:
    text: InputText
    references: List[Reference]

    def is_empty(self) -> bool:
        return self.text.value.strip() == "" and len(self.references) == 0

    def get_references(self) -> Iterable[Reference]:
        return self.references


class RichTextInputer:
    on_submit: Callable[[Draft], None]


if __name__ == "__main__":
    inputer = RichTextInputer()


    def on_submit(draft: Draft):
        # check not empty
        if draft.is_empty():
            raise ValueError

        urls_to_upload = []
        for reference in draft.get_references():
            urls_to_upload.append(reference.resource_url)
        pass


    inputer.on_submit = on_submit
    # do something
