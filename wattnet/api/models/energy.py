from abc import ABC, abstractmethod

from pydantic import BaseModel


class Energy(ABC, BaseModel):
    """Base class for all energy-related classes."""

    @abstractmethod
    def __init__(self, amount: float, unit: str, production_type: str):
        """Constructor.

        :param amount: The amount of energy
        :type amount: float

        :param unit: The unit of energy
        :type unit: str

        :param production_type: The type of production
        :type production_type: str
        """

        self.amount = amount
        self.unit = unit
        self.production_type = production_type

    @abstractmethod
    def __str__(self):
        pass


class Generation(Energy):
    """Class representing the generation of energy.
    - Generation is always to a specific production type.
    """

    def __init__(self, amount: float, unit: str, production_type: str):
        """Constructor.

        :param amount: The amount of energy
        :type amount: float

        :param unit: The unit of energy
        :type unit: str

        :param production_type: The type of production
        :type production_type: str
        """

        super().__init__(amount, unit, production_type)

    def __str__(self):
        return f"Generation: {self.production_type}: {self.amount} {self.unit}"


class Import(Energy):
    """Class representing the import of energy.
    - Imports are always to the MIX production type.
    - Imports are from a source zone.
    """

    def __init__(self, amount: float, unit: str, source: str):
        """Constructor.

        :param amount: The amount of energy
        :type amount: float

        :param unit: The unit of energy
        :type unit: str

        :param source: The source of the import
        :type source: str
        """
        super().__init__(amount, unit, "mix")
        self.source = source

    def __str__(self):
        return f"Import: {self.amount} {self.unit} from ({self.source})"


class Export(Energy):
    """Class representing the export of energy.
    - Exports are always to the MIX production type.
    - Exports are to a target zone.
    """

    def __init__(self, amount: float, unit: str, target: str):
        """Constructor.

        :param amount: The amount of energy
        :type amount: float

        :param unit: The unit of energy
        :type unit: str

        :param target: The target of the export
        :type target: str
        """
        super().__init__(amount, unit, "mix")
        self.target = target

    def __str__(self):
        return f"Export: {self.amount} {self.unit} to ({self.target})"
