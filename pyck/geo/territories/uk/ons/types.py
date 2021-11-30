from dataclasses import dataclass


class OnsCodeType:
    WESTMINSTER_CONSTITUENCY_ENGLAND = "E14"
    WESTMINSTER_CONSTITUENCY_WALES = "W07"
    WESTMINSTER_CONSTITUENCY_SCOTLAND = "S14"
    WESTMINSTER_CONSTITUENCY_NI = "N06"


@dataclass
class OnsCode:
    code: str
    label: str

    def is_type(self, *types: str) -> bool:
        return next((True for t in types if self.code.startswith(t)), False)

    @property
    def is_westminster_constituency(self) -> bool:
        return self.is_type(
            OnsCodeType.WESTMINSTER_CONSTITUENCY_ENGLAND,
            OnsCodeType.WESTMINSTER_CONSTITUENCY_WALES,
            OnsCodeType.WESTMINSTER_CONSTITUENCY_SCOTLAND,
            OnsCodeType.WESTMINSTER_CONSTITUENCY_NI,
        )
