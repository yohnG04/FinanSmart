class ExpenseDomainError(Exception):
    """Excepción base para errores del dominio de gastos."""


class ExpenseBuildError(ExpenseDomainError):
    """Se lanza cuando no se puede construir un gasto válido."""


class BudgetNotFoundError(ExpenseDomainError):
    """Se lanza cuando no existe un presupuesto para validar el gasto."""


class IncomeDomainError(Exception):
    """Excepción base para errores del dominio de ingresos."""


class SavingsGoalDomainError(Exception):
    """Excepción base para errores del dominio de metas de ahorro."""


class SavingsContributionDomainError(Exception):
    """Error relacionado con los abonos a una meta de ahorro."""


class CategoryNotFoundError(Exception):
    """Se lanza cuando una categoría no existe o no está activa."""


class SavingsGoalNotFoundError(Exception):
    """Se lanza cuando una meta no pertenece al usuario o no existe."""