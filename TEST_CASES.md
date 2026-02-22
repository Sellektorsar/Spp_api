# Документация по Интеграционным Тест-Кейсам

Этот документ содержит описание всех автоматизированных интеграционных тестов API, расположенных в директории `tests/integration/`. Тесты проверяют взаимодействие с реальным сервером SPP API.

## 1. Управление сессиями агрегации (Aggregation Session)
**Файл:** `tests/integration/test_aggregation_session.py`
**Описание:** Проверяет управление сессиями агрегации: создание, фильтрация, статистика, получение иерархии деталей. Тесты жизненного цикла используют выделенную тестовую линию.

### Класс: TestAggregationSessionFilter
*   **test_filter_all_sessions**
    *   Получение списка всех сессий агрегации. Проверяет наличие полей `total_count` и `result`.
*   **test_filter_sessions_pagination**
    *   Проверка пагинации: параметры `limit` и `offset` корректно обрабатываются сервером.
*   **test_filter_sessions_with_limit**
    *   Фильтрация с ограниченным лимитом записей.

### Класс: TestAggregationSessionDetail
*   **test_get_session_detail_real**
    *   Получение иерархии вложенности реальной сессии. Для надежности тест сначала запрашивает свежий ID из списка сессий.
*   **test_get_session_detail_nonexistent**
    *   Запрос несуществующей сессии по ID (ожидается ошибка 400/404/422).
*   **test_get_session_stats**
    *   Получение статистики по конкретной сессии за период.
*   **test_get_global_stats**
    *   Получение глобальной статистики агрегации (без указания ID сессии).

### Класс: TestAggregationSessionLifecycle
*   **test_start_pallets_session**
    *   Запуск новой pallets-сессии на тестовой линии. Проверяет параметры `line_number`, `read_type`, `print_type`.
*   **test_add_code_to_pallets_session**
    *   Добавление GS1-кода в активную pallets-сессию.
*   **test_add_package_to_pallets_session**
    *   Добавление SSCC-упаковки в активную pallets-сессию (Негативный тест: используется фиктивный код, ожидается ошибка валидации).
*   **test_add_pallet_to_pallets_session**
    *   Добавление поддона в активную pallets-сессию.
*   **test_finish_pallets_session**
    *   Завершение pallets-сессии по номеру линии.
*   **test_create_dashboard_session**
    *   Создание dashboard-сессии агрегации (отдельный тип сессии).

### Класс: TestAggregationSessionCorrections
*   **test_withdrawal_code_nonexistent**
    *   Попытка изъятия несуществующего кода из упаковки (ожидается ошибка).
*   **test_disbandment_package_nonexistent**
    *   Попытка расформирования несуществующей упаковки (ожидается ошибка).

---

## 2. Авторизация (Auth)
**Файл:** `tests/integration/test_auth.py`
**Описание:** Проверяет эндпоинт авторизации `/api/web/v1/auth`.

### Класс: TestAuth
*   **test_login_success**
    *   Успешный вход с валидными учетными данными. Проверяет получение Bearer-токена.
*   **test_login_invalid_credentials**
    *   Попытка входа с неверным паролем (ожидается 400/401/403).
*   **test_login_missing_fields**
    *   Попытка входа с отсутствующими обязательными полями (ожидается 400/422).

---

## 3. Сквозные цепочки (Chain Scenarios)
**Файл:** `tests/integration/test_chain.py`
**Описание:** Демонстрирует сквозное чтение данных между подсистемами: GTIN -> Смены -> Сессии.

*   **test_gtin_to_shift_chain**
    *   Цепочка: Найти GTIN для товарной группы -> Убедиться в его наличии -> Получить смены на соответствующей линии.
*   **test_multi_product_group_chain**
    *   Последовательная проверка наличия GTIN для 5 разных товарных групп.
*   **test_active_shifts_across_lines**
    *   Проверка наличия активных смен одновременно на нескольких линиях.
*   **test_shift_and_aggregation_session_chain**
    *   Проверка существования активной смены и агрегационной сессии в системе.
*   **test_create_shift_and_finish_chain**
    *   Полный цикл: Старт тестовой смены -> Проверка фильтром -> Завершение смены.

---

## 4. Управление оборудованием (Devices & Printers)
**Файл:** `tests/integration/test_devices_and_printers.py`
**Описание:** Управление устройствами (сканеры, камеры) и принтерами этикеток.

### Класс: TestDeviceManagement
*   **test_filter_devices_default**
    *   Получение списка всех устройств.
*   **test_filter_devices_pagination**
    *   Проверка пагинации списка устройств.
*   **test_real_device_in_list**
    *   Проверка наличия реального рабочего устройства в списке.
*   **test_add_new_device**
    *   Регистрация нового тестового устройства.
*   **test_block_test_device**
    *   Блокировка тестового устройства.
*   **test_delete_test_device**
    *   Удаление тестового устройства.
*   **test_block_nonexistent_device**
    *   Блокировка несуществующего устройства (ожидается ошибка).
