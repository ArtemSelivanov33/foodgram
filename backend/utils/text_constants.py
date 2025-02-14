class Message:
    class ErrorMessage:
        """Сообщения об ошибках."""

        NO_ENTRY = 'Ошибка. Нет записи в базе данных для удаления.'
        SUBSCRIPTION_ERROR = 'Ошибка подписки.'
        ADD_ENTRY_ERROR = 'Ошибка добавления записи.'
        ENTRIES_IN_LIST_MORE_THAN_ONE = (
            'Количество элементов словаря должно быть больше 1.'
        )

    class SuccessMessage:
        """Сообщения об успешном результате."""

        ENTRY_ADDED = 'Запись успешно добавлена.'
        SUBSCRIPTION_SUCCESS = 'Подписка успешна.'
