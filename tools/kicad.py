from decimal import Decimal


type Attribute = Node | bool | float | int | str


class Node:
    def __init__(self, name: str, *attributes: Attribute) -> None:
        self._name = name
        self._attributes = list(attributes)

    def append(self, *attributes: Attribute) -> None:
        self._attributes += attributes

    def serialize(self, indentation: str = "") -> str:
        result = f"{indentation}({self._name}"

        for attribute in self._attributes:
            match attribute:
                case Node():
                    result += f"\n{attribute.serialize(indentation + "\t")}"
                case bool():
                    result += f" {"yes" if attribute else "no"}"
                case float():
                    result += f" {Decimal(f"{attribute:.12g}"):zf}"
                case _:
                    result += f" {attribute}"

        if "\n" in result:
            result += f"\n{indentation}"

        return f"{result})"


def property_node(property: str, value: str, *attributes: Attribute) -> Node:
    return Node("property", quote(property), quote(value), *attributes)


def quote(value: int | str) -> str:
    return f'"{value}"'
