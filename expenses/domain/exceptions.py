class ExpenseDomainError(Exception):
    """Excepción base para errores del dominio de gastos."""


class ExpenseBuildError(ExpenseDomainError):
    """Se lanza cuando no se puede construir un gasto válido."""


class BudgetNotFoundError(ExpenseDomainError):
    """Se lanza cuando no existe un presupuesto para validar el gasto."""