*   **test_delete_nonexistent_device**
    *   Удаление несуществующего устройства (ожидается ошибка).

### Класс: TestPrinterManagement
*   **test_filter_printers_default**
    *   Получение списка принтеров.
*   **test_real_printer_in_list**
    *   Проверка наличия реального принтера в списке.
*   **test_toggle_printer_favorite**
    *   Переключение статуса "Избранный" для принтера.
*   **test_send_to_print_by_gtin_milk**
    *   Отправка задания на печать по GTIN.
*   **test_send_to_print_by_gtin_invalid_printer**
    *   Отправка задания на несуществующий принтер (ожидается ошибка).
*   **test_add_printer**
    *   Добавление нового принтера.
*   **test_delete_test_printer**
    *   Удаление тестового принтера.
*   **test_filter_printers_pagination**
    *   Проверка пагинации списка принтеров.

---

## 5. Управление линиями и GTIN (GTIN & Line Management)
**Файл:** `tests/integration/test_gtin_and_line.py`
**Описание:** Проверка справочников производственных линий и GTIN.

### Класс: TestLineManagement
*   **test_filter_lines_default**
    *   Получение списка линий без фильтров.
*   **test_filter_lines_by_product_group_milk**
    *   Фильтрация линий по товарной группе 'milk'.
*   **test_filter_lines_by_product_group_water**
    *   Фильтрация линий по товарной группе 'water'.
*   **test_filter_lines_all_product_groups**
    *   Проверка наличия линий для всех ключевых товарных групп.
*   **test_create_line**
    *   Создание новой производственной линии.
*   **test_edit_line_created**
    *   Редактирование созданной линии.
*   **test_delete_line_created**
    *   Деактивация (удаление) созданной линии.
*   **test_recover_line_created**
    *   Восстановление деактивированной линии.
*   **test_filter_lines_pagination**
    *   Проверка пагинации списка линий.
*   **test_edit_nonexistent_line**
    *   Редактирование несуществующей линии (идемпотентность, 200 OK).
*   **test_delete_nonexistent_line**
    *   Удаление несуществующей линии (Known Issue: сервер может вернуть 500).
*   **test_recover_nonexistent_line**
    *   Восстановление несуществующей линии (идемпотентность, 200 OK).
*   **test_filter_lines_per_product_group**
    *   Параметризованный тест: фильтрация линий для каждой из 29 товарных групп.

### Класс: TestGTINManagement
*   **test_filter_gtin_default**
    *   Получение списка GTIN.
*   **test_filter_gtin_milk**
    *   Фильтрация GTIN по группе 'milk'.
*   **test_filter_gtin_water**
    *   Фильтрация GTIN по группе 'water'.
*   **test_filter_gtin_shoes**
    *   Фильтрация GTIN по группе 'shoes'.
*   **test_filter_gtin_all_known_groups**
    *   Проверка наличия GTIN для всех 30 товарных групп.
*   **test_add_existing_gtin**
    *   Попытка добавления уже существующего GTIN.
*   **test_edit_gtin_milk**
    *   Редактирование записи GTIN (обновление имени).
*   **test_filter_gtin_by_gtin_value**
    *   Поиск GTIN по конкретному значению.
*   **test_filter_gtin_pagination**
    *   Проверка пагинации GTIN.

---

## 6. Расширенное управление линиями (Line Management Extended)
**Файл:** `tests/integration/test_line_management.py`
**Описание:** Дополнительные проверки CRUD операций над линиями.

*   **test_filter_lines_returns_data**
    *   Базовая проверка, что фильтр возвращает непустой список.
*   **test_filter_lines_by_model**
    *   Фильтрация с использованием Pydantic модели `LineFilterInput`.
*   **test_filter_lines_milk_has_line**
    *   Проверка наличия минимум одной линии для 'milk'.
*   **test_create_and_find_line**
    *   Полный цикл: Создание -> Проверка видимости -> Редактирование -> Удаление -> Восстановление.

---

## 7. Управление заказами (Orders)
**Файл:** `tests/integration/test_orders.py`
**Описание:** Проверка работы с заказами на эмиссию КМ через Network Proxy.

### Класс: TestOrderRetrieval
*   **test_get_order_form_data**
    *   Получение данных для формы заказа (доступные группы и GTIN).
*   **test_get_order_statistics**
    *   Получение статистики заказов.
*   **test_get_contract_areas**
    *   Получение контрактных зон (поставщиков кодов).
*   **test_get_approvable_orders**
    *   Получение списка заказов, ожидающих подтверждения.
*   **test_get_order_by_nonexistent_id**
    *   Запрос заказа с несуществующим ID (ожидается ошибка).

### Класс: TestOrderCreation
*   **test_create_order_invalid_gtin**
    *   Создание заказа с невалидным GTIN (ожидается ошибка).
*   **test_create_order_zero_quantity**
    *   Создание заказа с нулевым количеством (ожидается ошибка).
*   **test_create_order_negative_quantity**
    *   Создание заказа с отрицательным количеством (ожидается ошибка).
*   **test_create_order_missing_gtin**
    *   Создание заказа без GTIN (ожидается ошибка).
*   **test_create_order_real_gtin**
    *   Создание заказа с реальным GTIN.

### Класс: TestOrderWorkflow
*   **test_approve_nonexistent_order**
    *   Подтверждение несуществующего заказа (ожидается ошибка).
*   **test_reject_nonexistent_order_manual**
    *   Ручное отклонение несуществующего заказа (ожидается ошибка).
*   **test_approve_invalid_id_format**
    *   Подтверждение заказа с невалидным форматом ID (ожидается ошибка).

---

## 8. Отчеты (Reports)
**Файл:** `tests/integration/test_reports.py`
**Описание:** Проверка работы с отчетами: фильтрация, ввод в оборот, нанесение, агрегация.

### Класс: TestReportFilter
*   **test_filter_reports_default**
    *   Получение списка отчетов.
*   **test_filter_reports_by_type_...**
    *   Серия тестов фильтрации по типам: ввод в оборот (2), нанесение (1), агрегация (31).
*   **test_filter_reports_by_status_...**
    *   Серия тестов фильтрации по статусам: новый (0), отправлен (102), ошибка (103).
*   **test_report_statistics**
    *   Получение статистики по отчетам.
*   **test_filter_reports_real_error_report**
    *   Проверка наличия отчета с ошибкой в списке.
*   **test_filter_reports_pagination**
    *   Проверка пагинации отчетов.

### Класс: TestSendCirculation
*   **test_send_circulation_finished_shift**
    *   Отправка отчета о вводе в оборот по завершенной смене.
*   **test_send_circulation_missing_inn**
    *   Отправка без ИНН (ожидается ошибка).
*   **test_send_circulation_nonexistent_shift**
    *   Отправка по несуществующей смене (ожидается ошибка).

### Класс: TestSendUtilisation
*   **test_send_utilisation_finished_shift**
    *   Отправка отчета о нанесении по завершенной смене.
*   **test_send_utilisation_by_aggregation_session**
    *   Отправка отчета о нанесении по агрегационной сессии.

### Класс: TestSendAggregation
*   **test_send_aggregation_report**
    *   Отправка отчета об агрегации.
*   **test_send_atk_report**
    *   Отправка отчета АТК (таможенная агрегация).

### Класс: TestReportManagement
*   **test_resend_error_report**
    *   Повторная отправка отчета со статусом ошибки.
*   **test_set_report_status_to_sent**
    *   Ручная установка статуса отчета "отправлен".
*   **test_real_report_ids_are_valid**
    *   Верификация существования всех тестовых ID отчетов в системе.

---

## 9. Отгрузка (Shipment)
**Файл:** `tests/integration/test_shipment.py`
**Описание:** Управление отгрузками.

### Класс: TestShipment
*   **test_filter_shipments_default**
    *   Получение списка отгрузок.
*   **test_filter_active_shipments**
    *   Фильтрация только активных отгрузок.
*   **test_filter_finished_shipments**
    *   Фильтрация только завершенных отгрузок.
*   **test_start_shipment_validation**
    *   Валидация запуска отгрузки (проверка ответа сервера).

---

## 10. Склад (Warehouse)
**Файл:** `tests/integration/test_warehouse.py`
**Описание:** Управление складскими остатками (рулонами).

### Класс: TestWarehouse
*   **test_filter_rolls_default**
    *   Получение списка рулонов на складе.
*   **test_filter_rolls_by_product_group**
    *   Фильтрация рулонов по товарной группе.
*   **test_get_roll_metadata**
    *   Получение метаданных конкретного рулона (по unit_serial_number).

---

## 11. Рабочие смены (Work Shift)
**Файл:** `tests/integration/test_work_shift.py`
**Описание:** Жизненный цикл рабочих смен: старт, работа, завершение.

### Класс: TestWorkShiftFilter
*   **test_filter_all_shifts**
    *   Получение списка всех смен.
*   **test_filter_shifts_by_line_...**
    *   Фильтрация смен по линиям (milk, water).
*   **test_filter_shifts_pagination**
    *   Проверка пагинации.
*   **test_active_shift_milk_exists**
    *   Проверка наличия активной смены в системе.

### Класс: TestWorkShiftLifecycle
*   **test_start_shift_milk**
    *   Старт новой рабочей смены на тестовой линии.
*   **test_add_code_to_created_shift**
    *   Добавление кода маркировки в созданную смену.
*   **test_finish_created_shift**
    *   Завершение созданной смены.
*   **test_start_shift_invalid_line**
    *   Старт смены с невалидным номером линии (ожидается ошибка).
*   **test_finish_nonexistent_shift**
    *   Завершение несуществующей смены (ожидается ошибка).

### Класс: TestWorkShiftActiveShifts
*   **test_active_shift_..._exists**
    *   Серия тестов на существование активных смен для различных товарных групп (read-only проверка).
